from dataclasses import dataclass
from datetime import datetime

from models import (
    HistoricalSignatureVerificationReceipt,
    KeyCompromiseEvent,
)


class HistoricalSignatureCompromiseAssessmentError(ValueError):
    """Raised when historical compromise assessment fails."""


@dataclass(frozen=True, slots=True)
class HistoricalSignatureCompromiseAssessment:
    """Observer-only assessment of signature timing against compromise."""

    assessment_id: str
    receipt_id: str
    verification_id: str
    signature_id: str

    key_id: str
    material_id: str
    public_key_fingerprint: str

    compromise_event_id: str
    compromise_type: str

    signed_at: datetime
    compromise_effective_at: datetime
    compromise_detected_at: datetime
    compromise_recorded_at: datetime
    assessed_at: datetime

    assessed_by: str

    signature_precedes_compromise: bool
    signature_at_or_after_compromise: bool
    historical_validity_preserved: bool
    automatic_retroactive_invalidation: bool

    status: str

    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("assessment_id", self.assessment_id),
            ("receipt_id", self.receipt_id),
            ("verification_id", self.verification_id),
            ("signature_id", self.signature_id),
            ("key_id", self.key_id),
            ("material_id", self.material_id),
            (
                "public_key_fingerprint",
                self.public_key_fingerprint,
            ),
            (
                "compromise_event_id",
                self.compromise_event_id,
            ),
            ("compromise_type", self.compromise_type),
            ("assessed_by", self.assessed_by),
            ("status", self.status),
        ):
            self._require_non_empty(value, field_name)

        self._validate_digest(
            self.public_key_fingerprint,
            "public_key_fingerprint",
        )

        for field_name, value in (
            ("signed_at", self.signed_at),
            (
                "compromise_effective_at",
                self.compromise_effective_at,
            ),
            (
                "compromise_detected_at",
                self.compromise_detected_at,
            ),
            (
                "compromise_recorded_at",
                self.compromise_recorded_at,
            ),
            ("assessed_at", self.assessed_at),
        ):
            self._validate_datetime(value, field_name)

        for field_name, value in (
            (
                "signature_precedes_compromise",
                self.signature_precedes_compromise,
            ),
            (
                "signature_at_or_after_compromise",
                self.signature_at_or_after_compromise,
            ),
            (
                "historical_validity_preserved",
                self.historical_validity_preserved,
            ),
            (
                "automatic_retroactive_invalidation",
                self.automatic_retroactive_invalidation,
            ),
        ):
            if not isinstance(value, bool):
                raise TypeError(
                    f"{field_name} must be a boolean."
                )

        if (
            self.signature_precedes_compromise
            == self.signature_at_or_after_compromise
        ):
            raise ValueError(
                "Exactly one compromise timing classification "
                "must be true."
            )

        expected_preserved = (
            self.signature_precedes_compromise
        )

        if (
            self.historical_validity_preserved
            is not expected_preserved
        ):
            raise ValueError(
                "historical_validity_preserved must match "
                "the compromise timing classification."
            )

        if (
            self.automatic_retroactive_invalidation
            is not False
        ):
            raise ValueError(
                "Historical compromise assessment must not "
                "automatically invalidate historical signatures."
            )

        expected_status = (
            "PRE_COMPROMISE_VALID"
            if self.signature_precedes_compromise
            else "AT_OR_AFTER_COMPROMISE"
        )

        if self.status != expected_status:
            raise ValueError(
                "status must match the compromise timing "
                "classification."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "HistoricalSignatureCompromiseAssessment "
                "must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "HistoricalSignatureCompromiseAssessment "
                "must not permit side effects."
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

        if (
            value.tzinfo is None
            or value.utcoffset() is None
        ):
            raise ValueError(
                f"{field_name} must be timezone-aware."
            )

    @staticmethod
    def _validate_digest(
        digest: str,
        field_name: str,
    ) -> None:
        if not isinstance(digest, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        prefix = "sha256:"

        if not digest.startswith(prefix):
            raise ValueError(
                f"{field_name} must use the sha256 prefix."
            )

        digest_value = digest.removeprefix(prefix)

        if len(digest_value) != 64:
            raise ValueError(
                f"{field_name} must contain "
                "64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise ValueError(
                f"{field_name} must contain only lowercase "
                "hexadecimal characters."
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


class HistoricalSignatureCompromiseAssessmentService:
    """Assesses signature time against confirmed compromise time."""

    def assess(
        self,
        *,
        assessment_id: str,
        receipt: HistoricalSignatureVerificationReceipt,
        compromise_event: KeyCompromiseEvent,
        assessed_by: str,
        assessed_at: datetime,
    ) -> HistoricalSignatureCompromiseAssessment:
        self._require_non_empty(
            assessment_id,
            "assessment_id",
        )
        self._require_non_empty(
            assessed_by,
            "assessed_by",
        )

        if not isinstance(
            receipt,
            HistoricalSignatureVerificationReceipt,
        ):
            raise TypeError(
                "receipt must be a "
                "HistoricalSignatureVerificationReceipt."
            )

        if not isinstance(
            compromise_event,
            KeyCompromiseEvent,
        ):
            raise TypeError(
                "compromise_event must be a KeyCompromiseEvent."
            )

        self._validate_datetime(
            assessed_at,
            "assessed_at",
        )

        if receipt.verified is not True:
            raise HistoricalSignatureCompromiseAssessmentError(
                "Assessment requires a verified receipt."
            )

        if compromise_event.confirmed is not True:
            raise HistoricalSignatureCompromiseAssessmentError(
                "Assessment requires a confirmed compromise event."
            )

        if receipt.key_id != compromise_event.key_id:
            raise HistoricalSignatureCompromiseAssessmentError(
                "Receipt and compromise event contain a key "
                "identity mismatch."
            )

        if (
            receipt.public_key_fingerprint
            != compromise_event.public_key_fingerprint
        ):
            raise HistoricalSignatureCompromiseAssessmentError(
                "Receipt and compromise event contain a "
                "fingerprint mismatch."
            )

        if assessed_at < compromise_event.recorded_at:
            raise HistoricalSignatureCompromiseAssessmentError(
                "Assessment cannot occur before compromise recording."
            )

        signature_precedes_compromise = (
            receipt.signed_at
            < compromise_event.effective_at
        )
        signature_at_or_after_compromise = (
            receipt.signed_at
            >= compromise_event.effective_at
        )

        historical_validity_preserved = (
            signature_precedes_compromise
        )

        status = (
            "PRE_COMPROMISE_VALID"
            if signature_precedes_compromise
            else "AT_OR_AFTER_COMPROMISE"
        )

        return HistoricalSignatureCompromiseAssessment(
            assessment_id=assessment_id,
            receipt_id=receipt.receipt_id,
            verification_id=receipt.verification_id,
            signature_id=receipt.signature_id,
            key_id=receipt.key_id,
            material_id=compromise_event.material_id,
            public_key_fingerprint=(
                receipt.public_key_fingerprint
            ),
            compromise_event_id=compromise_event.event_id,
            compromise_type=compromise_event.compromise_type,
            signed_at=receipt.signed_at,
            compromise_effective_at=(
                compromise_event.effective_at
            ),
            compromise_detected_at=(
                compromise_event.detected_at
            ),
            compromise_recorded_at=(
                compromise_event.recorded_at
            ),
            assessed_at=assessed_at,
            assessed_by=assessed_by,
            signature_precedes_compromise=(
                signature_precedes_compromise
            ),
            signature_at_or_after_compromise=(
                signature_at_or_after_compromise
            ),
            historical_validity_preserved=(
                historical_validity_preserved
            ),
            automatic_retroactive_invalidation=False,
            status=status,
            execution_requested=False,
            side_effects_permitted=False,
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

        if (
            value.tzinfo is None
            or value.utcoffset() is None
        ):
            raise HistoricalSignatureCompromiseAssessmentError(
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
            raise HistoricalSignatureCompromiseAssessmentError(
                f"{field_name} must not be empty."
            )