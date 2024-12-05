


def parse_client_data(data):
    """Parse the client data string into a list of data objects."""
    markers = []
    try:
        # Split the data string by ';' to get individual marker information
        if ";" in data:
            for marker_info in data.split(";"):
                marker_info = marker_info.strip()  # Remove any extra whitespace
                if marker_info:
                    # Split each marker information by ',' and expect 4 values: ID, angle, X, Y
                    marker_id, marker_angle, marker_x, marker_y = marker_info.split(",")
                    markers.append({
                        'id': int(marker_id),  # Convert ID to integer
                        'angle': float(marker_angle),  # Convert angle to float
                        'x': float(marker_x)*window_width,  # Convert X-coordinate to float
                        'y': float(marker_y)*window_height   # Convert Y-coordinate to float
                    })
        else:
            

            # If there's no ';', split the data by ',' (this assumes single marker data is sent)
            marker_id, marker_angle, marker_x, marker_y = data.split(",")
            markers.append({
                'id': int(marker_id),  # Convert ID to integer
                'angle': float(marker_angle),  # Convert angle to float
                'x': float(marker_x)*window_width,  # Convert X-coordinate to float
                'y': float(marker_y)*window_height   # Convert Y-coordinate to float
            })
    except ValueError as e:
        print(f"Invalid data format received: {data} - Error: {e}")
    return markers


def handle_client_data(client_socket):
    """Continuously receive data from the client and update the GUI."""
    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            markers = parse_client_data(data)
            for marker in markers:
                update_gui_based_on_marker(marker)
                


def update_gui_based_on_marker(marker):
    """Update the GUI based on the received marker data."""
    print(f"Received marker ID: {marker['id']} with angle: {marker['angle']},X: {marker['x']}  ; Y:{marker['y']}")
    # Highlight the image based on marker ID (for example)

def highlighted_image(marker):
    """Highlight the image based on the ID."""
    # This function will be used to update the image in the GUI.
    print(f"Highlighting image with ID: {marker['id']},Marker x: {marker['x']},Y:{marker['y']}")
    # You can implement visual feedback here, such as changing the image border or color
    
    def start_server(root, status_label):
    """Start the socket server and wait for a connection."""
    listensocket = socket.socket()
    Port = 8000
    IP = socket.gethostname()

    listensocket.bind(('', Port))
    listensocket.listen(1)
    status_label.configure(text="Server started. Waiting for connection...")
    print("Server started at " + IP + " on port " + str(Port))
    print("Waiting for a client to connect...")

    client_socket, address = listensocket.accept()
    print(f"New connection made from {address}")
    
    global current_client_socket
    current_client_socket = client_socket

    # Update the GUI to start the Image Matching GUI
    root.after(0, lambda: start_image_matching_gui(root))

    # Start a thread to handle client data
    threading.Thread(target=handle_client_data, args=(client_socket,), daemon=True).start()