import logging

from taskiq import AsyncBroker

from backend.application.vars import KYIV_TZ
from backend.infrastructure.tasks.tasks import generate_recurring_orders

logger = logging.getLogger(__name__)


def setup_tasks(broker: AsyncBroker) -> None:
    logger.info("Setup tasks")

    broker.register_task(
        generate_recurring_orders,
        task_name="generate_recurring_orders",
        schedule=[
            {
                "cron": "0 0 * * *",
                "cron_offset": str(KYIV_TZ),
                "schedule_id": "daily-recurring-order-generation",
            }
        ],
        retry_on_error=True,
        max_retries=3,
    )
