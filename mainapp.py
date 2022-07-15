import asyncio
from loguru import logger


async def main():
    logger.debug("loader")
    from loader import bot  # type: ignore

    logger.debug("init_models")
    from db import init_models

    await init_models()
    logger.debug("bps")
    from blueprints import bps

    for bp in bps:
        bp.load(bot)
    logger.debug("apiserver")
    from apiserver import app, web

    runner = web.AppRunner(app)
    await runner.setup()
    import config

    host, port = (config.apiserver_host, config.apiserver_port)
    logger.info(f"Running server on {host}:{port}")
    site = web.TCPSite(runner, host, port)
    await asyncio.gather(bot.run_polling(), site.start())


if __name__ == "__main__":
    print("The bot is running!")
    asyncio.run(main())
