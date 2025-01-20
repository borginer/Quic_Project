#!/usr/bin/env python3


import asyncio
from lib.path_challenge import construct_frame
from lib.path_challenge import PathChallenge, PathResponse


class BeaconReceiver(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport = None
        self.dest_port: int = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        frame = construct_frame(data)

        if isinstance(frame, PathChallenge):
            self.dest_port = int.from_bytes(frame.challenge)
            response_frame = PathResponse(frame.challenge)
            # send path response
            self.transport.sendto(response_frame.to_bytes(), addr)
            self.transport.close()

    def error_received(self, exc):
        pass

    # will be used to finish
    def connection_lost(self, exc):
        pass


async def transmit_beacon(remote_addr: tuple[str, int], local_port=1337, challenge=b'\x00'*8, burst=1, timeout=1) -> int:
    # Get a reference to the event loop as we plan to use
    # low-level APIs.

    loop = asyncio.get_running_loop()
    challenge_frame = PathChallenge(challenge)

    remote_addr = (
        "127.0.0.1" if remote_addr[0] == "localhost" else remote_addr[0], remote_addr[1])
    transport, protocol = await loop.create_datagram_endpoint(lambda: BeaconReceiver(), local_addr=("0.0.0.0", local_port))

    while not transport.is_closing():
        for _ in range(burst):
            transport.sendto(challenge_frame.to_bytes(), remote_addr)
        await asyncio.sleep(timeout)
    transport.close()

    return protocol.dest_port


def main_loop(addr: tuple[str, int], local_port=1337, challenge=b'\x00'*8, burst=1, timeout=1):
    asyncio.run(transmit_beacon(addr, local_port, challenge, burst, timeout))


# Used for testing
if __name__ == "__main__":
    main_loop(("127.0.0.1", 1338), 1337, challenge=b"AAAABBBB")
