from taskiq_aio_pika import AioPikaBroker

from delivery_service.infrastructure.tasks.telegram import (
    check_for_update_telegram_users,
)


def setup_tasks(broker: AioPikaBroker) -> None:
    broker.register_task(
        check_for_update_telegram_users,
        task_name="Check telegram data",
        schedule=[{"cron": "*/15 * * * *"}],
    )
