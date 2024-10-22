import socket

hostname = socket.gethostname()

ip_address = socket.gethostbyname(hostname)

print("Hostname: " + hostname + "\nIP: " + ip_address)

def start_server(host='0.0.0.0', port=2000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Server listening on {host}:{port}")

        while True:
            print("Waiting for connections...")
            try:
                conn, addr = server_socket.accept()
                print(f"Connected by {addr}")
                with conn:
                    data = conn.recv(1024)
                    print(f"Received: {data.decode()}")
                    # Optionally send a response back to the client
                    conn.sendall(b'Hello, Client!')
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    start_server()