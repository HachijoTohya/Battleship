import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = "169.254.245.40"
port = 27015
s.bind((ip, port))

s.listen(4)
print(f"Server listening on port {port}")
users = {}
conn_list = []


class ClientConnection:
    def __init__(self, id_info):
        self.conn, self.addr = id_info
        users[self.addr] = (self.conn.recv(1024)).decode('utf-8')
        self.sendthread = threading.Thread(target=send_to_client, args=(self.conn, self.addr))


def send_to_client(conn, addr):
    while True:
        message = (f"{users[addr]}: " + conn.recv(1024).decode('utf-8'))
        for connection in conn_list:
            connection.conn.send(message.encode("utf-8"))


def create_new_connection():
    conn_list.append(ClientConnection(s.accept()))
    print(users[conn_list[len(conn_list)-1].addr] + " connected")


while True:
    create_new_connection()
    for c in conn_list:
        if not c.sendthread.is_alive():
            c.sendthread.start()







