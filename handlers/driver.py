from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from config import Config
from filters import DriverCheck
from keyboards.driver import reg_button, make_driver_reg_menu, DriverCallbacks
from keyboards.keyboards import auth_phone
from loader import dp, messages, drivers


class DriverStates(StatesGroup):
    FIO = State()
    Phone = State()
    Passport = State()
    PassportPhoto = State()


@dp.message_handler(DriverCheck(), commands=['driver'])
async def driver_start(message: types.Message):
    await message.answer("Вы водитель")


@dp.message_handler(commands=['driver'])
async def driver_start_no_auth(message: types.Message):
    await message.answer(await messages.get_message("driver_reg_prompt"), reply_markup=reg_button)


@dp.callback_query_handler(text=DriverCallbacks.driver_back)
async def driver_start_no_auth(callback: types.CallbackQuery):
    await callback.message.edit_text(await messages.get_message("driver_reg_prompt"), reply_markup=reg_button)


@dp.callback_query_handler(text=DriverCallbacks.driver_reg_menu)
async def driver_reg_menu(callback: types.CallbackQuery):
    driver = await drivers.add_driver(callback.from_user.id)
    menu = make_driver_reg_menu(
        fio=True if driver.fio else False,
        phone=True if driver.phone else False,
        passport=True if driver.passport else False,
        passport_photo=True if driver.passport_photo else False,
    )
    await callback.message.edit_text(await messages.get_message("driver_reg_menu"), reply_markup=menu)


@dp.callback_query_handler(text=DriverCallbacks.driver_fio)
async def driver_fio_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(await messages.get_message("driver_input_fio"))
    await DriverStates.FIO.set()


@dp.message_handler(state=DriverStates.FIO)
async def driver_input_fio(message: types.Message, state: FSMContext):
    if message.text:
        driver = await drivers.update_driver_info(message.from_user.id, fio=message.text)
        menu = make_driver_reg_menu(
            fio=True if driver.fio else False,
            phone=True if driver.phone else False,
            passport=True if driver.passport else False,
            passport_photo=True if driver.passport_photo else False,
        )
        await message.answer(await messages.get_message("driver_correct_input"))
        await message.answer(await messages.get_message("driver_reg_menu"), reply_markup=menu)
        await state.finish()
    else:
        return await message.answer(await messages.get_message("driver_wrong_input"))


@dp.callback_query_handler(text=DriverCallbacks.driver_phone)
async def driver_phone_menu(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(await messages.get_message("driver_input_phone"), reply_markup=auth_phone)
    await DriverStates.Phone.set()


@dp.message_handler(state=DriverStates.Phone, content_types=types.ContentType.CONTACT)
async def driver_input_phone(message: types.Message, state: FSMContext):
    if message.contact.user_id == message.from_user.id:
        phone_number = ''.join([n for n in message.contact.phone_number if n.isdigit()])
        driver = await drivers.update_driver_info(message.from_user.id, phone=phone_number)
        menu = make_driver_reg_menu(
            fio=True if driver.fio else False,
            phone=True if driver.phone else False,
            passport=True if driver.passport else False,
            passport_photo=True if driver.passport_photo else False,
        )
        await message.answer(
            await messages.get_message("driver_correct_input"),
            reply_markup=types.ReplyKeyboardRemove()
        )
        await message.answer(await messages.get_message("driver_reg_menu"), reply_markup=menu)
        await state.finish()
    else:
        return await message.answer(await messages.get_message("wrong_number"))


@dp.message_handler(state=DriverStates.Phone)
async def driver_input_phone(message: types.Message, state: FSMContext):
    if message.text:
        phone_number = ''.join([n for n in message.text if n.isdigit()])
        if len(phone_number) == 11:
            driver = await drivers.update_driver_info(message.from_user.id, phone=phone_number)
            menu = make_driver_reg_menu(
                fio=True if driver.fio else False,
                phone=True if driver.phone else False,
                passport=True if driver.passport else False,
                passport_photo=True if driver.passport_photo else False,
            )
            await message.answer(
                await messages.get_message("driver_correct_input"),
                reply_markup=types.ReplyKeyboardRemove()
            )
            await message.answer(await messages.get_message("driver_reg_menu"), reply_markup=menu)
            await state.finish()
        else:
            return await message.answer(await messages.get_message("wrong_number"))
    else:
        return await message.answer(await messages.get_message("wrong_number"))


@dp.callback_query_handler(text=DriverCallbacks.driver_passport)
async def driver_passport_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(await messages.get_message("driver_input_passport"))
    await DriverStates.Passport.set()


@dp.message_handler(state=DriverStates.Passport)
async def driver_input_passport(message: types.Message, state: FSMContext):
    if message.text:
        driver = await drivers.update_driver_info(message.from_user.id, passport=message.text)
        menu = make_driver_reg_menu(
            fio=True if driver.fio else False,
            phone=True if driver.phone else False,
            passport=True if driver.passport else False,
            passport_photo=True if driver.passport_photo else False,
        )
        await message.answer(await messages.get_message("driver_correct_input"))
        await message.answer(await messages.get_message("driver_reg_menu"), reply_markup=menu)
        await state.finish()
    else:
        return await message.answer(await messages.get_message("driver_wrong_input"))


@dp.callback_query_handler(text=DriverCallbacks.driver_passport_photo)
async def driver_passport_photo_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(await messages.get_message("driver_input_passport_photo"))
    await DriverStates.PassportPhoto.set()


@dp.message_handler(state=DriverStates.PassportPhoto, content_types=types.ContentType.PHOTO)
async def driver_input_passport_photo(message: types.Message, state: FSMContext):
    passport_path = f"passports/{message.from_user.id}.png"
    passport_destination = f"{Config.MEDIA}/{passport_path}"
    await message.photo[-1].download(passport_destination)

    driver = await drivers.update_driver_info(message.from_user.id, passport_photo=passport_path)
    menu = make_driver_reg_menu(
        fio=True if driver.fio else False,
        phone=True if driver.phone else False,
        passport=True if driver.passport else False,
        passport_photo=True if driver.passport_photo else False,
    )
    await message.answer(await messages.get_message("driver_correct_input"))
    await message.answer(await messages.get_message("driver_reg_menu"), reply_markup=menu)
    await state.finish()
