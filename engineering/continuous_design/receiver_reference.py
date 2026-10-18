"""Independent declarative receiver oracle and adverse event sequences.

This module does not import the generator or its parameters. The accepted
behaviour is fixed here; implementation alternatives cannot edit the oracle.
"""
import itertools
import zlib


def frame(sequence=1,observed=1000,flags=15):
    body=bytes([sequence&255,sequence>>8])+bytes([(observed>>(8*i))&255 for i in range(4)])+bytes([flags])
    checksum=zlib.crc32(body)
    return body+bytes([(checksum>>(8*i))&255 for i in range(4)])


class Oracle:
    def __init__(self):
        self.state="BOOT";self.sequence=self.observed=self.receipt=None
    def reset(self,stopped):
        if stopped is not True:return False
        self.state="BOOT";self.sequence=self.observed=self.receipt=None
        return True
    def receive(self,data,received):
        if self.state=="FAULT":return False
        decoded=None
        if type(data) is bytes and len(data)==11 and type(received) is int:
            seq=data[0]+256*data[1]
            observed=sum(data[2+i]*256**i for i in range(4))
            checksum=sum(data[7+i]*256**i for i in range(4))
            gap=(seq-self.sequence+65536)%65536 if self.sequence is not None else 1
            conditions=[0<=received<2**32,checksum==zlib.crc32(data[:7]),data[6]==15,
                observed<=received<=observed+100,1<=gap<=32767,
                self.observed is None or self.observed<=observed,self.receipt is None or self.receipt<=received]
            if all(conditions):decoded=(seq,observed,received)
        if decoded is None:self.state="FAULT";return False
        self.sequence,self.observed,self.receipt=decoded;self.state="READY";return True


def cases():
    for seq,observed,age,flags in itertools.product((0,1,32767,32768,65535),(0,1000,2**32-102),(-1,0,1,100,101),(0,15,16,255)):
        yield f"wire-{seq}-{observed}-{age}-{flags}",[("frame",frame(seq,observed,flags),observed+age)]
    alphabet=[("frame",frame(1,1000),1001),("frame",frame(2,1002),1003),
        ("frame",b"bad",1004),("reset",True),("reset",False),("frame",frame(3,1000),1101)]
    for index,events in enumerate(itertools.product(alphabet,repeat=4)):
        yield f"ordered-concurrency-interleaving-{index}",events
    for sequence in ((65534,65535,0,1),(0,32767,32768),(1,1),(1,32769),(2,1)):
        yield "wrap-"+str(sequence),[("frame",frame(seq,1000+i),1000+i) for i,seq in enumerate(sequence)]
    good=frame()
    for i in range(11):
        bad=bytearray(good);bad[i]^=1
        yield f"bit-corruption-{i}",[("frame",bytes(bad),1000),("reset",False),("frame",good,1000),("reset",True),("frame",good,1000)]
    for value in (None,"bad",bytearray(good),b"",good[:-1],good+b"x",bytes(10000)):
        yield "malformed",[("frame",value,1000)]
    for received in (None,True,float("nan"),float("inf"),-1,2**32):
        yield "invalid-receipt",[("frame",good,received)]
    yield "clock-regression",[("frame",frame(1,1000),1050),("frame",frame(2,1001),1049)]
    yield "observation-regression",[("frame",frame(1,1000),1000),("frame",frame(2,999),1001)]
    yield "bounded-retained-state",[("frame",frame(i,i),i) for i in range(500)]
