from bitarray import bitarray
from message import Message


def test_message_read_bits():
    msg = Message(bitarray('1001 1100 1011 01'))
    assert msg.read_bits(8) == 14 and msg.read_bits(8) == 13
    assert msg.read_bits(16, 0) == 14 + 13 * 256

    msg = Message(bitarray('1001 1100 0111'))
    assert msg.read_bits(8) == 14

    msg = Message(bitarray('11 0010 0111'))
    assert msg.read_bits(10) == 3 + 255 * 4

    msg = Message(bitarray('01 11011'))
    assert msg.read_bits(10) == 2 + 1 * 4


def test_message_write_bits():
    msg = Message(bitarray())
    msg.write_bits(1023, 10)
    assert msg._data == bitarray('1100 1001') and msg.index == 8

    msg = Message(bitarray('011101110001'))
    msg.write_bits(1023, 10)
    assert msg._data == bitarray('1100 1001 011101110001') and msg.index == 8

    msg.write_bits(6, 10)
    assert msg._data == bitarray('01 1101 1 1100 1001 011101110001') and msg.index == 7

    msg = Message(bitarray('0000 0000 0000 0000 0000 0000'))
    msg.write_bits(1023, 10, 10)
    assert msg.index == 18

    # 1000000 => (0000 1111) (0100 0010) (0100 0000)
    # 1000000 = 15 * 256^2 + 66 * 256 + 64
    # 15 => 001101010, 66 => 0011111, 64 => 11110011
    # reverse -> 11110011 0011111 001101010
    msg.index = 0
    msg.write_bits(1000000, 32)
    assert msg._data == bitarray('1111 0011 0011 1110 0110 1010 01')
    assert msg.index == 26


def test_message_read(msg):
    msg = Message(bitarray('0011 1101 1000 0011 1001 1001 1010 1111'))
    assert msg.read_long() == 7_292_859

    msg.index = 0
    msg = Message(bitarray('101'))
    assert msg.read_boolean() == 1
    assert msg.read_boolean() == 0

    msg.index = 0
    msg = Message(bitarray('1101 0100 01'))
    assert msg.read_byte() == 22

    msg.index = 0
    msg = Message(bitarray('1100 0010 0101 0100'))
    assert msg.read_short() == 29

    msg.index = 0
    msg = Message(bitarray('0011 0101 0010 1010 0010 0111 0000 1001'))
    assert msg.read_long() == 15

    msg.index = 0
    msg = Message(bitarray('1011 0001 01 0000 1110 0 1100110101010'))
    assert msg.read_long() == 0 * pow(256, 3) + 111 * pow(256, 2) + 71 * 256 + 253

    msg.index = 0
    msg = Message(bitarray('1111 0011'))
    assert msg.read_short() == 64

    msg.index = 0
    msg = Message(bitarray('1111 0011 0011 1110 0110 1010'))
    assert msg.read_long() == 1_000_000

    msg.index = 0
    msg = Message(bitarray('1111 0011 0011 1110 0110 1010 01'))
    assert msg.read_long() == 1_000_000
