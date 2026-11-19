import os

from locust import HttpUser, between, task

key = os.environ.get("LOCUST_TELEGRAM_WEBHOOK_SECRET", "")


class TelegramBotUser(HttpUser):
    host = os.environ.get("LOCUST_TARGET_URL", "http://127.0.0.1:8000")
    wait_time = between(1, 5)  # Пользователи будут отправлять запрос каждые 1-5 секунд

    @task
    def send_message(self):
        if not key:
            raise RuntimeError("LOCUST_TELEGRAM_WEBHOOK_SECRET is required")
        headers = {"X-Telegram-Bot-Api-Secret-Token": key}
        self.client.post(
            "/telegram_webhook",
            json={
                "update_id": 123456789,
                "message": {
                    "message_id": 123,
                    "from": {
                        "id": 900000001,
                        "is_bot": False,
                        "first_name": "Test",
                        "username": "testuser",
                    },
                    "chat": {
                        "id": 900000001,
                        "first_name": "Test",
                        "username": "testuser",
                        "type": "private",
                    },
                    "date": 9000000020,
                    "text": "/start",
                },
            },
            headers=headers,
        )
