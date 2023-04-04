import logging

from aiogram import types
from aiogram.dispatcher.filters import Text

from filters import ManagerCheck, AdminCheck
from keyboards.driver import DriverCallbacks
from loader import dp, drivers, messages, users


# @dp.callback_query_handler(Text(startswith=DriverCallbacks.driver_manager_decline), ManagerCheck())
@dp.callback_query_handler(Text(startswith=DriverCallbacks.driver_manager_decline), ManagerCheck(), AdminCheck())
async def manager_driver_decline(callback: types.CallbackQuery):
    driver_id = int(callback.data.split("=")[1])
    driver = await drivers.get_driver_info(driver_id)
    await drivers.remove_driver(driver_id)
    await dp.bot.send_message(
        chat_id=driver_id,
        text=(await messages.get_message("driver_manager_decline")),
    )
    logging.info(f"Водитель {driver_id} отклонен менеджером {callback.from_user.id}")
    await callback.answer(f"Вы отклонили водителя {driver.fio}", show_alert=True)
    await callback.message.delete()


@dp.callback_query_handler(Text(startswith=DriverCallbacks.driver_manager_agree), ManagerCheck(), AdminCheck())
async def manager_driver_accept(callback: types.CallbackQuery):
    driver_id = int(callback.data.split("=")[1])
    driver = await drivers.get_driver_info(driver_id)
    driver_user_type = await users.select_user_type("driver")
    await users.update_user_type(driver_user_type, driver_id)
    await dp.bot.send_message(
        chat_id=driver_id,
        text=(await messages.get_message("driver_manager_accept")),
    )
    logging.info(f"Водитель {driver_id} назначен менеджером {callback.from_user.id}")
    await callback.answer(f"Вы назначили водителя {driver.fio}", show_alert=True)
    await callback.message.delete()
