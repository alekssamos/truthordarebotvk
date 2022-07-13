import asyncio


async def main():
    from loader import bot  # type: ignore
    from db import init_models

    await init_models()
    from blueprints import bps

    for bp in bps:
        bp.load(bot)
    await bot.run_polling()


if __name__ == "__main__":
    print("The bot is running!")
    asyncio.run(main())
