# Imports modules
import socket
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

# Initialize the browser (Chrome in this example)
flag_start = 0
flag_next = 0
def get_question_info():
    try:
        print("Retrieving current question and total questions...")
        # Wait for the element containing the question numbers to be present
        question_info_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div/span[2]"))
        )

        # Extract the text (e.g., "1/15")
        question_info_text = question_info_element.text
        print(f"Question info found: {question_info_text}")

        # Split the text into current question and total questions
        current_question, total_questions = question_info_text.split('/')

        # Convert to integers and return
        return int(current_question), int(total_questions)
    except Exception as e:
        print(f"Error retrieving question info: {e}")
        return None, None


def click_play_again():
    try:
        print("Trying to click the 'Play again' button...")
        # Wait for the button to be clickable
        play_again_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "_1cidUqGCJTA-XiToCa9duj"))
        )
        play_again_button.click()
        print("'Play again' button clicked.")
        flag_start = 0  # Reset flag_start after clicking "Play again"
    except TimeoutException:
        print("Failed to find or click the 'Play again' button.")
    except Exception as e:
        print(f"Error clicking the 'Play again' button: {e}")


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


def get_true_false_answers():
    try:
        print("Trying to retrieve True/False answers...")

        # Use a shorter wait for True/False buttons and look for both elements inside the parent div
        true_false_elements = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "_1A4GF3OVkmOdz0S_wXGfWV"))
        )

        if true_false_elements and len(true_false_elements) == 2:
            print("True/False answers found.")
            answers = [element.text for element in true_false_elements]
            return answers, true_false_elements
        else:
            print("True/False elements not found.")
            return [], []

    except TimeoutException:
        print(f"Error: Timeout while retrieving True/False answers.")
        return [], []

    except StaleElementReferenceException:
        print("Stale element encountered. Retrying...")
        return get_true_false_answers()  # Retry in case of stale elements


def get_answers():
    try:
        print("Trying to retrieve answers...")

        # Try to locate the multiple-choice answers first
        try:
            answers_elements = WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "_94mY16LZtYWqNB_Y8y-Dh"))
            )
            print("Multiple-choice answers found.")
        except TimeoutException:
            answers_elements = []  # No answers found in this class, fallback to the next step

        # If no multiple-choice answers, check for True/False answers
        if not answers_elements:
            return get_true_false_answers()  # This will handle True/False questions specifically

        # Extract text from multiple-choice buttons
        answers = [answer.get_attribute("innerText") or answer.text for answer in answers_elements]
        return answers, answers_elements

    except TimeoutException:
        print(f"Error: Timeout while retrieving answers.")
        return [], []

    except StaleElementReferenceException:
        print("Stale element encountered. Retrying...")
        return get_answers()  # Retry in case of stale elements


# Retry in case of stale elements
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


def mcq(x):
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
            choice = int(x)
            valid_range = 4
        elif num_answers == 2:
            # Get the user's choice for True/False questions (assumed to be 2 answers)
            choice = int(x)
            valid_range = 2
        else:
            print(f"Unexpected number of answers: {num_answers}")

        # Validate the input
        if 1 <= choice <= valid_range:
            try:
                print(f"Trying to select answer {choice}")

                selected_answer = answer_elements[choice - 1]
                selected_answer.click()
                answer_elements.clear()
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
driver = webdriver.Chrome()
# Open the URL
driver.get(
    "https://player.quizalize.com/quiz/a20a8c25-6a51-42ea-9543-303a96ffb0ac")  # Replace with the actual URL of the webpage
running = True

current_question = 0
total_questions = 0

while running:
    message = clientsocket.recv(1024).decode()  # Gets the incoming message
    if message:
        # Split the message by the comma
        parts = message.split(',')
        # Check if there are at least two parts
        if len(parts) >= 2:
            id, angle = parts[0], parts[1]
        else:
            raise ValueError("Not enough values to unpack")
        print(id,angle)
        if id == '0':
            click_button_by_css("._2K6khW87cf5FWvjCSSXG9z")
            flag_start = 1
        elif id == '1' and flag_start == 1 :
            mcq(id)
        elif id == '2' and flag_start == 1 :
            mcq(id)
        elif id == '3' and flag_start == 1 :
            mcq(id)
        elif id == '4' and flag_start == 1 :
            mcq(id)
        elif id == '5' and flag_start == 1 :
            click_next_button()
        elif id == '6' and flag_start == 1:
            click_play_again()
        elif id == '7' and flag_start == 1:
            print("Closing the browser.")
            driver.quit()  # Closes the browser
            running = False  # Exit the loop to stop the server after closing the browser
        else:
            print("Unexpected id, please enter a valid one")

