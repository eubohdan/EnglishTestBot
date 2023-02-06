from config_reader import config
from aiogram import Bot
import aioredis


bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
redis = aioredis.from_url("redis://localhost")

