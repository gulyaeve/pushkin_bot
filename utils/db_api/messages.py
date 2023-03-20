import asyncio
from logging import log, INFO

from utils.db_api.db import Database


class Messages(Database):
    def __init__(self):
        super().__init__()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.create_tables())

    async def create_tables(self):
        sql = """
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            description text NOT NULL UNIQUE,
            content text
        );
        """
        await self._execute(sql, execute=True)

    # Сообщения
    async def add_message(self, description, content):
        sql = "INSERT INTO messages (description, content) VALUES($1, $2) returning *"
        return await self._execute(sql, description, content, fetchrow=True)

    async def select_all_messages(self):
        sql = "SELECT * FROM messages"
        return await self._execute(sql, fetch=True)

    async def get_message_content(self, description):
        return await self._execute("SELECT content FROM messages WHERE description=$1", description, fetchval=True)

    async def get_message_content_by_id(self, message_id):
        return await self._execute("SELECT content FROM messages WHERE id=$1", message_id, fetchval=True)

    async def update_text_content(self, new_text, message_id):
        sql = "UPDATE messages SET content=$1 WHERE id=$2"
        return await self._execute(sql, new_text, message_id, execute=True)

    async def create_message(self, description: str, content: str):
        """
        Сохраняет сообщение в базе данных
        :param description: описание сообщения
        :param content: содержимое сообщения
        """
        message = await self.get_message(description)
        if message is None:
            await self.add_message(
                description=description,
                content=content
            )
            log(INFO, f"Message {description} success save in db")

    async def get_message(self, description: str) -> str:
        """
        Возвращает контент сообщения по описанию из базы данных
        :param description: description in database
        :return: content of message
        """
        try:
            return await self.get_message_content(description)
        except Exception as e:
            raise ValueError(e)
