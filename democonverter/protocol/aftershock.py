from enum import Enum, auto

from tabulate import tabulate

from democonverter.protocol.quake3 import Quake3


class Aftershock(Quake3):
    """
    OpenArena protocol 71. Aftershock-XE, revision 330v2.
    """

    class Stats(Enum):
        STAT_HEALTH = 0
        STAT_HOLDABLE_ITEM = auto()
        STAT_PERSISTANT_POWERUP = auto()
        STAT_WEAPONS = auto()
        STAT_ARMOR = auto()
        STAT_DEAD_YAW = auto()
        STAT_CLIENTS_READY = auto()
        STAT_MAX_HEALTH = auto()
        STAT_JUMPTIME = auto()
        STAT_RAILTIME = auto()
        STAT_ZOOMED = auto()
        STAT_RULESET = auto()
        STAT_PING = auto()

    class StatsPersistent(Enum):
        PERS_SCORE = 0
        PERS_HITS = auto()
        PERS_RANK = auto()
        PERS_TEAM = auto()
        PERS_SPAWN_COUNT = auto()
        PERS_PLAYEREVENTS = auto()
        PERS_ATTACKER = auto()
        PERS_ATTACKEE_ARMOR = auto()
        PERS_KILLED = auto()
        PERS_IMPRESSIVE_COUNT = auto()
        PERS_EXCELLENT_COUNT = auto()
        PERS_DEFEND_COUNT = auto()
        PERS_ASSIST_COUNT = auto()
        PERS_GAUNTLET_FRAG_COUNT = auto()
        PERS_CAPTURES = auto()
        PERS_DAMAGE_DONE = auto()

    class StatsWeapon(Enum):
        WP_NONE = 0
        WP_GAUNTLET = auto()
        WP_MACHINEGUN = auto()
        WP_SHOTGUN = auto()
        WP_GRENADE_LAUNCHER = auto()
        WP_ROCKET_LAUNCHER = auto()
        WP_LIGHTNING = auto()
        WP_RAILGUN = auto()
        WP_PLASMAGUN = auto()
        WP_BFG = auto()
        WP_GRAPPLING_HOOK = auto()
        WP_NAILGUN = auto()
        WP_PROX_LAUNCHER = auto()
        WP_CHAINGUN = auto()
        WP_NUM_WEAPONS = auto()

    class StatsPowerup(Enum):
        PW_NONE = 0
        PW_QUAD = auto()
        PW_BATTLESUIT = auto()
        PW_HASTE = auto()
        PW_INVIS = auto()
        PW_REGEN = auto()
        PW_FLIGHT = auto()
        PW_REDFLAG = auto()
        PW_BLUEFLAG = auto()
        PW_NEUTRALFLAG = auto()
        PW_SCOUT = auto()
        PW_GUARD = auto()
        PW_DOUBLER = auto()
        PW_AMMOREGEN = auto()
        PW_INVULNERABILITY = auto()
        PW_NUM_POWERUPS = auto()

    @staticmethod
    def _set_entity_types():
        entity_type = Quake3.entity_types.copy()
        entity_type.insert(13, 'ET_PING')
        entity_type.insert(14, 'ET_PING_DANGER')
        return entity_type

    entity_types = _set_entity_types()

    @staticmethod
    def _set_events():
        events = Quake3.events.copy()
        events.insert(42, 'EV_PROJECTILE_TELEPORT_IN')
        events.insert(43, 'EV_PROJECTILE_TELEPORT_OUT')
        events += ['EV_WEAPONDROP', 'EV_DAMAGEPLUM']
        return events

    events = _set_events()

    score_count = 42

    class ClientScore(Enum):
        NAME = 0
        SCORE = auto()
        ACCURACY = 6
        DAMAGE_DONE = 15
        DAMAGE_TAKEN = auto()

    score_duel_count = 47

    class ClientScoreDuel(Enum):
        NAME = 0
        SCORE = auto()
        ACCURACY = 6
        DAMAGE_DONE = 15
        DAMAGE_TAKEN = auto()
        YELLOW = 27
        RED = auto()
        MEGA = auto()

    @staticmethod
    def scores_table(clients):
        scoreboard = []
        for client, score in clients.items():
            if score[Aftershock.ClientScoreDuel.DAMAGE_DONE.value] != 0:
                scoreboard.append(
                    [
                        score[Aftershock.ClientScore.NAME.value],
                        score[Aftershock.ClientScore.SCORE.value],
                        score[Aftershock.ClientScore.DAMAGE_DONE.value],
                        score[Aftershock.ClientScore.DAMAGE_TAKEN.value],
                        score[Aftershock.ClientScore.ACCURACY.value],
                    ]
                )
        return tabulate(
            scoreboard, headers=['player', 'score', 'damage', 'taken', 'acc'], tablefmt='plain'
        )

    @staticmethod
    def scores_duel_table(clients):
        scoreboard = []
        for client, score in clients.items():
            if score[Aftershock.ClientScoreDuel.DAMAGE_DONE.value] != 0:
                scoreboard.append(
                    [
                        score[Aftershock.ClientScore.NAME.value],
                        score[Aftershock.ClientScoreDuel.SCORE.value],
                        score[Aftershock.ClientScoreDuel.DAMAGE_DONE.value],
                        score[Aftershock.ClientScoreDuel.ACCURACY.value],
                        score[Aftershock.ClientScoreDuel.MEGA.value],
                        score[Aftershock.ClientScoreDuel.RED.value],
                        score[Aftershock.ClientScoreDuel.YELLOW.value],
                    ]
                )
        return tabulate(
            scoreboard,
            headers=['player', 'score', 'damage', 'acc', 'mega', 'red', 'yel'],
            tablefmt='plain',
        )
