from __future__ import annotations

# Core Imports
import datetime
import os
from typing import Dict, Literal, Union


class Logger:
    """Custom Logger, writes logs to files and optionally to the console"""

    def __init__(
        self,
        name: str,
        console: bool = False,
    ) -> None:
        self.name = name
        self.console = console
        os.makedirs(os.path.dirname(f"logs/{self.name}/"), exist_ok=True)

    # Colour variants based on the log type
    LEVEL_COLOURS: Dict[str, str] = {
        "debug": "[0;1;34m{}[0m",
        "info": "[0;1;32m{}[0m",
        "warning": "[0;1;33m{}[0m",
        "error": "[0;1;31m{}[0m",
        "critical": "[0;1;31;47m{}[0m",
    }

    def to_file(self, text: str) -> None:
        """Writes the log message to the configured log file"""

        filename = datetime.datetime.now().date()
        with open(f"logs/{self.name}/{filename}-log.log", "a") as f:
            f.write(f"{text}\n")

    def format(
        self,
        message: str,
        *,
        level: Literal["debug", "info", "warning", "error", "critical"] = "info",
    ) -> None:
        """Formats and dispatches the log message"""

        log_message = (
            f"{datetime.datetime.now().strftime('%d/%m %H:%M:%S')} "
            f"[{self.name.upper()}] {level.upper()}: {message}"
        )
        self.to_file(log_message)
        if self.console:
            log_type = self.LEVEL_COLOURS.get(level, "[0;1;35m{}[0m").format(
                level.upper()
            )
            print(f"{self.name} | {log_type} {log_message}")

    def info(self, message: str) -> None:
        """Logs the given message with severity `INFO`"""

        self.format(message, level="info")

    def warn(self, message: str) -> None:
        """Logs the given message with severity `WARN`"""

        self.format(message, level="warning")

    def debug(self, message: str) -> None:
        """Logs the given message with severity `DEBUG`"""

        self.format(message, level="debug")

    def critical(self, message: str) -> None:
        """Logs the given message with severity `CRITICAL`"""

        self.format(message, level="critical")

    def error(self, message: Union[str, Exception]) -> None:
        """Logs the given message with severity `ERROR`"""

        message = (
            str(message) + str(message.__traceback__)
            if isinstance(message, Exception)
            else message
        )
        self.format(message, level="error")
