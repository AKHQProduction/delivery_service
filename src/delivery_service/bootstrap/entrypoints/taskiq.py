from dishka.integrations.taskiq import setup_dishka
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

from delivery_service.bootstrap.configs import (
    load_bot_config,
    load_database_config,
    load_rabbit_config,
    load_redis_config,
)
from delivery_service.bootstrap.containers import taskiq_container
from delivery_service.infrastructure.tasks import setup_tasks


def setup_broker() -> AioPikaBroker:
    rabbit_config = load_rabbit_config()
    redis_config = load_redis_config()
    tg_config = load_bot_config()
    db_config = load_database_config()

    broker = AioPikaBroker(
        url=rabbit_config.uri,
        declare_exchange=True,
        declare_queues_kwargs={"durable": True},
        declare_exchange_kwargs={"durable": True},
    ).with_result_backend(
        result_backend=RedisAsyncResultBackend(
            redis_url=redis_config.taskiq_result
        )
    )

    setup_tasks(broker)
    setup_dishka(
        taskiq_container(
            tg_config=tg_config,
            database_config=db_config,
            redis_config=redis_config,
            rabbit_config=rabbit_config,
        ),
        broker,
    )

    return broker


def setup_scheduler() -> TaskiqScheduler:
    broker = setup_broker()

    return TaskiqScheduler(
        broker=broker, sources=[LabelScheduleSource(broker=broker)]
    )
