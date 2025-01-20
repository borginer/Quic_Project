#!/usr/bin/env python3

import time
import argparse


import asyncio
from lib.path_challenge import construct_frame
from lib.path_challenge import PathChallenge, PathResponse


freshness = None


def is_attacker(challenge: bytes) -> bool:
    return '1' == challenge.decode()[0]


def get_attacker_challenge(challenge: bytes) -> bytes:
    return b'0%b' % challenge[1:]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QUIC coordination server")

    parser.add_argument("-port",
                        type=int,
                        default=1338,
                        help="listening port for quic challenges")

    parser.add_argument("-fresh",
                        type=int,
                        default=60,
                        help="time to consider the quic challenge fresh and legitimate to use")

    args = parser.parse_args()
    return args


class TraversalHandler(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport = None
        self.client_stat = {}

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        global freshness

        frame = construct_frame(data)
        if isinstance(frame, PathChallenge):
            response_frame = PathResponse(frame.challenge)
            # here we track the quic path challenge protocol
            self.transport.sendto(response_frame.to_bytes(), addr)

            if not is_attacker(frame.challenge):
                # time, (ip addr, port)
                print(
                    f"Received path challenge from bot {addr}, id:{frame.challenge.decode()}")

                self.client_stat[frame.challenge] = (time.time(), addr)

            else:
                challenge = get_attacker_challenge(frame.challenge)
                print(
                    f"Received path challenge from attacker {addr}, id:{challenge.decode()}")

                if challenge in self.client_stat.keys():
                    measured_time, client_addr = self.client_stat[challenge]
                    if time.time() - measured_time < freshness:
                        # attacker external port for the bot
                        bot_frame = PathChallenge(addr[1])
                        # bot external port for the attacker
                        attacker_frame = PathChallenge(client_addr[1])

                        self.transport.sendto(bot_frame.to_bytes(), client_addr)
                        self.transport.sendto(attacker_frame.to_bytes(), addr)

    def error_received(self, exc):
        pass

    # will be used to finish
    def connection_lost(self, exc):
        pass


async def main_loop(args: argparse.Namespace):
    global freshness

    print("Starting QUIC coordination server")

    freshness = args.fresh

    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    lock = loop.create_future()

    # One protocol instance will be created to serve all
    # client requests.
    transport, _ = await loop.create_datagram_endpoint(
        TraversalHandler,
        local_addr=('0.0.0.0', args.port))

    try:
        await lock
    finally:
        transport.close()

if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main_loop(args))
