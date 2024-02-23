# Core Imports
import asyncio
import os

# Third Party Packages
import dotenv


# Local Imports
from bot import ThrawnsGambit


async def main() -> None:
    # Load our dotenv file
    dotenv.load_dotenv()

    # Get our bot token
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("No BOT_TOKEN found in .env file")

    # Create our bot instance
    bot = ThrawnsGambit()

    # Run our bot
    await bot.start()


asyncio.run(main())
