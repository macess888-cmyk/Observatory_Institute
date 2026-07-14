from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessState:
    """Immutable declared process state for prototype version 0.1."""

    service_id: str
    runtime_id: str
    execution_id: str
    state_id: str
    host_id: str
    address: str
    authority_role: str
    is_active: bool

    state_hash: str | None = None
    code_version: str | None = None
    environment_id: str | None = None

    def __post_init__(self) -> None:
        required_text_fields = {
            "service_id": self.service_id,
            "runtime_id": self.runtime_id,
            "execution_id": self.execution_id,
            "state_id": self.state_id,
            "host_id": self.host_id,
            "address": self.address,
            "authority_role": self.authority_role,
        }

        for field_name, value in required_text_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")

        if not isinstance(self.is_active, bool):
            raise TypeError("is_active must be a boolean.")

        optional_text_fields = {
            "state_hash": self.state_hash,
            "code_version": self.code_version,
            "environment_id": self.environment_id,
        }

        for field_name, value in optional_text_fields.items():
            if value is not None and (
                not isinstance(value, str) or not value.strip()
            ):
                raise ValueError(
                    f"{field_name} must be None or a non-empty string."
                )