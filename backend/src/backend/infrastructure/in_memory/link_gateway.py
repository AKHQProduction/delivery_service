from backend.application.usecases.invite_employee.interfaces import (
    Link,
    LinkGateway,
)


class InMemoryLinkGateway(LinkGateway):
    def __init__(self) -> None:
        self.links: dict[str, Link] = {}

    async def add(self, link: Link) -> None:
        self.links[link.payload] = link

    async def load_by_payload(self, payload: str) -> Link | None:
        return self.links.get(payload)

    async def delete(self, payload: str) -> None:
        self.links.pop(payload, None)
