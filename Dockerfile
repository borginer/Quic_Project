FROM ubuntu:latest

# Install Python and any other dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get install -y net-tools iputils-ping && \
    apt-get install -y libssl-dev python3-dev

RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip3 install --break-system-packages -r /tmp/requirements.txt

WORKDIR /home/usr

SHELL ["/bin/bash", "-c"]

RUN echo "TOP SECRET" > /home/secret.txt
