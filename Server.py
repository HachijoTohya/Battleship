import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = "169.254.245.40"
port = 27015
s.bind((ip, port))

s.listen(2)
print(f"Server listening on port {port}")
while True:
    conn, addr = s.accept()
    print(f"{addr} connected.")
    message = "Greetings, traveller."
    conn.send(message.encode("utf-8"))


