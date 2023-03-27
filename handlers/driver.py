from aiogram import types

from filters import DriverCheck
from loader import dp, messages


@dp.message_handler(DriverCheck(), commands=['driver'])
async def driver_start(message: types.Message):
    await message.answer("Вы водитель")


@dp.message_handler(commands=['driver'])
async def driver_start_no_auth(message: types.Message):
    reg_button = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Регистрация водителя",
                    callback_data="reg_menu",
                )
            ]
        ]
    )
    await message.answer(await messages.get_message("driver_reg_prompt"), reply_markup=reg_button)
