import asyncio
import json
from loguru import logger
from db import async_session  # type: ignore
from vkbottle.bot import Blueprint, Message  # type: ignore
from vkbottle import Callback, GroupEventType, GroupTypes, ShowSnackbarEvent  # type: ignore

from db.models import VKUsers  # type: ignore
from db.models import VKChats  # type: ignore
from services.users import get_or_create_user  # type: ignore
from services.chats import get_or_create_chat  # type: ignore
from rules import ChatAdminRule, TextContainsRule
import errors
import keyboards
import strings

bp = Blueprint()
bp.labeler.message_view.replace_mention = True
bp.labeler.vbml_ignore_case = True
bp.labeler.custom_rules["text_contains"] = TextContainsRule
bp.labeler.custom_rules["chat_admin"] = ChatAdminRule


@logger.catch
async def select_what(message):
    logger.info("The choice is truth or action")
    async with async_session() as session:
        chat = await get_or_create_chat(message.peer_id, session)
        if not chat.is_active_game:
            return None
        pair = await chat.take_pair(session)
        if pair is None:
            await end_game_handler(message)
            return None
        u1, u2 = pair
        logger.info(f"between {u1.mention} and {u2.mention}")
        chat.last_selection = ""
        msg = await bp.api.messages.send(
            message=strings.ru.select_toa.format(u1.mention, u2.mention),
            peer_id=message.peer_id,
            keyboard=keyboards.TOA_SELECT,
            random_id=0,
        )
        chat.last_message_id = msg


@logger.catch
async def end_recruitment_expired(message):
    import config

    minutes = config.recruitmentendtimeminute
    seconds = minutes * 60
    logger.info(f"waiting {minutes} minutes ({seconds} seconds)...")
    await asyncio.sleep(seconds)
    try:
        await end_recruitment_handler(message)
    except errors.BaseGameException:
        pass


@bp.on.chat_message(ChatAdminRule(), text=["!ни", "!играть", "!начать игру"])
@logger.catch
async def start_game_handler(message: Message):
    import config

    logger.info("new game...")
    try:
        async with async_session() as session:
            chat = await get_or_create_chat(message.peer_id, session)
            await chat.start_recruitment(session)
    except errors.RecruitmentOlreadyStarted as e:
        logger.exception(e.peer_id)
        asyncio.create_task(end_recruitment_expired(message))
        msg = await message.answer(strings.ru.recruitment_already_started)
        await asyncio.sleep(10)
        await bp.api.messages.delete(
            peer_id=message.peer_id, message_ids=msg, delete_for_all=1
        )
        return None
    except errors.GameOlreadyStarted as e:
        logger.exception(e.peer_id)
        msg = await message.answer(strings.ru.game_already_started)
        await asyncio.sleep(10)
        await bp.api.messages.delete(
            peer_id=message.peer_id, message_ids=msg, delete_for_all=1
        )
        return None
    await message.answer(
        strings.ru.recruitment_started.format(
            config.maxplayers, config.recruitmentendtimeminute
        ).strip(),
        # keyboard = keyboards.GAME_JOIN
        keyboard=keyboards.EMPTY,
    )
    asyncio.create_task(end_recruitment_expired(message))


@bp.on.chat_message(ChatAdminRule(), text=["!зн", "!завершить набор"])
@logger.catch
async def end_recruitment_handler(message: Message):
    logger.info("end recruitment")
    enum_players: str = ""
    enum_not_players: str = ""
    async with async_session() as session:
        chat = await get_or_create_chat(message.peer_id, session)
        if not chat.is_recruitment_of_new_players:
            return None
        players_in_game: list = list(filter(lambda x: x.is_field_in, chat.users))
        players_not_in_game: list = list(
            filter(lambda x: not x.is_field_in, chat.users)
        )
        chat.users = players_in_game
        await session.commit()
        if len(players_not_in_game) > 0:
            enum_not_players = ", ".join([u.nickname for u in players_not_in_game])
            await message.answer(
                strings.ru.drops_out_of_the_game.format(enum_not_players),
                keyboard=keyboards.EMPTY,
            )
        try:
            await chat.stop_recruitment(session)
            await chat.start_game(session)
        except errors.NotEnoughParticipants as e:
            logger.exception(e.peer_id)
            await message.answer(
                strings.ru.not_enough_participants, keyboard=keyboards.EMPTY
            )
            return None
        finally:
            await session.commit()
        enum_players = ", ".join([u.mention for u in players_in_game])
        await message.answer(
            strings.ru.recruitment_completed.format(enum_players),
            keyboard=keyboards.EMPTY,
        )
        await select_what(message)


@bp.on.chat_message(ChatAdminRule(), text=["!зи", "!завершить игру"])
@logger.catch
async def end_game_handler(message: Message):
    async with async_session() as session:
        chat = await get_or_create_chat(message.peer_id, session)
        try:
            await chat.stop_game(session)
            await session.commit()
        except errors.BaseGameException:
            return None
        await bp.api.messages.send(
            message=strings.ru.game_completed,
            peer_id=message.peer_id,
            keyboard=keyboards.EMPTY,
            random_id=0,
        )


@bp.on.chat_message(
    text_contains=["+", "плюс", "plus", "➕", "✖", "†", strings.ru.i_want_to_play]
)
@bp.on.chat_message(payload={"cmd": "implay"})
@logger.catch
async def join_player_handler(message: Message):
    import config

    logger.info("join player...")
    async with async_session() as session:
        chat = await get_or_create_chat(message.peer_id, session)
        u = await get_or_create_user(message.from_id, bp.api, session)
        if u.chats is not None and u.chats.peer_id != chat.peer_id:
            logger.info("The user wants to join the games in two chats")
            msg = await message.answer(
                strings.ru.player_already_joind_in_another_chat.format(u.mention)
            )
            await asyncio.sleep(10)
            await bp.api.messages.delete(
                peer_id=message.peer_id, message_ids=msg, delete_for_all=1
            )
            return None
        if not chat.is_recruitment_of_new_players:
            logger.debug("no recruitment in thith moment")
            msg = await message.answer(strings.ru.not_recruitment.format(u.mention))
            await asyncio.sleep(10)
            await bp.api.messages.delete(
                peer_id=message.peer_id, message_ids=msg, delete_for_all=1
            )
            return None
        c = len(chat.users)
        if u.user_id not in [i.user_id for i in chat.users]:
            chat.users.append(u)
            c = len(chat.users)
            await session.commit()
            await message.answer(
                strings.ru.player_joind.format(u.mention, c, config.maxplayers)
            )
            if c >= config.maxplayers:
                await end_game_handler(message)
                return None
        else:
            logger.info("olready joind")
            msg = await message.answer(
                strings.ru.player_already_joind.format(u.mention)
            )
            await asyncio.sleep(10)
            await bp.api.messages.delete(
                peer_id=message.peer_id, message_ids=msg, delete_for_all=1
            )


@bp.on.chat_message(text_contains=strings.ru.continue_game.strip("!"))
@logger.catch
async def continue_game_by_word(message: Message):
    logger.info("checking user...")
    async with async_session() as session:
        chat = await get_or_create_chat(message.peer_id, session)
        u1, u2 = await chat.get_current_combination()
        if ["truth", "action"] in chat.last_selection and u1.user_id == message.from_id:
            await select_what(message)


@bp.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=GroupTypes.MessageEvent)
@logger.catch
async def handle_message_event(event: GroupTypes.MessageEvent):
    payload = event.object.payload
    if payload.get("cmd", "") in ["truth", "action"]:
        return await handle_toa_event(event)
    if payload.get("cmd", "") == "continue":
        return await handle_selected_toa_event(event)


async def handle_selected_toa_event(event: GroupTypes.MessageEvent):
    async with async_session() as session:
        chat = await get_or_create_chat(event.object.peer_id, session)
        if not chat.is_active_game:
            await bp.api.messages.delete(
                peer_id=event.object.peer_id,
                cmids=event.object.conversation_message_id,
                delete_for_all=1,
            )
            await bp.api.messages.send_message_event_answer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=ShowSnackbarEvent(text=strings.ru.game_completed).json(),
            )
            return None
        u1, u2 = await chat.get_current_combination()
        text_answer = ""
        if u1.user_id == event.object.user_id:
            logger.info(f"{u1.mention} completed")
            msg = await bp.api.messages.get_by_conversation_message_id(
                peer_id=event.object.peer_id,
                conversation_message_ids=event.object.conversation_message_id,
            )
            await bp.api.messages.edit(
                peer_id=event.object.peer_id,
                conversation_message_id=event.object.conversation_message_id,
                message=msg.items[0].text,
                keyboard=keyboards.EMPTY,
            )
            messages = await bp.api.messages.get_by_conversation_message_id(
                peer_id=event.object.peer_id,
                conversation_message_ids=event.object.conversation_message_id,
            )
            await select_what(message=messages.items[0])
            text_answer = "OK"
        else:
            logger.info("another user press this button")
            text_answer = strings.ru.button_only_for.format(u1.nickname)
        await bp.api.messages.send_message_event_answer(
            event_id=event.object.event_id,
            user_id=event.object.user_id,
            peer_id=event.object.peer_id,
            event_data=ShowSnackbarEvent(text=text_answer).json(),
        )


async def handle_toa_event(event: GroupTypes.MessageEvent):
    what: str = event.object.payload.get("cmd", "")
    what_str: str = ""
    if what == "":
        raise ValueError("what")
    if what == "action":
        what_str = strings.ru.action
    if what == "truth":
        what_str = strings.ru.truth
    async with async_session() as session:
        chat = await get_or_create_chat(event.object.peer_id, session)
        if not chat.is_active_game:
            await bp.api.messages.delete(
                peer_id=event.object.peer_id,
                cmids=event.object.conversation_message_id,
                delete_for_all=1,
            )
            await bp.api.messages.send_message_event_answer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=ShowSnackbarEvent(text=strings.ru.game_completed).json(),
            )
            return None
        u1, u2 = await chat.get_current_combination()
        if u2.user_id == event.object.user_id:
            logger.info(f"{u2.mention} selected {what}")
            chat.last_selection = what
            chat.last_message_id = event.object.conversation_message_id
            msg = await bp.api.messages.get_by_conversation_message_id(
                peer_id=event.object.peer_id,
                conversation_message_ids=event.object.conversation_message_id,
            )
            await bp.api.messages.edit(
                peer_id=event.object.peer_id,
                conversation_message_id=event.object.conversation_message_id,
                message=msg.items[0].text,
                keyboard=keyboards.EMPTY,
            )
            await bp.api.messages.send(
                peer_id=event.object.peer_id,
                conversation_message_id=event.object.conversation_message_id,
                message=strings.ru.selected_toa.format(u2.mention, what_str),
                keyboard=keyboards.GAME_CONTINUE,
                random_id=0,
            )
            text_answer = what_str
        else:
            logger.info("another user press this button")
            text_answer = strings.ru.button_only_for.format(u2.nickname)
        await bp.api.messages.send_message_event_answer(
            event_id=event.object.event_id,
            user_id=event.object.user_id,
            peer_id=event.object.peer_id,
            event_data=ShowSnackbarEvent(text=text_answer).json(),
        )
