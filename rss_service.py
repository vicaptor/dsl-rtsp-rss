import asyncio
from aiohttp import web
import aiofiles
import os
from feedgen.feed import FeedGenerator
from datetime import datetime
import logging
from collections import deque
from typing import Dict, Deque
from urllib.parse import urlparse, urljoin
from datetime import timezone
import cv2
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RSSFeedService:
    def __init__(self, output_config):
        self.config = output_config
        self.items: Deque[Dict] = deque(maxlen=output_config.params.get('max_items', 100))
        self.last_update = datetime.now(timezone.utc)
        self.update_interval = output_config.params.get('update_interval', 60)
        
        # Parse the URI to get host and port
        parsed_uri = urlparse(output_config.uri)
        self.host = parsed_uri.hostname or 'localhost'
        self.port = parsed_uri.port or 8080
        self.path = parsed_uri.path or '/parking/feed'
        
        # Create images directory
        self.images_dir = 'static/images'
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Initialize web app
        self.app = web.Application()
        self.app.router.add_get(self.path, self.handle_feed)
        self.app.router.add_static('/static/images', self.images_dir)
        
        # Base URL for images
        self.base_url = f"http://{self.host}:{self.port}"
        
        # Initialize feed generator
        self.fg = FeedGenerator()
        self.fg.title(output_config.params.get('title', 'Parking Lot Events'))
        self.fg.description(output_config.params.get('description', 'Vehicle detection and license plate recognition events'))
        self.fg.link(href=output_config.uri)
        self.fg.language('en')

    async def start(self):
        """Start the RSS feed service."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        logger.info(f"RSS feed service started at http://{self.host}:{self.port}{self.path}")

    async def save_frame(self, frame: np.ndarray, timestamp: float) -> str:
        """Save frame as image and return its URL."""
        filename = f"frame_{int(timestamp)}.jpg"
        filepath = os.path.join(self.images_dir, filename)
        
        # Save frame as JPEG
        success = cv2.imwrite(filepath, frame)
        if not success:
            logger.error("Failed to save frame image")
            return None
            
        # Return URL for the image
        return urljoin(self.base_url, f"static/images/{filename}")

    def add_event(self, event: Dict):
        """Add a new event to the feed."""
        # Create feed entry
        fe = self.fg.add_entry()
        fe.id(str(event.get('timestamp', datetime.now(timezone.utc).timestamp())))
        
        # Create title based on event type
        title = "Parking Event Detected"
        if event.get('motion_detected'):
            title = "Motion Detected in Parking Area"
        
        fe.title(title)
        
        # Create description from event data
        description = []
        if 'frame_size' in event:
            description.append(f"Frame size: {event['frame_size']}")
        if 'brightness' in event:
            description.append(f"Brightness level: {event['brightness']:.2f}")
        if 'motion_detected' in event:
            description.append(f"Motion detected: {event['motion_detected']}")
        
        # Add image if available
        if 'image_url' in event:
            description.append(f'<img src="{event["image_url"]}" />')
            fe.enclosure(event['image_url'], 0, 'image/jpeg')
            
        fe.description('\n'.join(description))
        
        # Create timezone-aware datetime
        timestamp = event.get('timestamp', datetime.now(timezone.utc).timestamp())
        pub_date = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        fe.pubDate(pub_date)
        
        # Add to items queue
        self.items.append(event)
        self.last_update = datetime.now(timezone.utc)

    async def handle_feed(self, request):
        """Handle RSS feed request."""
        # Generate RSS feed
        feed_xml = self.fg.rss_str(pretty=True)
        return web.Response(
            body=feed_xml,
            content_type='application/rss+xml'
        )
