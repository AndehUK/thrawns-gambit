from __future__ import annotations

# Core Imports
from typing import TYPE_CHECKING

# Third Party Packages
from discord.ext import commands

# Local Imports
from .logger import Logger

# Type Imports
if TYPE_CHECKING:
    from bot import ThrawnsGambit


class Cog(commands.Cog):
    """
    Subclass of :class:`Cog` that adds a unique Logger instance for
    creating logs in a specific :class:`Cog`
    """

    bot: ThrawnsGambit
    logger: Logger

    def __init__(self, bot: ThrawnsGambit) -> None:
        self.bot = bot
        self.logger = Logger(f"cogs/{self.__class__.__name__.lower()}")
