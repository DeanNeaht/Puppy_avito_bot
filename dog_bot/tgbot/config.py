from dataclasses import dataclass
from environs import Env


@dataclass
class Bot:
    token: str
    ip: str
    port: int


@dataclass
class DB:
    host: str
    db_name: str
    user: str
    password: str


@dataclass
class Config:
    bot: Bot
    db: DB


def load_config():
    env = Env()
    env.read_env()

    return Config(
        bot=Bot(token=env.str("BOT_TOKEN"),
                ip=env.str("IP"),
                port=env.int('PORT')),
        db=DB(
            host=env.str("DB_HOST"),
            db_name=env.str("DB_NAME"),
            user=env.str("DB_USER"),
            password=env.str("DB_PASS")
        )
    )
