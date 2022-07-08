from db import async_session # type: ignore
from vkbottle.bot import Blueprint, Message # type: ignore

from db.models import VKUsers # type: ignore
from services.users import get_or_create_user # type: ignore

bp = Blueprint()
bp.labeler.message_view.replace_mention = True
bp.labeler.vbml_ignore_case = True

@bp.on.message(text=["Начать", "Start", "?", "Help", "Помощь", "Справка"])
@bp.on.message(payload={"cmd":"start"})
async def hi_handler(message: Message):
    u = await get_or_create_user(message.from_id, bp.api)
    await message.answer("""
    Бот для помощи с игрой "Правда или действие".
    Команды:
    !ник Новый_псевдоним -- изменить Ваше имя в игре.
    Сейчас Ваш ник {}.
    
    Остальные команды доступны в беседе. Добавьте этого бота в беседу и сделайте админом.
    !ни или !играть -- Начать новую  игру (только для админа беседы). После этого начнётся набор участников, остановится по команде !зн, по достижению 5 минут или 10 участников.
    !зн или !завершить набор -- Завершить набор участников досрочно.
    !зи или !завершить игру -- Завершить игру немедленно.
    """.strip().format(u.mention))

@bp.on.message(text="!ник <nickname>")
async def change_nick(message: Message, nickname=None):
    if not nickname: return
    for s in "[]()@\r\n": nickname = nickname.replace(s, '').strip()
    if not nickname: return
    if len(nickname) > 55:
        await message.answer("Слишком большая длина ника!")
        return None
    async with async_session() as session:
        u = await get_or_create_user(message.from_id, bp.api, session)
        old_nickname = u.nickname
        u.nickname = nickname
        await session.commit()
        await message.answer(f"Ваш ник успешно изменён!\n{old_nickname} → {nickname}")

