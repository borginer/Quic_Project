import socket

hostname = socket.gethostname()

ip_address = socket.gethostbyname(hostname)

print("Hostname: " + hostname + "\nIP: " + ip_address)