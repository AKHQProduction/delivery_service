import logging
from dataclasses import dataclass

from backend.application.errors import AccessDeniedError, FieldError
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
            raise FieldError(
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
        logger.info(
            "Generating invite link",
            extra={"role": command.role, "full_name": command.full_name},
        )

        current_user = await self._idp.current_user()
        logger.debug(
            "Current user retrieved", extra={"user_id": current_user.user_id}
        )

        if not IsOwner().is_satisfied_by(current_user):
            logger.warning(
                "Access denied: user is not owner",
                extra={
                    "user_id": current_user.user_id,
                    "user_role": current_user.role,
                },
            )
            raise AccessDeniedError

        link = await self._link_generator.generate()
        logger.debug("Invite link generated", extra={"payload": link.payload})

        await self._link_gateway.add(
            Link(
                payload=link.payload,
                role=command.role,
                shop_id=current_user.shop_id,
                full_name=command.full_name,
            )
        )
        logger.info(
            "Invite link saved to gateway",
            extra={
                "shop_id": current_user.shop_id,
                "role": command.role,
                "full_name": command.full_name,
            },
        )

        return link.link
