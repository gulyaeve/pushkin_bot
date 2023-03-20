import logging

import aiohttp
from aiogram import types
from aiohttp import ClientConnectorError

from config import Config


class AdminPageRestAPI:
    def __init__(self, bot_data):
        self._link = Config.rest_link
        self._bot_data = bot_data
        if Config.rest_token:
            self._headers = {
                "Authorization": f"Bearer {Config.rest_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        else:
            self._headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

    async def _post_json(self, route: str, data: dict | None) -> dict:
        """
        Send post request to host
        :param route: request link
        :param data: json object to send
        :return: json object from host
        """
        async with aiohttp.ClientSession(headers=self._headers) as session:
            try:
                async with session.post(f'{self._link}{route}',
                                        json=data if data is not None else {}) as post:
                    logging.info(f"{post.status} {post.reason} {self._link}{route} {data=}")
                    return await post.json()
            except ClientConnectorError:
                logging.warning(f"Rest api is unreachable")
            except Exception as e:
                logging.warning(f"Rest api is unreachable: {e}")

    async def _post_file(self, route: str, files) -> dict:
        """
        Send post request to host
        :param route: request link
        :param file: file to send
        :return: json object from host
        """
        if Config.rest_token:
            headers = {"Authorization": f"Bearer {Config.rest_token}"}
        else:
            headers = {}
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(f'{self._link}{route}', data=files) as post:
                    logging.info(f"{post.status=} {self._link}{route}")
                    return await post.json()
        except ClientConnectorError:
            logging.warning(f"Rest api is unreachable")
        except Exception as e:
            logging.warning(f"Rest api is unreachable: {e}")

    async def _get_json(self, route: str, params: dict | None) -> dict:
        """
        Send get request to host
        :param route: request link
        :return: json object answer from host
        """
        try:
            async with aiohttp.ClientSession(headers=self._headers) as session:
                async with session.get(f'{self._link}{route}',
                                       params=params if params is not None else {}) as resp:
                    logging.info(f"{resp.status=} {self._link}{route} {params=}")
                    return await resp.json()
        except ClientConnectorError:
            logging.warning(f"Rest api is unreachable")
        except Exception as e:
            logging.warning(f"Rest api is unreachable: {e}")

    async def _get_file(self, route: str) -> bytes:
        """
        Download file from server
        :param route: request link
        :return: file in bytes
        """
        if Config.rest_token:
            headers = {"Authorization": f"Bearer {Config.rest_token}"}
        else:
            headers = {}
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(f'{self._link}{route}') as resp:
                    logging.info(f"{resp.status=} {self._link}{route}")
                    return await resp.read()
        except ClientConnectorError:
            logging.warning(f"Rest api is unreachable")
        except Exception as e:
            logging.warning(f"Rest api is unreachable: {e}")

    async def post_update(self, update: types.Update):
        data = {
            "bot_data": self._bot_data,
        }
        data.update(update.to_python())
        answer = await self._post_json('updates/create/', data)
        logging.info(f"{answer=}")

