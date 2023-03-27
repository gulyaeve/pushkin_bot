from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

reg_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Регистрация водителя",
                callback_data="reg_menu",
            )
        ]
    ]
)


def make_driver_reg_menu(fio: bool = False, phone: bool = False, passport: bool = False, passport_photo: bool = False):
    reg_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="ФИО" if not fio else "ФИО ✅",
                    callback_data="driver_fio",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Телефон" if not phone else "Телефон ✅",
                    callback_data="driver_phone",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Паспорт" if not passport else "Паспорт ✅",
                    callback_data="driver_passport",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Фото паспорта" if not passport_photo else "Фото паспорта ✅",
                    callback_data="driver_passport_photo",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️Назад",
                    callback_data="driver_back",
                ),
                InlineKeyboardButton(
                    text="Готово",
                    callback_data="driver_ready",
                )
            ],

        ],
        row_width=1,
    )
    return reg_menu
