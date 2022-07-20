from typing import Any
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
import config


def tobool(o: Any) -> bool:
    if isinstance(o, str) and o.lower() in ["1", "true", "on"]:
        return True
    if isinstance(o, str) and o.lower() in ["0", "false", "off"]:
        return False
    return not not o


try:
    path_to_static_folder = os.path.join(os.path.dirname(__file__), "static")
    if not os.path.isdir(path_to_static_folder):
        os.mkdir(path_to_static_folder)
        logger.info(f"static folder created: {path_to_static_folder}")
except Exception:
    logger.exception(f"static folder {path_to_static_folder} creation error")


@web.middleware
async def check_request(request, handler):
    full_query = dict(request.query)
    full_query.update((await request.post()))
    if full_query.get("vk_user_id", None) is not None and not is_valid(
        query=full_query, secret=config.vk_app_secret
    ):
        logger.debug("The request failed verification")
        return web.json_response({"error": "sign"})
    response = await handler(request)
    return response


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


app = web.Application(middlewares=[append_headers, check_request])
routes = web.RouteTableDef()
routes.static("/static", path_to_static_folder)


@routes.get("/settings")
@routes.post("/settings")
async def get_settings(request):
    from loader import bot

    full_query = dict(request.query)
    full_query.update((await request.post()))
    user_id = int(full_query.get("vk_user_id", 0))
    if user_id == 0:
        logger.error(f"incorrect user_id: {request.query}")
        return web.json_response({"error": "user"}, status=404)
    logger.info(f"get settings for user_id={user_id}")
    locked = False
    settings = {}
    async with async_session() as session:
        u = await get_or_create_user(user_id=user_id, session=session, api=bot.api)
        the_chat = u.chats
        if the_chat is not None:
            locked = the_chat.is_active_game
            logger.debug(f"found chat with peer_id={the_chat.peer_id}")
        else:
            logger.debug("the user does not belong to any chats")
        updated: bool = False
        if not locked:
            if full_query.get("dch", None) is not None:
                u.dch = tobool(full_query.get("dch"))
                updated = True
            if full_query.get("gg", None) is not None:
                u.gg = tobool(full_query.get("gg"))
                updated = True
            if full_query.get("ul", None) is not None:
                u.ul = tobool(full_query.get("ul"))
                updated = True
            await session.commit()
            if updated:
                logger.info("The settings have been updated!")
        settings.update(
            {
                "locked": locked,
                "nickname": u.nickname,
                "dch": u.dch,
                "gg": u.gg,
                "ul": u.ul,
                "updated": updated,
            }
        )
    return web.json_response(settings)


app.add_routes(routes)
