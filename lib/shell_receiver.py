import asyncio
from typing import Callable, Dict, Optional

from aioquic.quic.connection import QuicConnection
from aioquic.asyncio import QuicConnectionProtocol, serve
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived
from aioquic.tls import SessionTicket
from lib.shell import execute_command
from lib.resettable_timer import ResettableTimer

waiter: asyncio.Future = None
con_close_timer: ResettableTimer = None  # (timeout, self.__set_future)


class ShellReceiver:
    CERT_FILE_PATH = "lib/cert/ssl_cert.pem"
    CERT_FILE_KEY = "lib/cert/ssl_key.pem"

    def __init__(self, addr: str, port: int, timeout: int) -> None:
        self.addr = addr
        self.port = port
        self.timeout = timeout
        self.future: asyncio.Future = None

        self.configuration = QuicConfiguration(is_client=False)

        self.session_ticket_store = SessionTicketStore()

        self.configuration.load_cert_chain(
            self.CERT_FILE_PATH, self.CERT_FILE_KEY)

    async def listen(self) -> None:
        global waiter
        global con_close_timer

        loop = asyncio.get_running_loop()
        waiter = loop.create_future()
        con_close_timer = ResettableTimer(self.timeout, set_future_callback)
        con_close_timer.start()

        await serve(self.addr, self.port,
                    configuration=self.configuration,
                    create_protocol=ShellReceiverProtocol,
                    session_ticket_fetcher=self.session_ticket_store.pop,
                    session_ticket_handler=self.session_ticket_store.add
                    )
        await waiter


async def set_future_callback():
    global waiter
    if waiter is not None:
        waiter.set_result('')


class ShellReceiverProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def quic_event_received(self, event: QuicEvent):
        if isinstance(event, StreamDataReceived):
            global con_close_timer
            con_close_timer.reset()

            # print(event.data)
            # perform lookup and serialize answer
            stdout, stderr = execute_command(event.data.decode())
            if stdout:
                self._quic.send_stream_data(
                    event.stream_id, stdout.encode(), end_stream=True)
                # self._quic.send_stream_data(event.stream_id, stdout.encode())
            if stderr:
                self._quic.send_stream_data(
                    event.stream_id, stderr.encode(), end_stream=True)
                # self._quic.send_stream_data(event.stream_id, stderr.encode())


class SessionTicketStore:
    """
    Simple in-memory store for session tickets.
    """

    def __init__(self) -> None:
        self.tickets: Dict[bytes, SessionTicket] = {}

    def add(self, ticket: SessionTicket) -> None:
        self.tickets[ticket.ticket] = ticket

    def pop(self, label: bytes) -> Optional[SessionTicket]:
        return self.tickets.pop(label, None)


if __name__ == "__main__":

    shell_receiver = ShellReceiver("::", 1337, 60)

    try:
        asyncio.run(shell_receiver.listen())
    except KeyboardInterrupt:
        pass
