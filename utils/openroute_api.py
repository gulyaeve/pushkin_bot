import asyncio

from config import Config
from utils.rest_api import RestAPI


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

    async def get_distance_and_duration(self, point_a: list, point_b: list) -> [int]:
        answer = await self.post_json("/v2/directions/driving-car", {"coordinates": [point_a, point_b]})
        distance = int(answer['routes'][0]['summary']['distance'])
        duration = int(answer['routes'][0]['summary']['duration'])
        distance = round(distance / 1000)
        duration = round(duration / 60)
        return distance, duration

    async def get_coordinates(self, address: str) -> [int]:
        params = {
            "api_key": self._token,
            "text": address,
        }
        answer = await self.get_json("/geocode/search", params)
        if answer['features']:
            longitude = answer['features'][0]['geometry']['coordinates'][0]
            latitude = answer['features'][0]['geometry']['coordinates'][1]
            return longitude, latitude
        else:
            return None, None


# loop = asyncio.get_event_loop()
# api = OpenrouteApi()
# asyncio.run(api.get_distance_and_duration([37.404065, 55.814640], [37.476696, 55.802767]))
# loop.run_until_complete(api.get_distance_and_duration())
