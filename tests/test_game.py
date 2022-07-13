import os
from unittest import IsolatedAsyncioTestCase, skip
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from types import SimpleNamespace
import vkbottle.api.api  # type: ignore

_api = AsyncMock(name="vkbottle_VK_API", spec=vkbottle.api.api.API)
_api.users.get.side_effect = lambda user_ids: [
    SimpleNamespace(id=user_ids, first_name="Тестовый", last_name="Юзер"),
]

session = AsyncMock()
session.add.return_value = MagicMock()


@patch("sqlalchemy.create_engine")
def _sc(peer_id, s, p):
    from db.models import VKChats

    m = AsyncMock()
    m.return_value = Mock()
    m.scalars.first.return_value = VKChats(peer_id=peer_id)
    return m


@patch("sqlalchemy.create_engine")
def _su(user_id, s, p):
    from db.models import VKUsers

    m = AsyncMock()
    m.return_value = Mock()
    m.scalars.first.return_value = VKUsers(user_id=user_id, nickname="Тестовый Юзер")
    return m


@patch("services.chats._select_chat", AsyncMock(side_effect=_sc))
@patch("services.users._select_user", AsyncMock(side_effect=_su))
@patch("vkbottle.api.api.API", _api)
@skip("Запарился с моками и патчами, не дописал до конца, может позже")
class TestGame(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        dburl = "sqlite+aiosqlite:///:memory:"
        os.environ["dburl"] = dburl
        os.environ["TOKEN"] = "test"
        import config
        import importlib

        importlib.reload(config)
        assert config.dburl == dburl
        assert config.TOKEN == "test"

    @classmethod
    def tearDownClass(cls):
        del os.environ["dburl"]
        del os.environ["TOKEN"]

    async def test_get_or_create_chat(self, *args, **kwargs):
        from pprint import pprint

        pprint("args", args)
        pprint("kwargs", kwargs)
        from services import chats  # type: ignore

        the_chat = await chats.get_or_create_chat(2000000001, session)
        self.assertEqual(the_chat.peer_id, 2000000001)

    async def test_get_or_create_user(self, *args, **kwargs):
        from services import users  # type: ignore

        the_user = await users.get_or_create_user(1, _api, session)
        self.assertEqual(the_user.user_id, 1)
        self.assertEqual(the_user.nickname, "Первый Юзер")

        the_new_user = await users.get_or_create_user(5, _api, session)
        self.assertEqual(the_new_user.user_id, 5)
        self.assertEqual(the_new_user.nickname, "Пятый Юзер")

    async def test_start_recruitment(self, *args, **kwargs):
        from services.chats import get_or_create_chat  # type: ignore
        import errors

        the_chat = await get_or_create_chat(2000000001, session)
        await the_chat.start_recruitment(session)
        self.assertTrue(the_chat.is_recruitment_of_new_players)
        self.assertFalse(the_chat.is_active_game)

        with self.assertRaises(errors.RecruitmentOlreadyStarted):
            the_chat = await get_or_create_chat(2000000001, session)
            await the_chat.start_recruitment(session)

    async def test_stop_recruitment(self, *args, **kwargs):
        from services.chats import get_or_create_chat  # type: ignore

        the_chat = await get_or_create_chat(2000000001, session)
        await the_chat.stop_recruitment(session)
        self.assertFalse(the_chat.is_recruitment_of_new_players)
        self.assertFalse(the_chat.is_active_game)

    async def test_start_game(self, *args, **kwargs):
        from services.chats import get_or_create_chat  # type: ignore
        from services.users import get_or_create_user  # type: ignore
        import errors

        the_chat = await get_or_create_chat(2000000001, session)
        with self.assertRaises(errors.NotEnoughParticipants):
            await the_chat.start_game(session)
        self.assertFalse(the_chat.is_recruitment_of_new_players)
        self.assertFalse(the_chat.is_active_game)

        for uid in range(1, 3):
            the_chat.users.append(await get_or_create_user(uid))
        self.assertEqual(len(the_chat.users), 2)
        await session.commit()
        the_chat = await get_or_create_chat(2000000001, session)
        await the_chat.start_game(session)
        await session.commit()
        self.assertFalse(the_chat.is_recruitment_of_new_players)
        self.assertTrue(the_chat.is_active_game)
        self.assertEqual(len(the_chat.users), 2)

        with self.assertRaises(errors.GameOlreadyStarted):
            the_chat = await get_or_create_chat(2000000001, session)
            await the_chat.start_game(session)

    async def test_stop_game(self, *args, **kwargs):
        from services.chats import get_or_create_chat  # type: ignore
        from services.users import get_or_create_user  # type: ignore
        import errors

        the_chat = await get_or_create_chat(2000000001, session)
        for uid in range(1, 3):
            the_chat.users.append(await get_or_create_user(uid))
        await session.commit()
        the_chat = await get_or_create_chat(2000000001, session)
        await the_chat.start_game(session)
        the_chat = await get_or_create_chat(2000000001, session)
        await the_chat.stop_game(session)
        await session.commit()
        self.assertFalse(the_chat.is_active_game)
        with self.assertRaises(errors.GameNotStarted):
            await the_chat.stop_game(session)


if __name__ == "__main__":
    import unittest

    unittest.main()
