import customtkinter as ctk  # type: ignore
import cv2
import pyautogui
import mediapipe as mp
import threading
import time
from F_Final_Student_Context import Student_TUIO
from Teacher_Context import Teacher_TUIO
from recg import Student_DollarPy

# Global Variables
stop_hand_tracking = False
click_flag = False
hold_flag = False

def Create_GUI():
    """Sets up the GUI with buttons for user selection."""
    ctk.set_appearance_mode("dark")  # Modes: "light" or "dark"
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    root.geometry("500x400")  # Adjusted height to fit new buttons
    root.title("Detect")
    root.attributes("-topmost", True)

    # Frame for grouping widgets
    frame = ctk.CTkFrame(root, width=500, height=250, corner_radius=25)
    frame.pack(pady=30)

    # Label inside the frame
    frame_label = ctk.CTkLabel(frame, text="Who are you? (Student / Teacher)", font=("Arial", 14))
    frame_label.pack(pady=10)

    # Existing buttons
    teacher_button_tuio = ctk.CTkButton(frame, text="Teacher TUIO", fg_color='red',
                                        command=lambda: on_closing(root, Teacher_TUIO))
    teacher_button_tuio.pack(pady=10)
    student_button_tuio = ctk.CTkButton(frame, text="Student TUIO", fg_color="green",
                                        command=lambda: on_closing(root, Student_TUIO))
    student_button_tuio.pack(pady=10)

    #New button for DollarPy functionality
    student_button_dollarpy = ctk.CTkButton(frame, text="Student DollarPy", fg_color="green", command=lambda: on_closing(root, Student_DollarPy))
    student_button_dollarpy.pack(pady=10)

    # Handle closing the GUI and stopping hand tracking
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))

    # Start hand tracking in a separate thread
    hand_thread = threading.Thread(target=track_hand, daemon=True)
    hand_thread.start()

    root.mainloop()


def track_hand():
    """Tracks hand movements and performs actions based on hand landmarks."""
    global stop_hand_tracking, click_flag, hold_flag
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    screen_width, screen_height = pyautogui.size()
    cap = cv2.VideoCapture(0)
    with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.9) as hands:
        while not stop_hand_tracking:
            ret, frame = cap.read()
            if not ret:
                break

            # Flip and convert frame for processing
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(frame_rgb)

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

                    # Move the mouse cursor based on the index finger position
                    index_x, index_y = int(index_finger_tip.x * screen_width), int(index_finger_tip.y * screen_height)
                    pyautogui.moveTo(index_x, index_y)

                    # Trigger a click if the middle fingertip is below the index fingertip
                    if middle_finger_tip.y < index_finger_tip.y:
                        if not click_flag:
                            click_flag = True
                            pyautogui.click()
                            print(click_flag)
                            time.sleep(0.1)
                    else:
                        click_flag = False

                    # Pinky-based hold action
                    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                    pinky_dip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_DIP]
                    if pinky_tip.y < pinky_dip.y and not hold_flag:
                        hold_flag = True
                        pyautogui.mouseDown()
                    elif pinky_tip.y >= pinky_dip.y and hold_flag:
                        hold_flag = False
                        pyautogui.mouseUp()

                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Show the video frame with landmarks
            cv2.imshow("Hand Tracking", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()


def on_closing(root, fun=None):
    """Handles cleanup when the GUI is closed."""
    global stop_hand_tracking
    stop_hand_tracking = True  # Signal to stop hand tracking
    root.destroy()  # Close the GUI window
    print("Application closed.")
    if fun:
        fun()


# Run the GUI
if __name__ == "__main__":
    Create_GUI()
