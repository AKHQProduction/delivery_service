import logging
from dataclasses import dataclass

from application.employee.gateway import EmployeeReader
from application.employee.output_data import EmployeeCard
from entities.employee.models import EmployeeId


@dataclass(frozen=True)
class GetEmployeeCardInputData:
    employee_id: int


@dataclass
class GetEmployeeCard:
    employee_reader: EmployeeReader

    async def __call__(self, data: GetEmployeeCardInputData) -> EmployeeCard:
        card = await self.employee_reader.card_by_id(
            EmployeeId(data.employee_id)
        )

        logging.info(
            "Get employee card for employee with id=%s", data.employee_id
        )

        return card
