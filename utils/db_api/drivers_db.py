import asyncio
from dataclasses import dataclass
from typing import Sequence

import asyncpg
from aiogram.types import InlineKeyboardButton

from keyboards.manager import ManagerCallbacks
from utils.db_api.db import Database


@dataclass
class Driver:
    telegram_id: int
    fio: str
    phone: str
    passport: str
    passport_photo: str
    sts_photo_1: str
    sts_photo_2: str
    car_number: str

    def validate_info(self) -> bool:
        if self.fio \
                and self.phone \
                and self.passport \
                and self.passport_photo \
                and self.sts_photo_1 \
                and self.sts_photo_2\
                and self.car_number:
            return True
        else:
            return False

    def __str__(self):
        msg = f"ФИО: {self.fio}\n" \
              f"Телефон: {self.phone}\n" \
              f"Паспорт: {self.passport}\n" \
              f"Номер машины: {self.car_number}"
        return msg

    def make_info(self):
        answer = "Необходимо заполнить:\n"
        if not self.fio:
            answer += "ФИО\n"
        if not self.phone:
            answer += "Номер телефона\n"
        if not self.passport:
            answer += "Паспортные данные\n"
        if not self.car_number:
            answer += "Номер авто\n"
        if not self.passport_photo:
            answer += "Фото паспорта\n"
        if not self.sts_photo_1:
            answer += "Фото СТС (лицевая сторона)\n"
        if not self.sts_photo_2:
            answer += "Фото СТС (оборотная сторона)\n"
        return answer

    def make_button(self):
        return InlineKeyboardButton(
            text=f"{self.fio} {self.car_number}",
            callback_data=f"{ManagerCallbacks.manage_driver_info}={self.telegram_id}",
        )


class Drivers:
    def __init__(self, drivers: Sequence[Driver]):
        self._drivers = drivers

    def __getitem__(self, key: int) -> Driver:
        return self._drivers[key]


class DriversDB(Database):
    def __init__(self):
        super().__init__()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.create_tables())

    async def create_tables(self):
        sql = """
        CREATE TABLE IF NOT EXISTS drivers (
            telegram_id bigint NOT NULL UNIQUE PRIMARY KEY,
            fio character varying(255) DEFAULT NULL,
            phone character varying(255) UNIQUE DEFAULT NULL,
            car_number character varying(255) UNIQUE DEFAULT NULL,
            passport character varying(255) DEFAULT NULL,
            passport_photo character varying(255) DEFAULT NULL,
            sts_photo_1 character varying(255) DEFAULT NULL,
            sts_photo_2 character varying(255) DEFAULT NULL
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    async def _format_driver(record: asyncpg.Record) -> Driver:
        return Driver(
            telegram_id=record['telegram_id'],
            phone=record['phone'],
            fio=record['fio'],
            passport=record['passport'],
            passport_photo=record['passport_photo'],
            sts_photo_1=record['sts_photo_1'],
            sts_photo_2=record['sts_photo_2'],
            car_number=record['car_number']
        )

    async def _select_driver(self, telegram_id: int) -> asyncpg.Record:
        sql = "SELECT * FROM drivers WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def get_driver_info(self, telegram_id: int) -> Driver:
        return await self._format_driver(await self._select_driver(telegram_id))

    async def add_driver(self, telegram_id: int) -> Driver:
        exist_driver = await self._select_driver(telegram_id)
        if exist_driver is not None:
            return await self._format_driver(exist_driver)
        else:
            sql = "INSERT INTO drivers (telegram_id) VALUES($1) returning *"
            record = await self.execute(sql, telegram_id, fetchrow=True)
            return await self._format_driver(record)

    async def update_driver_info(self, telegram_id: int, **kwargs):
        for name, value in kwargs.items():
            sql = f"UPDATE drivers SET {name}=$2 WHERE telegram_id=$1"
            await self.execute(sql, telegram_id, value, execute=True)
        return await self.get_driver_info(telegram_id)

    async def remove_driver(self, telegram_id: int):
        await self.execute("DELETE FROM drivers WHERE telegram_id=$1", telegram_id, execute=True)

    async def select_all_drivers(self) -> Drivers:
        sql = "SELECT * FROM drivers"
        list_of_records = await self.execute(sql, fetch=True)
        return Drivers([await self._format_driver(record) for record in list_of_records])


# loop = asyncio.get_event_loop()
# test_drive = DriversDB()
# loop.run_until_complete(test_drive.update_driver_info(telegram_id=253122, fio="1", phone="2"))
