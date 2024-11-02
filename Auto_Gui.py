from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import socket
import pyautogui  # Import pyautogui for mouse control
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

# Initialize Chrome options for Incognito mode
options = webdriver.ChromeOptions()
options.add_argument("--incognito")

# Socket configuration
listensocket = socket.socket()  # Creates an instance of socket
Port = 8000  # Port to host server on
maxConnections = 999
IP = socket.gethostname()  # IP address of local machine

listensocket.bind(('', Port))

# Starts server
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

def enter_fixed_username():
    fixed_username = "hugo doro00"
    try:
        # Wait for the input field to be present
        search_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "enter-name-field"))
        )
        search_box.clear()  # Clear if any text is pre-entered

        # Simulate real typing with a short delay between each character
        for char in fixed_username:
            search_box.send_keys(char)
            time.sleep(0.1)

        # Attempt to click the start button, handling overlay issues
        try:
            # Close the overlay if it has a close button
            overlay_close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".close-button-class"))  # Replace with actual close button selector if available
            )
            overlay_close_button.click()
            print("Closed the overlay or dialog box.")
        except:
            print("No overlay dialog found.")

        # Wait for the overlay to disappear, if it exists
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".dialog-container"))  # Replace with the actual overlay selector
        )
        print("Overlay has disappeared.")

        # Attempt JavaScript click as a fallback if overlay issues persist
        button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".start-game.hover\\:cursor-pointer.primary-button"))
        )
        driver.execute_script("arguments[0].click();", button)
        print("Button clicked successfully with username:", fixed_username)

        # Check for any error messages displayed on the page
        try:
            error_message = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "error-message-class"))  # Replace with the actual class for error message, if any
            )
            if error_message.is_displayed():
                print("Error message found:", error_message.text)
                return False  # Indicate that an error occurred
        except:
            # No error message found, continue as normal
            pass

        return True  # Username accepted

    except Exception as e:
        print("An error name occurred:", e)
        return False  # Indicate an error if the username couldn't be entered

# Run the function once with the fixed username
if enter_fixed_username():
    print("Successfully entered username and clicked button.")
else:
    print("Failed to enter username or click the button.")

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
