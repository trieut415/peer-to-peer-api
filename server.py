# server.py
import socket
import threading
import json
from datetime import datetime
from common import HOST, PORT, BUFFER_SIZE
import database

# Initialize the database.
database.init_db()

# Dictionary mapping username to client socket.
clients = {}
lock = threading.Lock()

def broadcast(message_dict, exclude_username=None):
    """Send a JSON message to all online clients except the excluded user."""
    message_json = json.dumps(message_dict)
    with lock:
        for username, client in clients.items():
            if username != exclude_username:
                try:
                    client.send(message_json.encode('utf-8'))
                except Exception as e:
                    print(f"Error broadcasting to {username}: {e}")
                    client.close()
                    del clients[username]

def send_offline_messages(username, client_socket):
    offline_msgs = database.get_offline_messages(username)
    if offline_msgs:
        message_ids = []
        for msg in offline_msgs:
            msg_id, sender, timestamp, content = msg
            msg_dict = {
                "type": "offline_message",
                "sender": sender,
                "recipient": username,
                "timestamp": timestamp,
                "content": content
            }
            try:
                client_socket.send(json.dumps(msg_dict).encode('utf-8'))
                message_ids.append(msg_id)
            except Exception as e:
                print(f"Error sending offline message to {username}: {e}")
        # Mark these messages as delivered.
        database.mark_messages_delivered(message_ids)

def handle_client(client_socket, addr):
    """Handle login and messages from a client."""
    try:
        # First expect a login message in JSON format.
        login_data = client_socket.recv(BUFFER_SIZE).decode("utf-8")
        login_msg = json.loads(login_data)
        if login_msg.get("type") != "login" or "username" not in login_msg:
            client_socket.close()
            return
        username = login_msg["username"]
        # Register the user.
        database.register_user(username)
        with lock:
            clients[username] = client_socket
        
        # Send welcome message.
        welcome_msg = {"type": "notification", "content": f"Welcome {username}!"}
        client_socket.send(json.dumps(welcome_msg).encode('utf-8'))
        
        # Notify others that this user connected.
        broadcast({"type": "notification", "content": f"{username} has connected."}, exclude_username=username)
        
        # Send any offline messages.
        send_offline_messages(username, client_socket)
        
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            try:
                msg = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                continue
            
            if msg.get("type") == "message":
                sender = username
                content = msg.get("content", "")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message_dict = {
                    "type": "message",
                    "sender": sender,
                    "recipient": "broadcast",
                    "timestamp": timestamp,
                    "content": content
                }
                print(f"[{addr}] {sender}: {content}")
                
                # Store the message for offline users.
                all_users = database.get_all_registered_users()
                # Offline recipients are those registered but not currently online (and not the sender).
                offline_recipients = [user for user in all_users if user not in clients and user != sender]
                for recipient in offline_recipients:
                    database.store_message(sender, recipient, content)
                
                # Broadcast to online users.
                broadcast(message_dict, exclude_username=sender)
            
            elif msg.get("type") == "logout":
                break
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        with lock:
            if username in clients:
                del clients[username]
        print(f"{username} disconnected.")
        broadcast({"type": "notification", "content": f"{username} has disconnected."})

def start_server(host=HOST, port=PORT):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"[LISTENING] Server is listening on {host}:{port}")
    
    try:
        while True:
            client_socket, addr = server.accept()
            print(f"[NEW CONNECTION] Connection from {addr}")
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.start()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.close()

if __name__ == '__main__':
    start_server()
