from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards.keyboards import location_button
from loader import dp, openroute_api, taxi_fares
from utils.utilities import taxi_fare_price, make_keyboard_list


class OrderTaxi(StatesGroup):
    Departure = State()
    Destination = State()
    Fare = State()


@dp.message_handler(commands=['taxi'])
async def taxi_start_order(message: types.Message):
    await message.answer("Укажите адрес отправления:", reply_markup=location_button)
    await OrderTaxi.Departure.set()


@dp.message_handler(state=OrderTaxi.Departure, content_types=types.ContentType.LOCATION)
async def taxi_set_departure(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['departure_longitude'] = message.location.longitude
        data['departure_latitude'] = message.location.latitude
    await message.answer("Укажите адрес назначения:")
    await OrderTaxi.Destination.set()


@dp.message_handler(state=OrderTaxi.Destination, content_types=types.ContentType.LOCATION)
async def taxi_set_destination(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['destination_longitude'] = message.location.longitude
        data['destination_latitude'] = message.location.latitude
    fares = await taxi_fares.select_all_taxi_fare_name()
    keyboard = make_keyboard_list(fares)
    keyboard.one_time_keyboard = True
    await message.answer("Выберите тариф:", reply_markup=keyboard)
    await OrderTaxi.Fare.set()


@dp.message_handler(state=OrderTaxi.Fare)
async def taxi_set_fare(message: types.Message, state: FSMContext):
    if message.text in (await taxi_fares.select_all_taxi_fare_name()):
        data = await state.get_data()
        distance, duration = await openroute_api.get_distance_and_duration(
            point_a=[data['departure_longitude'], data['departure_latitude']],
            point_b=[data['destination_longitude'], data['destination_latitude']]
        )
        taxi_fare = await taxi_fares.select_fare_by_name(message.text)
        price = taxi_fare_price(
            distance=distance,
            duration=duration,
            min_price=taxi_fare.min_price,
            min_distance=taxi_fare.min_distance,
            min_duration=taxi_fare.min_duration,
            km_price=taxi_fare.km_price,
            minute_price=taxi_fare.minute_price,
        )
        await message.answer(
            f"Расстояние: {distance} км\n"
            f"Примерное время в пути: {duration} минут\n"
            f"Тариф: {taxi_fare.name}\n"
            f"Цена поездки: {price} рублей",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.finish()
    else:
        fares = await taxi_fares.select_all_taxi_fare_name()
        keyboard = make_keyboard_list(fares)
        keyboard.one_time_keyboard = True
        return await message.reply("Выберите тариф из предложенных:", reply_markup=keyboard)
