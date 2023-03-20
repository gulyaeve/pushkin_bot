from .db import DBmiddleware
from .admin_page_api import AdminPage

from loader import dp

if __name__ == "middlewares":
    dp.middleware.setup(DBmiddleware())
    dp.middleware.setup(AdminPage())
