import asyncio
import datetime
from dataclasses import dataclass
from typing import Sequence

import asyncpg
from aiogram.types import InlineKeyboardButton

from keyboards.manager import ManagerCallbacks
from utils.db_api.db import Database


@dataclass
class Order:
    id: int
    customer_id: int
    driver_id: int
    departure_latitude: float
    departure_longitude: float
    destination_latitude: float
    destination_longitude: float
    distance: int
    duration: int
    fare: str
    status: str
    time_created: datetime.datetime

    def make_button(self):
        return InlineKeyboardButton(
            text=f"№{self.id} 🗓️{self.time_created.strftime('%d.%m.%Y')} {self.validate_status(self.status)}",
            callback_data=f"{ManagerCallbacks.manage_order_info}={self.id}",
        )

    @staticmethod
    def validate_status(status):
        type_emoji = status
        match status:
            case OrderStatuses.new:
                type_emoji = "🆕"
            case OrderStatuses.in_progress:
                type_emoji = "🚀"
            case OrderStatuses.finished:
                type_emoji = "🏁"
        return type_emoji


class Orders:
    def __init__(self, orders: Sequence[Order]):
        self._orders = orders

    def __getitem__(self, key: int) -> Order:
        return self._orders[key]


class OrderStatuses:
    new = "new"
    in_progress = "in_progress"
    finished = "finished"


class OrdersDB(Database):
    def __init__(self):
        super().__init__()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.create_tables())

    async def create_tables(self):
        sql = """
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            customer_id bigint references users (telegram_id),
            driver_id bigint references drivers (telegram_id) DEFAULT NULL,
            departure_latitude float,
            departure_longitude float,
            destination_latitude float,
            destination_longitude float,
            distance int,
            duration int,
            fare int references taxi_fares (id),
            status character varying(255),
            time_created timestamp,
            time_assigned timestamp,
            time_finished timestamp
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    async def _format_order(record: asyncpg.Record) -> Order:
        return Order(
            id=record['id'],
            customer_id=record['customer_id'],
            driver_id=record['driver_id'],
            departure_latitude=record['departure_latitude'],
            departure_longitude=record['departure_longitude'],
            destination_latitude=record['destination_latitude'],
            destination_longitude=record['destination_longitude'],
            distance=record['distance'],
            duration=record['duration'],
            fare=record['fare'],
            status=record['status'],
            time_created=record['time_created']
        )

    async def new_order(
            self,
            customer_id: int,
            departure_latitude: float,
            departure_longitude: float,
            destination_latitude: float,
            destination_longitude: float,
            distance: int,
            duration: int,
            fare: int,
            status: str = OrderStatuses.new,
            time_created: datetime.datetime = datetime.datetime.now(),
    ):
        sql = "INSERT INTO " \
              "orders (customer_id, departure_latitude, departure_longitude, " \
              "destination_latitude, destination_longitude, distance, duration, fare, status, time_created) " \
              "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) returning *"
        record = await self.execute(
            sql,
            customer_id,
            departure_latitude,
            departure_longitude,
            destination_latitude,
            destination_longitude,
            distance,
            duration,
            fare,
            status,
            time_created,
            fetchrow=True,
        )
        return await self._format_order(record)

    async def get_order_info(self, order_id: int) -> Order:
        sql = "SELECT * FROM orders WHERE id=$1"
        return await self._format_order(await self.execute(sql, order_id, fetchrow=True))

    async def update_order_info(self, order_id: int, **kwargs) -> Order:
        for name, value in kwargs.items():
            sql = f"UPDATE orders SET {name}=$2 WHERE id=$1"
            await self.execute(sql, order_id, value, execute=True)
        return await self.get_order_info(order_id)

    async def find_active_order_for_driver(self, driver_id: int) -> Order | None:
        sql = "SELECT * FROM orders WHERE driver_id=$1 AND status='in_progress'"
        try:
            return await self._format_order(await self.execute(sql, driver_id, fetchrow=True))
        except TypeError:
            return None

    async def find_active_order_for_customer(self, customer_id: int) -> Order | None:
        sql = "SELECT * FROM orders WHERE customer_id=$1 AND status='in_progress'"
        try:
            return await self._format_order(await self.execute(sql, customer_id, fetchrow=True))
        except TypeError:
            return None

    async def remove_driver_from_orders(self, driver_id: int):
        sql = "UPDATE orders SET driver_id=null WHERE driver_id=$1"
        return await self.execute(sql, driver_id, execute=True)

    async def select_all_orders(self) -> Orders:
        sql = "SELECT * FROM orders ORDER BY time_created DESC "
        list_of_records = await self.execute(sql, fetch=True)
        return Orders([await self._format_order(record) for record in list_of_records])


