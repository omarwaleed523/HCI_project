import time
import cv2
import mediapipe as mp
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

# Global variables with thread-safe locking
fingers_count = 0
stop_hand_tracking = False
fingers_lock = threading.Lock()  # Lock for thread-safe access to fingers_count

# Hand Tracking Function (runs in a separate thread)
def hand_tracking():
    global fingers_count, stop_hand_tracking
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)

    with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
        while cap.isOpened() and not stop_hand_tracking:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(frame_rgb)
            fingers_up = [False] * 5  # [Thumb, Index, Middle, Ring, Pinky]

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    wrist = hand_landmarks.landmark[0]
                    index_mcp = hand_landmarks.landmark[5]
                    is_left_hand = wrist.x > index_mcp.x
                    
                    thumb_tip = hand_landmarks.landmark[4]
                    thumb_mcp = hand_landmarks.landmark[2]
                    if (thumb_tip.x > thumb_mcp.x if is_left_hand else thumb_tip.x < thumb_mcp.x):
                        fingers_up[0] = True

                    index_tip = hand_landmarks.landmark[8]
                    index_dip = hand_landmarks.landmark[7]
                    if index_tip.y < index_dip.y:
                        fingers_up[1] = True

                    middle_tip = hand_landmarks.landmark[12]
                    middle_dip = hand_landmarks.landmark[11]
                    if middle_tip.y < middle_dip.y:
                        fingers_up[2] = True

                    ring_tip = hand_landmarks.landmark[16]
                    ring_dip = hand_landmarks.landmark[15]
                    if ring_tip.y < ring_dip.y:
                        fingers_up[3] = True

                    pinky_tip = hand_landmarks.landmark[20]
                    pinky_dip = hand_landmarks.landmark[19]
                    if pinky_tip.y < pinky_dip.y:
                        fingers_up[4] = True

                    with fingers_lock:
                        fingers_count = sum(fingers_up)  # Update the global fingers_count
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            fingers_count = sum(fingers_up)
            cv2.putText(frame, f'Fingers Up: {fingers_count}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Hand Tracking", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    
    cap.release()
    cv2.destroyAllWindows()

# Selenium Function to Control Quiz Flow
def quiz_control():
    global fingers_count, stop_hand_tracking
    driver = webdriver.Chrome()
    driver.get("https://player.quizalize.com/quiz/2f3179e7-66aa-40ad-a682-7cc42c4210c1?token=16428492-a3e8-4c3e-a016-e6c0c8d52773")

    def click_button_by_css(css_selector):
        try:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            )
            button.click()
        except Exception as e:
            print(f"Error clicking button: {e}")

    def get_answers():
        try:
            answers_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "_94mY16LZtYWqNB_Y8y-Dh"))
            )
            answers = [answer.get_attribute("innerText") or answer.text for answer in answers_elements]
            return answers, answers_elements
        except (TimeoutException, StaleElementReferenceException):
            return [], []

    def click_next_button():
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "_3G_jaZsdvRi15WbVL8QP62"))
            )
            next_button.click()
            return True
        except (TimeoutException, StaleElementReferenceException):
            return False

    click_button_by_css("._2K6khW87cf5FWvjCSSXG9z")

    # Main loop to handle questions
    while True:
        answers, answer_elements = get_answers()
        selected_answer = False

        # Poll `fingers_count` and select an answer if in range
        if answers:
            with fingers_lock:
                count = fingers_count
            if 1 <= count <= len(answers):
                try:
                    print(f"Selecting answer {count}")
                    answer_elements[count - 1].click()
                    selected_answer = True
                    fingers_count=-1
                except StaleElementReferenceException:
                    print("Encountered stale element while selecting answer.")
                
        # If an answer was selected, move to next question
        if selected_answer:
            time.sleep(1)  # Delay to allow for next question to load
            if not click_next_button():
                print("Quiz completed or no more questions.")
                break

    stop_hand_tracking = True
    driver.quit()

# Create and start threads
hand_tracking_thread = threading.Thread(target=hand_tracking)
quiz_thread = threading.Thread(target=quiz_control)

hand_tracking_thread.start()
quiz_thread.start()

hand_tracking_thread.join()
quiz_thread.join()
