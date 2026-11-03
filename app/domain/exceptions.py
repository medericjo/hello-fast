"""Domain-level errors. Outer layers translate these to HTTP responses."""


class DomainError(Exception):
    """Base class for all domain errors."""


class NotFoundError(DomainError):
    def __init__(self, resource: str, resource_id: int) -> None:
        super().__init__(f"{resource} with id={resource_id} not found")
        self.resource = resource
        self.resource_id = resource_id


class ExternalServiceError(DomainError):
    """The upstream data source failed or is unreachable."""
