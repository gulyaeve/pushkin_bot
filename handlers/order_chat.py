import logging

from aiogram import types
from aiogram.dispatcher.filters import ChatTypeFilter

from filters import DriverCheck, ActiveOrderCheck
from loader import dp, orders


@dp.message_handler(DriverCheck(), ActiveOrderCheck(), ChatTypeFilter(chat_type=types.ChatType.PRIVATE))
async def driver_chat(message: types.Message):
    active_order = await orders.find_active_order_for_driver(message.from_id)
    await dp.bot.send_message(
        chat_id=active_order.customer_id,
        text="<i>Водитель сообщает:</i>"
    )
    await dp.bot.copy_message(
        chat_id=active_order.customer_id,
        from_chat_id=message.from_id,
        message_id=message.message_id
    )
    logging.info(f'От водителя [{active_order.driver_id}] пользователю [{active_order.customer_id}] отправлено: {message.message_id}')
    await message.answer('Сообщение отправлено клиенту')


@dp.message_handler(ActiveOrderCheck(), ChatTypeFilter(chat_type=types.ChatType.PRIVATE))
async def customer_chat(message: types.Message):
    active_order = await orders.find_active_order_for_customer(message.from_id)
    await dp.bot.send_message(
        chat_id=active_order.driver_id,
        text="<i>Клиент сообщает:</i>"
    )
    await dp.bot.copy_message(
        chat_id=active_order.driver_id,
        from_chat_id=message.from_id,
        message_id=message.message_id
    )
    logging.info(f'От пользователя [{active_order.customer_id}] водителю [{active_order.driver_id}] отправлено: {message.message_id}')
    await message.answer('Сообщение отправлено')

