from logging import log, INFO

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp, Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram_inline_paginations.paginator import Paginator

from keyboards.admin import AdminCallbacks
from loader import messages, dp


class TextMessages(StatesGroup):
    Content = State()
    Edit = State()
    SaveText = State()


@dp.callback_query_handler(text="text_back", state=TextMessages.Edit)
@dp.callback_query_handler(Text(startswith="messagespage_"), state=TextMessages.Content)
@dp.callback_query_handler(text=AdminCallbacks.text_messages.value)
async def choose_description(callback: types.CallbackQuery, state: FSMContext):
    page_n = 0
    if callback.data.startswith("messagespage_"):
        page_n = int(callback.data.split("_")[1])
    all_messages = await messages.select_all_messages()
    inline_keyboard = types.InlineKeyboardMarkup()
    for message in all_messages:
        inline_keyboard.add(
            types.InlineKeyboardButton(
                message['description'],
                callback_data=f"message_id={message['id']}")
        )
    messages_inline = Paginator(callback_startswith="messagespage_", data=inline_keyboard)
    await callback.message.edit_text("Выбери описание сообщения:", reply_markup=messages_inline(current_page=page_n))
    await TextMessages.Content.set()


@dp.callback_query_handler(Regexp('message_id=([0-9]*)'), state=TextMessages.Content)
async def choose_content(callback: types.CallbackQuery, state: FSMContext):
    message_id = int(callback.data.split("=")[1])
    message_text = await messages.get_message_content_by_id(message_id)
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="◀️", callback_data="text_back"),
             types.InlineKeyboardButton(text="🖍", callback_data="text_edit")]
        ])
    async with state.proxy() as data:
        data['message_id'] = message_id
    await callback.message.edit_text(message_text, reply_markup=keyboard)
    await TextMessages.Edit.set()


@dp.callback_query_handler(text="text_edit", state=TextMessages.Edit)
async def edit_text(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введи новый текст:")
    await TextMessages.SaveText.set()


@dp.message_handler(state=TextMessages.SaveText)
async def save_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await messages.update_text_content(message.html_text, data['message_id'])
    log(INFO, f"Text edited [{message.html_text}]")
    await message.answer("Текст сохранён")
    await state.finish()

