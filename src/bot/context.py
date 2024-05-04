import time

from telebot.types import Message


class Context:
    def __init__(self, start_node, faiss_idx):
        self.is_subscribed = False
        self.user_message_history = []
        self.bot_message_history = []
        self.current_node = start_node
        self.faiss_idx = faiss_idx
        self.daily_statuses = {}
        self.misc = {}

    def get_chat_id(self):
        if len(self.user_message_history) == 0:
            return None
        return self.user_message_history[-1].chat.id

    def get_user_id(self):
        if len(self.user_message_history) == 0:
            return None
        return self.user_message_history[-1].chat.id

    def last_message_datetime(self):
        user_messages = self.user_message_history
        bot_messages = self.bot_message_history

        last_user_dt = user_messages[-1].date if user_messages else None
        last_bot_dt = bot_messages[-1].date if bot_messages else None

        if last_user_dt is not None and last_bot_dt is not None:
            return max(last_user_dt, last_bot_dt)
        elif last_user_dt is not None:
            return last_user_dt
        elif last_bot_dt is not None:
            return last_bot_dt
        else:
            return None

    def last_user_message(self):
        if len(self.user_message_history) == 0:
            return None
        return self.user_message_history[-1].text

    def last_bot_message(self):
        if len(self.bot_message_history) == 0:
            return None
        return self.bot_message_history[-1].text

    def add_response(self, response):
        self.bot_message_history.append(
            Message(
                len(self.bot_message_history),
                None,
                time.time(),
                self.get_chat_id(),
                None,
                {"text": response},
                None
            )
        )
