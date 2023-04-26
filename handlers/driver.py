import datetime
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, ChatTypeFilter, Regexp
from aiogram.dispatcher.filters.state import StatesGroup, State

from config import Config
from filters import DriverCheck, ActiveOrderCheck
from keyboards.driver import reg_button, make_driver_reg_menu, DriverCallbacks, make_manager_view, driver_menu, \
    make_order_menu
from keyboards.keyboards import auth_phone
from loader import dp, messages, drivers, users, orders, bot_info, openroute_api, osm_api
from utils.db_api.orders_db import OrderStatuses
from utils.utilities import make_rus

car_number_regexp = r"^[АВЕКМНОРСТXУABEKMHOPCTXYавекмнорстхуabekmhopctxy]{1}[0-9]{3}" \
                    r"[АВЕКМНОРСТXУABEKMHOPCTXYавекмнорстхуabekmhopctxy]{2}[0-9]{2,3}$"


class DriverStates(StatesGroup):
    FIO = State()
    Phone = State()
    Passport = State()
    CarNumber = State()
    PassportPhoto = State()
    STSPhoto1 = State()
    STSPhoto2 = State()


@dp.message_handler(
    ActiveOrderCheck(),
    ChatTypeFilter(chat_type=types.ChatType.PRIVATE),
    DriverCheck(),
    commands=['driver']
)
async def driver_order_start(message: types.Message):
    order = await orders.find_active_order_for_driver(message.from_id)
    # distance, duration = await openroute_api.get_distance_and_duration(
    #     departure=[order.departure_longitude, order.departure_latitude],
    #     destination=[order.destination_longitude, order.destination_latitude],
    # )
    await message.answer(f"<b>Заказ № {order.id}. Отправление:</b>")
    await message.answer_location(
        latitude=order.departure_latitude,
        longitude=order.departure_longitude,
    )
    await message.answer(f"<b>Заказ № {order.id}. Назначение:</b>")
    await message.answer_location(
        latitude=order.destination_latitude,
        longitude=order.destination_longitude,
    )
    await message.answer(
        f"Активный заказ №{order.id}:\n"
        f"Примерное расстояние: {order.distance} км\n"
        f"Примерное время в пути (без пробок): {order.duration} минут\n"
        f"Тариф: {order.fare}\n"
        f"Клиенту можно отправлять сообщения прямо в этом диалоге.\n\n"
        f"Адрес подачи: {osm_api.get_address(order.departure_latitude, order.departure_longitude)}",
        reply_markup=make_order_menu(order_id=order.id)
    )


@dp.message_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), DriverCheck(), commands=['driver'])
async def driver_start(message: types.Message):
    await message.answer(await messages.get_message("driver_menu"), reply_markup=driver_menu)


@dp.message_handler(DriverCheck(), commands=['driver'])
async def driver_start(message: types.Message):
    msg = await messages.get_message("wrong_chat")
    await message.reply(f"{msg} {bot_info.mention}")


@dp.callback_query_handler(DriverCheck(), state=DriverStates.all_states)
@dp.callback_query_handler(DriverCheck(), text=[DriverCallbacks.driver_back, DriverCallbacks.driver_reg_menu])
async def driver_start(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text(await messages.get_message("driver_menu"), reply_markup=driver_menu)


@dp.message_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), commands=['driver'])
async def driver_start_no_auth(message: types.Message):
    await message.answer(await messages.get_message("driver_reg_prompt"), reply_markup=reg_button)


@dp.message_handler(commands=['driver'])
async def driver_start_no_auth(message: types.Message):
    msg = await messages.get_message("wrong_chat")
    await message.reply(f"{msg} {bot_info.mention}")


@dp.callback_query_handler(text=DriverCallbacks.driver_back)
async def driver_start_no_auth(callback: types.CallbackQuery):
    await callback.message.edit_text(await messages.get_message("driver_reg_prompt"), reply_markup=reg_button)


@dp.callback_query_handler(text=DriverCallbacks.driver_reg_menu)
async def driver_reg_menu(callback: types.CallbackQuery):
    driver = await drivers.add_driver(callback.from_user.id)
    menu = make_driver_reg_menu(driver)
    await callback.message.edit_text(await messages.get_message("driver_reg_menu"), reply_markup=menu)


@dp.callback_query_handler(text=DriverCallbacks.driver_fio)
async def driver_fio_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(await messages.get_message("driver_input_fio"))
    await DriverStates.FIO.set()


@dp.message_handler(state=DriverStates.FIO)
async def driver_input_fio(message: types.Message, state: FSMContext):
    if message.text:
        driver = await drivers.update_driver_info(message.from_user.id, fio=message.text)
        menu = make_driver_reg_menu(driver)
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
        menu = make_driver_reg_menu(driver)
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
            menu = make_driver_reg_menu(driver)
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


@dp.callback_query_handler(text=DriverCallbacks.driver_car_number)
async def driver_car_number_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(await messages.get_message("driver_input_car_number"))
    await DriverStates.CarNumber.set()


@dp.message_handler(Regexp(car_number_regexp), state=DriverStates.CarNumber, content_types=types.ContentType.TEXT)
async def driver_input_car_number(message: types.Message, state: FSMContext):
    logging.info(f"[{message.from_id}] Введен корректный номер авто {message.text}")
    try:
        car_number = make_rus(message.text.upper())
        driver = await drivers.update_driver_info(message.from_user.id, car_number=car_number)
        menu = make_driver_reg_menu(driver)
        await message.answer(await messages.get_message("driver_correct_input"))
        await message.answer(await messages.get_message("driver_reg_menu"), reply_markup=menu)
        await state.finish()
    except Exception as e:
        logging.info(f"Номер {message.text} уже есть в базе или другая ошибка {e}")
        return await message.answer(
            await messages.get_message("driver_wrong_car_number"),
            reply_markup=types.ForceReply()
        )


@dp.message_handler(state=DriverStates.CarNumber, content_types=types.ContentType.TEXT)
async def driver_input_car_number(message: types.Message):
    logging.info(f"[{message.from_id}] Введен НЕ корректный номер авто {message.text}")
    return await message.answer(
        await messages.get_message("driver_wrong_car_number"),
        reply_markup=types.ForceReply()
    )


@dp.callback_query_handler(text=DriverCallbacks.driver_passport)
async def driver_passport_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(await messages.get_message("driver_input_passport"))
    await DriverStates.Passport.set()


@dp.message_handler(state=DriverStates.Passport)
async def driver_input_passport(message: types.Message, state: FSMContext):
    if message.text:
        driver = await drivers.update_driver_info(message.from_user.id, passport=message.text)
        menu = make_driver_reg_menu(driver)
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
    menu = make_driver_reg_menu(driver)
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
    menu = make_driver_reg_menu(driver)
    await message.answer(await messages.get_message("driver_correct_input"))
    await message.answer(await messages.get_message("driver_reg_menu"), reply_markup=menu)
    await state.finish()


@dp.message_handler(state=DriverStates.STSPhoto2, content_types=types.ContentType.PHOTO)
async def driver_input_passport_photo(message: types.Message, state: FSMContext):
    sts_path = f"sts2/{message.from_user.id}.png"
    sts_destination = f"{Config.MEDIA}/{sts_path}"
    await message.photo[-1].download(destination_file=sts_destination)

    driver = await drivers.update_driver_info(message.from_user.id, sts_photo_2=sts_path)
    menu = make_driver_reg_menu(driver)
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
        await callback.answer(driver.make_info(), show_alert=True)


@dp.callback_query_handler(DriverCheck(), ActiveOrderCheck(), Text(startswith=DriverCallbacks.driver_order_confirm))
async def driver_order_not_confirm(callback: types.CallbackQuery):
    order_id = int(callback.data.split("=")[1])
    order = await orders.get_order_info(order_id)
    await callback.answer(f"У вас уже есть активный заказ №{order.id}", show_alert=True)


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
    await callback.answer(f"Вы взяли заказ {changed_order.id}, информация в личной беседе", show_alert=True)
    await dp.bot.send_message(
        chat_id=changed_order.driver_id,
        text=f"У вас активный заказ № {changed_order.id}. Подробности: /driver",
        reply_markup=make_order_menu(order_id=changed_order.id),
    )
    await dp.bot.send_message(
        chat_id=changed_order.customer_id,
        text=f"Водитель <b>{driver.fio}</b> автомобиля с госномером <b>{driver.car_number}</b> начал выполнение "
             f"вашего заказа.\n"
             f"Вы можете общаться с ним прямо в этом диалоге.",
        # reply_markup=make_customer_answer_button(order_id=changed_order.id),
    )
    await callback.message.delete_reply_markup()


@dp.callback_query_handler(Text(startswith=DriverCallbacks.driver_order_confirm))
async def no_driver_order_confirm(callback: types.CallbackQuery):
    await callback.answer("Вы не зарегистрированы как водитель", show_alert=True)


@dp.callback_query_handler(Text(startswith=DriverCallbacks.driver_order_start_location))
async def driver_on_start_location(callback: types.CallbackQuery):
    order_id = int(callback.data.split("=")[1])
    order = await orders.get_order_info(order_id)
    driver = await drivers.get_driver_info(order.driver_id)
    logging.info(f"По заказу {order.id} водитель {order.driver_id} приехал к клиенту {order.customer_id}")
    await dp.bot.send_message(
        chat_id=order.customer_id,
        text=f"Водитель ожидает вас 🚖<b>{driver.car_number}</b>",
    )
    await callback.answer("Клиенту отправлено уведомление о подаче", show_alert=True)


@dp.callback_query_handler(Text(startswith=DriverCallbacks.driver_order_finish))
async def driver_order_finish(callback: types.CallbackQuery):
    order_id = int(callback.data.split("=")[1])
    order = await orders.get_order_info(order_id)
    logging.info(f"Водитель {order.driver_id} завершил заказ {order.id}")
    changed_order = await orders.update_order_info(
        order_id,
        status=OrderStatuses.finished,
        time_finished=datetime.datetime.now(),
    )
    logging.info(f"Заказ изменен {changed_order}")
    await callback.answer(f"Вы завершили заказ {order.id}", show_alert=True)
    await dp.bot.send_message(
        chat_id=changed_order.customer_id,
        text=f"Водитель завершил ваш заказ 🏁"
    )
    await callback.message.delete()


# @dp.callback_query_handler(Text(startswith=DriverCallbacks.driver_order_message))
# async def driver_order_message(callback: types.CallbackQuery, state: FSMContext):
#     order_id = int(callback.data.split("=")[1])
#     order = await orders.get_order_info(order_id)
#     async with state.proxy() as data:
#         data["driver_private_user_id"] = order.customer_id
#         data["order_id"] = order.id
#     await callback.message.answer(f"Введите сообщение:")
#     await state.set_state(f"DRIVER_PRIVATE_MSG")
#
#
# @dp.message_handler(state="DRIVER_PRIVATE_MSG", content_types=types.ContentType.ANY)
# async def driver_send_answer(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     try:
#         await dp.bot.send_message(
#             chat_id=data['driver_private_user_id'],
#             text="Водитель сообщает:"
#         )
#         await dp.bot.copy_message(
#             chat_id=data['driver_private_user_id'],
#             from_chat_id=message.from_id,
#             message_id=message.message_id,
#             reply_markup=make_customer_answer_button(data['order_id'])
#         )
#         logging.info(f'От водителя пользователю [{data["driver_private_user_id"]=}] отправлено: {message.message_id}')
#         await message.answer('Сообщение отправлено')
#     except Exception as e:
#         await message.answer('Ошибка при отправке')
#         logging.info(f"Failed to send message: {e}")
#     await state.finish()
