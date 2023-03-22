from aiogram import types

from loader import dp


@dp.message_handler(commands=['taxi'])
async def start_taxi(message: types.Message):
    await message.answer("Укажи координаты начала пути")

