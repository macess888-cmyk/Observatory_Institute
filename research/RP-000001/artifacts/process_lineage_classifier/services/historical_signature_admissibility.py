from dataclasses import dataclass
from datetime import datetime

from models import HistoricalSignatureVerificationReceipt
from services.historical_signature_compromise_assessment import (
    HistoricalSignatureCompromiseAssessment,
)


class HistoricalSignatureAdmissibilityError(ValueError):
    """Raised when historical signature admissibility fails."""


@dataclass(frozen=True, slots=True)
class HistoricalSignatureAdmissibilityAssessment:
    """Observer-only admissibility assessment for a historical signature."""

    admissibility_id: str

    receipt_id: str | None
    verification_id: str | None
    signature_id: str | None
    key_id: str | None
    public_key_fingerprint: str | None

    compromise_assessment_id: str | None
    compromise_event_id: str | None

    assessed_by: str
    assessed_at: datetime

    verification_evidence_available: bool
    compromise_evidence_available: bool
    historical_validity_preserved: bool | None

    outcome: str
    admissible: bool
    hold_required: bool
    rejected: bool

    authorization_granted: bool = False
    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        self._require_non_empty(
            self.admissibility_id,
            "admissibility_id",
        )
        self._require_non_empty(
            self.assessed_by,
            "assessed_by",
        )
        self._validate_datetime(
            self.assessed_at,
            "assessed_at",
        )

        for field_name, value in (
            (
                "verification_evidence_available",
                self.verification_evidence_available,
            ),
            (
                "compromise_evidence_available",
                self.compromise_evidence_available,
            ),
            ("admissible", self.admissible),
            ("hold_required", self.hold_required),
            ("rejected", self.rejected),
            (
                "authorization_granted",
                self.authorization_granted,
            ),
            (
                "execution_requested",
                self.execution_requested,
            ),
            (
                "side_effects_permitted",
                self.side_effects_permitted,
            ),
        ):
            if not isinstance(value, bool):
                raise TypeError(
                    f"{field_name} must be a boolean."
                )

        if (
            self.historical_validity_preserved
            is not None
            and not isinstance(
                self.historical_validity_preserved,
                bool,
            )
        ):
            raise TypeError(
                "historical_validity_preserved must be "
                "a boolean or None."
            )

        if self.outcome not in {
            "PASS",
            "HOLD",
            "REJECT",
        }:
            raise ValueError(
                "outcome must be PASS, HOLD, or REJECT."
            )

        expected_flags = {
            "PASS": (True, False, False),
            "HOLD": (False, True, False),
            "REJECT": (False, False, True),
        }[self.outcome]

        actual_flags = (
            self.admissible,
            self.hold_required,
            self.rejected,
        )

        if actual_flags != expected_flags:
            raise ValueError(
                "Outcome flags must match the declared outcome."
            )

        if self.authorization_granted is not False:
            raise ValueError(
                "Historical signature admissibility must not "
                "grant authorization."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "Historical signature admissibility must remain "
                "observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "Historical signature admissibility must not "
                "permit side effects."
            )

    @staticmethod
    def _validate_datetime(
        value: datetime,
        field_name: str,
    ) -> None:
        if not isinstance(value, datetime):
            raise TypeError(
                f"{field_name} must be a datetime."
            )

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                f"{field_name} must be timezone-aware."
            )

    @staticmethod
    def _require_non_empty(
        value: str,
        field_name: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"{field_name} must not be empty."
            )


class HistoricalSignatureAdmissibilityService:
    """Combines historical verification and compromise evidence."""

    def assess(
        self,
        *,
        admissibility_id: str,
        receipt: HistoricalSignatureVerificationReceipt | None,
        compromise_assessment: (
            HistoricalSignatureCompromiseAssessment | None
        ),
        assessed_by: str,
        assessed_at: datetime,
    ) -> HistoricalSignatureAdmissibilityAssessment:
        self._require_non_empty(
            admissibility_id,
            "admissibility_id",
        )
        self._require_non_empty(
            assessed_by,
            "assessed_by",
        )
        self._validate_datetime(
            assessed_at,
            "assessed_at",
        )

        if (
            receipt is not None
            and not isinstance(
                receipt,
                HistoricalSignatureVerificationReceipt,
            )
        ):
            raise TypeError(
                "receipt must be a "
                "HistoricalSignatureVerificationReceipt or None."
            )

        if (
            compromise_assessment is not None
            and not isinstance(
                compromise_assessment,
                HistoricalSignatureCompromiseAssessment,
            )
        ):
            raise TypeError(
                "compromise_assessment must be a "
                "HistoricalSignatureCompromiseAssessment or None."
            )

        if receipt is not None:
            if receipt.verified is not True:
                raise HistoricalSignatureAdmissibilityError(
                    "Admissibility requires a verified receipt."
                )

            if assessed_at < receipt.verified_at:
                raise HistoricalSignatureAdmissibilityError(
                    "Admissibility assessment cannot occur "
                    "before verification."
                )

        if (
            receipt is not None
            and compromise_assessment is not None
        ):
            self._validate_reference_binding(
                receipt,
                compromise_assessment,
            )

        if receipt is None or compromise_assessment is None:
            outcome = "HOLD"
            admissible = False
            hold_required = True
            rejected = False
            historical_validity_preserved = (
                None
                if compromise_assessment is None
                else compromise_assessment
                .historical_validity_preserved
            )
        elif (
            compromise_assessment
            .historical_validity_preserved
            is True
        ):
            outcome = "PASS"
            admissible = True
            hold_required = False
            rejected = False
            historical_validity_preserved = True
        else:
            outcome = "REJECT"
            admissible = False
            hold_required = False
            rejected = True
            historical_validity_preserved = False

        return HistoricalSignatureAdmissibilityAssessment(
            admissibility_id=admissibility_id,
            receipt_id=(
                receipt.receipt_id
                if receipt is not None
                else None
            ),
            verification_id=(
                receipt.verification_id
                if receipt is not None
                else None
            ),
            signature_id=(
                receipt.signature_id
                if receipt is not None
                else (
                    compromise_assessment.signature_id
                    if compromise_assessment is not None
                    else None
                )
            ),
            key_id=(
                receipt.key_id
                if receipt is not None
                else (
                    compromise_assessment.key_id
                    if compromise_assessment is not None
                    else None
                )
            ),
            public_key_fingerprint=(
                receipt.public_key_fingerprint
                if receipt is not None
                else (
                    compromise_assessment
                    .public_key_fingerprint
                    if compromise_assessment is not None
                    else None
                )
            ),
            compromise_assessment_id=(
                compromise_assessment.assessment_id
                if compromise_assessment is not None
                else None
            ),
            compromise_event_id=(
                compromise_assessment.compromise_event_id
                if compromise_assessment is not None
                else None
            ),
            assessed_by=assessed_by,
            assessed_at=assessed_at,
            verification_evidence_available=(
                receipt is not None
            ),
            compromise_evidence_available=(
                compromise_assessment is not None
            ),
            historical_validity_preserved=(
                historical_validity_preserved
            ),
            outcome=outcome,
            admissible=admissible,
            hold_required=hold_required,
            rejected=rejected,
            authorization_granted=False,
            execution_requested=False,
            side_effects_permitted=False,
        )

    @staticmethod
    def _validate_reference_binding(
        receipt: HistoricalSignatureVerificationReceipt,
        assessment: HistoricalSignatureCompromiseAssessment,
    ) -> None:
        if assessment.receipt_id != receipt.receipt_id:
            raise HistoricalSignatureAdmissibilityError(
                "Receipt and compromise assessment contain "
                "a receipt identity mismatch."
            )

        if assessment.signature_id != receipt.signature_id:
            raise HistoricalSignatureAdmissibilityError(
                "Receipt and compromise assessment contain "
                "a signature identity mismatch."
            )

        if assessment.key_id != receipt.key_id:
            raise HistoricalSignatureAdmissibilityError(
                "Receipt and compromise assessment contain "
                "a key identity mismatch."
            )

        if (
            assessment.public_key_fingerprint
            != receipt.public_key_fingerprint
        ):
            raise HistoricalSignatureAdmissibilityError(
                "Receipt and compromise assessment contain "
                "a fingerprint mismatch."
            )

    @staticmethod
    def _validate_datetime(
        value: datetime,
        field_name: str,
    ) -> None:
        if not isinstance(value, datetime):
            raise TypeError(
                f"{field_name} must be a datetime."
            )

        if value.tzinfo is None or value.utcoffset() is None:
            raise HistoricalSignatureAdmissibilityError(
                f"{field_name} must be timezone-aware."
            )

    @staticmethod
    def _require_non_empty(
        value: str,
        field_name: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        if not value.strip():
            raise HistoricalSignatureAdmissibilityError(
                f"{field_name} must not be empty."
            )