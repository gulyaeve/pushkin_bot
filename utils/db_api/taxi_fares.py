import asyncio
import logging
from dataclasses import dataclass

import asyncpg

from utils.db_api.db import Database


@dataclass
class TaxiFare:
    id: int
    name: str
    min_price: int
    km_price: int
    minute_price: int
    min_distance: int
    min_duration: int


class TaxiFaresDB(Database):
    def __init__(self):
        super().__init__()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.create_tables())

    async def create_tables(self):
        sql = """
        CREATE TABLE IF NOT EXISTS taxi_fares (
            id SERIAL PRIMARY KEY,
            name character varying(255) NOT NULL,
            min_price int8 DEFAULT 0,
            km_price int8 DEFAULT 0,
            minute_price int8 DEFAULT 0,
            min_distance int8 DEFAULT 0,
            min_duration int8 DEFAULT 0
        );
        """
        await self._execute(sql, execute=True)

    async def _format_fare(self, record: asyncpg.Record) -> TaxiFare:
        return TaxiFare(
            id=record['id'],
            name=record['name'],
            min_price=record['min_price'],
            km_price=record['km_price'],
            minute_price=record['minute_price'],
            min_distance=record['min_distance'],
            min_duration=record['min_duration'],
        )

    async def select_all_taxi_fare_name(self) -> [str]:
        sql = "SELECT * FROM taxi_fares ORDER BY name DESC"
        list_of_records = await self._execute(sql, fetch=True)
        return [record['name'] for record in list_of_records]

    async def select_fare_by_name(self, name: str) -> TaxiFare:
        sql = "SELECT * FROM taxi_fares WHERE name=$1"
        record = await self._execute(sql, name, fetchrow=True)
        return await self._format_fare(record)

    async def add_fare(
            self,
            name: str,
            min_price: int,
            km_price: int,
            minute_price: int,
            min_distance: int,
            min_duration: int) -> TaxiFare:
        fare = await self._execute("SELECT * FROM taxi_fares WHERE name=$1", name, fetchrow=True)
        if fare is None:
            sql = "INSERT INTO taxi_fares (name, min_price, km_price, minute_price, min_distance, min_duration) " \
                  "VALUES($1, $2, $3, $4, $5, $6) returning *"
            record = await self._execute(
                sql, name, min_price, km_price, minute_price, min_distance, min_duration, fetchrow=True
            )
            logging.info(f"Fare {name} success save in db")
            return await self._format_fare(record)
