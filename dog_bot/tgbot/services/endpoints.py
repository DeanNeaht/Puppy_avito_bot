import logging

from aiogram import types
from aiogram.utils.exceptions import BotBlocked, TelegramAPIError
from aiohttp import web
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from db.models import Users
from tgbot.config import Config, load_config
from tgbot.loader import bot


async def send_dogs_to_users(request):
    dog = await request.json()
    config: Config = load_config()
    engine = create_async_engine(
        f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.db_name}",
        future=True
    )
    db_pool = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    session = db_pool()
    users = await session.execute(select(Users).where(Users.is_send == True))
    users_id = [x[0].user_id for x in users.fetchall()]
    kb = types.InlineKeyboardMarkup()
    bt = types.InlineKeyboardButton(text='Ссылка', url=dog.get('item_url'))
    kb.add(bt)
    for user in users_id:
        try:
            await bot.send_photo(chat_id=user, photo=dog.get('photo_url'),
                                 caption=f'<b>{dog.get("name")}</b>\n\nЦена: <b>{dog.get("price")}</b>\n\n{dog.get("description")}',
                                 reply_markup=kb,
                                 parse_mode=types.ParseMode.HTML)
        except BotBlocked:
            pass
        except TelegramAPIError as ex:
            logging.info('TelegramApiError %r', ex)
    await session.close()
    return web.Response(text='Hello Aiohttp!')

