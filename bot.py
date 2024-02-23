from __future__ import annotations

# Core Imports
import re
import traceback

# Third Party Imports
import aiohttp
import discord
from discord.ext import commands

# Local Imports
from cogs import COGS
from utils.comlink import SwgohComlink
from utils.env import Env
from utils.logger import Logger
from utils.regex import RegEx
from utils.tree import Tree


class ThrawnsGambit(commands.Bot):
    """The main Discord Bot class"""

    _is_ready: bool
    comlink: SwgohComlink
    config: Env
    logger: Logger
    regex: RegEx
    session: aiohttp.ClientSession
    user: discord.ClientUser

    def __init__(self) -> None:
        self._is_ready = False
        self.logger = Logger("bot", console=True)
        self.config = Env()
        self.comlink = SwgohComlink(self)
        self.logger.info(
            f"Loaded {len(self.config.__annotations__)} environment variables."
        )
        self.regex = RegEx()

        super().__init__(
            command_prefix="t!",
            description="Discord Bot for the Lazy Chiss Warriors Alliance.",
            intents=discord.Intents.all(),
            tree_cls=Tree,
        )

        # Setting this decides who can use owner-only commands such as jsk
        self.owner_ids = {957437570546012240}  # Andrew

    async def setup_hook(self) -> None:
        """
        A coroutine to be called to setup the bot after logging in
        but before we connect to the Discord Websocket.

        Mainly used to load our cogs / extensions.
        """
        # Jishaku is our debugging tool installed from PyPi
        await self.load_extension("jishaku")
        loaded_cogs = 1

        # Looping through and loading our local extensions (cogs)
        for cog in COGS:
            try:
                await self.load_extension(cog)
                loaded_cogs += 1
            except Exception as e:
                tb = traceback.format_exc()
                self.logger.error(f"{type(e)} Exception in loading {cog}\n{tb}")
                continue

        self.logger.info(f"Successfully loaded {loaded_cogs}/{len(COGS)+1} cogs!")

    async def on_ready(self) -> None:
        """
        A coroutine to be called every time the bot connects to the
        Discord Websocket.

        This can be called multiple times if the bot disconnects and
        reconnects, hence why we create the `_is_ready` class variable
        to prevent functionality that should only take place on our first
        start-up from happening again.
        """
        if self._is_ready:
            # We've already connected to the websocket, so we don't need to
            # do anything in this event.
            return self.logger.critical("Bot reconnected to discord gateway")

        # We're ready to start!
        self._is_ready = True
        self.logger.info(f"{self.user} is now online!")

        await self.comlink.create_localised_unit_name_dictionary()

    async def start(self) -> None:
        """
        Logs in the client with the specified credentials and calls the :meth:`setup_hook` method
        then creates a websocket connection and lets the websocket listen to messages / events
        from Discord.
        """
        self.logger.info("Starting bot...")
        async with aiohttp.ClientSession() as self.session:
            # Initialises our ClientSession as a bot variable
            try:
                await super().start(self.config.BOT_TOKEN)
            finally:
                self.logger.info("Shutdown Bot")

    def is_valid_ally_code(self, ally_code: str) -> bool:
        if re.match(self.regex.ally_code_regex, ally_code):
            return True
        return False

    def is_swgoh_gg_link(self, url: str) -> bool:
        if re.match(self.regex.swgoh_gg_regex, url):
            return True
        return False

    def build_swgoh_gg_link(self, ally_code: str) -> str:
        return f"https://swgoh.gg/p/{ally_code}/"

    def get_ally_code_from_url(self, url: str) -> str:
        match = re.search(r"/p/(\d{9})/?", url)
        if match:
            return match.group(1)
        else:
            raise ValueError("The provided URL does not contain a valid ally code.")
