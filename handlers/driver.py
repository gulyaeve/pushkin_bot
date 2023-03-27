from aiogram import types
from aiogram.dispatcher.filters import Text

from filters import DriverCheck
from keyboards.driver import reg_button, make_driver_reg_menu
from loader import dp, messages, drivers


@dp.message_handler(DriverCheck(), commands=['driver'])
async def driver_start(message: types.Message):
    await message.answer("Вы водитель")


@dp.message_handler(commands=['driver'])
async def driver_start_no_auth(message: types.Message):
    await message.answer(await messages.get_message("driver_reg_prompt"), reply_markup=reg_button)


@dp.callback_query_handler(Text(equals="reg_menu"))
async def driver_reg_menu(callback: types.CallbackQuery):
    new_driver = await drivers.add_driver(callback.from_user.id)
    menu = make_driver_reg_menu(
        fio=True if new_driver.fio else False,
        phone=True if new_driver.phone else False,
        passport=True if new_driver.passport else False,
        passport_photo=True if new_driver.passport_photo else False,
    )
    await callback.message.edit_text(await messages.get_message("driver_reg_menu"), reply_markup=menu)
