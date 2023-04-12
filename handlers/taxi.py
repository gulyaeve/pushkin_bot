import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, ChatTypeFilter
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ChatType

from keyboards.driver import make_confirm_button
from keyboards.keyboards import location_button, request_submit
from loader import dp, openroute_api, taxi_fares, messages, orders, bot_info
from utils.db_api.orders_db import OrderStatuses


class OrderTaxi(StatesGroup):
    Departure = State()
    Destination = State()
    Fare = State()
    Confirm = State()


@dp.message_handler(ChatTypeFilter(chat_type=ChatType.PRIVATE), commands=['taxi'])
async def taxi_start_order(message: types.Message):
    await message.answer(await messages.get_message("taxi_departure"), reply_markup=location_button)
    await OrderTaxi.Departure.set()


@dp.message_handler(commands=['taxi'])
async def taxi_start_order(message: types.Message):
    msg = await messages.get_message("wrong_chat")
    await message.answer(f"{msg} {bot_info.mention}")


@dp.message_handler(state=OrderTaxi.Departure, content_types=types.ContentType.LOCATION)
async def taxi_set_departure(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['departure_longitude'] = message.location.longitude
        data['departure_latitude'] = message.location.latitude
    await message.answer(await messages.get_message("taxi_destination"), reply_markup=types.ReplyKeyboardRemove())
    await OrderTaxi.Destination.set()


@dp.message_handler(state=OrderTaxi.Departure, content_types=types.ContentType.TEXT)
async def taxi_set_departure(message: types.Message, state: FSMContext):
    list_of_addresses = await openroute_api.get_list_of_addresses(message.text)
    if list_of_addresses:
        address_keyboard = types.InlineKeyboardMarkup()
        for address in list_of_addresses:
            address_keyboard.add(
                types.InlineKeyboardButton(
                    text=address.label,
                    callback_data=f"departure={address.coordinates[0]},{address.coordinates[1]}"
                )
            )
        await message.answer(await messages.get_message("taxi_select_address"), reply_markup=address_keyboard)
    else:
        return await message.answer(await messages.get_message("taxi_wrong_address"))


@dp.callback_query_handler(Text(startswith="departure="), state=OrderTaxi.Departure)
async def taxi_set_departure(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    coordinates = callback.data.split("=")[1]
    longitude = coordinates.split(",")[0]
    latitude = coordinates.split(",")[1]
    async with state.proxy() as data:
        data['departure_longitude'] = longitude
        data['departure_latitude'] = latitude
    await callback.message.answer(await messages.get_message("taxi_destination"), reply_markup=types.ReplyKeyboardRemove())
    await OrderTaxi.Destination.set()


@dp.message_handler(state=OrderTaxi.Destination, content_types=types.ContentType.LOCATION)
async def taxi_set_destination(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['destination_longitude'] = message.location.longitude
        data['destination_latitude'] = message.location.latitude
    fares = await taxi_fares.select_all_taxi_fare_name()
    fares_keyboard = types.InlineKeyboardMarkup()
    for fare in fares:
        fares_keyboard.add(
            types.InlineKeyboardButton(
                text=fare,
                callback_data=f"fare={fare}"
            )
        )
    await message.answer(await messages.get_message("taxi_select_fare"), reply_markup=fares_keyboard)
    await OrderTaxi.Fare.set()


@dp.message_handler(state=OrderTaxi.Destination, content_types=types.ContentType.TEXT)
async def taxi_set_destination(message: types.Message, state: FSMContext):
    list_of_addresses = await openroute_api.get_list_of_addresses(message.text)
    if list_of_addresses:
        address_keyboard = types.InlineKeyboardMarkup()
        for address in list_of_addresses:
            address_keyboard.add(
                types.InlineKeyboardButton(
                    text=address.label,
                    callback_data=f"destination={address.coordinates[0]},{address.coordinates[1]}"
                )
            )
        await message.answer(await messages.get_message("taxi_select_address"), reply_markup=address_keyboard)
    else:
        return await message.answer(await messages.get_message("taxi_wrong_address"))


@dp.callback_query_handler(Text(startswith="destination="), state=OrderTaxi.Destination)
async def taxi_set_departure(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    coordinates = callback.data.split("=")[1]
    longitude = coordinates.split(",")[0]
    latitude = coordinates.split(",")[1]
    async with state.proxy() as data:
        data['destination_longitude'] = longitude
        data['destination_latitude'] = latitude
    fares = await taxi_fares.select_all_taxi_fare_name()
    fares_keyboard = types.InlineKeyboardMarkup()
    for fare in fares:
        fares_keyboard.add(
            types.InlineKeyboardButton(
                text=fare,
                callback_data=f"fare={fare}"
            )
        )
    await callback.message.answer(await messages.get_message("taxi_select_fare"), reply_markup=fares_keyboard)
    await OrderTaxi.Fare.set()


@dp.callback_query_handler(Text(startswith="fare="), state=OrderTaxi.Fare)
async def taxi_set_fare(callback: types.CallbackQuery, state: FSMContext):
    fare = callback.data.split("=")[1]
    # data = await state.get_data()
    async with state.proxy() as data:
        data['fare'] = fare
    taxi_fare = await taxi_fares.select_fare_by_name(fare)
    # price = taxi_fare_price(
    #     distance=distance,
    #     duration=duration,
    #     min_price=taxi_fare.min_price,
    #     min_distance=taxi_fare.min_distance,
    #     min_duration=taxi_fare.min_duration,
    #     km_price=taxi_fare.km_price,
    #     minute_price=taxi_fare.minute_price,
    # )
    await callback.message.delete()
    await callback.message.answer(
        f"<b>Ваша поездка:</b>\n"
        f"Тариф: {taxi_fare.name}\n"
        f"<i>Минимальная стоимость: {taxi_fare.min_price}\n"
        f"Включено километров: {taxi_fare.min_distance}\n"
        f"Цена за каждый дополнительный километр: {taxi_fare.km_price}\n"
        f"Включено минут: {taxi_fare.min_duration}\n"
        f"Цена за дополнительные минуты: {taxi_fare.minute_price}\n\n</i>"
        f"Отправляем заказ водителям?",
        reply_markup=request_submit,
    )
    await OrderTaxi.Confirm.set()


@dp.message_handler(Text(equals="Отправить"), state=OrderTaxi.Confirm)
async def taxi_order_confirm(message: types.Message, state: FSMContext):
    data = await state.get_data()
    fare = data['fare']
    taxi_fare = await taxi_fares.select_fare_by_name(fare)
    distance, duration = await openroute_api.get_distance_and_duration(
        departure=[data['departure_longitude'], data['departure_latitude']],
        destination=[data['destination_longitude'], data['destination_latitude']],
    )
    new_order = await orders.new_order(
        customer_id=message.from_user.id,
        departure_latitude=float(data['departure_latitude']),
        departure_longitude=float(data['departure_longitude']),
        destination_latitude=float(data['destination_latitude']),
        destination_longitude=float(data['destination_longitude']),
        distance=distance,
        duration=duration,
        fare=taxi_fare.id,
        status=OrderStatuses.new,
    )
    logging.info(f"Order saved {new_order}")
    await dp.bot.send_location(
        chat_id=taxi_fare.chat_id,
        latitude=float(data['departure_latitude']),
        longitude=float(data['departure_longitude']),
    )
    await dp.bot.send_location(
        chat_id=taxi_fare.chat_id,
        latitude=float(data['destination_latitude']),
        longitude=float(data['destination_longitude']),
    )
    await dp.bot.send_message(
        chat_id=taxi_fare.chat_id,
        text=f"Новый заказ №{new_order.id}:\n"
             f"Примерное расстояние: {distance} км\n"
             f"Примерное время в пути (без пробок): {duration} минут\n"
             f"Тариф: {taxi_fare.name}\n",
        reply_markup=make_confirm_button(new_order.id),
    )
    await message.answer(
        text=(await messages.get_message("taxi_order_save")),
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.finish()
