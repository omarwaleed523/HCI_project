# Import necessary libraries
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import socket
import asyncio
from bleak import BleakScanner
from datetime import datetime

# Initialize Chrome options for Incognito mode
options = webdriver.ChromeOptions()
options.add_argument("--incognito")

# Socket configuration
listensocket = socket.socket()
Port = 8000
maxConnections = 999
IP = socket.gethostname()

try:
    listensocket.bind(('', Port))
    listensocket.listen(maxConnections)
    print("Server started at " + IP + " on port " + str(Port))

    # Accept the incoming connection
    clientsocket, address = listensocket.accept()
    print("New connection made!")
except Exception as e:
    print(f"Socket error: {e}")

# Initialize the WebDriver with options
driver = webdriver.Chrome(options=options)

# Open the webpage
driver.get("https://quizizz.com/admin?createUsingAI=true&forLesson=false")

# Clear cache and cookies
driver.delete_all_cookies()

# Define a time delay (in seconds) between consecutive letter entries
DETECTION_DELAY = 3  # 3 seconds rest period
last_detection_time = time.time()  # Initialize with current time

# Function to enter a letter into a single text box based on the message data
def enter_letter_from_message(letter):
    global last_detection_time  # Use global variable to track time
    current_time = time.time()

    # Check if the delay period has passed
    if current_time - last_detection_time >= DETECTION_DELAY:
        try:
            text_box = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "whsOnd.zHQkBf"))
            )

            # Get the current content of the text box
            current_content = text_box.get_attribute("value")
            new_content = current_content + letter  # Append the new letter to the existing content

            text_box.clear()  # Clear the text box before entering updated content
            text_box.send_keys(new_content)
            print(f"Updated content in the text box: '{new_content}'")

            last_detection_time = current_time  # Update the last detection time
        except TimeoutException:
            print("Text box with the class name 'whsOnd zHQkBf' not found.")
        except Exception as e:
            print(f"Error entering letter: {e}")
    else:
        print(f"Detection delay active. Waiting {DETECTION_DELAY - (current_time - last_detection_time):.1f} seconds.")

# Run the main asynchronous function for Bluetooth scanning (keeping as-is if no issues)

# Wait and listen for a message from the client to trigger each letter entry
while True:
    try:
        message = clientsocket.recv(1024).decode()
        print(f"Debug: Received raw message: {message}")  # Print raw message for debugging
        if message:
            parts = message.split(',')
            print(f"Debug: Message split parts: {parts}")

            # Process letter and Caps Lock state messages
            if parts[0] == "0" and len(parts) >= 6:
                letter = parts[5]  # Extract the letter from the message
                enter_letter_from_message(letter)
            elif message == "Caps Lock ON":
                print("Caps Lock has been turned ON.")
            elif message == "Caps Lock OFF":
                print("Caps Lock has been turned OFF.")
            else:
                print("Message format does not match expected conditions.")
        else:
            print("Received empty message or no message.")

    except Exception as e:
        print(f"Error receiving message: {e}")

    time.sleep(0.5)  # Adjust the delay as needed for cycle frequency

print("Code execution complete. Browser remains open.")
