from struct import pack, unpack

from bitarray import bitarray, util

from democonverter.huffman import Huffman


class Message:
    """
    Server message.
    Demo is split in blocks which are server to client messages (also used in normal game).
    Frequency: 1 message/24.5ms or 40 messages/s (10 minutes demo => 24.5k messages)

    By default, each message is Huffman encoded, except numbers with non-byte size,
    where the offset is not encoded.
    """

    _FLOAT_BITS = 13
    _huffman = Huffman()

    def __init__(self, data):
        self.player_state_delta = {}  # one player state
        self.entity_state_deltas = []  # multiple packet entities
        self.index = 0

        if isinstance(data, bitarray):
            self._data = bitarray(data, endian='little')
        else:
            self._data = bitarray(endian='little')
            self._data.frombytes(data)

    def get_message_bytes(self):
        return self._data.tobytes()

    def get_size_bits(self):
        return len(self._data)

    def get_size(self):
        return int(self.get_size_bits() / 8)

    def fill(self):
        self._data.fill()

    def read_bits(self, count, offset=None, signed=False):
        """
        Reads bits from demo message. A byte value is encoded. Values that are not of byte length
        are calculated differently, where the bit offset is not encoded but appended to encoded
        byte.
        """
        if offset is None:
            offset = self.index

        value = 0
        # if self._data[offset:] == bitarray():
        #     return value

        if bit_offset := count % 8:
            value_bytes = self._data[offset : offset + bit_offset]
            value = util.ba2int(value_bytes)
            offset += bit_offset
        for i in range(int(count / 8)):
            decoded_value, size = self._huffman.decode(self._data[offset:])
            value += decoded_value * pow(2, (8 * i) + bit_offset)
            offset += size
        self.index = offset

        if signed:
            value = util.ba2int(util.int2ba(value, count), True)
        return value

    def write_bits(self, value, count, offset=None):
        if isinstance(value, int):
            value = util.int2ba(value)
        value.reverse()

        # calculate code
        code = bitarray()
        if bit_offset := count % 8:
            code += value[:bit_offset]
        for index in range(int(count / 8)):
            bit_start = 8 * index + bit_offset
            symbol = value[bit_start : bit_start + 8]
            symbol.reverse()
            code += self._huffman.encode(symbol if symbol != bitarray() else 0)

        # write to msg
        if offset is None:
            offset = self.index
        old_size = self.index - offset
        self._data[offset : offset + old_size] = code
        self.index = offset + len(code)

    def read_boolean(self):
        return self.read_bits(1)

    def read_byte(self):
        return self.read_bits(8)

    def read_short(self):
        return self.read_bits(16)

    def read_long(self):
        return self.read_bits(32)

    def read_float(self):
        if self.read_boolean():
            value_bytes = pack('>L', self.read_long())  # convert to bytes
            return unpack('>f', value_bytes)[0]  # convert to float
        else:  # integral
            return self.read_bits(self._FLOAT_BITS) - pow(2, self._FLOAT_BITS - 1)

    def read_string(self, max_chars=1024):
        string_array = []
        while True:
            value = self.read_byte()
            if value == ord('%') or 127 < value < max_chars - 1:
                string_array.append('.')
            elif 0 < value <= 127:
                string_array.append(chr(value))
            else:
                break
        return ''.join(string_array)
