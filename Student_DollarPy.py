from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import socket
import pyautogui
import mediapipe as mp
import cv2
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import asyncio
from bleak import BleakScanner
import threading

# Global Variables for Hand Tracking
click_flag = False
hold_flag = False


def Student_DollarPy():
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1

    # Initialize MediaPipe for hand tracking
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    # Get screen resolution
    screen_width, screen_height = pyautogui.size()
    flag = False

    # Initialize Chrome options for Incognito mode
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")

    # Function to wait for thumbs-up
    def wait_for_thumbs_up():
        # Set up the thumbs-up socket for testing
        thumbs_up_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        thumbs_up_port = 8001  # Port for thumbs-up communication

        try:
            thumbs_up_socket.bind(('', thumbs_up_port))
            thumbs_up_socket.listen(1)
            print(f"Thumbs-up server started and listening on port {thumbs_up_port}")

            while True:
                print("Waiting to accept a new connection on the thumbs-up socket...")
                thumbs_up_client, client_address = thumbs_up_socket.accept()
                print(f"Connection received from {client_address}")

                # Receive the thumbs-up message
                thumbs_up_message = thumbs_up_client.recv(1024).decode()
                print("Message received:", thumbs_up_message)

                # Check if the message is a thumbs-up signal
                if thumbs_up_message == "thumbs_up":
                    return True  # Return True to indicate thumbs-up received

        except Exception as e:
            print("Error setting up the socket:", e)
        finally:
            thumbs_up_socket.close()

        return False  # Default return False if no thumbs-up is received

    # Initialize the WebDriver with options
    driver = webdriver.Chrome(options=options)

    # Open the webpage
    driver.get(
        "https://quizizz.com/join?gc=98746518")

    # Clear cache and cookies
    driver.delete_all_cookies()

    # Asynchronous function to scan for the first device within the RSSI threshold
    async def get_mac_address():
        RSSI_THRESHOLD = -90
        try:
            print("Scanning for Bluetooth devices...")
            devices = await BleakScanner.discover()
            print(f"Found {len(devices)} devices")

            # Find the first device within the RSSI threshold
            for device in devices:
                if device.rssi >= RSSI_THRESHOLD:
                    print(f"Using first device within range as username: {device.address}")
                    return device.address  # Return the first device within range

            # If no device within range is found, return None
            print("No devices found within range.")
            return None
        except Exception as e:
            print(f"Bluetooth scanning error: {e}")
            return None

    # Function to enter the Bluetooth MAC address as username
    def enter_mac_as_username(mac_address):
        try:
            search_box = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "enter-name-field"))
            )
            search_box.clear()  # Clear any pre-entered text

            # Enter the MAC address as the username
            for char in mac_address:
                search_box.send_keys(char)
                time.sleep(0.1)

            # Close any overlay dialog if it exists
            try:
                overlay_close_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".close-button-class"))
                )
                overlay_close_button.click()
                print("Closed the overlay or dialog box.")
            except:
                print("No overlay dialog found.")

            # Wait for the overlay to disappear, if any
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, ".dialog-container"))
            )

            # Wait for the thumbs-up signal to click the start button
            if wait_for_thumbs_up():
                button = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".start-game.hover\\:cursor-pointer.primary-button"))
                )
                driver.execute_script("arguments[0].click();", button)
                print("Button clicked successfully with username:", mac_address)
                return
            else:
                print("No thumbs-up signal received. Button not clicked.")

        except Exception as e:
            print("An error occurred while entering the username:", e)

    # Hand tracking function
    def track_hand():
        click_flag = False
        hold_flag = False
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
                        index_x = int(index_finger_tip.x * screen_width)
                        index_y = int(index_finger_tip.y * screen_height)

                        # Ensure coordinates stay within screen bounds to avoid fail-safe trigger
                        index_x = min(max(index_x, 10), screen_width - 10)
                        index_y = min(max(index_y, 10), screen_height - 10)
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

                        # Check if pinky is raised to trigger hold
                        if pinky_tip.y < pinky_dip.y and not hold_flag:
                            hold_flag = True
                            pyautogui.mouseDown()
                            time.sleep(0.2)
                        elif pinky_tip.y >= pinky_dip.y and hold_flag:
                            hold_flag = False
                            pyautogui.mouseUp()
                            time.sleep(0.2)

                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Show the video frame with landmarks
                cv2.imshow("Hand Tracking", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

        cap.release()
        cv2.destroyAllWindows()

    # Main Bluetooth scanning and username entry function
    def bluetooth_scan_and_run():
        """Separate thread to handle Bluetooth scanning and run the main logic."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        mac_address = loop.run_until_complete(get_mac_address())

        # If a Bluetooth device is found, proceed with further actions
        if mac_address:
            enter_mac_as_username(mac_address)
            track_hand()
        else:
            print("No action taken as no device was found within the threshold.")

    # Create a new thread for Bluetooth scanning and handling the main function
    bluetooth_thread = threading.Thread(target=bluetooth_scan_and_run)
    bluetooth_thread.start()
