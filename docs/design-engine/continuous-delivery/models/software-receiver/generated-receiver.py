# Generated offline receiver; physical/manufacturing release remains false.
import struct
import zlib
class Receiver:
    CAPACITY = 4
    def __init__(self):
        self.state = 'BOOT'
        self.sequence = self.observed = self.receipt = None
        self.history = []
    def reset(self, stopped):
        if not (stopped is True):
            return False
        self.__init__()
        return True
    def receive(self, packet, receipt):
        if self.state == 'FAULT':
            return False
        valid = type(packet) is bytes and len(packet) == 11 and type(receipt) is int and 0 <= receipt <= 4294967295
        if valid:
            sequence, observed, flags = (int.from_bytes(packet[:2], 'little'), int.from_bytes(packet[2:6], 'little'), packet[6])
            valid = zlib.crc32(packet[:7]) == int.from_bytes(packet[7:], 'little')
            valid = valid and flags == 15 and 0 <= receipt-observed <= 100
            valid = valid and (self.sequence is None or (0 < ((sequence-self.sequence) % 65536) < 32768))
            valid = valid and (self.observed is None or observed >= self.observed)
            valid = valid and (self.receipt is None or receipt >= self.receipt)
        if not valid:
            self.state = 'FAULT'
            return False
        self.state = 'READY'
        self.sequence, self.observed, self.receipt = sequence, observed, receipt
        self.history.append(sequence)
        del self.history[:-self.CAPACITY]
        return True
