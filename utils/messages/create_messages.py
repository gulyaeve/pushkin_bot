import json

from loader import messages


async def create_messages():
    with open("templates/messages_template.json", "r", encoding="utf-8") as file:
        new_messages = json.loads(file.read())
    for message in new_messages:
        await messages.create_message(
            message,
            new_messages[message]
        )
