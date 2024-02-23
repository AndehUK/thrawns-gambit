# Core imports
import os
from typing import Literal, Union

# Third-party imports
import dotenv


class Env:
    ACCESS_KEY: str
    BOT_TOKEN: str
    COMLINK_URL: str
    ENVIRONMENT_MODE: Union[Literal["DEV"], Literal["PROD"]]
    JISHAKU_HIDE: str
    JISHAKU_NO_DM_TRACEBACK: str
    JISHAKU_NO_UNDERSCORE: str
    SECRET_KEY: str
    STATS_URL: str

    def __init__(self) -> None:
        dotenv.load_dotenv()
        self._verify_env_variables()

    def _verify_env_variables(self) -> None:
        for var in self.__class__.__annotations__:
            if not os.getenv(var):
                raise ValueError(f"Environment variable {var} is not set.")
            setattr(self, var, os.getenv(var))
