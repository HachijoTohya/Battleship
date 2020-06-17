import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(("169.254.245.40", 27015))
buffer = 1024
username = input("Enter Username: ")
s.send(username.encode('utf-8'))


def rec_message():
    while True:
        recmsg = s.recv(buffer)
        print(recmsg.decode('utf-8'))


tr = threading.Thread(target=rec_message)

while True:
    message = input()
    s.send(message.encode('utf-8'))
    if message.lower() == "!disconnect":
        s.close()
    if not tr.is_alive():
        tr.start()
