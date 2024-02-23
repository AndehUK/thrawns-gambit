from typing import List, Optional, TypedDict


class Tag(TypedDict):
    # Assuming no further details provided for tags; adjust as necessary
    pass


class Affix(TypedDict):
    tag: List[Tag]
    targetRule: str
    abilityId: str
    statType: int
    statValue: str
    requiredUnitTier: int
    requiredRelicTier: int
    scopeIcon: str


class Datacron(TypedDict):
    tag: List[Tag]
    affix: List[Affix]
    rerollOption: List[Optional[str]]  # Assuming optional, adjust as necessary
    id: str
    setId: int
    templateId: str
    locked: bool
    rerollIndex: int
    rerollCount: int
