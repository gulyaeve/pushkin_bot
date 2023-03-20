from handlers.admins.admins import notify_admins
from loader import storage, dp
import filters, middlewares, handlers
from aiogram import executor

from utils.commands import set_default_commands
from utils.messages.create_messages import create_messages
from utils.users.create_user_types import create_user_types


async def on_shutdown(dp):
    await dp.bot.delete_my_commands()
    # await notify_admins("Бот выключен...")
    await storage.close()
    await dp.bot.close()


async def on_startup(dp):
    await set_default_commands()
    await create_user_types()
    await create_messages()
    await notify_admins(f"Бот запущен и готов к работе.\n\n<code>{(await dp.bot.get_me()).to_python()}</code>")


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=on_shutdown, on_startup=on_startup, skip_updates=True)
