from typing import Iterable, Union
from vkbottle.bot import Message # type: ignore
from vkbottle.dispatch.rules import ABCRule # type: ignore
from vkbottle import VKAPIError # type: ignore
from vkbottle.exception_factory import ErrorHandler # type: ignore
from loguru import logger

class ChatAdminRule(ABCRule[Message]):
    def __init__(self, flag:bool = True):
        self.flag = flag
    async def check(self, message: Message) -> bool:
        if not self.flag: return False
        try:
            members = await message.ctx_api.messages.get_conversation_members(
                peer_id=message.peer_id
            )
        except VKAPIError[917]:
            logger.exception("I not admin")
            return False
        admins = {member.member_id for member in members.items if member.is_admin}
        if message.from_id in admins:
            return True
        return False

class TextContainsRule(ABCRule[Message]):
    def __init__(self, sc: Union[str, Iterable]):
        self.sc = sc
    async def check(self, message: Message) -> bool:
        if isinstance(self.sc, str):
            return self.sc.strip().lower() in message.text.strip().lower()
        for s in self.sc:
            if s.strip().lower() in message.text.strip().lower(): return True
        return False
