from loguru import logger
from db import async_session
from db.models import VKUsers
from typing import Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from vkbottle_types.objects import UsersUserFull # type: ignore
from vkbottle import ABCAPI # type: ignore

async def _select_user(user_id, session):
    return await session.execute(select(VKUsers).where(
        VKUsers.user_id == user_id
    ).options(selectinload("chats")))

async def get_or_create_user(user_id:int, api:Optional[ABCAPI]=None, session=None)->Optional[VKUsers]: # type: ignore
    logger.info(f"get user info for id{user_id}")
    need_close = session is None
    try:
        if session is None: session = async_session()
        result = await _select_user(user_id, session)
        the_user = result.scalars().first()
        if the_user is None and api is not None:
            logger.info(f"request user info id{user_id} from VK")
            u = (await api.users.get(user_id))[0]
            logger.debug(str(u))
            session.add(VKUsers(
                user_id=user_id,
                nickname = u.first_name+" "+u.last_name
            ))
            await session.commit()
            result = await _select_user(user_id, session)
            the_user = result.scalars().first()
        return the_user
    except:
        raise
    finally:
        if need_close:
            await session.close() # type: ignore
