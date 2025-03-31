# client.py
import socket
import threading
import json
from common import HOST, PORT, BUFFER_SIZE

def receive_messages(client_socket):
    """Continuously listens for incoming JSON messages."""
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE)
            if not message:
                break
            try:
                msg = json.loads(message.decode("utf-8"))
            except json.JSONDecodeError:
                continue
            
            msg_type = msg.get("type")
            if msg_type == "notification":
                print("\n[Notification] " + msg.get("content", ""))
            elif msg_type == "message":
                sender = msg.get("sender", "Unknown")
                content = msg.get("content", "")
                print(f"\n{sender}: {content}")
            elif msg_type == "offline_message":
                sender = msg.get("sender", "Unknown")
                timestamp = msg.get("timestamp", "")
                content = msg.get("content", "")
                print(f"\n[Offline][{timestamp}] {sender}: {content}")
            # Reprint prompt.
            print(f"You ({client_username}): ", end="", flush=True)
        except Exception:
            break

def start_client():
    global client_username
    client_username = input("Enter your username: ")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    
    # Send login message.
    login_msg = {"type": "login", "username": client_username}
    client_socket.send(json.dumps(login_msg).encode("utf-8"))
    
    # Wait for welcome message.
    welcome_message = client_socket.recv(BUFFER_SIZE).decode("utf-8")
    try:
        welcome_msg = json.loads(welcome_message)
        if welcome_msg.get("type") == "notification":
            print(welcome_msg.get("content", ""))
    except json.JSONDecodeError:
        print(welcome_message)
    
    print(f"Connected to server at {HOST}:{PORT}")
    print("If you want to exit, type 'exit' in the command line.")
    # Start a thread to receive messages.
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()

    try:
        while True:
            message = input(f"You ({client_username}): ")
            if message.lower() == "exit":
                # Send logout message.
                logout_msg = {"type": "logout", "username": client_username}
                client_socket.send(json.dumps(logout_msg).encode("utf-8"))
                break
            msg_dict = {"type": "message", "content": message}
            client_socket.send(json.dumps(msg_dict).encode("utf-8"))
    except KeyboardInterrupt:
        pass
    finally:
        client_socket.close()
        print("Disconnected from server.")

if __name__ == '__main__':
    start_client()
