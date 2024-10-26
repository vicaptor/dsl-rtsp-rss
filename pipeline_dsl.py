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
            r'(?:[^:@/]+(?::[^:@/]*)?@)?'    # username:password
            r'(?:'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?))|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'  # ip
            r')'
            r'(?::\d+)?'  # port
            r'(?:/?|[/?][^#\s]*)?$',  # path
            re.IGNORECASE
        )
        return bool(uri_pattern.match(uri))
