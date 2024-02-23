from __future__ import annotations

# Core Imports
import base64
import functools
import hashlib
import hmac
import io
import json
import time
import zipfile
from json import dumps
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

# Local Imports
from utils.logger import Logger
from .types.player import Player


if TYPE_CHECKING:
    from bot import ThrawnsGambit


def _get_player_payload(
    allycode: Optional[str | int] = None,
    player_id: Optional[str] = None,
    enums: bool = False,
) -> Dict[Any, Any]:
    """
    Helper function to build payload for get_player functions
    :param allycode: player allyCode
    :param player_id: player game ID
    :param enums: boolean
    :return: Dict[Any, Any]
    """
    payload: Dict[str, Any] = {"payload": {}, "enums": enums}
    # If player ID is provided use that instead of allyCode
    if not allycode and player_id:
        payload["payload"]["playerId"] = f"{player_id}"
    # Otherwise use allyCode to lookup player data
    else:
        payload["payload"]["allyCode"] = f"{allycode}"
    return payload


def param_alias(
    param: str, alias: str
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            alias_param_value = kwargs.get(alias)
            if alias_param_value:
                kwargs[param] = alias_param_value
                del kwargs[alias]
            return func(*args, **kwargs)

        return wrapper

    return decorator


class SwgohComlink:
    """
    Class definition for swgoh-comlink interface and supported methods.
    Instances of this class are used to query the Star Wars Galaxy of Heroes
    game servers for exposed endpoints via the swgoh-comlink proxy library
    running on the same host.
    """

    bot: ThrawnsGambit
    hmac: bool
    logger: Logger
    stats_url_base: str
    unit_name_map: Dict[str, str]
    url_base: str

    def __init__(self, bot: ThrawnsGambit):
        """
        Set initial values when new class instance is created
        :param url: The URL where swgoh-comlink is running. Defaults to 'http://localhost:3000'
        :param access_key: The HMAC public key. Default to None which indicates HMAC is not used.
        :param secret_key: The HMAC private key. Default to None which indicates HMAC is not used.
        :param stats_url: The url of the swgoh-stats service (if used), such as 'http://localhost:3223'
        :param host: IP address or DNS name of server where the swgoh-comlink service is running
        :param port: TCP port number where the swgoh-comlink service is running [Default: 3000]
        :param stats_port: TCP port number of where the comlink-stats service is running [Default: 3223]
        """
        self.bot = bot
        self.hmac = False  # HMAC use disabled by default
        self.logger = Logger(
            "Comlink", console=True if bot.config.ENVIRONMENT_MODE == "DEV" else False
        )
        self.url_base = bot.config.COMLINK_URL
        self.stats_url_base = bot.config.STATS_URL

        if self.bot.config.ACCESS_KEY and self.bot.config.SECRET_KEY:
            self.hmac = True

    async def _get_game_version(self) -> str:
        """Get the current game version"""
        md = await self.get_game_metadata()
        return md["latestGamedataVersion"]

    async def _post(
        self,
        url_base: Optional[str] = None,
        endpoint: Optional[str] = None,
        payload: Optional[Dict[Any, Any]] = None,
    ) -> Dict[Any, Any]:
        """
        Execute HTTP POST operation against swgoh-comlink
        :param url_base: Base URL for the request method
        :param endpoint: which game endpoint to call
        :param payload: POST payload json data
        :return: Dict[Any, Any]
        """
        if not url_base:
            url_base = self.url_base
        post_url = url_base + f"/{endpoint}"
        req_headers = {}
        # If access_key and secret_key are set, perform HMAC security
        if self.hmac:
            assert self.bot.config.SECRET_KEY and self.bot.config.ACCESS_KEY
            req_time = str(int(time.time() * 1000))
            req_headers = {"X-Date": f"{req_time}"}
            hmac_obj = hmac.new(
                key=self.bot.config.SECRET_KEY.encode(), digestmod=hashlib.sha256
            )
            hmac_obj.update(req_time.encode())
            hmac_obj.update(b"POST")
            hmac_obj.update(f"/{endpoint}".encode())
            # json dumps separators needed for compact string formatting required for compatibility with
            # comlink since it is written with javascript as the primary object model
            # ordered dicts are also required with the 'payload' key listed first for proper MD5 hash calculation
            if payload:
                payload_string = dumps(payload, separators=(",", ":"))
            else:
                payload_string = dumps({})
            payload_hash_digest = hashlib.md5(payload_string.encode()).hexdigest()
            hmac_obj.update(payload_hash_digest.encode())
            hmac_digest = hmac_obj.hexdigest()
            req_headers["Authorization"] = (
                f"HMAC-SHA256 Credential={self.bot.config.ACCESS_KEY},Signature={hmac_digest}"
            )
        try:
            r = await self.bot.session.post(post_url, json=payload, headers=req_headers)
            return await r.json()
        except Exception as e:
            raise e

    async def get_unit_stats(
        self,
        request_payload: Dict[Any, Any],
        flags: Optional[List[Any]] = None,
        language: Optional[str] = None,
    ) -> Dict[Any, Any]:
        """
        Calculate unit stats using swgoh-stats service interface to swgoh-comlink

        :param request_payload: Dictionary containing units for which to calculate stats
        :param flags: List of flags to include in the request URI
        :param language: String indicating the desired localized language
        :return: Dict[Any, Any]
        """
        query_string = None
        flags_str = ""

        if flags:
            flags_str = "flags=" + ",".join(flags)
        if language:
            language = f"language={language}"
        if flags_str or language:
            query_string = f"?" + "&".join(filter(None, [flags_str, language]))
        endpoint_string = f"api" + query_string if query_string else "api"
        return await self._post(
            url_base=self.stats_url_base,
            endpoint=endpoint_string,
            payload=request_payload,
        )

    async def get_enums(self) -> Dict[Any, Any]:
        """
        Get an object containing the game data enums
        :return: Dict[Any, Any]
        """
        url = self.url_base + "/enums"
        try:
            r = await self.bot.session.get(url)
            return await r.json()
        except Exception as e:
            raise e

    # alias for non PEP usage of direct endpoint calls
    getEnums = get_enums

    def get_events(self, enums: bool = False):
        """
        Get an object containing the events game data
        :param enums: Boolean flag to indicate whether enum value should be converted in response. [Default is False]
        :return: Dict[Any, Any]
        """
        payload: Dict[str, Any] = {"payload": {}, "enums": enums}
        return self._post(endpoint="getEvents", payload=payload)

    # alias for non PEP usage of direct endpoint calls
    getEvents = get_events

    async def get_game_data(
        self,
        version: str = "",
        include_pve_units: bool = True,
        request_segment: int = 0,
        enums: bool = False,
    ) -> Dict[Any, Any]:
        """
        Get game data
        :param version: string (found in metadata key value 'latestGamedataVersion')
        :param include_pve_units: boolean [Defaults to True]
        :param request_segment: integer >=0 [Defaults to 0]
        :param enums: boolean [Defaults to False]
        :return: Dict[Any, Any]
        """
        if version == "":
            game_version = self._get_game_version()
        else:
            game_version = version
        payload = {
            "payload": {
                "version": f"{game_version}",
                "includePveUnits": include_pve_units,
                "requestSegment": request_segment,
            },
            "enums": enums,
        }
        return await self._post(endpoint="data", payload=payload)

    # alias for non PEP usage of direct endpoint calls
    getGameData = get_game_data

    async def get_localization(
        self, id: Optional[str] = None, unzip: bool = False, enums: bool = False
    ) -> Dict[Any, Any]:
        """
        Get localization data from game
        :param id: latestLocalizationBundleVersion found in game metadata. This method will collect the latest language
                    version if the 'id' argument is not provided.
        :param unzip: boolean [Defaults to False]
        :param enums: boolean [Defaults to False]
        :return: Dict[Any, Any]
        """
        if not id:
            current_game_version = await self.get_latest_game_data_version()
            id = current_game_version["language"]

        payload = {"unzip": unzip, "enums": enums, "payload": {"id": id}}
        return await self._post(endpoint="localization", payload=payload)

    # aliases for non PEP usage of direct endpoint calls
    getLocalization = get_localization
    getLocalizationBundle = get_localization
    get_localization_bundle = get_localization

    async def get_game_metadata(
        self, client_specs: Dict[Any, Any] = {}, enums: bool = False
    ) -> Dict[Any, Any]:
        """
        Get the game metadata. Game metadata contains the current game and localization versions.
        :param client_specs:  Optional dictionary containing
        :param enums: Boolean signifying whether enums in response should be translated to text. [Default: False]
        :return: Dict[Any, Any]

        {
          "payload": {
            "clientSpecs": {
              "platform": "string",
              "bundleId": "string",
              "externalVersion": "string",
              "internalVersion": "string",
              "region": "string"
            }
          },
          "enums": false
        }
        """
        if client_specs:
            payload = {"payload": {"client_specs": client_specs}, "enums": enums}
        else:
            payload = {}
        return await self._post(endpoint="metadata", payload=payload)

    # alias for non PEP usage of direct endpoint calls
    getGameMetaData = get_game_metadata
    getMetaData = get_game_metadata
    get_metadata = get_game_metadata

    async def get_player(
        self,
        allycode: Optional[str | int] = None,
        player_id: Optional[str] = None,
        enums: bool = False,
    ) -> Player:
        """
        Get player information from game
        :param allycode: integer or string representing player allycode
        :param player_id: string representing player game ID
        :param enums: boolean [Defaults to False]
        :return: Dict[Any, Any]
        """
        payload = _get_player_payload(
            allycode=allycode, player_id=player_id, enums=enums
        )
        data = await self._post(endpoint="player", payload=payload)
        return Player(**data)

    # alias for non PEP usage of direct endpoint calls
    getPlayer = get_player

    # Introduced in 1.12.0
    # Use decorator to alias the player_details_only parameter to 'playerDetailsOnly' to maintain backward compatibility
    # while fixing the original naming format mistake.
    @param_alias(param="player_details_only", alias="playerDetailsOnly")
    async def get_player_arena(
        self,
        allycode: Optional[str | int] = None,
        player_id: Optional[str] = None,
        player_details_only: bool = False,
        enums: bool = False,
    ) -> Dict[Any, Any]:
        """
        Get player arena information from game
        :param allycode: integer or string representing player allycode
        :param player_id: string representing player game ID
        :param player_details_only: filter results to only player details [Defaults to False]
        :param enums: boolean [Defaults to False]
        :return: Dict[Any, Any]
        """
        payload = _get_player_payload(
            allycode=allycode, player_id=player_id, enums=enums
        )
        payload["payload"]["playerDetailsOnly"] = player_details_only
        return await self._post(endpoint="playerArena", payload=payload)

    # alias to allow for get_arena() calls as a shortcut for get_player_arena() and non PEP variations
    get_arena = get_player_arena
    get_player_arena_profile = get_player_arena
    getPlayerArena = get_player_arena
    getPlayerArenaProfile = get_player_arena

    @param_alias(param="include_recent_guild_activity_info", alias="includeRecent")
    async def get_guild(
        self,
        guild_id: str,
        include_recent_guild_activity_info: bool = False,
        enums: bool = False,
    ) -> Dict[Any, Any]:
        """
        Get guild information for a specific Guild ID.
        :param guild_id: String ID of guild to retrieve. Guild ID can be found in the output
                            of the get_player() call. (Required)
        :param include_recent_guild_activity_info: boolean [Default: False] (Optional)
        :param enums: Should enums in response be translated to text. [Default: False] (Optional)
        :return: Dict[Any, Any]
        """
        payload = {
            "payload": {
                "guildId": guild_id,
                "includeRecentGuildActivityInfo": include_recent_guild_activity_info,
            },
            "enums": enums,
        }
        guild = await self._post(endpoint="guild", payload=payload)
        if "guild" in guild.keys():
            guild = guild["guild"]
        return guild

    # alias for non PEP usage of direct endpoint calls
    getGuild = get_guild

    async def get_guilds_by_name(
        self, name: str, start_index: int = 0, count: int = 10, enums: bool = False
    ) -> Dict[Any, Any]:
        """
        Search for guild by name and return match.
        :param name: string for guild name search
        :param start_index: integer representing where in the resulting list of guild name matches
                            the return object should begin
        :param count: integer representing the maximum number of matches to return, [Default: 10]
        :param enums: Whether to translate enums in response to text, [Default: False]
        :return: Dict[Any, Any]
        """
        payload = {
            "payload": {
                "name": name,
                "filterType": 4,
                "startIndex": start_index,
                "count": count,
            },
            "enums": enums,
        }
        return await self._post(endpoint="getGuilds", payload=payload)

    # alias for non PEP usage of direct endpoint calls
    getGuildByName = get_guilds_by_name

    async def get_guilds_by_criteria(
        self,
        search_criteria: Dict[Any, Any],
        start_index: int = 0,
        count: int = 10,
        enums: bool = False,
    ) -> Dict[Any, Any]:
        """
        Search for guild by guild criteria and return matches.
        :param search_criteria: Dictionary
        :param start_index: integer representing where in the resulting list of guild name matches the return object should begin
        :param count: integer representing the maximum number of matches to return
        :param enums: Whether to translate enum values to text [Default: False]
        :return: Dict[Any, Any]

        search_criteria_template = {
            "minMemberCount": 1,
            "maxMemberCount": 50,
            "includeInviteOnly": True,
            "minGuildGalacticPower": 1,
            "maxGuildGalacticPower": 500000000,
            "recentTbParticipatedIn": []
        }
        """
        payload = {
            "payload": {
                "searchCriteria": search_criteria,
                "filterType": 5,
                "startIndex": start_index,
                "count": count,
            },
            "enums": enums,
        }
        return await self._post(endpoint="getGuilds", payload=payload)

    # alias for non PEP usage of direct endpoint calls
    getGuildByCriteria = get_guilds_by_criteria

    async def get_leaderboard(
        self,
        leaderboard_type: int,
        league: Optional[int | str] = None,
        division: Optional[int | str] = None,
        event_instance_id: Optional[str] = None,
        group_id: Optional[str] = None,
        enums: bool = False,
    ) -> Dict[Any, Any]:
        """
        Retrieve Grand Arena Championship leaderboard information.
        :param leaderboard_type: Type 4 is for scanning gac brackets, and only returns results while an event is active.
                                    When type 4 is indicated, the "league" and "division" arguments must also be provided.
                                 Type 6 is for the global leaderboards for the league + divisions.
                                    When type 6 is indicated, the "event_instance_id" and "group_id" must also be provided.
        :param league: Enum values 20, 40, 60, 80, and 100 correspond to carbonite, bronzium, chromium, aurodium,
                       and kyber respectively. Also accepts string values for each league.
        :param division: Enum values 5, 10, 15, 20, and 25 correspond to divisions 5 through 1 respectively.
                         Also accepts string or int values for each division.
        :param event_instance_id: When leaderboard_type 4 is indicated, a combination of the event Id and the instance
                                ID separated by ':'
                                Example: CHAMPIONSHIPS_GRAND_ARENA_GA2_EVENT_SEASON_36:O1675202400000
        :param group_id: When leaderboard_type 4 is indicated, must start with the same eventInstanceId, followed
                         by the league and bracketId, separated by :. The number at the end is the bracketId, and
                         goes from 0 to N, where N is the last group of 8 players.
                            Example: CHAMPIONSHIPS_GRAND_ARENA_GA2_EVENT_SEASON_36:O1675202400000:CARBONITE:10431
        :param enums: Whether to translate enum values to text [Default: False]
        :return: Dict[Any, Any]
        """
        leagues = {
            "kyber": 100,
            "aurodium": 80,
            "chromium": 60,
            "bronzium": 40,
            "carbonite": 20,
        }
        divisions = {"1": 25, "2": 20, "3": 15, "4": 10, "5": 5}
        # Translate parameters if needed
        if isinstance(league, str):
            league = leagues[league.lower()]
        if isinstance(division, int) and len(str(division)) == 1:
            division = divisions[str(division).lower()]
        if isinstance(division, str):
            division = divisions[division.lower()]
        payload: Dict[str, Any] = {
            "payload": {
                "leaderboardType": leaderboard_type,
            },
            "enums": enums,
        }
        if leaderboard_type == 4:
            payload["payload"]["eventInstanceId"] = event_instance_id
            payload["payload"]["groupId"] = group_id
        elif leaderboard_type == 6:
            payload["payload"]["league"] = league
            payload["payload"]["division"] = division
        leaderboard = await self._post(endpoint="getLeaderboard", payload=payload)
        return leaderboard

    # alias for non PEP usage of direct endpoint calls
    getLeaderboard = get_leaderboard
    get_gac_leaderboard = get_leaderboard
    getGacLeaderboard = get_leaderboard

    async def get_guild_leaderboard(
        self, leaderboard_id: List[Any], count: int = 200, enums: bool = False
    ) -> Dict[Any, Any]:
        """
        Retrieve leaderboard information from SWGOH game servers.
        :param leaderboard_id: List of objects indicating leaderboard type, month offset, and depending on the
                                leaderboard type, a defId. For example, leaderboard type 2 would also require a
                                defId of one of "sith_raid", "rancor", "rancor_challenge", or "aat".
        :param count: Number of entries to retrieve [Default: 200]
        :param enums: Convert enums to strings [Default: False]
        :return: Dict[Any, Any]
        """
        payload: Dict[str, Any] = dict(
            payload={"leaderboardId": leaderboard_id, "count": count}, enums=enums
        )
        return await self._post(endpoint="getGuildLeaderboard", payload=payload)

    # alias for non PEP usage of direct endpoint calls
    getGuildLeaderboard = get_guild_leaderboard

    """
    Helper methods are below
    """

    # Get the latest game data and language bundle versions
    async def get_latest_game_data_version(self) -> Dict[Any, Any]:
        """
        Get the latest game data and language bundle versions
        :return: Dict[Any, Any]
        """
        current_metadata = await self.get_metadata()
        return {
            "game": current_metadata["latestGamedataVersion"],
            "language": current_metadata["latestLocalizationBundleVersion"],
        }

    # alias for shorthand call
    getVersion = get_latest_game_data_version

    async def create_localised_unit_name_dictionary(self) -> None:
        """
        Take a localisation element from the SwgohComlink.get_localization() result dictionary and
        extract the UNIT_NAME entries for building a conversion dictionary for translating BASEID values to in game
        descriptive names

        :param locale: The string element or List[bytes] from the SwgohComlink.get_localization() result key value
        :type locale: str or List[bytes]
        :return: A dictionary with the UNIT_NAME BASEID as keys and the UNIT_NAME description as values
        :rtype: dict

        TODO: Add other languages to the localisation bundle
        """
        self.logger.debug("Creating localisation dictionary...")
        game_data_versions = await self.get_latest_game_data_version()
        bundle = await self.get_localization_bundle(id=game_data_versions["language"])
        self.logger.debug("Localisation bundle retrieved.")

        decoded_bundle = base64.b64decode(bundle["localizationBundle"])
        self.logger.debug("Localisation bundle decoded.")
        zip_obj = zipfile.ZipFile(io.BytesIO(decoded_bundle))
        self.logger.debug("Localisation bundle unzipped.")
        eng_obj = zip_obj.read("Loc_ENG_US.txt")
        self.logger.debug("Localisation bundle read.")
        locale = eng_obj.decode("utf-8")
        self.logger.debug("Localisation bundle decoded to utf-8.")

        unit_name_map: Dict[str, str] = {}
        lines = locale.split("\n")
        for line in lines:
            if isinstance(line, bytes):
                line = line.decode()
            line = line.rstrip("\n")
            if line.startswith("#"):
                continue
            if "|" not in line:
                continue
            if line.startswith("UNIT_"):
                name_key, desc = line.split("|")
                if name_key.endswith("_NAME"):
                    unit_name_map[name_key] = desc
        self.logger.debug("Localisation dictionary created.")
        self.unit_name_map = unit_name_map
        with open("assets/localisation/en-US.json", "w+") as f:
            f.write(json.dumps(unit_name_map, indent=4, sort_keys=True))
        self.logger.info("Localisation dictionary created and saved to file.")
