import logging
from dataclasses import dataclass

from backend.application.errors import AccessDeniedError, ValidationError
from backend.application.interfaces import IdentityProvider
from backend.application.policies.access import IsOwner
from backend.application.usecases.invite_employee.interfaces import (
    InviteLinkGenerator,
    Link,
    LinkGateway,
)
from backend.application.vars import ShopRole

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GenerateInviteLinkCommand:
    role: ShopRole
    full_name: str

    def __post_init__(self) -> None:
        if self.role == ShopRole.OWNER:
            raise ValidationError(
                field="role",
                value=self.role,
                acceptable_values=[ShopRole.MANAGER, ShopRole.COURIER],
            )


class GenerateInviteLinkCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        link_generator: InviteLinkGenerator,
        link_gateway: LinkGateway,
    ) -> None:
        self._idp = idp
        self._link_generator = link_generator
        self._link_gateway = link_gateway

    async def handle(self, command: GenerateInviteLinkCommand) -> str:
        current_user = await self._idp.current_user()
        if not IsOwner().is_satisfied_by(current_user):
            raise AccessDeniedError

        link = await self._link_generator.generate()
        await self._link_gateway.add(
            Link(
                payload=link.payload,
                role=command.role,
                shop_id=current_user.shop_id,
                full_name=command.full_name,
            )
        )

        return link.link
