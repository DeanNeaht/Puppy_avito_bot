from aiogram import Dispatcher
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message, ChatType, ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.dispatcher.filters import Text

from db.models import Users


async def user_start(m: Message, session: AsyncSession):
    await session.merge(Users(user_id=m.from_user.id, full_name=m.from_user.full_name, username=m.from_user.username))
    await session.commit()
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text='Отписаться'))
    await m.answer('Вы теперь подписаны на собэк! Чтобы отписаться нажмите кнопку ниже.', reply_markup=kb)


async def stop_mailing(m: Message, session: AsyncSession):
    user: Users = await session.get(Users, m.from_user.id)
    user.is_send = False
    await session.commit()
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text='Подписаться'))
    await m.answer('Вы отписались от собэк((( Если захотите вернуться,нажмите кнопку ниже.', reply_markup=kb)


async def start_mailing(m: Message, session: AsyncSession):
    user: Users = await session.get(Users, m.from_user.id)
    user.is_send = False
    await session.commit()
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text='Отписаться'))
    await m.answer('Ура! Ты вернулся, скоро ты получишь новых собэк!', reply_markup=kb)


def register_reg_user(dp: Dispatcher):
    dp.register_message_handler(user_start, ChatTypeFilter(ChatType.PRIVATE), commands=["start"])
    dp.register_message_handler(stop_mailing, ChatTypeFilter(ChatType.PRIVATE), Text(equals='Отписаться'))
    dp.register_message_handler(start_mailing, ChatTypeFilter(ChatType.PRIVATE), Text(equals='Подписаться'))
