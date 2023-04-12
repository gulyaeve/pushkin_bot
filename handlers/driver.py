import datetime
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, ChatTypeFilter
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ChatType

from config import Config
from filters import DriverCheck
from keyboards.driver import reg_button, make_driver_reg_menu, DriverCallbacks, make_manager_view, driver_menu
from keyboards.keyboards import auth_phone
from loader import dp, messages, drivers, users, orders
from utils.db_api.orders_db import OrderStatuses


class DriverStates(StatesGroup):
    FIO = State()
    Phone = State()
    Passport = State()
    PassportPhoto = State()
    STSPhoto1 = State()
    STSPhoto2 = State()


@dp.message_handler(ChatTypeFilter(chat_type=ChatType.PRIVATE), DriverCheck(), commands=['driver'])
async def driver_start(message: types.Message):
    await message.answer(await messages.get_message("driver_menu"), reply_markup=driver_menu)


@dp.callback_query_handler(DriverCheck(), state=DriverStates.all_states)
@dp.callback_query_handler(DriverCheck(), text=[DriverCallbacks.driver_back, DriverCallbacks.driver_reg_menu])
async def driver_start(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text(await messages.get_message("driver_menu"), reply_markup=driver_menu)


@dp.message_handler(ChatTypeFilter(chat_type=ChatType.PRIVATE), commands=['driver'])
async def driver_start_no_auth(message: types.Message):
    await message.answer(await messages.get_message("driver_reg_prompt"), reply_markup=reg_button)


@dp.callback_query_handler(text=DriverCallbacks.driver_back)
async def driver_start_no_auth(callback: types.CallbackQuery):
    await callback.message.edit_text(await messages.get_message("driver_reg_prompt"), reply_markup=reg_button)


@dp.callback_query_handler(text=DriverCallbacks.driver_reg_menu)
async def driver_reg_menu(callback: types.CallbackQuery):
    driver = await drivers.add_driver(callback.from_user.id)
    menu = make_driver_reg_menu(
        fio=True if driver.fio else False,
        phone=True if driver.phone else False,
        passport=True if driver.passport else False,
        passport_photo=True if driver.passport_photo else False,
        sts_photo_1=True if driver.sts_photo_1 else False,
        sts_photo_2=True if driver.sts_photo_2 else False,
    )
    await callback.message.edit_text(await messages.get_message("driver_reg_menu"), reply_markup=menu)


@dp.callback_query_handler(text=DriverCallbacks.driver_fio)
async def driver_fio_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(await messages.get_message("driver_input_fio"))
    await DriverStates.FIO.set()


@dp.message_handler(state=DriverStates.FIO)
async def driver_input_fio(message: types.Message, state: FSMContext):
    if message.text:
        driver = await drivers.update_driver_info(message.from_user.id, fio=message.text)
        menu = make_driver_reg_menu(
            fio=True if driver.fio else False,
            phone=True if driver.phone else False,
            passport=True if driver.passport else False,
            passport_photo=True if driver.passport_photo else False,
            sts_photo_1=True if driver.sts_photo_1 else False,
            sts_photo_2=True if driver.sts_photo_2 else False,
        )
        await message.answer(await messages.get_message("driver_correct_input"))
        await message.answer(await messages.get_message("driver_reg_menu"), reply_markup=menu)
        await state.finish()
    else:
        return await message.answer(await messages.get_message("driver_wrong_input"))


@dp.callback_query_handler(text=DriverCallbacks.driver_phone)
async def driver_phone_menu(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(await messages.get_message("driver_input_phone"), reply_markup=auth_phone)
    await DriverStates.Phone.set()


@dp.message_handler(state=DriverStates.Phone, content_types=types.ContentType.CONTACT)
async def driver_input_phone(message: types.Message, state: FSMContext):
    if message.contact.user_id == message.from_user.id:
        phone_number = ''.join([n for n in message.contact.phone_number if n.isdigit()])
        driver = await drivers.update_driver_info(message.from_user.id, phone=phone_number)
        menu = make_driver_reg_menu(
            fio=True if driver.fio else False,
            phone=True if driver.phone else False,
            passport=True if driver.passport else False,
            passport_photo=True if driver.passport_photo else False,
            sts_photo_1=True if driver.sts_photo_1 else False,
            sts_photo_2=True if driver.sts_photo_2 else False,
        )
        await message.answer(
            await messages.get_message("driver_correct_input"),
            reply_markup=types.ReplyKeyboardRemove()
        )
        await message.answer(await messages.get_message("driver_reg_menu"), reply_markup=menu)
        await state.finish()
    else:
        return await message.answer(await messages.get_message("wrong_number"))


@dp.message_handler(state=DriverStates.Phone)
async def driver_input_phone(message: types.Message, state: FSMContext):
    if message.text:
        phone_number = ''.join([n for n in message.text if n.isdigit()])
        if len(phone_number) == 11:
            driver = await drivers.update_driver_info(message.from_user.id, phone=phone_number)
            menu = make_driver_reg_menu(
                fio=True if driver.fio else False,
                phone=True if driver.phone else False,
                passport=True if driver.passport else False,
                passport_photo=True if driver.passport_photo else False,
                sts_photo_1=True if driver.sts_photo_1 else False,
                sts_photo_2=True if driver.sts_photo_2 else False,
            )
            await message.answer(
                await messages.get_message("driver_correct_input"),
                reply_markup=types.ReplyKeyboardRemove()
            )
            await message.answer(await messages.get_message("driver_reg_menu"), reply_markup=menu)
            await state.finish()
        else:
            return await message.answer(await messages.get_message("wrong_number"))
    else:
        return await message.answer(await messages.get_message("wrong_number"))


@dp.callback_query_handler(text=DriverCallbacks.driver_passport)
async def driver_passport_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(await messages.get_message("driver_input_passport"))
    await DriverStates.Passport.set()


@dp.message_handler(state=DriverStates.Passport)
async def driver_input_passport(message: types.Message, state: FSMContext):
    if message.text:
        driver = await drivers.update_driver_info(message.from_user.id, passport=message.text)
        menu = make_driver_reg_menu(
            fio=True if driver.fio else False,
            phone=True if driver.phone else False,
            passport=True if driver.passport else False,
            passport_photo=True if driver.passport_photo else False,
            sts_photo_1=True if driver.sts_photo_1 else False,
            sts_photo_2=True if driver.sts_photo_2 else False,
        )
        await message.answer(await messages.get_message("driver_correct_input"))
        await message.answer(await messages.get_message("driver_reg_menu"), reply_markup=menu)
        await state.finish()
    else:
        return await message.answer(await messages.get_message("driver_wrong_input"))


@dp.callback_query_handler(text=DriverCallbacks.driver_passport_photo)
async def driver_passport_photo_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(await messages.get_message("driver_input_passport_photo"))
    await DriverStates.PassportPhoto.set()


@dp.message_handler(state=DriverStates.PassportPhoto, content_types=types.ContentType.PHOTO)
async def driver_input_passport_photo(message: types.Message, state: FSMContext):
    passport_path = f"passports/{message.from_user.id}.png"
    passport_destination = f"{Config.MEDIA}/{passport_path}"
    await message.photo[-1].download(destination_file=passport_destination)

    driver = await drivers.update_driver_info(message.from_user.id, passport_photo=passport_path)
    menu = make_driver_reg_menu(
        fio=True if driver.fio else False,
        phone=True if driver.phone else False,
        passport=True if driver.passport else False,
        passport_photo=True if driver.passport_photo else False,
        sts_photo_1=True if driver.sts_photo_1 else False,
        sts_photo_2=True if driver.sts_photo_2 else False,
    )
    await message.answer(await messages.get_message("driver_correct_input"))
    await message.answer(await messages.get_message("driver_reg_menu"), reply_markup=menu)
    await state.finish()


@dp.message_handler(state=DriverStates.PassportPhoto, content_types=types.ContentType.ANY)
async def driver_input_passport_photo(message: types.Message):
    return await message.answer(await messages.get_message("driver_wrong_photo"))


@dp.callback_query_handler(text=DriverCallbacks.driver_sts_1)
async def driver_passport_photo_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(await messages.get_message("driver_input_sts_photo_1"))
    await DriverStates.STSPhoto1.set()


@dp.callback_query_handler(text=DriverCallbacks.driver_sts_2)
async def driver_passport_photo_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(await messages.get_message("driver_input_sts_photo_2"))
    await DriverStates.STSPhoto2.set()


@dp.message_handler(state=DriverStates.STSPhoto1, content_types=types.ContentType.PHOTO)
async def driver_input_passport_photo(message: types.Message, state: FSMContext):
    sts_path = f"sts1/{message.from_user.id}.png"
    sts_destination = f"{Config.MEDIA}/{sts_path}"
    await message.photo[-1].download(destination_file=sts_destination)

    driver = await drivers.update_driver_info(message.from_user.id, sts_photo_1=sts_path)
    menu = make_driver_reg_menu(
        fio=True if driver.fio else False,
        phone=True if driver.phone else False,
        passport=True if driver.passport else False,
        passport_photo=True if driver.passport_photo else False,
        sts_photo_1=True if driver.sts_photo_1 else False,
        sts_photo_2=True if driver.sts_photo_2 else False,
    )
    await message.answer(await messages.get_message("driver_correct_input"))
    await message.answer(await messages.get_message("driver_reg_menu"), reply_markup=menu)
    await state.finish()


@dp.message_handler(state=DriverStates.STSPhoto2, content_types=types.ContentType.PHOTO)
async def driver_input_passport_photo(message: types.Message, state: FSMContext):
    sts_path = f"sts2/{message.from_user.id}.png"
    sts_destination = f"{Config.MEDIA}/{sts_path}"
    await message.photo[-1].download(destination_file=sts_destination)

    driver = await drivers.update_driver_info(message.from_user.id, sts_photo_2=sts_path)
    menu = make_driver_reg_menu(
        fio=True if driver.fio else False,
        phone=True if driver.phone else False,
        passport=True if driver.passport else False,
        passport_photo=True if driver.passport_photo else False,
        sts_photo_1=True if driver.sts_photo_1 else False,
        sts_photo_2=True if driver.sts_photo_2 else False,
    )
    await message.answer(await messages.get_message("driver_correct_input"))
    await message.answer(await messages.get_message("driver_reg_menu"), reply_markup=menu)
    await state.finish()


@dp.message_handler(state=DriverStates.STSPhoto1, content_types=types.ContentType.ANY)
@dp.message_handler(state=DriverStates.STSPhoto2, content_types=types.ContentType.ANY)
async def driver_input_passport_photo(message: types.Message):
    return await message.answer(await messages.get_message("driver_wrong_photo"))


@dp.callback_query_handler(text=DriverCallbacks.driver_ready)
async def driver_ready_menu(callback: types.CallbackQuery):
    driver = await drivers.get_driver_info(callback.from_user.id)
    if driver.validate_info():
        manager_user_type = await users.select_user_type("manager")
        admin_user_type = await users.select_user_type("admin")
        managers = await users.select_users_by_type(manager_user_type)
        admins = await users.select_users_by_type(admin_user_type)
        managers.extend(admins)
        for manager in managers:
            await dp.bot.send_media_group(
                chat_id=manager.telegram_id,
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
            await dp.bot.send_message(
                chat_id=manager.telegram_id,
                text=f"<b>Новая анкета:</b>\n{str(driver)}",
                reply_markup=make_manager_view(driver.telegram_id),
            )
        logging.info(f"Новая анкета водителя {driver}")
        await callback.answer(await messages.get_message("driver_info_validate_true"), show_alert=True)
        await callback.message.delete()
    else:
        answer = "Необходимо заполнить:\n"
        if not driver.fio:
            answer += "ФИО\n"
        if not driver.phone:
            answer += "Номер телефона\n"
        if not driver.passport:
            answer += "Паспортные данные\n"
        if not driver.passport_photo:
            answer += "Фото паспорта\n"
        if not driver.sts_photo_1:
            answer += "Фото СТС (лицевая сторона)\n"
        if not driver.sts_photo_2:
            answer += "Фото СТС (оборотная сторона)\n"
        await callback.answer(answer, show_alert=True)


@dp.callback_query_handler(DriverCheck(), Text(startswith=DriverCallbacks.driver_order_confirm))
async def driver_order_confirm(callback: types.CallbackQuery):
    driver = await drivers.get_driver_info(callback.from_user.id)
    order_id = int(callback.data.split("=")[1])
    order = await orders.get_order_info(order_id)
    changed_order = await orders.update_order_info(
        order.id,
        driver_id=driver.telegram_id,
        status=OrderStatuses.in_progress,
        time_assigned=datetime.datetime.now(),
    )
    logging.info(f"Заказ изменен {changed_order}")
    await callback.answer("Вы взяли заказ", show_alert=True)
    await dp.bot.send_message(
        chat_id=order.customer_id,
        text=f"Водитель {driver.fio} начал выполнение вашего заказа.",
    )
    await callback.message.delete_reply_markup()


@dp.callback_query_handler(Text(startswith=DriverCallbacks.driver_order_confirm))
async def no_driver_order_confirm(callback: types.CallbackQuery):
    await callback.answer("Вы не зарегистрированы как водитель", show_alert=True)
