from typing import Type
from processing_types import ProcessingType
from base_processor import BaseProcessor
from processors import (
    ObjectDetectionProcessor,
    FaceDetectionProcessor,
    MotionDetectionProcessor,
    LicensePlateProcessor,
    CrowdCountingProcessor,
    CustomProcessor
)

class ProcessorFactory:
    _processors = {
        ProcessingType.OBJECT_DETECTION: ObjectDetectionProcessor,
        ProcessingType.FACE_DETECTION: FaceDetectionProcessor,
        ProcessingType.MOTION_DETECTION: MotionDetectionProcessor,
        ProcessingType.LICENSE_PLATE: LicensePlateProcessor,
        ProcessingType.CROWD_COUNTING: CrowdCountingProcessor,
        ProcessingType.CUSTOM: CustomProcessor
    }

    @classmethod
    def create(cls, processing_type: ProcessingType, **kwargs) -> BaseProcessor:
        processor_class = cls._processors.get(processing_type)
        if not processor_class:
            raise ValueError(f"Unknown processing type: {processing_type}")
        return processor_class(**kwargs)

    @classmethod
    def register_processor(cls, processing_type: ProcessingType, processor_class: Type[BaseProcessor]):
        cls._processors[processing_type] = processor_class
