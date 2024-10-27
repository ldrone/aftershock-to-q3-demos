class Converter:
    _convert_events_map = {}

    def __init__(self, from_protocol, to_protocol):
        self.from_protocol = from_protocol
        self.to_protocol = to_protocol

        self.set_convert_events_map()
        # self._convert_events_map[22] = 0  # fix: remove use item when enemy hits
        # self._convert_events_map[88] = 0  # fix: event 88 EV_THAW_THICK

    def set_convert_events_map(self):
        for from_index, event in enumerate(self.from_protocol.events):
            try:
                to_index = self.to_protocol.events.index(event)
            except ValueError:
                continue
            if from_index != to_index:
                self._convert_events_map[from_index] = to_index

    def convert_entity_type_event(self, in_entity_type_event):
        event_from = in_entity_type_event - self.from_protocol.entity_types.index('ET_EVENTS')
        if event_from in self._convert_events_map:
            return self._convert_events_map[event_from] + self.to_protocol.entity_types.index(
                'ET_EVENTS'
            )

    def convert_bit_flag_event(self, event):
        bit_flags = event >> 8
        event_from = event & 0xFF
        if event_from in self._convert_events_map:
            return self._convert_events_map[event_from] + bit_flags * 256

    def convert_stats(self, bit_flags):
        bit_flags.fill()
        if len(bit_flags) < 16:
            bit_flags.append(0)
            bit_flags.fill()
        new_bit_flags = bit_flags.copy()
        # TODO: remove unused stats
        new_bit_flags[2] = bit_flags[3]
        new_bit_flags[3] = bit_flags[4]
        new_bit_flags[4] = bit_flags[2]  # 0 (if 2 is 1 remove the stat completely)
        new_bit_flags[5] = bit_flags[6]
        new_bit_flags[6] = bit_flags[7]
        new_bit_flags[7] = bit_flags[5]  # 0 (if 2 is 1 remove the stat completely)
        new_bit_flags.reverse()
        return new_bit_flags
