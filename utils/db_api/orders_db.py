import asyncio
import datetime
from dataclasses import dataclass

import asyncpg

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

    async def find_active_order_for_driver(self, driver_id: int) -> Order:
        sql = "SELECT * FROM orders WHERE driver_id=$1 AND status='in_progress'"
        return await self._format_order(await self.execute(sql, driver_id, fetchrow=True))

    async def find_active_order_for_customer(self, customer_id: int) -> Order:
        sql = "SELECT * FROM orders WHERE customer_id=$1 AND status='in_progress'"
        return await self._format_order(await self.execute(sql, customer_id, fetchrow=True))


