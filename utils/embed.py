from __future__ import annotations

# Core Imports
import datetime
from typing import List, Optional, TypedDict, Union

# Third Party Packages
import discord

# Local Imports
from utils.colour import Colours


class EmbedAuthor(TypedDict, total=False):
    icon_url: str
    name: str


class EmbedFooter(TypedDict, total=False):
    icon_url: str
    text: str


class EmbedField(TypedDict):
    name: str
    value: str
    inline: bool


class Embed(discord.Embed):
    """Subclass of :class:`discord.Embed` that provides some additional functionality"""

    _id: Optional[int] = None

    def __init__(
        self,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        colour: Optional[Union[discord.Colour, int]] = Colours.light_blue,
        timestamp: Optional[datetime.datetime] = None,
        author: Optional[EmbedAuthor] = None,
        footer: Optional[EmbedFooter] = None,
        thumbnail: Optional[str] = None,
        image: Optional[str] = None,
        fields: List[EmbedField] = [],
        url: Optional[str] = None,
        _id: Optional[int] = None,
    ) -> None:
        self._id = _id
        super().__init__(
            colour=colour,
            title=title,
            url=url,
            description=description,
            timestamp=timestamp,
        )
        if author:
            if "name" not in author:
                raise ValueError("missing author name")
            self.set_author(name=author["name"], icon_url=author.get("icon_url"))
        if footer:
            if "text" not in footer:
                raise ValueError("missing footer text")
            self.set_footer(text=footer["text"], icon_url=footer.get("icon_url"))
        self.set_thumbnail(url=thumbnail)
        self.set_image(url=image)
        for pos, field in enumerate(fields):
            if not field.get("name"):
                raise ValueError(f"missing name in field {pos}")
            elif not field.get("value"):
                raise ValueError(f"missing value in field {pos}")
            self.add_field(
                name=field["name"],
                value=field["value"],
                inline=field.get("inline", True),
            )

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value

    def is_minimal_ready(self) -> bool:
        return any(
            (
                self.title,
                self.description,
                self.fields,
                self.timestamp,
                self.author,
                self.thumbnail,
                self.footer,
                self.image,
            )
        )

    def add_named_field(self, name: str, *, inline: bool = True) -> None:
        """Creates a new :class:`Embed` field with the provided name and an invisible value"""
        self.add_field(name=name, value="\u200b", inline=inline)

    def add_invisible_field(self, *, inline: bool = True) -> Embed:
        """Creates a new invisible :class:`Embed` field"""
        self.add_field(name="\u200b", value="\u200b", inline=inline)
        return self

    def to_discord_embed(self) -> discord.Embed:
        """Converts our custom :class:`Embed` instance to an actual :class:`discord.Embed`"""
        super().from_dict
        return discord.Embed.from_dict(self.to_dict())
