import asyncio

from config import Config
from utils.rest_api import RestAPI


class OSMSearchApi(RestAPI):
    def __init__(self):
        super().__init__(
            rest_link=Config.OSM_API_SEARCH_LINK,
        )

    async def get_address(self, latitude: float, longitude: float) -> str:
        params = {
            "format": "json",
            "q": f"{latitude}, {longitude}"
        }
        answer = await self.get_json("/search.php", params)
        if "display_name" in answer[0].keys():
            return answer[0]["display_name"]
        else:
            return "Не определён"


if __name__ == "__main__":
    api = OSMSearchApi()
    ans = asyncio.run(api.get_address(55.814640, 37.404065))
    print(ans)
# loop = asyncio.get_event_loop()
# api = OpenrouteApi()
# asyncio.run(api.get_list_of_addresses("улица исаковского 2 корпус 2"))
# asyncio.run(api.get_distance_and_duration([37.404065, 55.814640], [37.476696, 55.802767]))
# loop.run_until_complete(api.get_distance_and_duration())
