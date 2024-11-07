# Import necessary libraries
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyautogui
import socket
import asyncio
from bleak import BleakScanner
from datetime import datetime
def Teacher_TUIO():
# Initialize Chrome options for Incognito mode
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")

    # Socket configuration
    listensocket = socket.socket()
    Port = 6000
    maxConnections = 999
    IP = socket.gethostname()

    try:
        listensocket.bind(('', Port))
        listensocket.listen(maxConnections)
        print("Server started at " + IP + " on port " + str(Port))

        #Accept the incoming connection
        clientsocket, address = listensocket.accept()
        print("New connection made!")
    except Exception as e:
        print(f"Socket error: {e}")

    # Initialize the WebDriver with options
    driver = webdriver.Chrome(options=options)

    # Open the webpage
    driver.get("https://quizizz.com/admin?createUsingAI=true")

    # Clear cache and cookies
    driver.delete_all_cookies()

    # Define a time delay (in seconds) between consecutive letter entries
    DETECTION_DELAY = 3  # 3 seconds rest period
    last_detection_time = time.time()  # Initialize with current time
    global BigBox

    def catch_boxes(driver):
        selectors = [
            (By.ID, "identifierId"),
            (By.CSS_SELECTOR, "div[data-testid='query-editor-tiptap'] div[contenteditable='true']"),
            (By.CSS_SELECTOR, "div[data-testid='question-option-1']"),
            (By.CSS_SELECTOR, "div[data-testid='question-option-2']"),
            (By.CSS_SELECTOR, "div[data-testid='question-option-3']"),
            (By.CSS_SELECTOR, "div[data-testid='question-option-4']"),
            (By.CSS_SELECTOR, "input[data-testid='fib-correct-answer']")
        ]

        for by, selector in selectors:
            try:
                target_element = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((by, selector))
                )
                # Get the location and size of the element
                element_location = target_element.location
                element_size = target_element.size
                mouse_x, mouse_y = pyautogui.position()

                # Calculate the element's bounding box
                left = element_location['x']
                top = element_location['y']
                right = left + element_size['width']
                bottom = top + element_size['height']

                # Check if the click was inside the element's bounding box
                if left <= mouse_x <= right and top <= mouse_y <= bottom:
                    print(f"Mouse click detected inside the element with selector: {selector}")
                    return target_element
                else:
                    print(f"Mouse click was outside the element with selector: {selector}")
                time.sleep(0.1)  # Small delay to reduce CPU usage

            except TimeoutException:
                print(f"Element with selector '{selector}' not found within the timeout period.")
            except NoSuchElementException:
                print(f"Element with selector '{selector}' does not exist on the page.")
            except Exception as e:
                print(f"An unexpected error occurred with selector '{selector}': {e}")

        print("All selectors have been checked.")

    # Function to enter a letter into a single text box based on the message data
    def enter_letter_from_message(letter, BigBox):
        global last_detection_time  # Use global variable to track time
        current_time = time.time()

        # Check if the delay period has passed
        if current_time - last_detection_time >= DETECTION_DELAY:
                # Get the current content of the text box
                current_content = BigBox.get_attribute("value")
                new_content = current_content + letter  # Append the new letter to the existing content

                BigBox.clear()  # Clear the text box before entering updated content
                BigBox.send_keys(new_content)
                print(f"Updated content in the text box: '{new_content}'")

                last_detection_time = current_time  # Update the last detection time
        else:
            print(f"Detection delay active. Waiting {DETECTION_DELAY - (current_time - last_detection_time):.1f} seconds.")

    marker_1_active = False
    marker_2_active = False
    Typing = False

    running = True
    while running:
        message = clientsocket.recv(1024).decode()  # Gets the incoming message
        if message:
            parts = message.split(',')

            if parts[0] == "0" and len(parts) >= 6:
                id, letter, angle = parts[1], parts[5], parts[2]

                # Check if parts[3] and parts[4] are numeric before converting
                try:
                    x = float(parts[3]) if parts[3].replace('.', '', 1).isdigit() else None
                    y = float(parts[4]) if parts[4].replace('.', '', 1).isdigit() else None
                    print("Received ID:", id, "Letter:", letter, "Angle:", angle, "X:", x, "Y:", y)
                except ValueError as e:
                    print("Error in converting coordinates to float:", e)
                    continue

            elif parts[0] == "1" and len(parts) >= 5:
                id, angle = parts[1], parts[2]

                # Check if parts[2] and parts[3] are numeric before converting
                try:
                    x = float(parts[3]) if parts[3].replace('.', '', 1).isdigit() else None
                    y = float(parts[4]) if parts[4].replace('.', '', 1).isdigit() else None
                    print("Received ID:", id, "Angle:", angle, "X:", x, "Y:", y)
                except ValueError as e:
                    print("Error in converting coordinates to float:", e)
                    continue

            else:
                print("Message format does not match expected conditions.")
                continue

            # Check for markers between 100 and 127 and apply detection delay
            if id.isdigit() and 100 <= int(id) <= 127 and Typing:
                current_time = time.time()
                if current_time - last_detection_time >= DETECTION_DELAY:
                    # Proceed with entering the letter if the delay has passed
                    print("Marker", id, "with letter", letter, "detected. Adding to text box.")
                    enter_letter_from_message(letter, BigBox)
                    last_detection_time = current_time  # Update the last detection time
                else:
                    print(f"Detection delay in effect. Skipping input for marker {id}.")

            # Mouse and marker actions based on ID (e.g., markers 0, 1, 2)
            # Only move the mouse if id is '0'
            if id == '0':
                # Scale `x` and `y` to your screen size
                original_width = 1920
                original_height = 1080

                scaled_x = int(0 + ((x - 0) * (original_width - 0)) / (1 - 0))
                scaled_y = int(0 + ((y - 0) * (original_height - 0)) / (1 - 0))

                # Avoid moving to (0, 0) by setting a minimum threshold
                if scaled_x < 10:
                    scaled_x = 10
                if scaled_y < 10:
                    scaled_y = 10

                print("Moving mouse based on scaled coordinates:", scaled_x, scaled_y)
                pyautogui.moveTo(scaled_x, scaled_y)
                print("Mouse moved to:", scaled_x, scaled_y)
                continue

            # Marker 1 triggers continuous clicking
            elif id == '1':
                if not marker_1_active:
                    print("Marker 1 detected - starting continuous click.")
                    marker_1_active = True
            else:
                marker_1_active = False

            # Marker 2 initiates click and hold
            if id == '2':
                if not marker_2_active:
                    print("Marker 2 detected - starting click and hold.")
                    marker_2_active = True

            # Marker 3 stops the click and hold action started by Marker 2
            elif id == '3' and marker_2_active:
                print("Marker 3 detected - releasing hold.")
                marker_2_active = False

            # Perform continuous clicks if Marker 1 is active
            if marker_1_active:
                pyautogui.click()
                print("Mouse clicked at current location.")
                time.sleep(0.2)  # Adjust the delay as needed for click rate
                BigBox = catch_boxes(driver)
                if BigBox:
                    Typing = True
                else:
                    Typing = False

            # Handle mouse hold for Marker 2
            if marker_2_active:
                pyautogui.mouseDown()
                print("Starting click and hold at current location.")
                time.sleep(0.2)
            else:
                pyautogui.mouseUp()
                print("Releasing hold at current location.")
                time.sleep(0.2)
