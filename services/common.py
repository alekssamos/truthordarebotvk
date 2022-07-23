from loguru import logger  # type: ignore
from vkbottle import ErrorHandler  # type: ignore
from vkbottle import VKAPIError  # type: ignore

error_handler = ErrorHandler()


@error_handler.register_error_handler(VKAPIError)
async def exc_handler(exc: VKAPIError):
    logger.exception("VKAPIError")


@error_handler.catch
async def messages_edit(api, *args, **kwargs):
    return await api.messages.edit(*args, **kwargs)


@error_handler.catch
async def messages_send(api, *args, **kwargs):
    return await api.messages.send(*args, **kwargs)


@error_handler.catch
async def messages_delete(api, *args, **kwargs):
    return await api.messages.delete(*args, **kwargs)


@error_handler.catch
async def messages_send_message_event_answer(api, *args, **kwargs):
    return await api.messages.send_message_event_answer(*args, **kwargs)
