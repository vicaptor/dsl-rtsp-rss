import asyncio
import cv2
import time
import yaml
from pipeline_executor import PipelineExecutor

async def main():
    # Load configuration from YAML file
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Initialize pipeline executor
    executor = PipelineExecutor(config)

    # For demo purposes, use webcam instead of RTSP stream
    # In production, you would use: cv2.VideoCapture(executor.get_source_uri())
    cap = cv2.VideoCapture(0)
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

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
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frame_id += 1

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    asyncio.run(main())
