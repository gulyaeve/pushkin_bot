from aiogram import types

from filters import DriverCheck
from loader import dp


@dp.message_handler(DriverCheck(), commands=['driver'])
async def driver_start(message: types.Message):
    await message.answer("Вы водитель")


@dp.message_handler(commands=['driver'])
async def driver_start_no_auth(message: types.Message):
    await message.answer("Необходимо пройти регистрацию")
