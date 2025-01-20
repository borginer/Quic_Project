import struct
from aioquic.quic.packet import QuicFrameType


class PathFrame:
    def __init__(self) -> None:
        self._frame_type = None
        self._challenge = None

    @property
    def frame_type(self):
        return self._frame_type

    @property
    def challenge(self):
        return self._challenge

    def to_bytes(self) -> bytes:
        return struct.pack('>B8s', self._frame_type, self._challenge)


class PathChallenge(PathFrame):

    def __init__(self, challenge) -> None:
        self._frame_type = QuicFrameType.PATH_CHALLENGE
        if isinstance(challenge, int):
            self._challenge = challenge.to_bytes(8)
        else:
            self._challenge = challenge


class PathResponse(PathFrame):

    def __init__(self, challenge) -> None:
        self._frame_type = QuicFrameType.PATH_RESPONSE
        if isinstance(challenge, int):
            self._challenge = challenge.to_bytes(8)
        else:
            self._challenge = challenge


def construct_frame(buffer: bytes) -> PathFrame:
    frame_type, challenge = struct.unpack('>B8s', buffer)
    match frame_type:
        case QuicFrameType.PATH_CHALLENGE:
            return PathChallenge(challenge)
        case QuicFrameType.PATH_RESPONSE:
            return PathResponse(challenge)
