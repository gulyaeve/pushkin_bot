import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp, Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from logging import log, INFO, WARN

from aiogram_inline_paginations.paginator import Paginator

from config import Config
from filters import ManagerCheck
from keyboards.manager import main_manager_menu, ManagerCallbacks, make_driver_menu
from loader import dp, users, drivers, orders


async def copy_to_managers(message: types.Message):
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Ответить", callback_data=f'reply_from_anytext_id={message.from_user.id}')]])
    manager_user_type = await users.select_user_type("manager")
    managers = await users.select_users_by_type(manager_user_type)
    admin_user_type = await users.select_user_type("admin")
    admins = await users.select_users_by_type(admin_user_type)
    managers.extend(admins)
    for manager in managers:
        try:
            await dp.bot.copy_message(manager.telegram_id,
                                      message.chat.id,
                                      message.message_id,
                                      "Сообщение от пользователя",
                                      reply_markup=inline_keyboard)
        except Exception as e:
            log(WARN, f"Failed to send to [{manager}] {e}")


@dp.callback_query_handler(Regexp('reply_from_anytext_id=([0-9]*)'))
async def answer_to_text(callback: types.CallbackQuery, state: FSMContext):
    reply_user_id = callback.data.split("=")[1]
    async with state.proxy() as data:
        data["reply_user_id"] = reply_user_id
    await callback.message.answer(f"Введите ответ:")
    await state.set_state("ANSWER_TO_ANY_TEXT")


@dp.message_handler(state="ANSWER_TO_ANY_TEXT", content_types=types.ContentType.ANY)
async def send_answer_to_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        await dp.bot.copy_message(data['reply_user_id'], message.from_id, message.message_id)
        log(INFO, f'Пользователю [{data["reply_user_id"]=}] отправлено: {message.message_id}')
        await message.answer('Сообщение отправлено')
    except Exception as e:
        await message.answer('Ошибка при отправке')
        log(INFO, f"Failed to send message: {e}")
    await state.finish()


@dp.message_handler(ManagerCheck(), commands=['manager', 'manage'])
async def open_manager_menu(message: types.Message):
    await message.answer(
        text="Меню менеджера",
        reply_markup=main_manager_menu,
    )


@dp.callback_query_handler(Text(startswith='driverspage_'))
@dp.callback_query_handler(ManagerCheck(), text=ManagerCallbacks.manage_drivers)
async def manager_driver_menu(callback: types.CallbackQuery):
    await callback.answer("Выгружаю")
    page_n = 0
    if callback.data.startswith("driverspage_"):
        page_n = int(callback.data.split("_")[1])
    drivers_list = await drivers.select_all_drivers()
    buttons_drivers = types.InlineKeyboardMarkup()
    for driver in drivers_list:
        buttons_drivers.add(driver.make_button())
    drivers_inline = Paginator(callback_startswith="driverspage_", data=buttons_drivers)
    await callback.message.edit_text("Готово:", reply_markup=drivers_inline(current_page=page_n))


@dp.callback_query_handler(Text(startswith=ManagerCallbacks.manage_driver_info))
async def manager_select_driver(callback: types.CallbackQuery):
    driver_id = int(callback.data.split("=")[1])
    driver = await drivers.get_driver_info(driver_id)
    await callback.message.edit_text(str(driver), reply_markup=make_driver_menu(driver.telegram_id))


@dp.callback_query_handler(Text(startswith=ManagerCallbacks.manage_driver_docs))
async def manager_get_driver_docs(callback: types.CallbackQuery):
    await callback.message.delete()
    driver_id = int(callback.data.split("=")[1])
    driver = await drivers.get_driver_info(driver_id)
    await callback.message.answer_media_group(
        media=types.MediaGroup(
            [
                types.InputMediaPhoto(
                    types.InputFile(f"{Config.MEDIA}/{driver.passport_photo}")
                ),
                types.InputMediaPhoto(
                    types.InputFile(f"{Config.MEDIA}/{driver.sts_photo_1}")
                ),
                types.InputMediaPhoto(
                    types.InputFile(f"{Config.MEDIA}/{driver.sts_photo_2}")
                ),
            ]
        ),
    )
    await callback.message.answer(str(driver), reply_markup=make_driver_menu(driver.telegram_id))


@dp.callback_query_handler(Text(startswith=ManagerCallbacks.manage_driver_remove))
async def manager_driver_remove(callback: types.CallbackQuery):
    driver_id = int(callback.data.split("=")[1])
    driver = await drivers.get_driver_info(driver_id)
    active_order = await orders.find_active_order_for_driver(driver.telegram_id)
    if not active_order:
        await orders.remove_driver_from_orders(driver.telegram_id)
        user_user_type = await users.select_user_type("user")
        await users.update_user_type(user_user_type, driver.telegram_id)
        await drivers.remove_driver(driver.telegram_id)
        await callback.answer(f"{str(driver)}\n\nЗАБЛОКИРОВАН", show_alert=True)
        logging.info(f"{callback.from_user.id} удалил водителя {driver.telegram_id}")
    else:
        await callback.answer("У этого водителя есть активный заказ", show_alert=True)
