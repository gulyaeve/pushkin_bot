import asyncio
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
            fare character varying(255) references taxi_fares (name),
            status character varying(255),
            time_created timestamp DEFAULT now()
        );
        """
        await self._execute(sql, execute=True)

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

    # async def new_order(self, customer_id, departure_latitude, departure_longitude, destination_latitude, destination_longitude):
