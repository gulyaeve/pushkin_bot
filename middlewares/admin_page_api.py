from logging import log, INFO

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from loader import admin_api


class AdminPage(BaseMiddleware):
    async def on_pre_process_update(self, update: types.Update, data: dict):
        if admin_api:
            await admin_api.post_update(update)
