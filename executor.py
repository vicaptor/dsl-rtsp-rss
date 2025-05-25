import asyncio
import cv2
import numpy as np
from typing import AsyncIterator, Dict
from pipeline_dsl import Pipeline, ProcessingType
from urllib.parse import urlparse, quote
import logging
from rss_service import RSSFeedService
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Executor:
    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline
        self.running = False
        self.rss_service = RSSFeedService(pipeline.output)

    async def start(self):
        self.running = True
        try:
            # Start RSS service
            await self.rss_service.start()
            
            # Process stream
            async for result in self._process_stream():
                # Save frame image and add URL to results
                image_url = self.rss_service.save_frame(result.pop('frame'), result['timestamp'])
                if image_url:
                    result['image_url'] = image_url
                
                self.rss_service.add_event(result)
        finally:
            self.running = False
            logger.info("Pipeline execution stopped")

    def _build_rtsp_url(self, source) -> str:
        """Build authenticated RTSP URL with credentials if provided."""
        if not hasattr(source, 'credentials') or not source.credentials:
            return source.uri
            
        parsed = urlparse(source.uri)
        username = quote(source.credentials.get('username', ''))
        password = quote(source.credentials.get('password', ''))
        
        # Reconstruct URL with auth credentials
        auth_url = f"rtsp://{username}:{password}@{parsed.netloc}{parsed.path}"
        if parsed.query:
            auth_url += f"?{parsed.query}"
            
        return auth_url

    async def _process_stream(self) -> AsyncIterator[Dict]:
        """Process RTSP stream and yield frames."""
        # Build authenticated RTSP URL
        rtsp_url = self._build_rtsp_url(self.pipeline.source)
        logger.info(f"Connecting to RTSP stream...")
        
        # Connect to RTSP source
        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            raise ConnectionError(f"Failed to connect to RTSP stream")

        logger.info("Successfully connected to RTSP stream")
        
        try:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Failed to read frame, retrying...")
                    await asyncio.sleep(1)
                    continue

                # Process frame
                processed_frame = await self._process_frame(frame)
                yield processed_frame
                
                # Control frame rate
                await asyncio.sleep(1/30)  # 30 fps
        finally:
            cap.release()
            logger.info("Released RTSP stream")

    async def _process_frame(self, frame: np.ndarray) -> Dict:
        """Process a single frame according to pipeline steps."""
        results = {
            'timestamp': datetime.now(timezone.utc).timestamp(),
            'frame_size': frame.shape,
            'frame': frame  # Store original frame for saving
        }
        
        # Basic frame processing
        # In a full implementation, this would integrate with ML models
        # For now, we'll just do basic frame analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        results['brightness'] = mean_brightness
        
        # Add motion detection
        if hasattr(self, 'last_frame'):
            diff = cv2.absdiff(self.last_frame, gray)
            motion = np.mean(diff) > 25
            results['motion_detected'] = motion
        
        self.last_frame = gray
        return results
