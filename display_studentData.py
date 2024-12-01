import customtkinter as ctk
from PIL import Image
from Students_data import read_highschool_students_from_csv
from QuizGen import start_server_and_quiz  # For TUIO Quiz Server Start
# Import or define CreateGestureQuiz function for Gesture Quiz
# from QuizGen import CreateGestureQuiz

# Read student data from CSV
student = read_highschool_students_from_csv('students data.csv')

def create_student_gui(student):
    # Initialize the application
    app = ctk.CTk()
    app.geometry("900x400+400+150")
    app.title("Student Information")

    # Main Frame
    main_frame = ctk.CTkFrame(app, width=900, height=600, corner_radius=10)
    main_frame.pack(padx=10, pady=10, fill="both", expand=True)

    # Left Frame for Image and Name
    left_frame = ctk.CTkFrame(main_frame, width=200, height=500, corner_radius=10)
    left_frame.grid(row=0, column=0, padx=30, pady=10, sticky="nsew")

    # Display Student Image
    try:
        image = Image.open(student['photo_path']).resize((180, 180))  # Resize the image
        student_image = ctk.CTkImage(image, size=(180, 180))
        image_label = ctk.CTkLabel(left_frame, image=student_image, text="")
        image_label.image = student_image  # Prevent garbage collection
        image_label.pack(pady=10)
    except Exception as e:
        print(f"Error loading image: {e}")
        image_label = ctk.CTkLabel(left_frame, text="Image Not Found")
        image_label.pack(pady=10)

    # Display Student Name
    name_label = ctk.CTkLabel(left_frame, text=student['name'], font=("Arial", 18, "bold"))
    name_label.pack()

    # Add Buttons for TUIO Quiz and Gesture Quiz
    start_tuio_quiz_button = ctk.CTkButton(
        left_frame, text="Start TUIO Quiz",
        command=lambda: [app.destroy(), start_server_and_quiz()]  # Call start_server_and_quiz
    )
    start_tuio_quiz_button.pack(pady=10)

    start_gesture_quiz_button = ctk.CTkButton(
        left_frame, text="Start Gesture Quiz",
        command=lambda: [app.destroy(), CreateGestureQuiz(student)]  # Function for Gesture Quiz
    )
    start_gesture_quiz_button.pack(pady=10)

    # Right Frame for Details and Images
    right_frame = ctk.CTkFrame(main_frame, width=600, height=500, corner_radius=10)
    right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    right_frame.grid_columnconfigure(0, weight=1)  # Configure column 0 for details
    right_frame.grid_columnconfigure(1, weight=1)  # Configure column 1 for images

    # Frames for Each Information Field (Column 0)
    fields = {
        "Student ID": student['student_id'],
        "Class": student['class'],
        "Grade": student['grade'],
        "Age": student['age'],
        "Gender": student['gender'],
        "Email": student['email'],
        "GPA": student['gpa'],
    }

    for i, (label, value) in enumerate(fields.items()):
        field_frame = ctk.CTkFrame(right_frame, corner_radius=10)
        field_frame.grid(row=i, column=0, padx=10, pady=5, sticky="ew")

        field_label = ctk.CTkLabel(field_frame, text=f"{label}: ", font=("Arial", 14, "bold"))
        field_label.pack(side="left", padx=5)

        field_value = ctk.CTkLabel(field_frame, text=value, font=("Arial", 14))
        field_value.pack(side="left", padx=5)

    # Frame for TUIO and Gesture Scores (Below GPA)
    score_frame = ctk.CTkFrame(right_frame, corner_radius=10)
    score_frame.grid(row=len(fields), column=0, padx=20, pady=10, sticky="ew")

    tuio_score_label = ctk.CTkLabel(score_frame, text=f"TUIO Score: {student['tuio_score']}", font=("Arial", 14))
    tuio_score_label.pack(pady=5)

    gesture_score_label = ctk.CTkLabel(score_frame, text=f"Gesture Score: {student['gesture_score']}", font=("Arial", 14))
    gesture_score_label.pack(pady=5)

    # Frame for TUIO and Gesture Images (Column 1)
    image_frame = ctk.CTkFrame(right_frame, corner_radius=10)
    image_frame.grid(row=0, column=1, padx=10, pady=10, rowspan=len(fields) + 1, sticky="nsew")  # Span rows including scores

    # TUIO Image and Text
    try:
        tuio_image = ctk.CTkImage(Image.open("tuio.png"), size=(100, 100))
        tuio_label = ctk.CTkLabel(image_frame, image=tuio_image, text="")
        tuio_label.image = tuio_image  # Prevent garbage collection
        tuio_label.pack(pady=5, padx=20)

        tuio_text_label = ctk.CTkLabel(image_frame, text="Show the ID 0", font=("Arial", 12))
        tuio_text_label.pack(pady=5, padx=10)
    except Exception as e:
        print(f"Error loading TUIO image: {e}")

    # Gesture Image and Text
    try:
        gesture_image = ctk.CTkImage(Image.open("handgesture.jpg"), size=(100, 100))
        gesture_label = ctk.CTkLabel(image_frame, image=gesture_image, text="")
        gesture_label.image = gesture_image  # Prevent garbage collection
        gesture_label.pack(pady=5, padx=10)

        gesture_text_label = ctk.CTkLabel(image_frame, text="Show your hand to the camera", font=("Arial", 12))
        gesture_text_label.pack(pady=5, padx=10)
    except Exception as e:
        print(f"Error loading Gesture image: {e}")

    app.mainloop()
