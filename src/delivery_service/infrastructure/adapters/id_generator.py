from uuid import UUID

from uuid_extensions import uuid7

from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.core.users.service_client import ServiceClientID


class IDGeneratorImpl(IDGenerator):
    def generate_service_client_id(self) -> ServiceClientID:
        return ServiceClientID(UUID(str(uuid7())))
