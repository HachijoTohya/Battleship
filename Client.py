import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(("169.254.245.40", 27015))

full = ''
buffer = 4
while True:
    message = s.recv(buffer)
    print(len(message))
    if len(message) < buffer:
        break
    full += message.decode('utf-8')

print(full)
s.close()