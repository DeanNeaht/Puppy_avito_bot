import asyncio
import logging
import gspread_asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher.webhook import configure_app
from aiogram.types import ParseMode, BotCommand, BotCommandScopeChat
from aiogram.utils.exceptions import ChatNotFound
from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from tgbot.loader import bot
from tgbot.services.endpoints import send_dogs_to_users
from db.models import Base
from tgbot.config import load_config, Config
from tgbot.handlers.users.user_command import register_reg_user
from tgbot.middlewares.db import DbSessionMiddleware


logger = logging.getLogger(__name__)


async def register_filters_and_middlewares(dp: Dispatcher, session: sessionmaker):
    dp.middleware.setup(DbSessionMiddleware(session))


def get_handled_updates_list(dp: Dispatcher) -> list:

    available_updates = (
        "message_handlers",
    )
    return [item.replace("_handlers", "") for item in available_updates
            if len(dp.__getattribute__(item).handlers) > 0]


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")
    config: Config = load_config()

    engine = create_async_engine(
        f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.db_name}",
        future=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db_pool = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    dp = Dispatcher(bot, storage=MemoryStorage())

    await register_filters_and_middlewares(dp, db_pool)
    register_reg_user(dp)

    app = web.Application()
    app.add_routes([web.post('/dogs/', send_dogs_to_users)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, config.bot.ip, config.bot.port)

    tasks = [
        site.start(),  # отдельно aiohttp
        dp.start_polling()  # aiogram
    ]

    await asyncio.gather(*tasks)

asyncio.run(main())
