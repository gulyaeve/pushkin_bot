import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from config import Config
from utils.db_api.db import Database
from utils.db_api.usersdb import UsersDB
from utils.db_api.messages import Messages
from utils.rest_api import AdminPageRestAPI

# ChatBot objects
bot = Bot(
    token=Config.telegram_token,
    parse_mode=types.ParseMode.HTML,
)
storage = RedisStorage2(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
)
dp = Dispatcher(
    bot=bot,
    storage=storage,
)

# Database objects
db = Database()
# Users from database
users = UsersDB()
# Messages from database
messages = Messages()

# REST_API for admin application
loop = asyncio.get_event_loop()
bot_info: types.User = loop.run_until_complete(dp.bot.get_me())
admin_api = AdminPageRestAPI(bot_info.to_python())

# Logging setup
logging.basicConfig(
    handlers=(logging.FileHandler('logs/log.txt'), logging.StreamHandler()),
    format=u'%(asctime)s %(filename)s [LINE:%(lineno)d] #%(levelname)-15s %(message)s',
    level=logging.INFO,
)
