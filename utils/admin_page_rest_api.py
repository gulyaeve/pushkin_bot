import logging

from aiogram import types

from config import Config
from utils.rest_api import RestAPI


class AdminPageRestAPI(RestAPI):
    def __init__(self, bot_data):
        super().__init__(Config.rest_link)
        self._bot_data = bot_data

    async def post_update(self, update: types.Update):
        data = {
            "bot_data": self._bot_data,
        }
        data.update(update.to_python())
        answer = await self._post_json('updates/create/', data)
        logging.info(f"{answer=}")

