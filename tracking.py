from ultralytics import YOLO
import cv2
from collections import defaultdict
import numpy as np
# Load an official or custom model
model = YOLO("yolo11n.pt")  # Load an official Detect model
#model = YOLO("yolo11n-seg.pt")  # Load an official Segment model
#model = YOLO("yolo11n-pose.pt")  # Load an official Pose model
#model = YOLO("path/to/best.pt")  # Load a custom trained model

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
        # Get the boxes and track IDs
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xywh.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()
        else:
            boxes = []
            track_ids = []
        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Plot the tracks
        for box, track_id in zip(boxes, track_ids):
            x, y, w, h = box
            track = track_history[track_id]
            track.append((float(x), float(y)))  # x, y center point
            if len(track) > 30:  # retain 90 tracks for 90 frames
                track.pop(0)

            # Draw the tracking lines
            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(
                annotated_frame,
                [points],
                isClosed=False,
                color=(230, 230, 230),
                thickness=10,
            )

            
            
        # Display the annotated frame
        cv2.imshow("YOLO11 Tracking", annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()

# Perform tracking with the model
#results = model.track("https://youtu.be/LNwODJXcvt4", show=True)  # Tracking with default tracker
#results = model.track("https://youtu.be/LNwODJXcvt4", show=True, tracker="bytetrack.yaml")  # with ByteTrack


# from ultralytics import YOLO
# import cv2
# from collections import defaultdict
# import numpy as np

# # Load an official or custom model
# model = YOLO("yolo11n.pt")  # Load an official Detect model

# cap = cv2.VideoCapture(0)

# # Check if the webcam is opened correctly
# if not cap.isOpened():
#     print("Error: Could not open webcam.")
#     exit()

# track_history = defaultdict(lambda: [])

# # Loop through the video frames
# while cap.isOpened():
#     # Read a frame from the video
#     success, frame = cap.read()

#     if success:
#         # Run YOLO11 tracking on the frame, persisting tracks between frames
#         results = model.track(frame, persist=True)
        
#         # Get the boxes and track IDs
#         if results[0].boxes.id is not None:
#             boxes = results[0].boxes.xywh.cpu()
#             track_ids = results[0].boxes.id.int().cpu().tolist()
#         else:
#             boxes = []
#             track_ids = []

#         # Draw bounding boxes manually on the frame without confidence scores
#         for box, track_id in zip(boxes, track_ids):
#             x, y, w, h = box
#             # Calculate the top-left corner of the bounding box
#             top_left_x = int(x - w / 2)
#             top_left_y = int(y - h / 2)
#             top_right_x = int(x + w / 2)
#             top_right_y = int(y + h / 2)
#             bottom_right_x
#             bottom_right_y
#             bottom_right_x = int(x + w / 2)
#             bottom_right_y = int(y + h / 2)
            
#             # Draw the bounding box
#             cv2.rectangle(
#                 frame,
#                 (top_left_x, top_left_y),
#                 (bottom_right_x, bottom_right_y),
#                 (0, 255, 0),  # color in BGR (green)
#                 2
#             )
            
#             # Draw the tracking lines
#             points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
#             cv2.polylines(
#                 annotated_frame,
#                 [points],
#                 isClosed=False,
#                 color=(230, 230, 230),
#                 thickness=10,
#             )
#             # Add bounding box coordinates as text
#             bbox_text = f"({top_left_x}, {top_left_y}), ({bottom_right_x}, {bottom_right_y})"
#             cv2.putText(
#                 frame,
#                 bbox_text,
#                 (top_left_x, top_left_y - 10),  # position above the box
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.5,
#                 (0, 255, 0),  # color in BGR (green)
#                 2
#             )

#         # Display the frame with custom bounding boxes
#         cv2.imshow("YOLO11 Tracking", frame)

#         # Break the loop if 'q' is pressed
#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break
#     else:
#         # Break the loop if the end of the video is reached
#         break

# # Release the video capture object and close the display window
# cap.release()
# cv2.destroyAllWindows()