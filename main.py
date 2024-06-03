import socket
import threading
import redis

# Підключення до Redis
r = redis.Redis(host='localhost', port=6379, db=0)

clients = []


def handle_client(client_socket, addr):
    print(f"New connection: {addr}")
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Received message from {addr}: {message}")

            r.rpush('chat_messages', message)

            broadcast(message, client_socket)
        except Exception as e:
            print(f"Error handling message from {addr}: {e}")
            break

    client_socket.close()
    clients.remove(client_socket)
    print(f"Connection closed: {addr}")


def broadcast(message, sending_socket):
    for client in clients:
        if client != sending_socket:
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting message: {e}")
                client.close()
                clients.remove(client)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(5)

print("Server is listening on port 12345")

while True:
    client_socket, addr = server_socket.accept()
    clients.append(client_socket)
    client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
    client_thread.start()
