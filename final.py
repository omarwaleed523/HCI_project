import cv2
import pyautogui
import mediapipe as mp
import asyncio
from bleak import BleakScanner
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

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

# Hand tracking function
def track_hand():
    global flag
    cap = cv2.VideoCapture(0)
    with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.9) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(frame_rgb)

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    finger = hand_landmarks.landmark[8]
                    point = hand_landmarks.landmark[5]
                    thumb=hand_landmarks.landmark[12]
                    frame_height, frame_width, _ = frame.shape
                    screen_x = int(finger.x * screen_width)
                    screen_y = int(finger.y * screen_height)

                    pyautogui.moveTo(screen_x, screen_y)

                    # Trigger click if the index fingertip is below the base of the index finger
                    if thumb.y <finger.y  and not flag:
                        pyautogui.click()
                        print("Clicked")
                        flag = True
                    elif finger.y < point.y:
                        flag = False

                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

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
