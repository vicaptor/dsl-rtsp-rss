from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import numpy as np

@dataclass
class Detection:
    class_name: str
    confidence: float
    bbox: tuple  # (x, y, width, height)
    additional_data: Optional[dict] = None

@dataclass
class ProcessingResult:
    processor_type: str
    frame_id: int
    timestamp: float
    detections: List[Detection]

class BaseProcessor(ABC):
    def __init__(self, model_path: Optional[str] = None, confidence: float = 0.5, **kwargs):
        self.model_path = model_path
        self.confidence = confidence
        self.kwargs = kwargs

    @abstractmethod
    def process(self, frame: np.ndarray, frame_id: int, timestamp: float) -> ProcessingResult:
        """Process a single frame and return the results.

        Args:
            frame: Input frame as numpy array
            frame_id: Unique identifier for the frame
            timestamp: Frame timestamp in seconds

        Returns:
            ProcessingResult containing detections and metadata
        """
        pass
