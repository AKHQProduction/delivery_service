from typing import NewType
from uuid import UUID

OrderID = NewType("OrderID", UUID)
OrderLineID = NewType("OrderLineID", int)
