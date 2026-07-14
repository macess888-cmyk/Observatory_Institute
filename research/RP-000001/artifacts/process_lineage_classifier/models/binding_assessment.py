from dataclasses import dataclass

from enums import BindingStatus


@dataclass(frozen=True)
class BindingAssessment:
    """Immutable binding-integrity assessment for prototype version 0.1."""

    binding_status: BindingStatus
    reference_type: str
    reference_value: str
    target_type: str
    target_value: str

    reasons: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.binding_status, BindingStatus):
            raise TypeError("binding_status must be a BindingStatus.")

        required_text_fields = {
            "reference_type": self.reference_type,
            "reference_value": self.reference_value,
            "target_type": self.target_type,
            "target_value": self.target_value,
        }

        for field_name, value in required_text_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")

        tuple_fields = {
            "reasons": self.reasons,
            "missing_evidence": self.missing_evidence,
        }

        for field_name, values in tuple_fields.items():
            if not isinstance(values, tuple):
                raise TypeError(f"{field_name} must be a tuple.")

            if any(not isinstance(value, str) or not value.strip() for value in values):
                raise ValueError(
                    f"{field_name} must contain only non-empty strings."
                )