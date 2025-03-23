# Peer-to-Peer Chat API

A simple chat API using Python’s socket module with a client–server architecture. Each client is assigned a unique user number, and the server broadcasts connection/disconnection events. The client displays incoming messages, formats your own messages with a "You (UserX):" prompt, and reprints the prompt after each message.



## How to Use

### Running the Server

1. Open a terminal and navigate to the project directory:
   ```bash
   cd peer-to-peer-api
   ```

2. Run the server:
   ```bash
   python3 server.py
   ```
3. Running a Client
Open a new terminal (or multiple terminals for multiple clients).

Navigate to the project directory:
   ```bash
   cd peer-to-peer-api
   python3 client.py
   ```
For new clients, just open a new terminal and redo this step. Then you can communicate!

---

### Server:

- Accepts client connections.
- Assigns a unique user ID (e.g., User1, User2, …).
- Broadcasts notifications when a user connects or disconnects.
- Echoes incoming messages by prefixing them with the sender’s user ID.

### Client: 

- Receives a welcome message (e.g., "Welcome User6!") upon connection.
- Displays "Connected to server at 127.0.0.1:12345" after the welcome.
- Uses an input prompt that shows your user ID (e.g., "You (User6): ").
- Formats outgoing and incoming messages so that if a message is from you, it is shown as "You (User6): ...".
