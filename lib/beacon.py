#!/usr/bin/env python3


import asyncio
from lib.path_challenge import construct_frame
from lib.path_challenge import PathChallenge, PathResponse


class BeaconReceiver(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        challenge_frame = construct_frame(data)
        response_frame = PathResponse(challenge_frame.challenge)
        # send path response
        self.transport.sendto(response_frame.to_bytes(), addr)
        self.transport.close()

    def error_received(self, exc):
        pass

    # will be used to finish
    def connection_lost(self, exc):
        pass


async def transmit_beacon(host: tuple[str, int], challenge=b'\x00'*8, burst=1, timeout=1):
    # Get a reference to the event loop as we plan to use
    # low-level APIs.

    loop = asyncio.get_running_loop()
    challenge_frame = PathChallenge(challenge)

    host = ("127.0.0.1" if host[0] == "localhost" else host[0], host[1])
    transport, _ = await loop.create_datagram_endpoint(lambda: BeaconReceiver(), local_addr=("0.0.0.0", host[1]))

    while not transport.is_closing():
        for _ in range(burst):
            transport.sendto(challenge_frame.to_bytes(), host)
        await asyncio.sleep(timeout)
    transport.close()


def main_loop(addr: tuple[str, int], challenge=b'\x00'*8, burst=1, timeout=1):
    asyncio.run(transmit_beacon(addr, challenge, burst, timeout))


# Used for testing
if __name__ == "__main__":
    main_loop(("127.0.0.1", 1337), challenge=b"AAAABBBB")
