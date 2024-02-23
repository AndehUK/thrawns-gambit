# Core Imports
import re
from functools import cached_property


class RegEx:
    """Class containing commonly-used regex patterns"""

    @cached_property
    def ally_code_regex(self) -> re.Pattern[str]:
        return re.compile(r"^(\d{9}|(\d{3}-){2}\d{3})$")

    @cached_property
    def swgoh_gg_regex(self) -> re.Pattern[str]:
        return re.compile(r"https:\/\/swgoh\.gg\/p\/\d{9}\/?")
