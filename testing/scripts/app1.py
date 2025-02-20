import socket
import time

hostname = socket.gethostname()

ip_address = socket.gethostbyname(hostname)

print("Hostname: " + hostname + "\nIP: " + ip_address)



def send_message(host='172.16.2.5', port=2000, message='Hello, Server!'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((host, port))
            client_socket.sendall(message.encode())
            print(f"Sent: {message}")
        except ConnectionRefusedError as e:
            print(f"Connection refused: {e}")

if __name__ == "__main__":
    time.sleep(1)
    send_message()