import asyncio
from loader import bot # type: ignore
from blueprints import bps

for bp in bps:
    bp.load(bot)


if __name__ == "__main__":
    print("The bot is running!")
    asyncio.run(bot.run_polling())
