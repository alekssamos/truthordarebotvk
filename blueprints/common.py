from db import async_session  # type: ignore
from vkbottle.bot import Blueprint, Message  # type: ignore

from db.models import VKUsers  # type: ignore
from services.users import get_or_create_user  # type: ignore

bp = Blueprint()
bp.labeler.message_view.replace_mention = True
bp.labeler.vbml_ignore_case = True


@bp.on.message(text=["Начать", "Start", "Help", "Помощь", "Справка"])
@bp.on.private_message(text=["?", "!"])
@bp.on.message(payload={"cmd": "start"})
async def hi_handler(message: Message):
    import strings

    u = await get_or_create_user(message.from_id, bp.api)
    await message.answer(strings.ru.start_message.format(u.mention).strip())


@bp.on.message(text="!ник <nickname>")
async def change_nick(message: Message, nickname=None):
    if not nickname:
        return
    for s in "[]()@\r\n":
        nickname = nickname.replace(s, "").strip()
    if not nickname:
        return
    if len(nickname) > 55:
        await message.answer("Слишком большая длина ника!")
        return None
    async with async_session() as session:
        u = await get_or_create_user(message.from_id, bp.api, session)
        old_nickname = u.nickname
        u.nickname = nickname
        await session.commit()
        await message.answer(f"Ваш ник успешно изменён!\n{old_nickname} → {nickname}")
