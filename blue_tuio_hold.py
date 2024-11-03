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

# Initialize the WebDriver with options
driver = webdriver.Chrome(options=options)

# Open the webpage
driver.get("https://quizizz.com/join/pre-game/running/U2FsdGVkX18N7Gbf%2BEwCpEujXcpGrnOgmiPKE%2Blt%2BbOQi5GZrXHQUAO%2FIm%2FMHCqDScS2E7UVa5p2OlJFZUx49A%3D%3D/start")

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
        # Wait for the input field to be present
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

        # Click the start button using JavaScript as a fallback
        button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".start-game.hover\\:cursor-pointer.primary-button"))
        )
        driver.execute_script("arguments[0].click();", button)
        print("Button clicked successfully with username:", mac_address)

    except Exception as e:
        print("An error occurred while entering the username:", e)

# Main function to orchestrate Bluetooth scanning and username entry
async def main():
    mac_address = await get_mac_address()
    if mac_address:
        enter_mac_as_username(mac_address)
    else:
        print("No action taken as no device was found within the threshold.")

# Run the main asynchronous function
asyncio.run(main())

# Replace these with the original resolution that `x` and `y` are based on.
original_width = 1920
original_height = 1080

# Track if marker 1 or 2 is active
marker_1_active = False
marker_2_active = False

running = True
while running:
    message = clientsocket.recv(1024).decode()  # Gets the incoming message
    if message:
        # Split the message by the comma
        parts = message.split(',')
        # Check if there are at least four parts
        if len(parts) >= 4:
            id, angle, x, y = parts[0], parts[1], float(parts[2]), float(parts[3])  # Parse x and y as floats
        else:
            raise ValueError("Not enough values to unpack")

        print("Received ID:", id, "X:", x, "Y:", y)

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
            # Marker 0 does not interrupt the hold-click action from Marker 2
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
                pyautogui.mouseDown()
                marker_2_active = True

        # Marker 3 stops the click and hold action started by Marker 2
        elif id == '3' and marker_2_active:
            print("Marker 3 detected - releasing hold.")
            pyautogui.mouseUp()
            marker_2_active = False

        # Perform continuous clicks if Marker 1 is active
        if marker_1_active:
            pyautogui.click()
            print("Mouse clicked at current location.")
            time.sleep(0.2)  # Adjust the delay as needed for click rate

# Close the browser after waiting
# time.sleep(5)
# driver.quit()
