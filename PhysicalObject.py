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
import customtkinter as ctk
def Student():
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

    # Accepts the incoming connection
    (clientsocket, address) = listensocket.accept()
    print("New connection made!")

    # Initialize the WebDriver with options
    driver = webdriver.Chrome(options=options)

    # Open the webpage
    driver.get("https://quizizz.com/join/pre-game/running/U2FsdGVkX18N7Gbf%2BEwCpEujXcpGrnOgmiPKE%2Blt%2BbOQi5GZrXHQUAO%2FIm%2FMHCqDScS2E7UVa5p2OlJFZUx49A%3D%3D/start")

    # Clear cache and cookies
    driver.delete_all_cookies()
    # Function to continuously enter the letter "E" in a text box with name 'box0' whenever it appears
    def enter_letter_e():
        try:
            # Locate the input field by data-cy attribute directly
            text_box = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-cy='box0']"))
            )
            text_box.clear()  # Clear any pre-entered text
            text_box.send_keys(letter)  # Enter the letter "E"
            print("Entered 'E' in the text box with data-cy 'box0'.")

        except TimeoutException:
            print("Text box with data-cy 'box0' not found.")
        except Exception as e:
            print("An error occurred while entering 'E' in the text box with data-cy 'box0':", e)

    def enter_letter_a():
        try:
            # Locate the input field by data-cy attribute directly
            text_box = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-cy='box1']"))
            )
            text_box.clear()  # Clear any pre-entered text
            text_box.send_keys("A")  # Enter the letter "E"
            print("Entered 'E' in the text box with data-cy 'box1'.")

        except TimeoutException:
            print("Text box with data-cy 'box1' not found.")
        except Exception as e:
            print("An error occurred while entering 'E' in the text box with data-cy 'box1':", e)

    def enter_letter_s():
        try:
            # Locate the input field by data-cy attribute directly
            text_box = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-cy='box2']"))
            )
            text_box.clear()  # Clear any pre-entered text
            text_box.send_keys("S")  # Enter the letter "E"
            print("Entered 'E' in the text box with data-cy 'box2'.")

        except TimeoutException:
            print("Text box with data-cy 'box2' not found.")
        except Exception as e:
            print("An error occurred while entering 'E' in the text box with data-cy 'box2':", e)

    def enter_letter_y():
        try:
            # Locate the input field by data-cy attribute directly
            text_box = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-cy='box3']"))
            )
            text_box.clear()  # Clear any pre-entered text
            text_box.send_keys("Y")  # Enter the letter "E"
            print("Entered 'E' in the text box with data-cy 'box3'.")

        except TimeoutException:
            print("Text box with data-cy 'box3' not found.")
        except Exception as e:
            print("An error occurred while entering 'E' in the text box with data-cy 'box3':", e)

    # Asynchronous function to get the first available MAC address
    async def get_first_mac_address():
        RSSI_THRESHOLD = -90
        try:
            print("Scanning for Bluetooth devices...")
            devices = await BleakScanner.discover()
            print(f"Found {len(devices)} devices")

            # Filter devices by RSSI threshold
            for device in devices:
                if device.rssi >= RSSI_THRESHOLD:
                    print(f"Using MAC Address as username: {device.address}")
                    return device.address  # Return the first MAC address found within range
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
        mac_address = await get_first_mac_address()
        if mac_address:
            enter_mac_as_username(mac_address)
        else:
            print("Failed to retrieve MAC address; no username entered.")

    # Run the main asynchronous function
    asyncio.run(main())
    # Call the function to enter "E" in the text box

    # Replace these with the original resolution that `x` and `y` are based on.
    original_width = 1920
    original_height = 1080

    # Track if marker 1 is active
    marker_1_active = False

    running = True
    while running:
        message = clientsocket.recv(1024).decode()  # Gets the incoming message
        if message:
            # Split the message by the comma
            parts = message.split(',')
            if len(parts) == 5:
                id, letter, angle, x, y = parts[0], parts[1], float(parts[2]), float(parts[3]), float(parts[4])
                print("Received ID:", id, "Letter:", letter, "X:", x, "Y:", y)
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
                marker_1_active = False

            # Activate continuous clicking if marker id is '1'
            elif id == '1':
                if not marker_1_active:
                    print("Marker 1 detected - starting continuous click.")
                    marker_1_active = True

            elif id == '11' and letter == 'E':
                    print("Marker 11 with 'E' detected. Custom behavior can be implemented here.")
                    # Add custom actions for marker 11 her
                    enter_letter_e()

            elif id == '9' and letter == 'A':
                    print("Marker 11 with 'E' detected. Custom behavior can be implemented here.")
                    # Add custom actions for marker 11 her
                    enter_letter_a()
            elif id == '10' and letter == 'S':
                    print("Marker 11 with 'E' detected. Custom behavior can be implemented here.")
                    # Add custom actions for marker 11 her
                    enter_letter_s()
            elif id == '6' and letter == 'Y':
                    print("Marker 11 with 'E' detected. Custom behavior can be implemented here.")
                    # Add custom actions for marker 11 her
                    enter_letter_y()
            else:
                # Deactivate continuous clicking if marker is not '1'
                marker_1_active = False



            # Perform continuous clicks if marker 1 is active
            if marker_1_active:
                pyautogui.click()
                print("Mouse clicked at current location.")
                time.sleep(0.2)  # Adjust the delay as needed for click rate

    # Close the browser after waiting
    # time.sleep(5)
    # driver.quit()
