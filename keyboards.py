import strings
from vkbottle import Keyboard, KeyboardButtonColor, Text, Callback  # type: ignore

EMPTY = Keyboard(one_time=False)
EMPTY_INLINE = Keyboard(one_time=False, inline=True)

GAME_JOIN = (
    Keyboard(one_time=False, inline=False)
    .add(
        Text(strings.ru.i_want_to_play, payload={"cmd": "implay"}),
        color=KeyboardButtonColor.POSITIVE,
    )
    .get_json()
)

GAME_CONTINUE = (
    Keyboard(one_time=False, inline=True)
    .add(Callback(strings.ru.continue_game, payload={"cmd": "continue"}))
    .get_json()
)

TOA_SELECT = (
    Keyboard(one_time=False, inline=True)
    .add(Callback(strings.ru.truth, payload={"cmd": "truth"}))
    .row()
    .add(Callback(strings.ru.action, payload={"cmd": "action"}))
    .get_json()
)
