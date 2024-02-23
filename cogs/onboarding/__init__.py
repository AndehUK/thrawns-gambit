from __future__ import annotations

# Core Imports
from typing import Optional, TYPE_CHECKING

# Third-Party Imports
import discord
from discord import app_commands

# Local Imports
from utils.cog import Cog
from utils.embed import Embed
from .views import OnboardingView

if TYPE_CHECKING:
    from bot import ThrawnsGambit


class Onboarding(Cog):
    """Onboarding Features"""

    @app_commands.command(name="onboarding", description="Send the onboarding menu")
    @app_commands.default_permissions(manage_messages=True)
    async def onboarding(
        self,
        itr: discord.Interaction[ThrawnsGambit],
        channel: Optional[discord.TextChannel] = None,
    ) -> None:
        if not channel:
            if not isinstance(itr.channel, discord.TextChannel):
                return await itr.response.send_message(
                    "This command can only be used in a text channel.", ephemeral=True
                )
            channel = itr.channel

        thrawn_image = discord.File("assets/thrawn.jpeg", filename="thrawn.jpeg")
        embed = Embed(
            title="Welcome to the Lazy Chiss Warriors Alliance!",
            description=(
                "Welcome to the Uncharted Territories just beyond the Outer Rim, where the Chiss rule supreme. The Chiss are great warriors. Clever, resourceful, proud, and intensely loyal to one another.\n\n"
                "The Lazy Chiss Warriors Alliance is a small alliance of independently run guilds. We help each other through knowledge sharing, recruiting, and sharing in general banter. Please let us know what questions you may have regarding this Alliance of guilds or the SWGOH game in general.\n\n"
                "> \"An enemy will almost never be anything except an enemy. All one can do with an enemy is defeat him, but an adversary can sometimes become an ally.\" - Mitth'raw'nuruodo"
            ),
            image="attachment://thrawn.jpeg",
            footer={"text": "Click one of the buttons to get started!"},
        )

        view = OnboardingView(timeout=None)

        try:
            msg = await channel.send(embed=embed, file=thrawn_image, view=view)
            await itr.response.send_message(
                f"Onboarding message sent to `#{channel.name}`. [Go to Message]({msg.jump_url})",
                ephemeral=True,
            )
        except Exception as e:
            return await itr.response.send_message(
                f"Failed to send onboarding message to `#{channel.name}` ({channel.mention}): ```{e}```",
                ephemeral=True,
            )


async def setup(bot: ThrawnsGambit) -> None:
    await bot.add_cog(Onboarding(bot))
