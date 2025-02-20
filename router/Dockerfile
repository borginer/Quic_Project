# Use Ubuntu as the base image
FROM ubuntu:latest

# Install dependencies (iptables and sysctl tools)
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y iproute2 inetutils-ping curl host mtr-tiny tcpdump iptables \
    && rm -rf /var/lib/apt/lists/*

# Copy the startup script into the container
COPY start_router.sh /usr/local/bin/start_router.sh
RUN chmod +x /usr/local/bin/start_router.sh

# Set entrypoint to the startup script
ENTRYPOINT ["/usr/local/bin/start_router.sh"]