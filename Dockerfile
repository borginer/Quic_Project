FROM ubuntu:latest

# Install Python and any other dependencies
RUN apt-get update && \
    apt-get install -y iproute2 inetutils-ping curl host mtr-tiny tcpdump iptables && \
    apt-get install -y python3 python3-pip && \
    apt-get install -y libssl-dev python3-dev

RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip3 install --break-system-packages -r /tmp/requirements.txt

WORKDIR /home/usr