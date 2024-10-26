import asyncio
import logging
from typing import Dict, Any, List
import numpy as np
from processing_types import ProcessingType
from processor_factory import ProcessorFactory
from base_processor import BaseProcessor, ProcessingResult

class PipelineExecutor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config['pipeline']['name']
        self.source = config['pipeline']['source']
        self.output_config = config['pipeline']['output']
        self.processors = self._initialize_processors()
        self.results_queue = asyncio.Queue()

    def _initialize_processors(self) -> List[BaseProcessor]:
        processors = []
        for proc_config in self.config['pipeline']['processing']:
            processor = ProcessorFactory.create(
                processing_type=ProcessingType(proc_config['type']),
                model_path=proc_config.get('model_path'),
                confidence=proc_config.get('confidence', 0.5),
                **proc_config.get('params', {})
            )
            processors.append(processor)
        return processors

    async def process_frame(self, frame: np.ndarray, frame_id: int, timestamp: float) -> List[ProcessingResult]:
        results = []
        for processor in self.processors:
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    processor.process,
                    frame,
                    frame_id,
                    timestamp
                )
                results.append(result)
            except Exception as e:
                logging.error(f"Error processing frame {frame_id} with {processor.__class__.__name__}: {e}")
        return results

    def get_source_uri(self) -> str:
        return self.source['uri']

    def get_source_credentials(self) -> Dict[str, str]:
        return self.source.get('credentials', {})

    def get_output_config(self) -> List[Dict[str, Any]]:
        return self.output_config
