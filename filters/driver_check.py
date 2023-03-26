from logging import log, INFO

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from loader import users


class DriverCheck(BoundFilter):
    async def check(self, message: types.Message):
        """
        Фильтр для проверки водителя
        """
        user = await users.select_user(telegram_id=message.from_user.id)
        try:
            if user.type == 'driver':
                log(INFO, f"[{message.from_user.id=}] пользователь является водителем")
                return True
            else:
                log(INFO, f"Пользователь не является водителем [{message.from_user.id=}]")
                return False
        except Exception as err:
            log(INFO, f"[{message.from_user.id=}] водитель не найден. {err}")
            return False
