from enum import Enum, auto

from tabulate import tabulate

from democonverter.protocol.quake3 import Quake3


class QuakeLive(Quake3):
    """
    Quake Live protocol 91.
    """

    @staticmethod
    def _set_entity_types():
        entity_type = Quake3.entity_types.copy()
        entity_type.insert(13, 'ET_PING')
        entity_type.insert(14, 'ET_PING_DANGER')
        return entity_type

    entity_types = _set_entity_types()

    events = [
        'EV_NONE',
        'EV_FOOTSTEP',
        'EV_FOOTSTEP_METAL',
        'EV_FOOTSPLASH',
        'EV_FOOTWADE',
        'EV_SWIM',
        'EV_FALL_SHORT',
        'EV_FALL_MEDIUM',
        'EV_FALL_FAR',
        'EV_JUMP_PAD',
        'EV_JUMP',
        'EV_WATER_TOUCH',
        'EV_WATER_LEAVE',
        'EV_WATER_UNDER',
        'EV_WATER_CLEAR',
        'EV_ITEM_PICKUP',
        'EV_GLOBAL_ITEM_PICKUP',
        'EV_NOAMMO',
        'EV_CHANGE_WEAPON',
        'EV_DROP_WEAPON',
        'EV_FIRE_WEAPON',
        'EV_USE_ITEM0',
        'EV_USE_ITEM1',
        'EV_USE_ITEM2',
        'EV_USE_ITEM3',
        'EV_USE_ITEM4',
        'EV_USE_ITEM5',
        'EV_USE_ITEM6',
        'EV_USE_ITEM7',
        'EV_USE_ITEM8',
        'EV_USE_ITEM9',
        'EV_USE_ITEM10',
        'EV_USE_ITEM11',
        'EV_USE_ITEM12',
        'EV_USE_ITEM13',
        'EV_USE_ITEM14',
        'EV_USE_ITEM15',
        'EV_ITEM_RESPAWN',
        'EV_ITEM_POP',
        'EV_PLAYER_TELEPORT_IN',
        'EV_PLAYER_TELEPORT_OUT',
        'EV_GRENADE_BOUNCE',
        'EV_GENERAL_SOUND',
        'EV_GLOBAL_SOUND',
        'EV_GLOBAL_TEAM_SOUND',
        'EV_BULLET_HIT_FLESH',
        'EV_BULLET_HIT_WALL',
        'EV_MISSILE_HIT',
        'EV_MISSILE_MISS',
        'EV_MISSILE_MISS_METAL',
        'EV_RAILTRAIL',
        'EV_SHOTGUN',
        None,
        'EV_PAIN',
        'EV_DEATH1',
        'EV_DEATH2',
        'EV_DEATH3',
        'EV_DROWN',
        'EV_OBITUARY',
        'EV_POWERUP_QUAD',
        'EV_POWERUP_BATTLESUIT',
        'EV_POWERUP_REGEN',
        'EV_POWERUP_ARMOR_REGEN',
        'EV_GIB_PLAYER',
        'EV_SCOREPLUM',
        'EV_PROXIMITY_MINE_STICK',
        'EV_PROXIMITY_MINE_TRIGGER',
        'EV_KAMIKAZE',
        'EV_OBELISKEXPLODE',
        'EV_OBELISKPAIN',
        'EV_INVUL_IMPACT',
        None,
        'EV_DEBUG_LINE',
        'EV_STOPLOOPINGSOUND',
        'EV_TAUNT',
        'EV_TAUNT_YES',
        'EV_TAUNT_NO',
        'EV_TAUNT_FOLLOWME',
        'EV_TAUNT_GETFLAG',
        'EV_TAUNT_GUARDBASE',
        'EV_TAUNT_PATROL',
        'EV_FOOTSTEP_SNOW',
        'EV_FOOTSTEP_WOOD',
        'EV_ITEM_PICKUP_SPEC',
        'EV_OVERTIME',
        'EV_GAMEOVER',
        'EV_THAW_PLAYER',
        'EV_THAW_TICK',
        'EV_HEADSHOT',
        'EV_POI',
        None,
        None,
        'EV_RACE_START',
        'EV_RACE_CHECKPOINT',
        'EV_RACE_END',
        'EV_DAMAGEPLUM',
        'EV_AWARD',
        'EV_INFECTED',
        'EV_NEW_HIGH_SCORE',
        # TODO
        'EV_STEP_4',  # 196
        'EV_STEP_8',
        'EV_STEP_12',
        'EV_STEP_16',
        'EV_JUICED',
        'EV_LIGHTNINGBOLT',
    ]

    @staticmethod
    def _set_entity_states():
        entity_states = Quake3.entity_states.copy()
        entity_states.insert(9, Quake3.State('pos.gravity', 32))
        entity_states.insert(46, Quake3.State('apos.gravity', 32))
        entity_states += [
            Quake3.State('jumpTime', 32),
            Quake3.State('doubleJumped', 1),
            Quake3.State('health', 16),
            Quake3.State('armor', 16),
            Quake3.State('location', 8),
        ]
        return entity_states

    entity_states = _set_entity_states()

    @staticmethod
    def _set_player_states():
        player_states = Quake3.player_states.copy()
        player_states[19] = Quake3.State('pm_flags', 24)
        player_states.insert(42, Quake3.State('weaponPrimary', 8))
        player_states += [
            Quake3.State('jumpTime', 32),
            Quake3.State('doubleJumped', 1),
            Quake3.State('crouchTime', 32),
            Quake3.State('crouchSlideTime', 32),
            Quake3.State('location', 8),
            Quake3.State('fov', 8),
            Quake3.State('forwardmove', 8),
            Quake3.State('rightmove', 8),
            Quake3.State('upmove', 8),
        ]
        return player_states

    player_states = _set_player_states()

    class ClientScoreDuel(Enum):
        NAME = 0
        SCORE = auto()
        ACCURACY = 6
        DAMAGE = 8
        RED = 13
        YELLOW = 15
        GREEN = 17
        MEGA = 19

    score_duel_count = 91  # 20 + 5 * weapon_count(14)

    @staticmethod
    def scores_duel_table(clients):
        scoreboard = []
        for client, score in clients.items():
            if score:
                scoreboard.append(
                    [
                        score[QuakeLive.ClientScoreDuel.NAME.value],
                        score[QuakeLive.ClientScoreDuel.SCORE.value],
                        score[QuakeLive.ClientScoreDuel.DAMAGE.value],
                        score[QuakeLive.ClientScoreDuel.ACCURACY.value],
                        score[QuakeLive.ClientScoreDuel.MEGA.value],
                        score[QuakeLive.ClientScoreDuel.RED.value],
                        score[QuakeLive.ClientScoreDuel.YELLOW.value],
                        score[QuakeLive.ClientScoreDuel.GREEN.value],
                    ]
                )
        return tabulate(
            scoreboard,
            headers=['player', 'score', 'damage', 'acc', 'mega', 'red', 'yellow', 'green'],
            tablefmt='plain',
        )
