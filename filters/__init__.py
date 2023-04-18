from aiogram import Dispatcher
from .admin_check import AdminCheck
from .manager_check import ManagerCheck
from .driver_check import DriverCheck
from .active_order_check import ActiveOrderCheck


def setup(dp: Dispatcher):
    dp.filters_factory.bind(AdminCheck)
    dp.filters_factory.bind(ManagerCheck)
    dp.filters_factory.bind(DriverCheck)
    dp.filters_factory.bind(ActiveOrderCheck)
