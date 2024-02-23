from typing import List, TypedDict

from .datacron import Datacron
from .profile_stat import ProfileStat
from .pvp_profile import PvpProfile
from .roster_unit import RosterUnit
from .season_status import SeasonStatus
from .unlocked_player_property import UnlockedPlayerProperty


class PlayerSkillRating(TypedDict):
    skillRating: int


class PlayerRankStatus(TypedDict):
    leagueId: str
    divisionId: int


class PlayerRating(TypedDict):
    playerSkillRating: PlayerSkillRating
    playerRankStatus: PlayerRankStatus


class Player(TypedDict):
    rosterUnit: List[RosterUnit]
    profileStat: List[ProfileStat]
    pvpProfile: List[PvpProfile]
    unlockedPlayerTitle: List[UnlockedPlayerProperty]
    unlockedPlayerPortrait: List[UnlockedPlayerProperty]
    seasonStatus: List[SeasonStatus]
    datacron: List[Datacron]
    name: str
    level: int
    allyCode: str
    playerId: str
    guildId: str
    guildName: str
    guildLogoBackground: str
    guildBannerColor: str
    guildBannerLogo: str
    selectedPlayerTitle: UnlockedPlayerProperty
    guildTypeId: str
    localTimeZoneOffsetMinutes: int
    lastActivityTime: str
    selectedPlayerPortrait: UnlockedPlayerProperty
    lifetimeSeasonScore: str
    playerRating: PlayerRating
