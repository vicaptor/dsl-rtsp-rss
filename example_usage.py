import asyncio
import cv2
import time
import yaml
import numpy as np
from pipeline_executor import PipelineExecutor

async def main():
    # Load configuration from YAML file
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Initialize pipeline executor
    executor = PipelineExecutor(config)

    # Create a test video: black background with moving white rectangle
    width, height = 640, 480
    fps = 30
    duration = 10  # seconds
    total_frames = fps * duration

    frame_id = 0
    while frame_id < total_frames:
        # Create a black frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Draw a moving white rectangle
        rect_width, rect_height = 50, 50
        x = int((frame_id / total_frames) * (width - rect_width))
        y = height // 2 - rect_height // 2
        frame[y:y+rect_height, x:x+rect_width] = 255

        timestamp = time.time()
        results = await executor.process_frame(frame, frame_id, timestamp)

        # Process results from each processor
        for result in results:
            if result.detections:
                for detection in result.detections:
                    print(f"Frame {frame_id}: Detected {detection.class_name} "
                          f"with confidence {detection.confidence:.2f}")

                    # Draw detection on frame
                    x, y, w, h = detection.bbox
                    cv2.rectangle(frame, (int(x), int(y)),
                                (int(x + w), int(y + h)), (0, 255, 0), 2)

                    # Add label
                    label = f"{detection.class_name}: {detection.confidence:.2f}"
                    cv2.putText(frame, label, (int(x), int(y - 10)),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display frame with detections
        cv2.imshow('Test Frame', frame)
        if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
            break

        frame_id += 1

    cv2.destroyAllWindows()

if __name__ == "__main__":
    asyncio.run(main())
