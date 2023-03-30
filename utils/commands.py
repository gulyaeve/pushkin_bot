from aiogram import types

from loader import dp


async def set_default_commands():
    """
    Установка команд для бота (кнопка "Меню")
    """
    return await dp.bot.set_my_commands([
        # types.BotCommand(command="/start", description="Начать работу с чат-ботом"),
        # types.BotCommand(command="/auth", description="Авторизация"),
        types.BotCommand(command="/taxi", description="Вызвать такси"),
        types.BotCommand(command="/driver", description="Для водителей"),
        types.BotCommand(command="/promo", description="Узнать акции в Пушкино"),
        types.BotCommand(command="/events", description="Узнать что и где происходит в Пушкино"),
        types.BotCommand(command="/help", description="Помощь по командам чат-бота"),
        types.BotCommand(command="/cancel", description="Отмена текущего действия"),
    ])


help_message = """<b>Команды чат-бота:</b>

    <b>/taxi</b> - Вызвать такси
    
    <b>/driver</b> - Для водителей
    
    <b>/promo</b> - Узнать акции в Пушкино
    
    <b>/events</b> - Узнать что и где происходит в Пушкино
    
    <b>/help</b> - Помощь по командам чат-бота
    
    <b>/cancel</b> - отмена любого текущего действия"""
