import json
import logging

from loader import taxi_fares


async def create_taxi_fares():
    with open("templates/taxi_fares.json", "r", encoding="utf-8") as file:
        new_fares = json.loads(file.read())
    for fare in new_fares:
        await taxi_fares.add_fare(
            name=fare['name'],
            min_price=fare['min_price'],
            km_price=fare['km_price'],
            minute_price=fare['minute_price'],
            min_distance=fare['min_distance'],
            min_duration=fare['min_duration'],
        )
