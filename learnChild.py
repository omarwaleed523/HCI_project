import customtkinter as ctk
import socket
import threading
from PIL import Image, ImageTk
from tkinter import messagebox
from Students_data import read_highschool_students_from_csv
student_data=read_highschool_students_from_csv('students data.csv')
# Define global variables
image_paths = [f"fruit_images/{i}.png" for i in range(1, 5)]
image_info = []
moving_images_info = []
marker_info=[]
gray_image_frame = None
mainframe = None  # Define mainframe as a global variable

# Fruit information (not used in the code provided but kept for future functionality)
fruit_info_list = [
    {'id': 1, 'name': 'Apple', 'color': 'Red or Green', 'fun_fact': 'Apples keep doctors away!'},
    {'id': 2, 'name': 'Banana', 'color': 'Yellow', 'fun_fact': 'Bananas are great for energy!'},
    {'id': 3, 'name': 'Orange', 'color': 'Orange', 'fun_fact': 'Oranges are packed with Vitamin C!'},
    {'id': 4, 'name': 'Grape', 'color': 'Purple or Green', 'fun_fact': 'Grapes are tiny, but full of flavor!'}
]

# Initialize the fruit info label
fruit_info_label = None

def CreateLearnScreen(root, student):
    global gray_image_frame, mainframe, fruit_info_label  # Declare as global

    root.geometry('800x450+400+250')
    root.title(f"Welcome {student['name']}")
    
    # Create main frame
    mainframe = ctk.CTkFrame(root, width=700, height=450, corner_radius=10)
    mainframe.pack(pady=20)
    mainframe.configure(bg_color="black")
    mainframe.pack_propagate(False)

    # Create the frame for gray images
    gray_image_frame = ctk.CTkFrame(mainframe, width=700, height=(int(450 / 2) - 100), corner_radius=10)
    gray_image_frame.place(x=0, y=0)

    start_x = 100
    start_y = 20
    x_offset = 150  # Distance between each image in the row

    try:
        # Loop over the image paths
        for col_idx, image_path in enumerate(image_paths):
            # Open and process the image (grayscale background)
            original_image = Image.open(image_path)
            grayscale_image = original_image.convert("L")  # Convert to grayscale
            resized_image = grayscale_image.resize((100, 100))  # Resize image

            image_tk = ImageTk.PhotoImage(resized_image)  # Convert to a format tkinter can use

            x_pos = start_x + (col_idx * x_offset)
            y_pos = start_y

            image_label = ctk.CTkLabel(gray_image_frame, image=image_tk, text="")
            image_label.image = image_tk  # Prevent garbage collection
            image_label.place(x=x_pos, y=y_pos)

            image_info.append({
                'id': col_idx + 1,  # Assign an ID based on index (1, 2, 3, 4)
                'image_path': image_path,
                'x': x_pos,
                'y': y_pos,
                'label': image_label,
                'image': image_tk  # Store initial image as well
            })

        # Create a label to display fruit info
        fruit_info_label = ctk.CTkLabel(mainframe, text="", font=("Arial", 14), wraplength=650, anchor="w")
        fruit_info_label.place(x=10, y=330)  # Place the label below the gray image frame

    except Exception as e:
        print(f"Error loading or processing image: {e}")

def parse_client_data(data):
    """Parse the client data string into a list of data objects."""
    markers = []
    try:
        if ";" in data:
            for marker_info in data.split(";"):
                marker_info = marker_info.strip()
                if marker_info:
                    marker_id, marker_angle, marker_x, marker_y = marker_info.split(",")
                    markers.append({
                        'id': int(marker_id),
                        'angle': float(marker_angle),
                        'x': float(marker_x) * 800,
                        'y': float(marker_y) * 450
                    })
        else:
            marker_id, marker_angle, marker_x, marker_y = data.split(",")
            markers.append({
                'id': int(marker_id),
                'angle': float(marker_angle),
                'x': float(marker_x) * 800,
                'y': float(marker_y) * 450,
                'ishit': False
            })
    except ValueError as e:
        print(f"Invalid data format received: {data} - Error: {e}")
    return markers

# def rotate(marker, student, item):
#     """Check if rotation is sufficient and display info based on the student data."""
#     # Check if the marker's angle is greater than 60 and the image has reached its destination
#     if marker['angle'] > 60 and item['is_there']:
#         if 14 <= student['age'] <= 17:  # Age range check
#             if student['gender'] == 'male':
#                 # Male student-specific message
#                 fruit_info_label.configure(
#                     text=f"Hey {student['name']}, this fruit is awesome! Did you know it keeps you healthy and strong?"
#                 )
#             elif student['gender'] == 'female':
#                 # Female student-specific message
#                 fruit_info_label.configure(
#                     text=f"Hey {student['name']}, this fruit is amazing! It will help you stay active and energized!"
#                 )
#         else:
#             fruit_info_label.configure(
#                 text="This fruit is great for boosting your energy!"
#             )
        
#         # Optional: Show a message box to grab attention
#         messagebox.showinfo("Fruit Info", f"You've discovered interesting info about the fruit!")
        
#         print(f"Rotation detected for marker {marker['id']}. Info displayed.")
#         return True
    
#     return False

# def update_gui_based_on_marker(marker, student):
#     """Update the GUI based on the received marker data."""
#     print(f"Received marker ID: {marker['id']} with angle: {marker['angle']}, X: {marker['x']}, Y: {marker['y']}")

#     found = False
#     for i, item in enumerate(moving_images_info):
#         if item['id'] == marker['id']:
#             if not item['is_there']:  # If image is not yet at its target
#                 # Update the label's position based on the new marker's position
#                 item['label'].place(x=marker['x'], y=marker['y'])
                
#                 # Update the position in the moving_images_info data
#                 item['x'] = marker['x']
#                 item['y'] = marker['y']
                
#                 # Check for proximity to the gray image
#                 for grayimage in image_info:
#                     if grayimage['image_path'] == item['image_path']:
#                         print(f"Checking if the marker is inside the gray image area...")
#                         image_width = 100
#                         image_height = 50

#                         # Check if the moving image is inside the target gray image area
#                         if (grayimage['x'] < marker['x'] < grayimage['x'] + image_width) and \
#                            (grayimage['y'] < marker['y'] < grayimage['y'] + image_height):
#                             print(f"Moving image {item['id']} has reached the target gray image!")
                            
#                             # Update the state of the image to show it has reached the target
#                             item['is_there'] = True
#                             item['x'] = grayimage['x']  # Set to target gray image position
#                             item['y'] = grayimage['y']
#                             item['label'].place(x=grayimage['x'], y=grayimage['y'])  # Move the label to the target
#                             item['image_path'] = grayimage['image_path']  # Update the image path

#                             # Update the item in moving_images_info list by its index (i)
#                             moving_images_info[i] = item

#                             # DEBUG: Print the updated moving_images_info for verification
#                             print(f"Updated moving_images_info: {moving_images_info}")

#                             found = True
#                 break
#             else: 
#                 # If the image is already at its target, check rotation
#                 rotate(marker, student, item)
#                 found = True

#     if not found:
#         # If the marker was not found in moving_images_info, create a new image entry
#         image_path = f'fruit_images/{marker["id"]}.png'
#         new_image = Image.open(image_path)
#         resized_image = new_image.resize((100, 100))
#         image_tk = ImageTk.PhotoImage(resized_image)
#         image_label = ctk.CTkLabel(mainframe, image=image_tk, text="")
#         image_label.image = image_tk
#         image_label.place(x=marker['x'], y=marker['y'])

#         moving_images_info.append({
#             'id': marker['id'],
#             'label': image_label,
#             'image': image_tk,
#             'x': marker['x'],
#             'y': marker['y'],
#             'is_there': False,
#             'image_path': image_path  # Store the path of the initial image
#         })

#         # DEBUG: Print the current state of moving_images_info for debugging
#         print(f"New moving image added: {moving_images_info}")

# The rest of the code remains the same as in your original script
def update_gui_based_on_marker(marker, student):
    cat = None
    index = -1
    # is hit
    for i, image in enumerate(moving_images_info):
        if marker['id'] == image['id']:
            cat = image
            index = i
            break

    if cat is not None and index >= 0:
        # Update the position of the image
        cat['label'].place(x=marker['x'], y=marker['y'])
        cat['x'] = marker['x']
        cat['y'] = marker['y']

        # Check if the image needs to be updated and placed correctly
        for gray_image in image_info:
            if gray_image['id'] == cat['id']:
                # Define a "stickiness" range (e.g., within 20px of the gray image)
                stickiness_range = 20  # Adjustable range for sticking
                if (gray_image['x'] - stickiness_range <= cat['x'] <= gray_image['x'] + 100 + stickiness_range) and \
                   (gray_image['y'] - stickiness_range <= cat['y'] <= gray_image['y'] + 100 + stickiness_range):
                    if not cat['is_there']:  # Only stick if not already done
                        cat['is_there'] = True
                        cat['x'] = gray_image['x']
                        cat['y'] = gray_image['y']
                        moving_images_info[index] = cat
                        print(f'List has been updated !!!!! {moving_images_info[index]}')
                    # Once stuck, make sure the position is aligned with the gray image
                    cat['label'].place(x=cat['x'], y=cat['y'])
                    break  # Stop checking once we find a match
    else:
        # If the marker doesn't exist in the moving images, add it
        image_path = f'fruit_images/{marker["id"]}.png'
        if image_path in image_paths:
            new_image = Image.open(image_path)
            resized_image = new_image.resize((100, 100))
            image_tk = ImageTk.PhotoImage(resized_image)
            image_label = ctk.CTkLabel(mainframe, image=image_tk, text="")
            image_label.image = image_tk
            image_label.place(x=marker['x'], y=marker['y'])

            moving_images_info.append({
                'id': marker['id'],
                'label': image_label,
                'image': image_tk,
                'x': marker['x'],
                'y': marker['y'],
                'is_there': False,
                'image_path': image_path  # Store the path of the initial image
            })


# Ensure CreateLearnScreen, handle_client_data, start_server, and create_server_gui functions
# are implemented exactly as they were in your original script
def handle_client_data(client_socket, student):
    """Continuously receive data from the client and update the GUI."""
    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            markers = parse_client_data(data)  # Parse the received data
            print(f"Received markers: {markers}")
            
            for marker in markers:
                if marker not in marker_info:
                    marker_info.append(marker)  # Save marker to marker_info if not already there
                    update_gui_based_on_marker(marker, student)
                else:
                    # Update marker if already exists (no need to add again)
                    update_gui_based_on_marker(marker, student)

def start_server(root, student):
    """Start the socket server and wait for a connection."""
    listensocket = socket.socket()
    Port = 8000
    IP = socket.gethostname()

    listensocket.bind(('', Port))
    listensocket.listen(1)
    print(f"Server started at {IP} on port {Port}")
    print("Waiting for a client to connect...")
    client_socket, address = listensocket.accept()
    print(f"New connection made from {address}")
    global current_client_socket
    current_client_socket = client_socket

    # Start a thread to handle client data
    threading.Thread(target=handle_client_data, args=(client_socket, student), daemon=True).start()

    # Update GUI to start the Learn Screen after server starts
    root.after(0, lambda: CreateLearnScreen(root, student))

def create_server_gui(student):
    """Create the server GUI and start the server."""
    root = ctk.CTk()
    root.geometry("400x200")
    root.title("Server Status")

    # Start the server after creating the GUI
    start_server(root, student)

    root.mainloop()

if __name__ == '__main__':
    # Example student data

    
    create_server_gui(student_data[0])



