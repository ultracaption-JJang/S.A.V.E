from ultralytics import YOLO
import cv2
from collections import defaultdict
import numpy as np
# Load an official or custom model
model = YOLO("yolo11n.pt")  # Load an official Detect model
#model = YOLO("yolo11n-seg.pt")  # Load an official Segment model
#model = YOLO("yolo11n-pose.pt")  # Load an official Pose model
#model = YOLO("path/to/best.pt")  # Load a custom trained model

# Perform tracking with the model
#results = model.track("https://youtu.be/LNwODJXcvt4", show=True)  # Tracking with default tracker
#results = model.track("https://youtu.be/LNwODJXcvt4", show=True, tracker="bytetrack.yaml")  # with ByteTrack


cap = cv2.VideoCapture(0)

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

track_history = defaultdict(lambda: [])

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLO11 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True)
        print(results)
        
        
        
        # Get the boxes and track IDs.
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xywh.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            class_ids = results[0].boxes.cls.int().cpu().tolist()

        else:
            boxes = []
            track_ids = []
            class_ids = []


        # Draw bounding boxes manually on the frame without confidence scores
        for box, track_id, class_id in zip(boxes, track_ids, class_ids):
            x, y, w, h = box
            # Calculate the top-left corner of the bounding box
            top_left_x = int(x - w / 2)
            top_left_y = int(y - h / 2)
            bottom_right_x = int(x + w / 2)
            bottom_right_y = int(y + h / 2)

            # Update the tracking history for this track ID
            center_point = (int(x), int(y))
            track_history[track_id].append(center_point)

            
            # Draw the bounding box
            cv2.rectangle(
                frame,
                (top_left_x, top_left_y),
                (bottom_right_x, bottom_right_y),
                (0, 255, 0),  # color in BGR (green)
                2
            )
            
            # get class name
            class_name = model.names[class_id] if class_id < len(model.names) else "Unknown"

            # customizing label
            label = f"{class_name} ({top_left_x}, {top_left_y}), ({bottom_right_x}, {bottom_right_y})"
            cv2.putText(
                frame,
                label,
                (top_left_x, top_left_y - 10),  # position above the box
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),  # color in BGR (RED)
                2
            )
            
            # Draw the tracking lines for this track ID
            if len(track_history[track_id]) > 1:
                points = np.array(track_history[track_id], np.int32).reshape((-1, 1, 2))
                cv2.polylines(
                    frame,
                    [points],
                    isClosed=False,
                    color=(230, 230, 230),  # light gray color for tracking lines
                    thickness=10
                )

            

        # Display the frame with custom bounding boxes
        cv2.imshow("YOLO11 Tracking", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
