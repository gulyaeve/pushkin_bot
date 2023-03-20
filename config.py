from environs import EnvError
from environs import Env

env = Env()
env.read_env()


class Config:
    # Telegram auth:
    telegram_token = env.str("TELEGRAM_API_TOKEN")

    # Bot admins
    bot_admins = env.list("BOT_ADMINS")

    # REST api link for admin application
    rest_link = ""
    try:
        rest_link = env.str("REST_API_ADMIN_LINK")
    except EnvError:
        rest_link = ""

    # REST api token for admin application
    rest_token = ""
    try:
        rest_token = env.str("REST_API_ADMIN_TOKEN")
    except EnvError:
        rest_token = ""

    # Email auth:
    # class Email:
    #     email_server = env.str("EMAIL_SERVER")
    #     email_port = env.int("EMAIL_PORT")
    #     sender_email = env.str("SENDER_EMAIL")
    #     email_login = env.str("EMAIL_LOGIN")
    #     email_password = env.str("EMAIL_PASSWORD")

    # PostgreSQL
    class DBConfig:
        DB_USER = env.str("POSTGRES_USER")
        DB_PASS = env.str("POSTGRES_PASSWORD")
        DB_HOST = env.str("POSTGRES_HOST")
        DB_PORT = env.int("POSTGRES_PORT")
        DB_NAME = env.str("POSTGRES_DB")

    # Redis
    REDIS_HOST = env.str("REDIS_HOST")
    REDIS_PORT = env.int("REDIS_PORT")

    # Proxy
    proxy_url = ""
    try:
        proxy_url = env.str("PROXY_URL")
    except EnvError:
        proxy_url = ""

