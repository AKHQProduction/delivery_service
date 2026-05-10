from dishka import FromDishka
from dishka.integrations.taskiq import inject

from backend.application.commands.run_recurring_order_automation import (
    RunRecurringOrderAutomationCommand,
    RunRecurringOrderAutomationCommandHandler,
)


@inject(patch_module=True)
async def generate_recurring_orders(
    handler: FromDishka[RunRecurringOrderAutomationCommandHandler],
) -> None:
    await handler.handle(RunRecurringOrderAutomationCommand())
