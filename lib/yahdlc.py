import crc16

FLAG = 0x7e
CONTROL_ESCAPE = 0x7d
ALL_STATION_ADDR = 0xff
I_FRAME = 0x0
S_U_FRAME = 0x01
FRAME_MASK = 0x01
POLL_FINAL = 0x12
FRAME_TYPE_MASK = 0xc
FRAME_TYPE_ACK = 0

class FrameType:
    DATA = 0
    ACK = 1
    ERROR = 2

class YAHDLC:
    crc_encode = crc16.CRC16()
    crc_decode = crc16.CRC16()
    def __init__(self):
       self.decode_buffer = ""
       self.flag_count = 0
       self.in_escape = False

    def start_encode_frame(self):
       self.encode_buffer = chr(ALL_STATION_ADDR) + chr(POLL_FINAL | I_FRAME)
       self.crc_encode.clear()

    def add_payload_to_encode_frame(self, s):
       for c in s:
           if c == chr(CONTROL_ESCAPE) or c == chr(FLAG):
               self.encode_buffer = self.encode_buffer + chr(CONTROL_ESCAPE) + chr(ord(c) ^ 0x20)
           else:
               self.encode_buffer = self.encode_buffer + c

    def finish_encode_frame(self):
        self.crc_encode.add(self.encode_buffer)
        c = self.crc_encode.get() ^ 0xffff
        self.add_payload_to_encode_frame(chr(c % 256) + chr(c / 256))
        self.encode_buffer = chr(FLAG) + self.encode_buffer + chr(FLAG)
        return self.encode_buffer

    def decode(self, s):
        for c in s:
            if (c == chr(FLAG)):
                self.flag_count = self.flag_count + 1
            self.decode_buffer = self.decode_buffer + c

    def has_decode_frame(self):
        return self.flag_count >= 2

    def get_decode_frame(self):
        start = self.decode_buffer.index(chr(FLAG))
        end = self.decode_buffer[start+1:].index(chr(FLAG)) + 1 + start
        raw_frame = self.decode_buffer[start+1:end]
        self.decode_buffer = self.decode_buffer[end+1:]
        self.flag_count = self.flag_count - 2

        in_escape = False
        frame = raw_frame[0:2]
        for f in raw_frame[2:]:
            if in_escape:
                frame = frame + chr(ord(f) ^ 0x20)
                in_escape = False
            elif ord(f) == CONTROL_ESCAPE:
                in_escape = True
            else:
                frame = frame + f

        self.crc_decode.clear()
        self.crc_decode.add(frame[:-2])
        received_crc = (ord(frame[-1]) * 256 + ord(frame[-2])) ^ 0xffff

        if received_crc != self.crc_decode.get():
            frame_type = FrameType.ERROR
        control = ord(frame[1])
        if control & S_U_FRAME == S_U_FRAME:
            if control & FRAME_TYPE_MASK == FRAME_TYPE_ACK:
                frame_type = FrameType.ACK
            else:
                frame_type = FrameType.ERROR
        else:
            frame_type = FrameType.DATA
        return frame_type, frame[2:-2]
