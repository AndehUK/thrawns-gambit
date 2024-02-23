from typing import TypedDict


class SeasonStatus(TypedDict):
    seasonId: str
    eventInstanceId: str
    league: str
    wins: int
    losses: int
    seasonPoints: int
    division: int
    joinTime: str
    endTime: str
    remove: bool
    rank: int
