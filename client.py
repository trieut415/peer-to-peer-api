# client.py
import socket
import threading
from common import HOST, PORT, BUFFER_SIZE

def receive_messages(client_socket, my_user_id):
    """Continuously listens for incoming messages and reprints the prompt afterward."""
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE)
            if not message:
                # Server closed connection
                break
            decoded_message = message.decode("utf-8")
            # If the message is from the current user, adjust the display.
            if my_user_id is not None and decoded_message.startswith(f"User{my_user_id}:"):
                new_message = f"You (User{my_user_id}):" + decoded_message[len(f"User{my_user_id}:"):]
                print("\n" + new_message)
            else:
                print("\n" + decoded_message)
            # After printing the received message, reprint the input prompt.
            if my_user_id is not None:
                print(f"You (User{my_user_id}): ", end="", flush=True)
            else:
                print("Enter message (or type 'exit' to quit): ", end="", flush=True)
        except Exception:
            break

def start_client(server_host=HOST, server_port=PORT):
    """Connects to the server, receives the welcome message, and handles sending messages."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))
    
    # Wait to receive the welcome message synchronously.
    welcome_message = client_socket.recv(1024).decode("utf-8")
    print(welcome_message)
    
    # Parse the user ID from the welcome message "Welcome UserX!"
    my_user_id = None
    try:
        if welcome_message.startswith("Welcome User") and welcome_message.endswith("!"):
            my_user_id = welcome_message[len("Welcome User"):-1].strip()
    except Exception:
        pass
    
    # Print the connection confirmation message.
    print(f"Connected to server at {server_host}:{server_port}")

    # Start a background thread to receive messages.
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, my_user_id))
    receive_thread.daemon = True
    receive_thread.start()

    try:
        while True:
            # Use the updated prompt which shows your user ID.
            message = input(f"You (User{my_user_id}): ")
            if message.lower() == "exit":
                break
            client_socket.send(message.encode("utf-8"))
    except KeyboardInterrupt:
        pass
    finally:
        client_socket.close()
        print("Disconnected from server.")

if __name__ == '__main__':
    start_client()
