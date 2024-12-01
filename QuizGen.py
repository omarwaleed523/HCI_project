import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImagePath
import socket
from Students_data import read_highschool_students_from_csv, update_student

count = 0  # Global question index
students_data = read_highschool_students_from_csv('students data.csv')

# Quiz questions
questions = [
    {
        "question": "What is the capital of France?",
        "options": ["Paris", "London", "Berlin", "Rome"],
        "answer": "Paris"
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Venus"],
        "answer": "Mars"
    },
    {
        "question": "What is the largest ocean on Earth?",
        "options": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"],
        "answer": "Pacific Ocean"
    },
    {
        "question": "Which organ pumps blood in the human body?",
        "options": ["Brain", "Stomach", "Heart", "Liver"],
        "answer": "Heart"
    },
    {
        "question": "What is the freezing point of water?",
        "options": ["0°C", "10°C", "50°C", "-10°C"],
        "answer": "0°C"
    },
    {
        "question": "Solve: What is the derivative of x^2?",
        "options": ["2x", "x^2", "x", "2"],
        "answer": "2x"
    },
    {
        "question": "Which programming language is known for web development?",
        "options": ["Python", "Java", "JavaScript", "C++"],
        "answer": "JavaScript"
    },
    {
        "question": "Who proposed the theory of relativity?",
        "options": ["Isaac Newton", "Albert Einstein", "Galileo Galilei", "Nikola Tesla"],
        "answer": "Albert Einstein"
    },
    {
        "question": "What is the chemical symbol for water?",
        "options": ["H2O", "O2", "CO2", "HO2"],
        "answer": "H2O"
    },
    {
        "question": "What does HTTP stand for?",
        "options": [
            "Hyper Text Transfer Protocol",
            "High Transfer Text Protocol",
            "Hyperlink Text Transfer Program",
            "High Traffic Transfer Protocol"
        ],
        "answer": "Hyper Text Transfer Protocol"
    },
    {
        "question": "Which of these is a renewable energy source?",
        "options": ["Solar", "Coal", "Gas", "Oil"],
        "answer": "Solar"
    },
    {
        "question": "What is the square root of 64?",
        "options": ["8", "6", "7", "9"],
        "answer": "8"
    },
    {
        "question": "What does HTML stand for?",
        "options": [
            "Hyper Text Markup Language",
            "Home Tool Markup Language",
            "Hyperlinks Text Markup Language",
            "Hyper Text Management Language"
        ],
        "answer": "Hyper Text Markup Language"
    },
    {
        "question": "Which gas do plants use for photosynthesis?",
        "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen"],
        "answer": "Carbon Dioxide"
    }
]

def show_message(quiz, text):
    """
    Displays a temporary message box for 2 seconds.
    """
    message_box = ctk.CTkLabel(quiz, text=text, font=("Arial", 14), fg_color="gray", text_color="white", corner_radius=10)
    message_box.place(relx=0.5, rely=0.8, anchor="center")
    quiz.after(2000, message_box.destroy)

def button_clicked(answer, correct_answer, button, quiz, qlabel, answers_buttons, student, score_label):
    """
    Handles button clicks and moves to the next question after a short delay.
    """
    if answer == correct_answer:
        button.configure(fg_color="green")
        show_message(quiz, "Correct!")
        student['tuio_score'] += 10
    else:
        button.configure(fg_color="red")
        show_message(quiz, "Not Correct!")
        student['tuio_score'] -= 5

    score_label.configure(text=f"{student['name']} : {student['tuio_score']}")
    quiz.after(2000, lambda: NextQ(quiz, qlabel, answers_buttons, student, score_label))

def NextQ(quiz, qlabel, answers_buttons, student, score_label):
    """
    Updates the question and answers for the next question.
    """
    global count
    count += 1
    if count < len(questions):
        qlabel.configure(text=questions[count]['question'])
        for i, button in enumerate(answers_buttons):
            button.configure(
                text=questions[count]['options'][i],
                fg_color="gray",
                command=lambda btn=button, option=questions[count]['options'][i]: button_clicked(option, questions[count]['answer'], btn, quiz, qlabel, answers_buttons, student, score_label)
            )
    else:
        qlabel.configure(text="Quiz Completed!")
        for button in answers_buttons:
            button.destroy()
        update_student(student=student)

def CreateQuiz(student):
    """
    Creates the quiz window with questions and options.
    """
    global count
    count = 0

    quiz = ctk.CTk()
    quiz.geometry('900x400+400+150')
    quiz.title(f'Question {count + 1}')

    mainframe = ctk.CTkFrame(quiz, width=500, height=400, corner_radius=15)
    mainframe.pack(pady=30)

    score_label = ctk.CTkLabel(mainframe, text=f"{student['name']} : {student['tuio_score']}")
    score_label.place(relx=0.5, rely=0.1, anchor='center')

    question_label = ctk.CTkLabel(mainframe, text=questions[count]['question'], font=("Arial", 16))
    question_label.place(relx=0.5, rely=0.3, anchor='center')

    answers_buttons = []
    for i, option in enumerate(questions[count]['options']):
        button = ctk.CTkButton(
            mainframe, text=option,
            command=lambda opt=option: button_clicked(opt, questions[count]['answer'], button, quiz, question_label, answers_buttons, student, score_label)
        )
        button.place(relx=0.3 + (i % 2) * 0.4, rely=0.5 + (i // 2) * 0.2, anchor='center')
        answers_buttons.append(button)

    quiz.mainloop()

# Socket configuration
def start_server_and_quiz(student):
    listensocket = socket.socket()
    Port = 8000
    maxConnections = 999
    IP = socket.gethostname()

    listensocket.bind(('', Port))
    listensocket.listen(maxConnections)
    print("Server started at " + IP + " on port " + str(Port))

    print("Waiting for a client to connect...")
    clientsocket, address = listensocket.accept()
    print(f"New connection made from {address}")

    CreateQuiz(student)

if __name__ == "__main__":
    start_server_and_quiz()
