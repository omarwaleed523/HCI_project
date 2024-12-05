import cv2
import face_recognition
from simple_facerec import SimpleFacerec
import time
from display_studentData import create_student_gui
def Face_recog(student):
    sfr = SimpleFacerec()
    sfr.load_encoding_images("images/")

    # Start webcam capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

    print("Press 'ESC' to exit.")
    is_detect = False
    start_time = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Detect known faces
        face_locations, face_names = sfr.detect_known_faces(frame)
        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc
            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)
            detect = name

            # If the person is recognized and it's the first detection
            if name != "Unknown" and not is_detect:
                is_detect = True
                start_time = time.time()  # Start the timer

        # If a person has been detected for 5 seconds, exit
        if is_detect and time.time() - start_time > 5 and name==student['name']:
            print(f"{detect} detected for 5 seconds, closing.")
            cap.release()
            cv2.destroyAllWindows()
            create_student_gui(student)
            break

        # Show the frame
        cv2.imshow("Frame", frame)

        # Wait for key press and break on 'ESC'
        key = cv2.waitKey(1)
        if key == 27:  # ASCII code for 'ESC'
            print("Exiting...")
            break

