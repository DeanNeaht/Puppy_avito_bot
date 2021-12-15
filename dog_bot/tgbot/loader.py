from aiogram import Bot
import environs
from aiogram.types import ParseMode

env = environs.Env()
env.read_env()

bot = Bot(env.str('BOT_TOKEN'), parse_mode=ParseMode.HTML)
