from typing import List, Optional, TypedDict


class Stat(TypedDict):
    unitStatId: int
    statValueDecimal: str
    unscaledDecimalValue: str
    uiDisplayOverrideValue: str
    scalar: str


class SecondaryStat(TypedDict):
    roll: List[str]
    unscaledRollValue: List[str]
    stat: Stat
    statRolls: int
    statRollerBoundsMin: str
    statRollerBoundsMax: str


class Currency(TypedDict):
    currency: int
    quantity: int
    bonusQuantity: int


class Mod(TypedDict):
    secondaryStat: List[SecondaryStat]
    id: str
    definitionId: str
    level: int
    tier: int
    sellValue: Currency
    removeCost: Currency
    locked: bool
    primaryStat: Stat
    xp: int
    levelCost: Currency
    bonusQuantity: int
    convertedItem: Optional[str]
    rerolledCount: int


class Skill(TypedDict):
    id: str
    tier: int


class Relic(TypedDict):
    currentTier: int


class RosterUnit(TypedDict):
    skill: List[Skill]
    equipment: List[str]
    equippedStatModOld: List[str]
    equippedStatMod: List[Mod]
    purchasedAbilityId: List[str]
    id: str
    definitionId: str
    currentRarity: int
    currentLevel: int
    currentXp: int
    promotionRecipeReference: str
    unitStat: Optional[str]
    currentTier: int
    relic: Relic
