import os
import os.path
from aiohttp import web
from services.vkapp import is_valid  # type: ignore
from services.users import get_or_create_user  # type: ignore
from db import async_session
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from db.models import VKChats, VKUsers
from loguru import logger

try:
    path_to_static_folder = os.path.join(os.path.dirname(__file__), "static")
    if not os.path.isdir(path_to_static_folder):
        os.mkdir(path_to_static_folder)
        logger.info(f"static folder created: {path_to_static_folder}")
except Exception:
    logger.exception(f"static folder {path_to_static_folder} creation error")


@web.middleware
async def append_headers(request, handler):
    response = await handler(request)
    response.headers.update(
        {
            "access-control-allow-origin": "*",
            "access-control-allow-methods": "GET, POST, OPTIONS",
            "access-control-allow-headers": "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Content-Range,Range,Accept,Authorization,Referer,Sec-Fetch-Mode",
        }
    )
    return response


app = web.Application(middlewares=[append_headers])
routes = web.RouteTableDef()
routes.static("/static", path_to_static_folder)


@routes.get("/settings")
async def get_settings(request):
    from loader import bot

    user_id = int(request.query.get("user_id", 0))
    if user_id == 0:
        logger.error(f"incorrect user_id: {request.query}")
        return web.json_response({"error": "user not found"}, status=404)
    logger.info(f"get settings for user_id={user_id}")
    locked = False
    settings = {}
    async with async_session() as session:
        u = await get_or_create_user(user_id=user_id, session=session, api=bot.api)
        result = await session.execute(
            select(VKUsers).where(VKChats.is_active_game is True)
        )
        if result.scalar() is not None and result.scalar().count() > 0:
            locked = True
        settings.update({"locked":locked, "nickname": u.nickname, "dch": u.dch, "gg": u.gg, "ul": u.ul})
    return web.json_response(settings)


app.add_routes(routes)
