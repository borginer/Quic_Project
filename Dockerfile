FROM ubuntu:latest

# Install Python and any other dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip

WORKDIR /usr
# Copy the Python scripts into the working directory
COPY ./scripts /usr