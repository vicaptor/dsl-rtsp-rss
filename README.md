# DSL RTSP RSS Processor

## License

```
#
# Copyright 2025 Tom Sapletta <info@softreck.dev>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
```

## Author
- Tom Sapletta <info@softreck.dev>


A modular video processing pipeline that supports multiple types of detection and processing capabilities, with configurable RTSP input and RSS/RTMP output streams.

## Project Structure

- `processing_types.py` - Defines the supported types of processors
- `base_processor.py` - Contains base classes and data structures
- `processors.py` - Implements specific processor types
- `processor_factory.py` - Factory for creating processor instances
- `pipeline_executor.py` - Main pipeline execution logic
- `example_usage.py` - Example usage with synthetic test video
- `config.yaml` - Pipeline configuration file

## Requirements

- Python 3.x
- OpenCV
- NumPy
- PyYAML

### Local Development Setup

1. Create a new virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```


Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The pipeline is configured using a YAML file (`config.yaml`). The configuration includes:

### Source Configuration
```yaml
source:
  uri: rtsp://camera.example.com/stream
  protocol: rtsp
  credentials:
    username: admin
    password: pass123
```

### Processing Pipeline
Configure multiple processors with their specific parameters:
```yaml
processing:
  - type: object_detection
    model_path: /models/yolov5s.pt
    confidence: 0.5
    params:
      classes: [0, 1, 2]
      nms_threshold: 0.45
```

### Output Streams
Configure RSS and RTMP output streams:
```yaml
output:
  - type: rss
    uri: http://events.example.com/feed
    format: xml
    params:
      update_interval: 60
      max_items: 100

  - type: rtmp
    uri: rtmp://streaming.example.com/live
    format: h264
    params:
      bitrate: 2000k
      fps: 30
```

## Running the Example

```bash
python main.py
```


```bash
python run.py
```

This will display a test window showing a synthetic video (moving white rectangle on black background) with the configured processing pipeline applied. The example demonstrates the pipeline's functionality without requiring actual video input.

In production, the pipeline would use the RTSP stream specified in the configuration.

Press 'q' to quit the application.

## Supported Processors

1. Object Detection
   - Uses YOLOv5 for general object detection
   - Configurable classes and confidence thresholds

2. Face Detection
   - Supports facial landmarks and attributes
   - Configurable minimum face size

3. Motion Detection
   - Basic motion detection without ML model requirement
   - Configurable sensitivity and area thresholds

4. License Plate Detection
   - Supports different regions (EU, US, Asia)
   - Includes OCR capabilities

5. Crowd Counting
   - Density-based crowd estimation
   - Supports tracking and minimum crowd size thresholds

## Output Formats

1. RSS Feed
   - XML format for event notifications
   - Configurable update interval and item limit

2. RTMP Stream
   - H.264 video streaming
   - Configurable bitrate and FPS

## Testing

The example includes a synthetic test video generator that creates a simple animation (moving white rectangle) to demonstrate the pipeline's functionality without requiring actual video input or webcam access. This allows for easy testing and verification of the processing pipeline.
