import asyncio
import logging

from loader import bot, dp
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands

from database import engine, Base


async def on_startup():
    await set_default_commands(bot)
    await on_startup_notify(bot)


async def main():
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


    logging.basicConfig(level=logging.INFO)
    middlewares.setup(dp)
    filters.setup(dp)
    handlers.setup(dp)

    await on_startup()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
