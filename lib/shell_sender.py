import os
import asyncio

from pathlib import Path
from typing import cast

from aioquic.asyncio import QuicConnectionProtocol, connect
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived

def change_host_if_inside_docker(dest_ip:str)->str:
    """
    To prevent from generating ssl certificate for each bot (aioquic needs url for creating connection)
    We use the same ssl certificate in the aioquic project folder which prevents us from using any other url
    other then "localhost" so we we edit the host file if we are in docker so we could connect to other machines
    using localhost as replacement for the dest ip of the bot.
    """
    cgroup = Path('/proc/self/cgroup')
    if Path('./dockerenv').is_file() or cgroup.is_file() and 'docker' in cgroup.read_text():
        os.system(f"echo {dest_ip}       localhost > /etc/hosts")
        return "localhost"
    return dest_ip

class ShellSender:
    CERT_FILE_PATH = "lib/cert/pycacert.pem"
    SECRETS_LOG_PATH = "tls_secrets.log"

    def __init__(self, remote: dict[str, int], local_port: int) -> None:
        self.remote = remote
        self.local_port = local_port

        self.configuration = QuicConfiguration(is_client=True)

        self.configuration.secrets_log_file = open(self.SECRETS_LOG_PATH, "a")
        self.configuration.load_verify_locations(self.CERT_FILE_PATH)

    async def send_command(self, cmd: str) -> None:
        async with connect(
            self.remote[0],
            self.remote[1],
            configuration=self.configuration,
            session_ticket_handler=None,  # save_session_ticket,
            create_protocol=ShellSenderProtocol,
            wait_connected=False,
            local_port=self.local_port
        ) as client:
            client = cast(ShellSenderProtocol, client)
            return await client.send(cmd)


class ShellSenderProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.stream_id = self._quic.get_next_available_stream_id()
        self._ack_waiter = None
        self.response = ""

    async def send(self, cmd: str) -> str:
        # send query and wait for answer
        self._quic.send_stream_data(self.stream_id, cmd.encode(), end_stream=True)
        waiter = self._loop.create_future()
        self._ack_waiter = waiter
        self.transmit()

        return await asyncio.shield(waiter)

    def quic_event_received(self, event: QuicEvent) -> None:
        if self._ack_waiter is not None:
            if isinstance(event, StreamDataReceived):
                self.response = f"{self.response}{event.data.decode()}"
                # return response
                if event.end_stream:
                    waiter = self._ack_waiter
                    self._ack_waiter = None
                    waiter.set_result(self.response)


if __name__ == "__main__":

    shell_sender = ShellSender(("localhost", 1337), 1338)
    asyncio.run(shell_sender.send_command("ipconfig"))
