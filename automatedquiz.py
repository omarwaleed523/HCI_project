import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

# Initialize the browser (Chrome in this example)
driver = webdriver.Chrome()

# Open the URL
driver.get("https://player.quizalize.com/quiz/a20a8c25-6a51-42ea-9543-303a96ffb0ac")  # Replace with the actual URL of the webpage

def click_button_by_css(css_selector):
    try:
        print(f"Trying to click button with CSS selector: {css_selector}")
        # Wait for the button to be clickable
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )
        button.click()
    except Exception as e:
        print(f"Error clicking button: {e}")

# Function to retrieve answers (handling True/False buttons)
def get_answers():
    try:
        print("Trying to retrieve answers...")

        # First, try using the class name for typical multiple-choice questions
        answers_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "_94mY16LZtYWqNB_Y8y-Dh"))
        )
        
        # If no multiple-choice answers found, try retrieving True/False answers from <button> elements
        if not answers_elements:
            print("Trying to retrieve True/False answers from <button> elements...")
            answers_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "button"))  # Locate all buttons for True/False
            )
        
        # Extract text from the buttons or spans (True/False or multiple-choice)
        answers = [answer.get_attribute("innerText") or answer.text for answer in answers_elements]
        return answers, answers_elements
    except TimeoutException:
        print(f"Error: Timeout while retrieving answers.")
        return [], []
    except StaleElementReferenceException:
        print("Stale element encountered. Retrying...")
        return get_answers()  # Retry in case of stale elements

# Function to check if the next button exists and click it
def click_next_button():
    try:
        print("Checking for next button...")
        # Wait for the next button to be clickable
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "_3G_jaZsdvRi15WbVL8QP62"))
        )
        next_button.click()
        print("Next button clicked.")
        return True
    except TimeoutException:
        print("No more questions or error clicking next button.")
        return False
    except StaleElementReferenceException:
        print("Stale element encountered when clicking next button. Retrying...")
        return click_next_button()  # Retry if there's a stale element issue

# Start by clicking the initial start button (replace with the correct button selector)
click_button_by_css("._2K6khW87cf5FWvjCSSXG9z")  # Replace with the actual CSS selector for your button

# Main loop to handle multiple questions
while True:
    # Get the answers for the current question
    answers, answer_elements = get_answers()

    # If answers are found, proceed to ask the user
    if answers:
        print("Here are the available answers:")
        for i, answer in enumerate(answers, start=1):
            print(f"{i}: {answer}")
        
        # Determine the range of valid input options based on the number of answers
        num_answers = len(answers)
        
        if num_answers == 4:
            # Get the user's choice for questions with four answers
            choice = int(input("Select your answer (1-4): "))
            valid_range = 4
        elif num_answers == 2:
            # Get the user's choice for True/False questions (assumed to be 2 answers)
            choice = int(input("Select your answer (1 for True, 2 for False): "))
            valid_range = 2
        else:
            print(f"Unexpected number of answers: {num_answers}")
            continue

        # Validate the input
        if 1 <= choice <= valid_range:
            try:
                print(f"Trying to select answer {choice}")
                # Click the selected answer (handles both True/False and multiple-choice)
                answer_elements[choice - 1].click()
            except StaleElementReferenceException:
                print("Stale element encountered while selecting answer. Retrying...")
                answer_elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "_94mY16LZtYWqNB_Y8y-Dh"))
                )
                answer_elements[choice - 1].click()
            except Exception as e:
                print(f"Error selecting answer: {e}")
        else:
            print(f"Invalid choice. Please enter a number between 1 and {valid_range}.")
    else:
        print("No answers found.")

    # Check if there is a next question by trying to click the next button
    if not click_next_button():
        break  # Exit the loop if there are no more questions

    # Add a small delay between questions to avoid stale elements
    time.sleep(2)

# Close the browser after the action
driver.quit()
 