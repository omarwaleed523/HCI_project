import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize the browser (Chrome in this example)
driver = webdriver.Chrome()

# Open the URL
driver.get("https://player.quizalize.com/quiz/a20a8c25-6a51-42ea-9543-303a96ffb0ac")  # Replace with the actual URL of the webpage


def click_button_by_css(css_selector):
    try:
        # Wait for the button to be clickable
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )
        button.click()
    except Exception as e:
        print(f"Error: {e}")
click_button_by_css("._2K6khW87cf5FWvjCSSXG9z")  # Replace with the actual CSS selector for your button
input("Press Enter to close the browser...")  # Keeps the browser open until you press Enter
# Close the browser after the action
driver.quit()
