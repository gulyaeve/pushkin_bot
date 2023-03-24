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

    async def get_distance_and_duration(self, point_a: list, point_b: list) -> [str]:
        answer = await self.post_json("", {"coordinates": [point_a, point_b]})
        # print(answer['routes'][0]['summary']['distance'], answer['routes'][0]['summary']['duration'])
        return answer['routes'][0]['summary']['distance'], answer['routes'][0]['summary']['duration']


# loop = asyncio.get_event_loop()
# api = OpenrouteApi()
# asyncio.run(api.get_distance_and_duration([37.404065, 55.814640], [37.476696, 55.802767]))
# loop.run_until_complete(api.get_distance_and_duration())
