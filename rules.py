from vkbottle.bot import Message # type: ignore
from vkbottle.dispatch.rules import ABCRule # type: ignore
from vkbottle import VKAPIError # type: ignore
from vkbottle.exception_factory import ErrorHandler # type: ignore
from loguru import logger

class ChatAdminRule(ABCRule[Message]):
    async def check(self, message: Message) -> bool:
        try:
            members = await message.ctx_api.messages.get_conversation_members(
                peer_id=message.peer_id
            )
        except VKAPIError[917]:
            loggger.exception("I not admin")
            return False
        admins = {member.member_id for member in members.items if member.is_admin}
        if message.from_id in admins:
            return True
        return False
