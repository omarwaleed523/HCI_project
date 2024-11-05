!pip install mediapipe dollarpy
import mediapipe as mp
import cv2
from dollarpy import Recognizer, Template, Point
import time
import pickle

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

# List of video paths to train on the same gesture
video_files = [
    r"C:\Users\omarw\Desktop\hci_train\1.mp4",
    r"C:\Users\omarw\Desktop\hci_train\2.mp4",
    r"C:\Users\omarw\Desktop\hci_train\3.mp4",
    r"C:\Users\omarw\Desktop\hci_train\4.mp4",
    r"C:\Users\omarw\Desktop\hci_train\5.mp4",
    r"C:\Users\omarw\Desktop\hci_train\6.mp4",
    r"C:\Users\omarw\Desktop\hci_train\7.mp4",
    r"C:\Users\omarw\Desktop\hci_train\11.mp4",
    r"C:\Users\omarw\Desktop\hci_train\22.mp4",
    r"C:\Users\omarw\Desktop\hci_train\33.mp4",
    r"C:\Users\omarw\Desktop\hci_train\44.mp4",
    r"C:\Users\omarw\Desktop\hci_train\55.mp4",
    # Add more video paths as needed
]

def getPoints(video_files, pinch_gesture=False):
    all_points = []
    for videoURL in video_files:
        cap = cv2.VideoCapture(videoURL)
        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                results = holistic.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # Draw hand landmarks
                mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
                mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

                # If landmarks are detected, process thumbs up gestures
                if results.right_hand_landmarks or results.left_hand_landmarks:
                    try:
                        hand_landmarks = results.right_hand_landmarks or results.left_hand_landmarks
                        index_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
                        thumb_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]

                        # Calculate distance between thumb and index fingertip to detect  thumbs up
                        distance = ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2) ** 0.5

                        # If pinch detected, add relevant points to the gesture points list
                        if pinch_gesture and distance < 0.05:  # Adjust threshold as needed
                            all_points.append(Point(index_tip.x, index_tip.y, 1))  # Label for pinch gesture

                    except:
                        pass

                # Display the frame
                cv2.imshow("Gesture Training", image)

                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break

        cap.release()
        cv2.destroyAllWindows()

    return all_points

# Train the model and create the template for the Circle Gesture
all_points = getPoints(video_files, pinch_gesture=True)

# Create a single template for the Circle Gesture
circle_template = Template("Circle Gesture", all_points)
templates = [circle_template]

# Initialize recognizer with the single gesture template
recognizer = Recognizer(templates)

import pickle

# Save the model
model_filename = 'thumbsup.pkl'
with open(model_filename, 'wb') as model_file:
    pickle.dump(templates, model_file)

print(f"Model saved to {model_filename}")

def thumbs_up_status_callback(thumbs_up_detected):
    if thumbs_up_detected:
        print("Thumbs up detected")
    else:
        print("No thumbs up")

def getPointsRealTime(thumbs_up_detected_callback):
    cap = cv2.VideoCapture(0)  # Use camera
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Flip the frame horizontally to mirror the camera feed
            frame = cv2.flip(frame, 1)

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            results = holistic.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Draw hand landmarks
            mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

            # Check for thumbs-up gesture
            thumbs_up_detected = False
            if results.right_hand_landmarks or results.left_hand_landmarks:
                try:
                    hand_landmarks = results.right_hand_landmarks or results.left_hand_landmarks

                    # Get the coordinates for landmarks needed for thumbs-up detection
                    thumb_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
                    thumb_ip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_IP]
                    index_mcp = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP]
                    middle_mcp = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP]

                    # Condition to check if thumb is up and other fingers are folded
                    # Check if thumb is higher than the knuckles of the index and middle fingers
                    if (thumb_tip.y < index_mcp.y and thumb_tip.y < middle_mcp.y) and \
                       (thumb_tip.x > thumb_ip.x):  # Thumb pointing upwards condition

                        thumbs_up_detected = True
                        # Draw a green dot at the thumb tip location
                        thumb_x = int(thumb_tip.x * image.shape[1])
                        thumb_y = int(thumb_tip.y * image.shape[0])
                        cv2.circle(image, (thumb_x, thumb_y), 10, (0, 255, 0), -1)  # Draw green dot

                except Exception as e:
                    print(f"Error processing hand landmarks: {e}")

            # Call the callback with the current thumbs up status
            thumbs_up_detected_callback(thumbs_up_detected)

            # Display the frame
            cv2.imshow("Gesture Detection", image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

# Start real-time gesture detection
getPointsRealTime(thumbs_up_status_callback)

