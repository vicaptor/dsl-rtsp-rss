# DSL RTSP RSS Processor

A modular video processing pipeline that supports multiple types of detection and processing capabilities, with configurable RTSP input and RSS/RTMP output streams.

## Project Structure

- `processing_types.py` - Defines the supported types of processors
- `base_processor.py` - Contains base classes and data structures
- `processors.py` - Implements specific processor types
- `processor_factory.py` - Factory for creating processor instances
- `pipeline_executor.py` - Main pipeline execution logic
- `run.py` - Example usage of the pipeline
- `config.yaml` - Pipeline configuration file

## Requirements

- Python 3.x
- OpenCV
- NumPy
- PyYAML

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
python run.py
```

This will start a video capture from your default camera (usually webcam) and apply the configured processing pipeline. In production, it would use the RTSP stream specified in the configuration.

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
