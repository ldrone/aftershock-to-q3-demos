import os.path
import pathlib
from enum import Enum, auto

from democonverter.message import Message
from democonverter.parser import Parser


class Demo:
    MSG_SIZE_MAX = 16_384

    def __init__(self, filename):
        self._filename = filename
        demo_path = pathlib.Path(self._filename)
        if not demo_path.exists():
            raise FileNotFoundError('Demo not found')
        if demo_path.suffix not in ('.dm_68', '.dm_71', '.dm_91'):
            raise ValueError('Not a valid demo file')

        self._size = os.path.getsize(filename)
        self.protocol = None
        self.mod = None
        self.date = None
        self.host_name = None
        self.map = None
        self.game_type = None
        self.clients = {}
        self.game_protocol = None  # protocol+mod

    def read(self, convert, output):
        with open(self._filename, 'rb') as demo_file:
            if convert:
                demo_path = pathlib.Path(self._filename)
                output_dir = pathlib.Path(output if output else 'out/')
                if not output_dir.exists():
                    os.makedirs(str(output_dir.resolve()), exist_ok=True)
                converted_filename = str(output_dir.resolve()) + '/' + demo_path.name

                with open(converted_filename, 'wb') as converted_demo_file:
                    self._read_messages(demo_file, converted_demo_file)
                print('Converted demo {} '.format(self._filename))
                return converted_filename
            else:
                print('Demo: {} '.format(self._filename))
                self._read_messages(demo_file)
                print(self)

    def _read_messages(self, demo_file, converted_demo_file=None):
        parser = Parser(self, True if converted_demo_file else None)

        last_scores = None
        while True:
            msg_seq = int.from_bytes(demo_file.read(4), 'little', signed=True)
            msg_size = int.from_bytes(demo_file.read(4), 'little', signed=True)

            if msg_size < 1:  # reached end of demo
                break
            if msg_size > self.MSG_SIZE_MAX:
                print(
                    'WARNING: Message size ({}) exceeds max size ({}).'.format(
                        msg_size, self.MSG_SIZE_MAX
                    )
                )
            msg = Message(demo_file.read(msg_size))
            scores = parser.parse_message(msg)
            if scores:
                last_scores = scores

            if converted_demo_file:
                converted_demo_file.write(msg_seq.to_bytes(4, 'little', signed=True))
                converted_demo_file.write(msg.get_size().to_bytes(4, 'little', signed=True))
                converted_demo_file.write(msg.get_message_bytes())

        if last_scores:
            parser.parse_scores(last_scores)

    def __str__(self):
        separator = '-' * 80 + '\n'
        info = separator
        info += 'Size: {} MiB\n'.format(round(self._size / pow(1024, 2), 2))
        if self.protocol:
            info += 'Protocol: {}'.format(self.protocol)
        if self.mod:
            info += ' ({})'.format(self.mod)
        info += '\n'
        if self.date:
            # TODO: mismatch of timezone in AS and QL
            info += 'Date: {}\n'.format(self.date)
        if self.host_name:
            info += 'Server: {}\n'.format(self.host_name)
        if isinstance(self.game_type, self.GameType):
            info += 'Game type: {}\n'.format(self.game_type.name.lower())
        if self.map:
            info += 'Map: {}\n'.format(self.map)
        info += separator
        if self.clients:
            info = self._client_scores(info)
            info += separator
        info += '\n'
        return info

    class GameType(Enum):
        FFA = 0
        Duel = auto()
        TDM = 3
        CTF = auto()

    def _client_scores(self, info):
        self.clients = {
            client: stats
            for client, stats in self.clients.items()
            if len(stats) > 1 and stats[0] != '.'
        }
        sorted_clients = {
            k: v
            for k, v in sorted(
                self.clients.items(), key=lambda c: c[1][1] if c[1] else 0, reverse=True
            )
        }

        if self.game_type == self.GameType.Duel:
            info += self.game_protocol.scores_duel_table(sorted_clients)
        else:
            info += self.game_protocol.scores_table(sorted_clients)
        info += '\n'
        return info
