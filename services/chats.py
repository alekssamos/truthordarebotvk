from db import async_session
from db.models import VKChats
from typing import Any, Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


async def _select_chat(peer_id, session):
    return await session.execute(
        select(VKChats).where(VKChats.peer_id == peer_id).options(selectinload("users"))
    )


async def get_or_create_chat(peer_id: int, session: Optional[Any] = None) -> Optional[VKChats]:  # type: ignore
    need_close = session is None
    try:
        if session is None:
            session = async_session()
        result = await _select_chat(peer_id, session)
        the_chat = result.scalars().first()
        if the_chat is None:
            the_chat = VKChats(peer_id=peer_id)
            session.add(the_chat)
            await session.commit()
            del the_chat
            result = await _select_chat(peer_id, session)
            the_chat = result.scalars().first()
        return the_chat  # type: ignore
    except Exception:
        raise
    finally:
        if need_close:
            await session.close()  # type: ignore
