# server.py
import socket
import threading
from common import HOST, PORT, BUFFER_SIZE

# Global dictionary to store client socket objects with their assigned user IDs.
clients = {}
client_counter = 0
lock = threading.Lock()

def broadcast(message, sender_socket=None):
    """Send a message to all clients except the sender."""
    for client in list(clients):
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting to a client: {e}")
                client.close()
                with lock:
                    if client in clients:
                        del clients[client]

def handle_client(client_socket, addr, user_id):
    """Handle messages from a client, broadcast join/disconnect events."""
    # Send a welcome message to the newly connected client
    welcome_message = f"Welcome User{user_id}!"
    client_socket.send(welcome_message.encode('utf-8'))
    
    # Notify all other clients that a new user has connected
    broadcast(f"User{user_id} has connected.", sender_socket=client_socket)
    
    try:
        while True:
            message = client_socket.recv(BUFFER_SIZE)
            if not message:
                # No message means the client disconnected.
                break
            decoded_message = message.decode("utf-8")
            full_message = f"User{user_id}: {decoded_message}"
            print(f"[{addr}] {full_message}")
            broadcast(full_message, sender_socket=client_socket)
    except ConnectionResetError:
        pass
    finally:
        client_socket.close()
        with lock:
            if client_socket in clients:
                del clients[client_socket]
        print(f"User{user_id} disconnected.")
        broadcast(f"User{user_id} has disconnected.")

def start_server(host=HOST, port=PORT):
    """Starts the server, accepts new connections, and spawns threads for clients."""
    global client_counter
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow immediate reuse of the address after the server is closed
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"[LISTENING] Server is listening on {host}:{port}")
    
    try:
        while True:
            client_socket, addr = server.accept()
            with lock:
                client_counter += 1
                user_id = client_counter
                clients[client_socket] = user_id
            print(f"[NEW CONNECTION] User{user_id} from {addr} connected.")
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr, user_id))
            client_thread.start()
            print(f"[ACTIVE CONNECTIONS] {len(clients)}")
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.close()

if __name__ == '__main__':
    start_server()
