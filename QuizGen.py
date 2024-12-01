import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImagePath
from Students_data import read_highschool_students_from_csv,update_student
count = 0  # Global question index
students_data=read_highschool_students_from_csv('students data.csv')
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

    # Remove the message box after 2 seconds
    quiz.after(2000, message_box.destroy)
def button_clicked(answer, correct_answer, button, quiz, qlabel, answers_buttons,student,score_label):
    
    """
    Handles button clicks and moves to the next question after a short delay.
    """
    if answer == correct_answer:
        button.configure(fg_color="green")
        show_message(quiz, "Correct!")
        student['tuio_score']+=10
    else:
        button.configure(fg_color="red")
        show_message(quiz, "Not Correct!")
        student['tuio_score']-=5

    score_label.configure(text=f"{student['name']} : {student['tuio_score']}")

    # Move to the next question after a delay
    quiz.after(2000, lambda: NextQ(quiz, qlabel, answers_buttons,student,score_label))



def NextQ(quiz, qlabel, answers_buttons,student,Score_label):
    """
    Updates the question and answers for the next question.
    """
    global count
    count += 1  # Increment question index
    quiz.title(f'Question {count + 1}')
    if count < len(questions):  # If there are more questions
        # Update question label
        qlabel.configure(text=questions[count]['question'])
        
        # Update answer buttons
        for i, button in enumerate(answers_buttons):
            button.configure(
                text=questions[count]['options'][i],
                fg_color="gray",
                command=lambda btn=button, option=questions[count]['options'][i]: button_clicked(option, questions[count]['answer'], btn, quiz, qlabel, answers_buttons,student,Score_label)
            )
    else:
        # If no more questions, display completion message
        qlabel.configure(text="Quiz Completed!")
        for button in answers_buttons:
            button.destroy()  # Remove answer buttons
        update_student(student=student)


def CreateQuiz(student):
    """
    Creates the quiz window with questions and options.
    """
    tuioScoure=student['tuio_score']
    global count
    count = 0  # Reset question index

    quiz = ctk.CTk()
    quiz.geometry('900x400+400+150')
    quiz.title(f'Question {count + 1}')

    mainframe = ctk.CTkFrame(quiz, width=500, height=400, corner_radius=15)
    mainframe.pack(pady=30)

    # Score label (placeholder for future use)
    Score_label = ctk.CTkLabel(mainframe, text=f"{student['name']} : {tuioScoure}")
    Score_label.place(relx=0.5, rely=0.1, anchor='center')

    # Question label
    question_label = ctk.CTkLabel(mainframe, text=questions[count]['question'], font=("Arial", 16))
    question_label.place(relx=0.5, rely=0.3, anchor='center')

    # Answer buttons
    answers_buttons = []

    # Button 1 (First row, left)
    answerButton1 = ctk.CTkButton(mainframe, text=questions[count]['options'][0],
                                  command=lambda: button_clicked(questions[count]['options'][0], questions[count]['answer'], answerButton1, quiz, question_label, answers_buttons,student,Score_label))
    answerButton1.place(relx=0.3, rely=0.5, anchor='center')
    answers_buttons.append(answerButton1)

    # Button 2 (First row, right)
    answerButton2 = ctk.CTkButton(mainframe, text=questions[count]['options'][1],
                                  command=lambda: button_clicked(questions[count]['options'][1], questions[count]['answer'], answerButton2, quiz, question_label, answers_buttons,student,Score_label))
    answerButton2.place(relx=0.7, rely=0.5, anchor='center')
    answers_buttons.append(answerButton2)

    # Button 3 (Second row, left)
    answerButton3 = ctk.CTkButton(mainframe, text=questions[count]['options'][2],
                                  command=lambda: button_clicked(questions[count]['options'][2], questions[count]['answer'], answerButton3, quiz, question_label, answers_buttons,student,Score_label))
    answerButton3.place(relx=0.3, rely=0.7, anchor='center')
    answers_buttons.append(answerButton3)

    # Button 4 (Second row, right)
    answerButton4 = ctk.CTkButton(mainframe, text=questions[count]['options'][3],
                                  command=lambda: button_clicked(questions[count]['options'][3], questions[count]['answer'], answerButton4, quiz, question_label, answers_buttons,student,Score_label))
    answerButton4.place(relx=0.7, rely=0.7, anchor='center')
    answers_buttons.append(answerButton4)

    quiz.mainloop()