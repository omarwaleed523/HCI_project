import cv2
import pyautogui
import mediapipe as mp
import asyncio
from bleak import BleakScanner
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import math
import time
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1
click_flag = False  # Flag to control click state
hold_flag = False 
# Initialize MediaPipe for hand tracking
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Get screen resolution
screen_width, screen_height = pyautogui.size()
flag = False

# Initialize Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--incognito")
driver = webdriver.Chrome(options=options)

# Open the webpage
driver.get("https://quizizz.com/join/pre-game/running/U2FsdGVkX18N7Gbf%2BEwCpEujXcpGrnOgmiPKE%2Blt%2BbOQi5GZrXHQUAO%2FIm%2FMHCqDScS2E7UVa5p2OlJFZUx49A%3D%3D/start")

# Define Bluetooth scanning function
async def get_mac_address(target_mac):
    try:
        devices = await BleakScanner.discover()
        for device in devices:
            if device.address == target_mac:
                print(f"Target MAC address {target_mac} found.")
                return 'raouff'  # Replace with Bluetooth-based username
        print("Target MAC address not found.")
        return None
    except Exception as e:
        print(f"Bluetooth scanning error: {e}")
        return None
click_flag = False  # Flag to control click state
hold_flag = False  # Flag for pinky hold action

# Hand tracking function
def track_hand():
    global click_flag, hold_flag
    cap = cv2.VideoCapture(0)
    with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.9) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Flip and convert frame for processing
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(frame_rgb)

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    # Get coordinates of index and middle finger tips
                    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

                    # Convert index finger coordinates to screen coordinates and move mouse
                    index_x, index_y = int(index_finger_tip.x * screen_width), int(index_finger_tip.y * screen_height)
                    pyautogui.moveTo(index_x, index_y)

                    # Trigger a click if the middle fingertip is below the index fingertip
                    if middle_finger_tip.y < index_finger_tip.y:
                        if not click_flag:
                            print("Click triggered by middle finger")
                            click_flag = True
                            time.sleep(0.1)  # Delay to improve click responsiveness
                    else:
                        click_flag = False  # Reset flag when fingers are not in clicking position

                    # Get coordinates for the pinky fingertip and its nearest joint
                    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                    pinky_dip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_DIP]  # Nearest joint to the tip

                    # Check if pinky is raised (tip higher than DIP joint) to trigger hold
                    if pinky_tip.y < pinky_dip.y and not hold_flag:  # Pinky raised
                        hold_flag = True
                        print("Hold action started with pinky raised")
                    elif pinky_tip.y >= pinky_dip.y and hold_flag:  # Pinky lowered
                        hold_flag = False
                        print("Hold action released with pinky lowered")
                    if hold_flag:
                        pyautogui.mouseDown() 
                        time.sleep(0.2)

                    elif not hold_flag:
                        pyautogui.mouseUp()  
                        time.sleep(0.2)
# Release the left mouse button

                    if click_flag:
                            pyautogui.click()
                            time.sleep(0.2)
                    # Draw landmarks on the frame
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Show the video frame with landmarks
            cv2.imshow("Hand Tracking", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    cap.release()
    cv2.destroyAllWindows()

# Main function for Bluetooth scanning and webpage automation
async def main():
    # Bluetooth target MAC address
    target_mac = 'F8:20:A9:EA:1A:16'  # Replace with your specific MAC address
    username = await get_mac_address(target_mac)

    if username:
        try:
            search_box = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "enter-name-field"))
            )
            search_box.clear()
            search_box.send_keys(username)

            start_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".start-game.hover\\:cursor-pointer.primary-button"))
            )
            start_button.click()
            print("Username entered and game started with:", username)
        except Exception as e:
            print("Error entering username:", e)

# Run Bluetooth scanning and hand tracking in parallel
asyncio.run(main())
track_hand()  # Start hand tracking function
