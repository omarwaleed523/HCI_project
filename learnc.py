import customtkinter as ctk
import socket
import threading
from PIL import Image, ImageTk  # Updated import for Tkinter-compatible image
from tkinter import messagebox
image_paths = [f"fruit_images/{i}.png" for i in range(1, 5)]
image_info = []
fruit_info_list = [
    {
        'id': 1,
        'name': 'Apple',
        'color': 'Red or Green',
        'fun_fact': 'Apples keep doctors away! They are super healthy and full of vitamins.'
    },
    {
        'id': 2,
        'name': 'Banana',
        'color': 'Yellow',
        'fun_fact': 'Bananas are great for energy! They are also very sweet and yummy!'
    },
    {
        'id': 3,
        'name': 'Orange',
        'color': 'Orange',
        'fun_fact': 'Oranges are packed with Vitamin C, helping you stay healthy and strong.'
    },
    {
        'id': 4,
        'name': 'Grape',
        'color': 'Purple or Green',
        'fun_fact': 'Grapes are tiny, but full of flavor! They make great snacks and juice.'
    }
]
def CreateLearnScreen():
    root=ctk.CTk()#create the form
    root.geometry('800x450+400+250')
    root.title("Welcome [student name]")
    mainframe = ctk.CTkFrame(root, width=700, height=450, corner_radius=10)
    mainframe.pack(pady=20)
    mainframe.configure(bg_color="black")
    mainframe.pack_propagate(False)
    gray_image_frame = ctk.CTkFrame(mainframe, width=700, height=(int(450/2)-100), corner_radius=10)
    gray_image_frame.place(x=0, y=0)
    start_x = 100
    start_y = 20
    x_offset = 150  # Distance between each image in the row

    try:
        # Loop over the image paths
        for col_idx, image_path in enumerate(image_paths):
            # Open and process the image (grayscale background)
            original_image = Image.open(image_path)

            # Convert the image to grayscale (already done in the file)
            grayscale_image = original_image.convert("L")

            # Resize the grayscale image to fit the GUI
            resized_image = grayscale_image.resize((100, 100))

            # Convert the image to a format compatible with customtkinter
            image_tk = ImageTk.PhotoImage(resized_image)

            # Calculate the X position for the image
            x_pos = start_x + (col_idx * x_offset)
            y_pos = start_y

            # Create a label with the image (static grayscale background) inside the gray_image_frame
            image_label = ctk.CTkLabel(gray_image_frame, image=image_tk, text="")
            image_label.image = image_tk  # Prevent garbage collection
            image_label.place(x=x_pos, y=y_pos)

            # Store the image path, its position (X, Y), and the label in image_info
            image_info.append({  # Use append to add a new dictionary
                'image_path': image_path,
                'x': x_pos,
                'y': y_pos,
                'label': image_label,
                'image': image_tk  # Store initial image as well
            })

    except Exception as e:
        print(f"Error loading or processing image: {e}")
    # Now image_info contains the image path, position, label, and image references
    print(image_info)  # For debugging or further use
    root.mainloop()


#parse data from the server
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
                        'x': float(marker_x) * 700,
                        'y': float(marker_y) * 450
                    })
        else:
            marker_id, marker_angle, marker_x, marker_y = data.split(",")
            markers.append({
                'id': int(marker_id),
                'angle': float(marker_angle),
                'x': float(marker_x) * 700,
                'y': float(marker_y) * 450
            })
    except ValueError as e:
        print(f"Invalid data format received: {data} - Error: {e}")
    return markers


# Server setup to listen for incoming client connections
def start_server(root, status_label):
    """Start the socket server and wait for a connection."""
    listensocket = socket.socket()
    Port = 8000
    IP = socket.gethostname()

    listensocket.bind(('', Port))
    listensocket.listen(1)
    status_label.configure(text="Server started. Waiting for connection...")
    print(f"Server started at {IP} on port {Port}")
    print("Waiting for a client to connect...")

    client_socket, address = listensocket.accept()
    print(f"New connection made from {address}")
    
    global current_client_socket
    current_client_socket = client_socket

    # Start a thread to handle client data
    threading.Thread(target=handle_client_data, args=(client_socket,), daemon=True).start()

    # Update GUI to start the Learn Screen after server starts
    root.after(0, lambda: CreateLearnScreen())

# Update GUI based on the received marker
def update_gui_based_on_marker(marker):
    """Update the GUI based on the received marker's position."""
    for image in image_info:
        if image['id'] == marker['id']:
            # Move image to new position based on marker
            image['label'].place(x=marker['x'], y=marker['y'])

# Handling client data in a separate thread
def handle_client_data(client_socket):
    """Continuously receive data from the client and update the GUI."""
    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            markers = parse_client_data(data)
            for marker in markers:
                update_gui_based_on_marker(marker)

def create_server_gui():
    # Initialize Tkinter root window here
    root = ctk.CTk()
    root.geometry("400x200")
    root.title("Server Status")
    
    # Update GUI to display initial message
    status_label = ctk.CTkLabel(root, text="Server not started", font=("Arial", 14))
    status_label.pack(pady=50)

    # Start the server after creating the GUI
    start_server(root)

    root.mainloop()
if __name__=='__main__':
    CreateLearnScreen()