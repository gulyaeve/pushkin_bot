from aiogram import Dispatcher
from .admin_check import AdminCheck
from .manager_check import ManagerCheck
from .driver_check import DriverCheck


def setup(dp: Dispatcher):
    dp.filters_factory.bind(AdminCheck)
    dp.filters_factory.bind(ManagerCheck)
    dp.filters_factory.bind(DriverCheck)
