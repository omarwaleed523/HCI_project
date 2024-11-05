from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import socket
import pyautogui
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
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

listensocket.bind(('', Port))
listensocket.listen(maxConnections)
print("Server started at " + IP + " on port " + str(Port))

# Accept the incoming connection
(clientsocket, address) = listensocket.accept()
print("New connection made!")


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
            if thumbs_up_message == "thumbs_up":  # Adjust based on the actual thumbs-up message
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
    "https://quizizz.com/join/pre-game/running/U2FsdGVkX18N7Gbf%2BEwCpEujXcpGrnOgmiPKE%2Blt%2BbOQi5GZrXHQUAO%2FIm%2FMHCqDScS2E7UVa5p2OlJFZUx49A%3D%3D/start")

# Clear cache and cookies
driver.delete_all_cookies()

# Define a time delay (in seconds) between consecutive letter entries
DETECTION_DELAY = 3  # 2 seconds rest period
last_detection_time = time.time()  # Initialize with current time


# Function to enter a letter in the text box
def enter_letter(letter, i):
    try:
        css_selector = f"[data-cy='box{i}']"
        text_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
        text_box.clear()
        text_box.send_keys(letter)
        print(f"Entered '{letter}' in the text box with {css_selector}.")
    except TimeoutException:
        print(f"Text box with {css_selector} not found.")
    except Exception as e:
        print("An error occurred while entering letters:", e)


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
                EC.presence_of_element_located((By.CSS_SELECTOR, ".start-game.hover\\:cursor-pointer.primary-button"))
            )
            driver.execute_script("arguments[0].click();", button)
            print("Button clicked successfully with username:", mac_address)
            return
        else:
            print("No thumbs-up signal received. Button not clicked.")

    except Exception as e:
        print("An error occurred while entering the username:", e)



# Main function to orchestrate Bluetooth scanning and username entry
async def main():
    mac_address = await get_mac_address()
    if mac_address:
        enter_mac_as_username(mac_address)
    else:
        print("No action taken as no device was found within the threshold.")
    # Replace these with the original resolution that `x` and `y` are based on.
    original_width = 1920
    original_height = 1080

    # Track if marker 1 or 2 is active
    marker_1_active = False
    marker_2_active = False

    running = True
    i = 0  # Initialize box index
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
            if id.isdigit() and 100 <= int(id) <= 127:
                current_time = time.time()
                if current_time - last_detection_time >= DETECTION_DELAY:
                    # Proceed with entering the letter if the delay has passed
                    print("Marker", id, "with letter", letter, "detected. Adding to text box.")
                    enter_letter(letter, i)
                    i += 1  # Increment i to move to the next box
                    last_detection_time = current_time  # Update the last detection time
                else:
                    print(f"Detection delay in effect. Skipping input for marker {id}.")

            # Mouse and marker actions based on ID (e.g., markers 0, 1, 2)
            # Only move the mouse if id is '0'
            if id == '0':
                # Scale `x` and `y` to your screen size
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

            # Handle mouse hold for Marker 2
            if marker_2_active:
                pyautogui.mouseDown()
                print("Starting click and hold at current location.")
                time.sleep(0.2)
            else:
                pyautogui.mouseUp()
                print("Releasing hold at current location.")
                time.sleep(0.2)


# Run the main asynchronous function
asyncio.run(main())


# Close the browser after waiting
# time.sleep(5)
# driver.quit()