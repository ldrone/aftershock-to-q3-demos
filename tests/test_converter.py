import pytest
from converter import Converter
from protocol.aftershock import Aftershock
from protocol.quake3 import Quake3


@pytest.fixture
def converter():
    return Converter(Aftershock, Quake3)


def test_events_map(converter):
    print(Converter._convert_events_map)


def test_entity_type_event_converter(converter):
    # assert converter.convert_entity_type_event(38) == 36  # use item on LG fire
    assert converter.convert_entity_type_event(66) == 62  # rail trail on MG
    assert converter.convert_entity_type_event(67) == 63  # remove haste on LG hit
    assert converter.convert_entity_type_event(70) == 66  # missing RG trail

    assert converter.convert_bit_flag_event(309) == 307  # rail trail on rocket miss


# statsConvert = {
#     3: 2,  # fix missing weapon bar ammo
#     4: 3,  # fix armor value
#     6: 5,  # fix clients ready
#     7: 6   # fix max health?
# }
