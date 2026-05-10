from dishka.integrations.taskiq import setup_dishka
from taskiq import AsyncBroker, SimpleRetryMiddleware, TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from backend.bootstrap.config import Config
from backend.bootstrap.entrypoints.di.containers import api_container
from backend.infrastructure.tasks import setup_tasks


def create_taskiq_broker(config: Config) -> AsyncBroker:
    broker = ListQueueBroker(
        url=config.redis_config.task_uri,
    ).with_result_backend(
        RedisAsyncResultBackend(redis_url=config.redis_config.task_uri)
    )
    broker = broker.with_middlewares(
        SimpleRetryMiddleware(default_retry_count=3),
    )
    setup_tasks(broker)
    return broker


def create_taskiq_scheduler(broker: AsyncBroker) -> TaskiqScheduler:
    return TaskiqScheduler(
        broker=broker,
        sources=[LabelScheduleSource(broker)],
    )


def setup_taskiq_broker() -> AsyncBroker:
    config = Config()
    broker = create_taskiq_broker(config)
    setup_dishka(api_container(config), broker)
    return broker


def setup_taskiq_scheduler() -> TaskiqScheduler:
    broker = setup_taskiq_broker()
    return create_taskiq_scheduler(broker)
