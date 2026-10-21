import socket

def check_port(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    result = s.connect_ex((host, port))
    s.close()
    return result == 0

port = int(input("Enter a port number: "))

if check_port("127.0.0.1", port):
    print(f"Port {port} is OPEN")
else:
    print(f"Port {port} is CLOSED")
