from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class DriverCallbacks:
    driver_reg_menu = "driver_reg_menu"
    driver_fio = "driver_fio"
    driver_phone = "driver_phone"
    driver_passport = "driver_passport"
    driver_passport_photo = "driver_passport_photo"
    driver_back = "driver_back"
    driver_ready = "driver_ready"
    driver_manager_decline = "driver_manager_decline"
    driver_manager_agree = "driver_manager_agree"
    driver_help = "driver_help"
    driver_fare = "driver_fare"


reg_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Регистрация водителя",
                callback_data=DriverCallbacks.driver_reg_menu,
            )
        ]
    ]
)


def make_manager_view(driver_id: int) -> InlineKeyboardMarkup:
    manager_view = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌",
                    callback_data=f"{DriverCallbacks.driver_manager_decline}={driver_id}",
                ),
                InlineKeyboardButton(
                    text="✅",
                    callback_data=f"{DriverCallbacks.driver_manager_agree}={driver_id}",
                ),

            ]
        ]
    )
    return manager_view


def make_driver_reg_menu(fio: bool = False, phone: bool = False, passport: bool = False, passport_photo: bool = False):
    reg_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="ФИО" if not fio else "ФИО ✅",
                    callback_data=DriverCallbacks.driver_fio,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Телефон" if not phone else "Телефон ✅",
                    callback_data=DriverCallbacks.driver_phone,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Паспорт" if not passport else "Паспорт ✅",
                    callback_data=DriverCallbacks.driver_passport,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Фото паспорта" if not passport_photo else "Фото паспорта ✅",
                    callback_data=DriverCallbacks.driver_passport_photo,
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️Назад",
                    callback_data=DriverCallbacks.driver_back,
                ),
                InlineKeyboardButton(
                    text="Готово",
                    callback_data=DriverCallbacks.driver_ready,
                )
            ],

        ],
        row_width=1,
    )
    return reg_menu


driver_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Полезное",
                callback_data=DriverCallbacks.driver_help,
            )
        ],
        [
            InlineKeyboardButton(
                text="Настройки тарифа",
                callback_data=DriverCallbacks.driver_fare,
            )
        ]
    ]
)
