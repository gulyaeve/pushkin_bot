import asyncio
from dataclasses import dataclass

from config import Config
from utils.rest_api import RestAPI

@dataclass
class AddressData:
    label: str
    coordinates: list


class OpenrouteApi(RestAPI):
    def __init__(self):
        super().__init__(
            rest_link=Config.OpenRouteConfig.OPENROUTE_API_LINK,
            rest_token=Config.OpenRouteConfig.OPENROUTE_API_TOKEN,
        )
        self._headers = {
            "Authorization": f"{self._token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def get_distance_and_duration(self, departure: list, destination: list) -> [int]:
        params = {
            "coordinates": [departure, destination],
        }
        answer = await self.post_json("/v2/directions/driving-car", params)
        try:
            distance = int(answer['routes'][0]['summary']['distance'])
            distance = round(distance / 1000)
        except KeyError:
            distance = 0
        try:
            duration = int(answer['routes'][0]['summary']['duration'])
            duration = round(duration / 60)
        except KeyError:
            duration = 0
        return distance, duration

    async def get_coordinates(self, address: str) -> [int]:
        params = {
            "api_key": self._token,
            "text": address,
        }
        answer = await self.get_json("/geocode/search", params)
        if answer['features']:
            for feature in answer['features']:
                print(feature)
            longitude = answer['features'][0]['geometry']['coordinates'][0]
            latitude = answer['features'][0]['geometry']['coordinates'][1]
            return longitude, latitude
        else:
            return None, None

    async def get_list_of_addresses(self, address: str) -> [AddressData]:
        params = {
            "api_key": self._token,
            "text": address,
        }
        answer = await self.get_json("/geocode/search", params)
        list_of_addresses = []
        if answer['features']:
            for feature in answer['features']:
                longitude = feature['geometry']['coordinates'][0]
                latitude = feature['geometry']['coordinates'][1]
                label = feature['properties']['label']
                list_of_addresses.append(AddressData(label, [longitude, latitude]))
        return list_of_addresses


# loop = asyncio.get_event_loop()
# api = OpenrouteApi()
# asyncio.run(api.get_list_of_addresses("улица исаковского 2 корпус 2"))
# asyncio.run(api.get_distance_and_duration([37.404065, 55.814640], [37.476696, 55.802767]))
# loop.run_until_complete(api.get_distance_and_duration())
