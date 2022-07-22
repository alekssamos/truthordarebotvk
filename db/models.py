from typing import Any, List, Tuple, Optional
from loguru import logger
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # type: ignore


def _get_pairs(players):
    from services.game import make_pairs_of_players as make  # type: ignore

    return make(players, False) + make(players, True)


class VKUsers(Base):  # type: ignore
    __tablename__ = "vkusers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    peer_id = Column(BigInteger, ForeignKey("vkchats.peer_id"))
    nickname = Column(String(55))
    dch = Column(Boolean, default=False)
    gg = Column(Boolean, default=False)
    ul = Column(Boolean, default=False)
    chats = relationship("VKChats", backref="users")  # type: ignore

    @property
    def is_field_in(self) -> bool:
        return self.dch or self.gg or self.ul or False  # type: ignore

    @property
    def mention(self) -> str:
        import strings

        nickname = self.nickname  # type: ignore
        for s in "[]()@|\r\n":
            nickname = nickname.replace(s, "")
        append_str = ""
        if self.dch:
            append_str = append_str + " Дч "
        if self.gg:
            append_str = append_str + " Гг "
        if self.ul:
            append_str = append_str + " Ул "
        if not self.is_field_in:
            append_str = strings.ru.the_questionnaire_is_not_filled_in
        return f"[id{self.user_id}|{nickname}] ({append_str})"

    def __repr__(self):
        return f"<VKUser with user_id={self.user_id}>"


class VKChats(Base):  # type: ignore
    __tablename__ = "vkchats"
    id = Column(Integer, primary_key=True)
    peer_id = Column(BigInteger, unique=True)
    is_recruitment_of_new_players = Column(Boolean, default=False)
    is_active_game = Column(Boolean, default=False)
    combination_current_index = Column(Integer, default=-1)
    last_message_id = Column(Integer, default=0)
    last_selection = Column(String(9), default="")

    async def start_recruitment(self, session: Any) -> None:
        "Запускает набор участников в новую игру"
        logger.info("start recruitment...")
        return await self._set_status_recruitment(True, session)

    async def stop_recruitment(self, session: Any) -> None:
        "Прекращает набор участников в игру"
        logger.info("stop recruitment...")
        return await self._set_status_recruitment(False, session)

    async def _set_status_recruitment(self, status: bool, session: Any) -> None:
        from db import async_session
        from errors import RecruitmentOlreadyStarted, GameOlreadyStarted, GameNotStarted

        if self.is_active_game and status:
            raise GameOlreadyStarted(
                "Recruitment of participants is not possible during the game",
                peer_id=self.peer_id,
            )  # type: ignore
        if self.is_recruitment_of_new_players and status:
            raise RecruitmentOlreadyStarted(
                "Recruitment of participants is olready started", peer_id=self.peer_id
            )  # type: ignore
        if status:
            self.users.clear()
        logger.info("setting...")
        self.is_recruitment_of_new_players = status  # type: ignore
        await session.commit()

    async def start_game(self, session: Optional[Any] = None) -> None:
        "Начинает игру"
        logger.info("Start game olready with players")
        return await self._set_status_game(True, session)

    async def stop_game(self, session: Optional[Any]):
        "Завершает игру"
        logger.info("Stop game")
        return await self._set_status_game(False, session)

    async def _set_status_game(self, status: bool, session: Any) -> None:
        from db import async_session
        from errors import GameOlreadyStarted, GameNotStarted, NotEnoughParticipants

        logger.info("Start or stop game")
        if status:
            if self.is_active_game:
                raise GameOlreadyStarted(
                    "The game has already started", peer_id=self.peer_id
                )  # type: ignore
            if len(self.users) < 2:
                self.users.clear()
                await session.commit()
                raise NotEnoughParticipants(
                    "not enough participants", peer_id=self.peer_id
                )  # type: ignore
            if self.is_recruitment_of_new_players:
                await self.stop_recruitment(session)
        else:
            if not self.is_active_game:
                raise GameNotStarted(
                    "The game has already been stopped", peer_id=self.peer_id
                )  # type: ignore
        self.is_active_game = status  # type: ignore
        self.combination_current_index = -1  # type: ignore
        self.last_message_id = 0  # type: ignore
        self.last_selection = ""  # type: ignore
        await session.commit()

    async def get_current_combination(self) -> Optional[Tuple[Any, Any]]:
        from errors import GameNotStarted  # type: ignore

        logger.info(f"get current pair: i={self.combination_current_index}")
        if not self.is_active_game:
            raise GameNotStarted(
                "The action can only be performed during the game", peer_id=self.peer_id
            )  # type: ignore
        pairs = _get_pairs(self.users)
        i = self.combination_current_index
        if i >= len(pairs) or i < 0:
            logger.debug(f"i={i}")
            return None  # type: ignore
        return pairs[i]  # type: ignore

    async def take_pair(self, session: Any) -> Optional[Tuple[Any, Any]]:
        from db import async_session  # type: ignore
        from errors import GameNotStarted  # type: ignore

        logger.info("Take new pair")
        if not self.is_active_game:
            raise GameNotStarted(
                "The action can only be performed during the game", peer_id=self.peer_id
            )  # type: ignore
            return None  # type: ignore
        pairs = _get_pairs(self.users)
        self.combination_current_index += 1  # type: ignore
        self.last_message_id = 0  # type: ignore
        self.last_selection = ""  # type: ignore
        if self.combination_current_index >= len(pairs):
            logger.debug("We've reached the end of the game!")
            self.combination_current_index -= 1  # type: ignore
            await session.commit()
            return None  # type: ignore
        await session.commit()
        logger.debug("i={}, len={}".format(self.combination_current_index, len(pairs)))
        pair = pairs[self.combination_current_index]
        logger.debug(pair)
        return pair  # type: ignore

    def __repr__(self):
        return f"<VKChat with peer_id={self.peer_id}>"
