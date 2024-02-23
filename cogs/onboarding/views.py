from __future__ import annotations

# Core Imports
from typing import Optional, TYPE_CHECKING

# Third-Party Imports
import discord
from discord import ui

# Type Imports
if TYPE_CHECKING:
    from bot import ThrawnsGambit


class AllyCodeModal(ui.Modal, title="Submit Ally Code"):
    ally_code = discord.ui.TextInput[ui.View](
        label="Ally Code OR swgoh.gg link",
        placeholder="https://swgoh.gg/p/123456789/ or 123456789",
        min_length=9,
        max_length=29,
    )

    async def on_submit(self, itr: discord.Interaction[ThrawnsGambit]) -> None:
        ally_code: Optional[int] = None
        if itr.client.is_valid_ally_code(self.ally_code.value):
            ally_code = int(self.ally_code.value.replace("-", ""))
        elif itr.client.is_swgoh_gg_link(self.ally_code.value):
            ally_code = int(itr.client.get_ally_code_from_url(self.ally_code.value))

        if ally_code:
            gg_profile = None
            swgoh_link = itr.client.build_swgoh_gg_link(str(ally_code))

            async with itr.client.session.get(swgoh_link) as resp:
                gg_profile = swgoh_link if resp.status == 200 else "`No Profile Found`"

            await itr.response.send_message(
                f"- Ally Code: `{ally_code}`\n" f"- SWGOH.GG Profile: `{gg_profile}`",
                ephemeral=True,
            )
        else:
            await itr.response.send_message(
                f"Invalid response. Please enter a valid Ally Code or SWGOH.GG profile url.",
                ephemeral=True,
            )


class OnboardingView(ui.View):
    @ui.button(label="Submit Ally Code", style=discord.ButtonStyle.blurple, emoji="🔑")
    async def submit_ally_code(
        self, itr: discord.Interaction[ThrawnsGambit], button: ui.Button[ui.View]
    ) -> None:
        await itr.response.send_modal(AllyCodeModal())

    @ui.button(label="Contact Senate", style=discord.ButtonStyle.gray, emoji="📤")
    async def contact_council(
        self, itr: discord.Interaction[ThrawnsGambit], button: ui.Button[ui.View]
    ) -> None:
        await itr.response.send_message(
            "This also does nothing yet. 😆", ephemeral=True
        )
