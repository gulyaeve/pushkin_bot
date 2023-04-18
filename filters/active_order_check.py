from logging import log, INFO
from typing import Union

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from loader import users, orders


class ActiveOrderCheck(BoundFilter):
    async def check(self, message: types.Message):
        """
        Фильтр для проверки активного заказа
        """
        user = await users.select_user(telegram_id=message.from_user.id)
        try:
            if user.type == 'driver':
                active_order = await orders.find_active_order_for_driver(user.telegram_id)
                if active_order:
                    log(INFO, f"Водитель [{message.from_user.id=}] имеет заказ {active_order.id}")
                    return True
                else:
                    return False
            else:
                active_order = await orders.find_active_order_for_customer(user.telegram_id)
                if active_order:
                    log(INFO, f"Клиент [{message.from_user.id=}] имеет заказ {active_order.id}")
                    return True
                else:
                    return False
        except Exception as err:
            log(INFO, f"[{message.from_user.id=}] ошибка {err}")
            return False
