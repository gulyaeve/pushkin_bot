from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from loader import dp, openroute_api


class OrderTaxi(StatesGroup):
    Departure = State()
    Destination = State()
    Fare = State()


@dp.message_handler(commands=['taxi'])
async def taxi_start_order(message: types.Message):
    await message.answer("Укажите адрес отправления (геолокация)")
    await OrderTaxi.Departure.set()


@dp.message_handler(state=OrderTaxi.Departure, content_types=types.ContentType.LOCATION)
async def taxi_set_departure(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['departure_longitude'] = message.location.longitude
        data['departure_latitude'] = message.location.latitude
    await message.answer("Укажите адрес назначения (геолокация)")
    await OrderTaxi.Destination.set()


@dp.message_handler(state=OrderTaxi.Destination, content_types=types.ContentType.LOCATION)
async def taxi_set_destination(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['destination_longitude'] = message.location.longitude
        data['destination_latitude'] = message.location.latitude
    distance, duration = await openroute_api.get_distance_and_duration(
        point_a=[data['departure_longitude'], data['departure_latitude']],
        point_b=[data['destination_longitude'], data['destination_latitude']]
    )
    await message.answer(
        f"distance: {distance}\n"
        f"duration: {duration}"
    )
    await state.finish()

