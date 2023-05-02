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
from loader import dp, users, drivers, orders, taxi_fares, osm_api


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


@dp.callback_query_handler(ManagerCheck(), text=ManagerCallbacks.manage_menu)
async def open_manager_menu_callback(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text="Меню менеджера",
        reply_markup=main_manager_menu,
    )


@dp.callback_query_handler(Text(startswith='driverspage_'))
@dp.callback_query_handler(ManagerCheck(), text=ManagerCallbacks.manage_drivers)
async def manager_driver_menu(callback: types.CallbackQuery):
    await callback.answer("Выгружаю")
    try:
        page_n = 0
        if callback.data.startswith("driverspage_"):
            page_n = int(callback.data.split("_")[1])
        drivers_list = await drivers.select_all_drivers()
        buttons_drivers = types.InlineKeyboardMarkup()
        for driver in drivers_list:
            buttons_drivers.add(driver.make_button())
        buttons_drivers.add(InlineKeyboardButton("◀️Назад", callback_data=ManagerCallbacks.manage_menu))
        drivers_inline = Paginator(callback_startswith="driverspage_", data=buttons_drivers)
        await callback.message.edit_text("Готово:", reply_markup=drivers_inline(current_page=page_n))
    except IndexError:
        await callback.answer("Пусто", show_alert=True)


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


@dp.callback_query_handler(Text(startswith='ordersdates_'))
@dp.callback_query_handler(ManagerCheck(), text=ManagerCallbacks.manage_orders)
async def manager_get_dates(callback: types.CallbackQuery):
    await callback.answer("Выгружаю")
    try:
        page_n = 0
        if callback.data.startswith("ordersdates_"):
            page_n = int(callback.data.split("_")[1])
        orders_dates = await orders.select_all_dates_created()
        buttons_orders_dates = types.InlineKeyboardMarkup()
        for date in orders_dates:
            buttons_orders_dates.add(orders.make_inline_button_for_date(date))
        buttons_orders_dates.add(InlineKeyboardButton("◀️Назад", callback_data=ManagerCallbacks.manage_menu))
        orders_inline = Paginator(callback_startswith="ordersdates_", data=buttons_orders_dates)
        await callback.message.edit_text("Выберите день:", reply_markup=orders_inline(current_page=page_n))
    except IndexError:
        await callback.answer("Пусто", show_alert=True)


@dp.callback_query_handler(Text(startswith='orderspage_'))
@dp.callback_query_handler(ManagerCheck(), Text(startswith=ManagerCallbacks.manage_order_dates))
async def manager_get_orders(callback: types.CallbackQuery):
    date = callback.data.split("=")[1]
    await callback.answer("Выгружаю")
    try:
        page_n = 0
        if callback.data.startswith("orderspage_"):
            page_n = int(callback.data.split("_")[1])
        orders_list = await orders.select_orders_by_date_created(date)
        buttons_orders = types.InlineKeyboardMarkup()
        for order in orders_list:
            buttons_orders.add(order.make_button())
        buttons_orders.add(InlineKeyboardButton("◀️Назад", callback_data=ManagerCallbacks.manage_orders))
        orders_inline = Paginator(callback_startswith="orderspage_", data=buttons_orders)
        await callback.message.edit_text("Готово:", reply_markup=orders_inline(current_page=page_n))
    except IndexError:
        await callback.answer("Пусто", show_alert=True)


@dp.callback_query_handler(Text(startswith=ManagerCallbacks.manage_order_info))
async def manager_get_order_info(callback: types.CallbackQuery):
    order_id = int(callback.data.split("=")[1])
    order = await orders.get_order_info(order_id)
    taxi_fare = await taxi_fares.select_fare_by_id(order.fare)
    driver = await drivers.get_driver_info(order.driver_id)
    msg = f"{str(order)}\nТариф: <i>{taxi_fare.name}</i>"
    if driver:
        msg += f"\nФИО водителя: <i>{driver.fio}</i>"
    buttons_back = types.InlineKeyboardMarkup()
    if order.driver_id:
        buttons_back.add(InlineKeyboardButton("Водитель", f"tg://user?id={order.driver_id}"))
    buttons_back.add(InlineKeyboardButton("Пассажир", f"tg://user?id={order.customer_id}"))
    buttons_back.add(InlineKeyboardButton("◀️Назад", callback_data=ManagerCallbacks.manage_orders))
    address_departure = await osm_api.get_address(order.departure_latitude, order.departure_longitude)
    address_destination = await osm_api.get_address(order.destination_latitude, order.destination_longitude)
    await callback.message.answer(f"<b>Заказ №{order.id}. Старт</b> 🚩:\n<i>{address_departure}:</i>")
    await callback.message.answer_location(order.departure_latitude, order.departure_longitude)
    await callback.message.answer(f"<b>Заказ №{order.id}. Финиш</b> 🏁:\n<i>{address_destination}:</i>")
    await callback.message.answer_location(order.destination_latitude, order.destination_longitude)
    await callback.message.answer(msg, reply_markup=buttons_back)

