import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from config import Config
from utils.db_api.drivers_db import DriversDB
from utils.db_api.taxi_fares import TaxiFaresDB
from utils.db_api.usersdb import UsersDB
from utils.db_api.messages import Messages
from utils.admin_page_rest_api import AdminPageRestAPI
from utils.openroute_api import OpenrouteApi

# ChatBot objects
if Config.proxy_url:
    bot = Bot(
        token=Config.telegram_token,
        parse_mode=types.ParseMode.HTML,
        proxy=Config.proxy_url,
    )
else:
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
# db = Database()
# Users from database
users = UsersDB()
# Messages from database
messages = Messages()

# REST_API for admin application
loop = asyncio.get_event_loop()
bot_info: types.User = loop.run_until_complete(dp.bot.get_me())
if Config.rest_link:
    admin_api = AdminPageRestAPI(bot_info.to_python())
else:
    admin_api = None

openroute_api = OpenrouteApi()
taxi_fares = TaxiFaresDB()
drivers = DriversDB()

# Logging setup
logging.basicConfig(
    handlers=(logging.FileHandler('logs/log.txt'), logging.StreamHandler()),
    format=u'%(asctime)s %(filename)s [LINE:%(lineno)d] #%(levelname)-15s %(message)s',
    level=logging.INFO,
)
