from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class ManagerCallbacks:
    manage_drivers = "manage_drivers"
    manage_orders = "manage_orders"
    manage_order_info = "manage_order_info"
    manage_driver_info = "manage_driver_info"
    manage_driver_docs = "manage_driver_docs"
    manage_driver_remove = "manage_driver_remove"


main_manager_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Водители",
                callback_data=ManagerCallbacks.manage_drivers,
            )
        ],
        [
            InlineKeyboardButton(
                text="Заказы",
                callback_data=ManagerCallbacks.manage_orders,
            )
        ],

    ],
)


def make_driver_menu(telegram_id: int) -> InlineKeyboardMarkup:
    driver_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Документы 📃",
                    callback_data=f"{ManagerCallbacks.manage_driver_docs}={telegram_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Отклонить водителя ❌",
                    callback_data=f"{ManagerCallbacks.manage_driver_remove}={telegram_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Назад ◀️",
                    callback_data=ManagerCallbacks.manage_drivers
                )
            ]
        ]
    )
    return driver_menu

