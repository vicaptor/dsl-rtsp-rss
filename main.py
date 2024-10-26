# File: pipeline_dsl.py

from dataclasses import dataclass
from typing import List, Dict, Optional
import yaml
from enum import Enum
import re


class ProcessingType(Enum):
    OBJECT_DETECTION = "object_detection"
    FACE_DETECTION = "face_detection"
    MOTION_DETECTION = "motion_detection"
    LICENSE_PLATE = "license_plate"
    CROWD_COUNTING = "crowd_counting"
    CUSTOM = "custom"


@dataclass
class ProcessingStep:
    type: ProcessingType
    model: str
    confidence: float
    params: Dict


@dataclass
class StreamSource:
    uri: str
    protocol: str
    credentials: Optional[Dict] = None
    params: Optional[Dict] = None


@dataclass
class StreamOutput:
    uri: str
    protocol: str
    format: str
    params: Optional[Dict] = None


@dataclass
class ProcessingNode:
    uri: str
    protocol: str
    steps: List[ProcessingStep]


@dataclass
class Pipeline:
    name: str
    source: StreamSource
    processing: ProcessingNode
    output: StreamOutput


class PipelineDSL:
    def __init__(self):
        self.pipelines: Dict[str, Pipeline] = {}

    def load_from_yaml(self, yaml_content: str) -> None:
        try:
            config = yaml.safe_load(yaml_content)
            for pipeline_config in config['pipelines']:
                pipeline = self._parse_pipeline(pipeline_config)
                self.pipelines[pipeline.name] = pipeline
        except Exception as e:
            raise ValueError(f"Failed to parse pipeline configuration: {e}")

    def _parse_pipeline(self, config: Dict) -> Pipeline:
        # Validate source
        if not self._validate_uri(config['source']['uri']):
            raise ValueError(f"Invalid source URI: {config['source']['uri']}")

        # Validate processing
        if not self._validate_uri(config['processing']['uri']):
            raise ValueError(f"Invalid processing URI: {config['processing']['uri']}")

        # Validate output
        if not self._validate_uri(config['output']['uri']):
            raise ValueError(f"Invalid output URI: {config['output']['uri']}")

        return Pipeline(
            name=config['name'],
            source=StreamSource(
                uri=config['source']['uri'],
                protocol=config['source']['protocol'],
                credentials=config['source'].get('credentials'),
                params=config['source'].get('params')
            ),
            processing=ProcessingNode(
                uri=config['processing']['uri'],
                protocol=config['processing']['protocol'],
                steps=[
                    ProcessingStep(
                        type=ProcessingType(step['type']),
                        model=step['model'],
                        confidence=step.get('confidence', 0.5),
                        params=step.get('params', {})
                    )
                    for step in config['processing']['steps']
                ]
            ),
            output=StreamOutput(
                uri=config['output']['uri'],
                protocol=config['output']['protocol'],
                format=config['output']['format'],
                params=config['output'].get('params')
            )
        )

    def _validate_uri(self, uri: str) -> bool:
        uri_pattern = re.compile(
            r'^(?:http|ftp|rtsp|grpc)s?://'  # protocol
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
            r'(?::\d+)?'  # port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(uri_pattern.match(uri))


# File: pipeline_executor.py

import asyncio
import grpc
import cv2
import numpy as np
from typing import AsyncIterator
from pipeline_dsl import Pipeline, ProcessingType


class PipelineExecutor:
    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline
        self.running = False

    async def start(self):
        self.running = True
        try:
            async for result in self._process_stream():
                await self._publish_result(result)
        finally:
            self.running = False

    async def _process_stream(self) -> AsyncIterator[Dict]:
        # Connect to RTSP source
        cap = cv2.VideoCapture(self.pipeline.source.uri)
        if not cap.isOpened():
            raise ConnectionError(f"Failed to connect to {self.pipeline.source.uri}")

        # Connect to gRPC processing service
        async with grpc.aio.insecure_channel(self.pipeline.processing.uri) as channel:
            stub = CameraAIServiceStub(channel)

            while self.running:
                ret, frame = cap.read()
                if not ret:
                    continue

                # Process frame through all steps
                results = {}
                for step in self.pipeline.processing.steps:
                    result = await self._process_step(stub, frame, step)
                    results[step.type.value] = result

                yield results

    async def _process_step(self, stub, frame, step) -> Dict:
        # Convert frame to proto message
        _, buffer = cv2.imencode('.jpg', frame)
        frame_data = buffer.tobytes()

        # Create processing request based on step type
        if step.type == ProcessingType.OBJECT_DETECTION:
            request = DetectionRequest(
                frame_data=frame_data,
                confidence_threshold=step.confidence,
                model_name=step.model,
                **step.params
            )
            response = await stub.DetectObjects(request)
        elif step.type == ProcessingType.FACE_DETECTION:
            request = FaceDetectionRequest(
                frame_data=frame_data,
                confidence_threshold=step.confidence,
                model_name=step.model,
                **step.params
            )
            response = await stub.DetectFaces(request)
        # Add other processing types...

        return self._parse_response(response)

    def _parse_response(self, response) -> Dict:
        # Convert protocol buffer response to dictionary
        return {
            'detections': [
                {
                    'class': det.class_name,
                    'confidence': det.confidence,
                    'bbox': {
                        'x': det.bbox.x,
                        'y': det.bbox.y,
                        'width': det.bbox.width,
                        'height': det.bbox.height
                    }
                }
                for det in response.detections
            ]
        }

    async def _publish_result(self, result: Dict):
        # Publish results to RSS feed
        # Implementation depends on RSS server implementation
        pass


# Example usage

# File: example_pipeline.yaml
example_yaml = """
pipelines:
  - name: parking-lot-monitor
    source:
      uri: rtsp://camera.example.com:554/parking
      protocol: rtsp
      credentials:
        username: admin
        password: pass123
      params:
        framerate: 30
        resolution: 1920x1080

    processing:
      uri: grpc://ai-service.example.com:50051
      protocol: grpc
      steps:
        - type: object_detection
          model: yolov5s
          confidence: 0.5
          params:
            classes: [2, 5, 7]  # car, bus, truck
            nms_threshold: 0.45

        - type: license_plate
          model: plate-recognizer-v2
          confidence: 0.7
          params:
            region: eu
            max_results: 10

    output:
      uri: http://events.example.com/parking/feed
      protocol: rss
      format: xml
      params:
        update_interval: 60
        max_items: 100
        title: "Parking Lot Events"
        description: "Vehicle detection and license plate recognition events"
"""


# File: example_usage.py

async def main():
    # Parse DSL
    dsl = PipelineDSL()
    dsl.load_from_yaml(example_yaml)

    # Get pipeline configuration
    pipeline = dsl.pipelines['parking-lot-monitor']

    # Create and start executor
    executor = PipelineExecutor(pipeline)
    await executor.start()


if __name__ == "__main__":
    asyncio.run(main())