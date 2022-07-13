import os
import unittest
import loguru
import sys

loguru.logger.remove()
loguru.logger.add(
    sys.stderr, format="\n{name}:{function}:{line} {level} {message}", level="DEBUG"
)


class apiStub:
    class users:
        @staticmethod
        async def get(*args, **kwargs):
            import types

            return [
                types.SimpleNamespace(id=5, first_name="Пятый", last_name="Юзер"),
            ]


class TestGameIntegrational(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        loguru.logger.debug("*" * 76)

    @classmethod
    def setUpClass(cls):
        loguru.logger.debug("*" * 76)
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
        loguru.logger.debug("*" * 76)
        del os.environ["dburl"]
        del os.environ["TOKEN"]

    async def asyncSetUp(self):
        loguru.logger.debug("*" * 76)
        from db import async_session, drop_db, create_db
        from db.models import VKUsers, VKChats

        await drop_db()
        await create_db()
        async with async_session() as session:
            session.add_all([VKChats(peer_id=2000000001), VKChats(peer_id=2000000002)])

            session.add_all(
                [
                    VKUsers(user_id=1, nickname="Первый Юзер"),
                    VKUsers(user_id=2, nickname="Второй Юзер"),
                    VKUsers(user_id=3, nickname="Третий юзер"),
                    VKUsers(user_id=4, nickname="Четвёртый юзер"),
                ]
            )

            await session.commit()

    async def asyncTearDown(self):
        loguru.logger.debug("*" * 76)

    def tearDown(self):
        loguru.logger.debug("*" * 76)

    async def test_get_or_create_chat(self):
        from services import chats  # type: ignore
        from db import async_session

        async with async_session() as session:
            the_chat = await chats.get_or_create_chat(2000000001, session)
        self.assertEqual(the_chat.peer_id, 2000000001)

    async def test_get_or_create_user(self):
        from services import users  # type: ignore
        from db import async_session

        async with async_session() as session:
            the_user = await users.get_or_create_user(1, apiStub, session)
        self.assertEqual(the_user.user_id, 1)
        self.assertEqual(the_user.nickname, "Первый Юзер")

        async with async_session() as session:
            the_new_user = await users.get_or_create_user(5, apiStub, session)
        self.assertEqual(the_new_user.user_id, 5)
        self.assertEqual(the_new_user.nickname, "Пятый Юзер")

    async def test_start_recruitment(self):
        from services.chats import get_or_create_chat  # type: ignore
        from db import async_session
        import errors

        async with async_session() as session:
            the_chat = await get_or_create_chat(2000000001, session)
            await the_chat.start_recruitment(session)
            self.assertTrue(the_chat.is_recruitment_of_new_players)
            self.assertFalse(the_chat.is_active_game)

            with self.assertRaises(errors.RecruitmentOlreadyStarted):
                the_chat = await get_or_create_chat(2000000001, session)
                await the_chat.start_recruitment(session)

    async def test_stop_recruitment(self):
        from services.chats import get_or_create_chat  # type: ignore
        from db import async_session

        async with async_session() as session:
            the_chat = await get_or_create_chat(2000000001, session)
            await the_chat.stop_recruitment(session)
            self.assertFalse(the_chat.is_recruitment_of_new_players)
            self.assertFalse(the_chat.is_active_game)

    async def test_start_game(self):
        from services.chats import get_or_create_chat  # type: ignore
        from services.users import get_or_create_user  # type: ignore
        from db import async_session
        import errors

        async with async_session() as session:
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

    async def test_stop_game(self):
        from services.chats import get_or_create_chat  # type: ignore
        from db import async_session
        from services.users import get_or_create_user  # type: ignore
        import errors

        async with async_session() as session:
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
    unittest.main()
