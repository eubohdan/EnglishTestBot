import logging
import redis
import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from create_bot import bot, redis
from config_reader import config
import test
import commands
import database as db


async def on_start() -> None:
    await bot.send_message(config.admin_id, '✅The bot has been launched.', disable_notification=True)
    for unit in range(4):
        for k, v in db.get_questions(unit).items():
            name = 100 * unit + k
            await redis.hset(name=name, mapping=v)
        if not await redis.exists("answers"+str(unit)):
            answers = db.get_answers(str(unit))
            await redis.rpush("answers"+str(unit), *answers)
    photos = db.get_illustrations()
    for k, v in photos.items():
        await redis.set(name=f"photo{k}", value=v)
    users_answers = db.get_users_answers()
    for user in users_answers:
        for k, v in enumerate(user[1:]):
            if v is not None:
                await redis.set(name=f"{user[0]}:res{k}", value=v)
    await redis.close()


async def on_finish() -> None:
    await bot.send_message(config.admin_id, '⚠The bot has been stopped.', disable_notification=True)
    await redis.close()


dp = Dispatcher(storage=RedisStorage(redis=redis))
dp.startup.register(on_start)
dp.shutdown.register(on_finish)


async def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")
    db.start_db()
    await dp.start_polling(bot)


test.register(dp)
commands.register(dp)


if __name__ == "__main__":
    asyncio.run(main())
