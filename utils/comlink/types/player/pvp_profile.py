from typing import List, Optional, TypedDict


class CrewBattleStat(TypedDict):
    # Assuming the structure based on the provided snippet; adjust as necessary.
    pass


class Affix(TypedDict):
    tag: List[str]
    targetRule: str
    abilityId: str
    statType: int
    statValue: str
    requiredUnitTier: int
    requiredRelicTier: int
    scopeIcon: str


class Datacron(TypedDict):
    tag: List[str]
    affix: List[Affix]
    id: str
    setId: int
    templateId: str


class Cell(TypedDict):
    crewBattleStat: List[CrewBattleStat]
    unitId: str
    unitDefId: str
    cellIndex: int
    unitBattleStat: Optional[
        str
    ]  # Assuming None indicates optional; adjust type if needed.
    messageReticle: str
    progressItem: bool
    squadUnitType: int
    unitState: Optional[str]  # Adjust type if needed.
    selectable: bool
    overkillItem: bool
    inheritFromDefinitionId: str


class Squad(TypedDict):
    cell: List[Cell]
    targetingTactic: int
    squadType: int
    targetingSetId: str
    expireTime: str
    lastSaveTime: str
    supportInheritFromDefinitionId: str
    datacron: Optional[Datacron]


class PvpProfile(TypedDict):
    tab: int
    rank: int
    squad: Squad
    eventId: str
