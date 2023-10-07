import asyncio
import json
import logging

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, BotCommand
from aiogram import F
import db_func
import config

bot_db = db_func.BotDB(r'C:\Users\Admin\Desktop\flowiki\flow_database.db')

TOKEN = config.API_TOKEN
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
# All handlers should be attached to the Router (or Dispatcher)
router = Router()


@router.message(Command('start'))
async def send_welcome(message: types.Message):
    if bot_db.user_exists(message.from_user.id):
        return await message.answer('hey i know you')
    await message.answer('dont know')
    
@router.message()
async def text(message: types.Message):
    await message.answer('text')
    



async def main() -> None:
    # Dispatcher is a root router
    dp = Dispatcher()
    # ... and all other routers should be attached to Dispatcher
    dp.include_router(router)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
