import re
from datetime import datetime
from enum import Enum

from bitarray import util

from democonverter.converter import Converter
from democonverter.protocol.aftershock import Aftershock
from democonverter.protocol.quake3 import Quake3
from democonverter.protocol.quakelive import QuakeLive


def sanitize_string(value):
    return re.sub(r'\^.', '', value).strip()


class Parser:
    """
    Parse demo message depending on type.
    - Game state message appears at the start of the demo and contains things like server
      and client info.
    - Snapshot has player state (e.g. view angle, HP, etc.) and other entities states
      (e.g. weapon hit event). Tracks only differences from last snapshot (delta).
    - Server command is a string that tracks each players score, shows chat messages,
      shows when the match ends, etc.

    Since messages are encoded, and some non-byte length numbers are not, we read the message data
    sequentially and cannot fast-forward.
    """

    _BIG_INFO_STRING = 8192
    _CONFIG_STRING_SEQUENCE_MAX = 1024
    _ENTITY_NUM_BITS = 10
    _converter = Converter(Aftershock, Quake3)  # only implemented conversion

    def __init__(self, demo, convert=False):
        self._demo = demo
        self._convert = convert
        self._abort = False
        self._msg = None

    def parse_message(self, msg):
        """
        client/cl_parse.c CL_ParseServerMessage
        """
        self._msg = msg
        self._msg.read_long()  # reliable_ack

        score = None
        while self._msg.index < self._msg.get_size_bits():
            server_cmd = self._msg.read_byte()
            if server_cmd == self._ServerCommand.EOF.value:
                # if self._demo.protocol == QuakeLive:
                #     if self._msg.read_byte() == self._ServerCommand.SVC_EXTENSION.value:
                #         pass
                break
            if server_cmd == self._ServerCommand.GAME_STATE.value:
                self._parse_game_state()
            elif server_cmd == self._ServerCommand.SNAPSHOT.value:
                self._parse_snapshot()
            elif server_cmd == self._ServerCommand.CMD_STRING.value:

                self._msg.read_long()  # command sequence
                cmd = self._msg.read_string()  # command string
                if cmd.startswith('cs'):
                    self._set_clients(cmd)
                elif cmd.startswith('scores'):
                    score = cmd
            else:
                print('Got unexpected server command:', server_cmd)
                break

        # fill bits to byte size
        if self._convert:
            self._msg.fill()

        return score

    def parse_scores(self, scores):
        """
        cgame/cg_servercmds.c CG_ParseScores

        Not implemented: QL non-duel scores.
        """
        scores = [eval(score) for score in scores.split()[1:]]

        if self._demo.game_type == self._demo.GameType.Duel:
            data_count = self._demo.game_protocol.score_duel_count
        else:
            data_count = self._demo.game_protocol.score_count

        if self._demo.game_protocol == Aftershock:
            # int(scores[1]) >> 8 & 0xFF
            scores = scores[4:]
        elif self._demo.game_protocol == QuakeLive:
            scores = scores[1:]

        for i in range(0, len(scores), data_count):
            client_id = scores[i]
            offset = i + 1
            if client_id in self._demo.clients:
                self._demo.clients[client_id] += scores[offset : offset + data_count]

    def _parse_game_state(self):
        """
        client/cl_parse.c CL_ParseGamestate
        """
        self._msg.read_long()  # server cmd sequence

        while True:
            server_cmd = self._msg.read_byte()
            if server_cmd == self._ServerCommand.EOF.value:
                break
            elif server_cmd == self._ServerCommand.CONFIG_STRING.value:
                config_string_sequence = int(self._msg.read_short())
                if not 0 <= config_string_sequence < self._CONFIG_STRING_SEQUENCE_MAX:
                    print('ERROR: Config string out of range', config_string_sequence)
                config_string = self._msg.read_string(self._BIG_INFO_STRING - 1)
                if config_string.startswith('\\'):
                    server_info = dict(zip(*[iter(config_string.split('\\')[1:])] * 2))
                    if game_type := server_info.get('g_gametype'):
                        self._demo.game_type = self._demo.GameType(int(game_type))
                    if map_name := server_info.get('mapname'):
                        self._demo.map = map_name
                    if host_name := server_info.get('sv_hostname'):
                        self._demo.host_name = sanitize_string(host_name)
                    if game_date := server_info.get('g_timestamp'):
                        self._demo.date = game_date
                    if game_protocol := server_info.get('protocol'):
                        self._demo.protocol = int(game_protocol)
                    if game_protocol := server_info.get('com_protocol'):
                        self._demo.protocol = int(game_protocol)
                    if game_mod := server_info.get('fs_game'):
                        self._demo.mod = game_mod
                    if game_date := server_info.get('g_levelStartTime'):  # QL91 date
                        self._demo.date = datetime.fromtimestamp(int(game_date))
                    self._set_from_protocol()
                elif config_string.startswith('n\\'):
                    client_info = dict(zip(*[iter(config_string.split('\\'))] * 2))
                    if client_name := client_info.get('n'):
                        self._demo.clients[len(self._demo.clients)] = [
                            sanitize_string(client_name)
                        ]
            elif server_cmd == self._ServerCommand.BASE_LINE.value:
                self._read_delta_entity()
        self._msg.read_long()  # client num
        self._msg.read_long()  # checksum feed

    def _parse_snapshot(self):
        """
        client/cl_parse.c: CL_ParseSnapshot
        """
        self._msg.read_long()  # command time
        self._msg.read_byte()  # delta number
        self._msg.read_byte()  # snap flags
        area_bytes = self._msg.read_byte()
        self._msg.read_byte()  # area mask
        for i in range(area_bytes - 1):
            self._msg.read_byte()

        self._parse_player_state()
        self._parse_stats()

        # client/cl_parse.c: CL_ParsePacketEntities
        while True:
            if self._read_delta_entity():
                break

    def _parse_player_state(self):
        """
        qcommon/msg.c: MSG_ReadDeltaPlayerstate
        """
        field_count = self._msg.read_byte()
        player_states = self._demo.game_protocol.player_states
        if field_count > len(player_states):
            raise ValueError(
                'Invalid player state field count {} > {}'.format(field_count, len(player_states))
            )
        self._msg.player_state_delta = self._read_delta(player_states, field_count)

    def _parse_stats(self):
        """
        qcommon/msg.c MSG_ReadDeltaPlayerstate
        """
        if self._msg.read_boolean():  # read stats
            for stat in ['STAT', 'PERS', 'AMMO', 'POWERUPS']:
                if self._msg.read_boolean():  # read stats group
                    # print(stat, end=': ')
                    offset = self._msg.index
                    bit_flags = util.int2ba(self._msg.read_short())
                    bit_flags.reverse()
                    if self._convert and stat == 'STAT':
                        new_bit_flags = self._converter.convert_stats(bit_flags)
                        self._msg.write_bits(util.ba2int(new_bit_flags), 16, offset)
                    for i, flag_set in enumerate(bit_flags):
                        if flag_set:
                            if stat == 'POWERUPS':
                                value = self._msg.read_bits(count=32, signed=True)
                                # print(self._demo.game_protocol.StatsPowerup(i).name, ':', value, end=' ')
                            else:
                                value = self._msg.read_bits(count=16, signed=True)
                    #             if stat == 'STAT':
                    #                 print(self._demo.game_protocol.Stats(i).name, ':', value, end=' ')
                    #             if stat == 'PERS':
                    #                 print(self._demo.game_protocol.StatsPersistent(i).name, ':', value, end=' ')
                    #             elif stat == 'AMMO':
                    #                 print(self._demo.game_protocol.StatsWeapon(i).name, ':', value, end=' ')
                    # print()

    def _read_delta_entity(self):
        """
        code/qcommon/msg.c: MSG_ReadDeltaEntity
        """
        delta_entity_number = self._msg.read_bits(self._ENTITY_NUM_BITS)
        if not 0 <= delta_entity_number < pow(2, self._ENTITY_NUM_BITS) - 1:
            return True
        if self._msg.read_boolean():  # remove
            return False
        if not self._msg.read_boolean():  # no delta
            return False

        field_count = self._msg.read_byte()
        entity_states = self._demo.game_protocol.entity_states
        if field_count > len(entity_states):
            raise ValueError(
                'Invalid entity state field count {} > {}'.format(field_count, len(entity_states))
            )

        delta = self._read_delta(entity_states, field_count, True)
        self._msg.entity_state_deltas.append(delta)

    def _read_delta(self, states, field_count, check_null=False):
        delta = {}
        for i in range(field_count):
            if self._msg.read_boolean():  # entity changed
                entity_state = states[i]
                if check_null and not self._msg.read_boolean():
                    value = 0
                elif entity_state.bit_size:  # int
                    offset = self._msg.index
                    value = self._msg.read_bits(
                        abs(entity_state.bit_size),
                        signed=True if entity_state.bit_size < 0 else False,
                    )
                    if self._convert:
                        self._convert_events(
                            entity_state.name, entity_state.bit_size, value, offset
                        )
                else:
                    value = self._msg.read_float()
                delta[entity_state.name] = value
        return delta

    def _convert_events(self, field_name, field_size, value, write_offset):
        """
        For both player and packet events.
        Packet entity changes: eType, event
        Player entity changes: events[0], events[1], externalEvent
        NOTE: fixes are hardcoded and only make sense for AS=>Q3 conversion
        """
        if field_name == 'modelindex' and value == 61:
            # fix bad item index 61 on entity
            self._msg.write_bits(0, field_size, write_offset)

        if field_name == 'eType' and value == 101:
            # fix event 88 EV_THAW_THICK
            self._msg.write_bits(0, field_size, write_offset)

        # 1:23 2:44

        if field_name == 'eType' and value == 16:
            # fix event: 14 => 10
            self._msg.write_bits(14, field_size, write_offset)

        if field_name == 'eType' and value == 29:
            # fix event: 14 => 10
            self._msg.write_bits(27, field_size, write_offset)

        if field_name == 'eType' and value == 37:
            # fix event: 24 => 22
            self._msg.write_bits(35, field_size, write_offset)

        if field_name == 'eType' and value == 38:
            # fix event: 25 => 23
            self._msg.write_bits(36, field_size, write_offset)

        if field_name in ('eType', 'events[0]', 'events[1]'):
            if converted_value := self._converter.convert_entity_type_event(value):
                self._msg.write_bits(converted_value, field_size, write_offset)
        if field_name in ('event', 'externalEvent'):
            if converted_value := self._converter.convert_bit_flag_event(value):
                self._msg.write_bits(converted_value, field_size, write_offset)

    def _set_from_protocol(self):
        """
        After reading server info we should know what protocol+mod the demo is.
        """
        if self._demo.protocol == 91:
            self._demo.game_protocol = QuakeLive
        elif not self._demo.mod:
            return
        elif self._demo.protocol == 71 and self._demo.mod == 'aftershock':
            self._demo.game_protocol = Aftershock
        else:
            raise ValueError('Unknown demo protocol', self._demo.protocol, self._demo.mod)

    def _set_clients(self, cmd):
        first_client_id = 544  # Quake 3 / Aftershock
        if self._demo.game_protocol == QuakeLive:
            first_client_id = 529
        cmd = cmd.split()
        if len(cmd) == 3 and first_client_id <= int(cmd[1]) < first_client_id + 64:
            client_id = int(cmd[1]) - first_client_id
            cmd[2] = cmd[2].lstrip('"').rstrip('"')
            if len(cmd[2]) > 0:
                client_info = dict(zip(*[iter(cmd[2].split('\\'))] * 2))
                client_name = client_info.get('n')
                self._demo.clients[client_id] = [sanitize_string(client_name)]

    class _ServerCommand(Enum):
        """
        Message type.
        """

        GAME_STATE = 2
        CONFIG_STRING = 3
        BASE_LINE = 4
        CMD_STRING = 5
        SNAPSHOT = 7
        EOF = 8
        SVC_EXTENSION = 9
