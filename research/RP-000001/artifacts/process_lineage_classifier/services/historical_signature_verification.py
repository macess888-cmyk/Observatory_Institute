from datetime import datetime

from models import (
    DetachedSignature,
    RecoveryIntegrityBundle,
    SignatureVerificationReceipt,
)
from services.canonical_signed_payload import (
    CanonicalSignedPayloadService,
)
from services.ed25519_signature_verifier import (
    Ed25519SignatureVerificationError,
    Ed25519SignatureVerifier,
)
from services.historical_registry_reconstruction import (
    HistoricalRegistryReconstructionError,
    HistoricalRegistryReconstructionService,
)
from services.signature_verification_receipt_service import (
    SignatureVerificationReceiptError,
    SignatureVerificationReceiptService,
)


class HistoricalSignatureVerificationError(ValueError):
    """Raised when historical signature verification fails."""


class HistoricalSignatureVerificationService:
    """Verifies signatures against reconstructed historical registry state."""

    def verify(
        self,
        *,
        bundle: RecoveryIntegrityBundle,
        signature: DetachedSignature,
        registry_id: str,
        signing_registry_version: str,
        verification_registry_version: str,
        snapshots: tuple,
        version_records: tuple,
        receipt_id: str,
        verification_id: str,
        verifier_id: str,
        verified_at: datetime,
    ) -> SignatureVerificationReceipt:
        if not isinstance(bundle, RecoveryIntegrityBundle):
            raise TypeError(
                "bundle must be a RecoveryIntegrityBundle."
            )

        if not isinstance(signature, DetachedSignature):
            raise TypeError(
                "signature must be a DetachedSignature."
            )

        self._require_non_empty(
            registry_id,
            "registry_id",
        )
        self._require_non_empty(
            signing_registry_version,
            "signing_registry_version",
        )
        self._require_non_empty(
            verification_registry_version,
            "verification_registry_version",
        )
        self._require_non_empty(
            receipt_id,
            "receipt_id",
        )
        self._require_non_empty(
            verification_id,
            "verification_id",
        )
        self._require_non_empty(
            verifier_id,
            "verifier_id",
        )

        if not isinstance(snapshots, tuple):
            raise TypeError(
                "snapshots must be a tuple."
            )

        if not isinstance(version_records, tuple):
            raise TypeError(
                "version_records must be a tuple."
            )

        self._validate_datetime(
            verified_at,
            "verified_at",
        )

        if verified_at < signature.signed_at:
            raise HistoricalSignatureVerificationError(
                "Verification cannot occur before signature creation."
            )

        if signature.subject_id != bundle.bundle_id:
            raise HistoricalSignatureVerificationError(
                "Signature contains a subject identity mismatch."
            )

        if (
            signature.subject_type
            != "RECOVERY_INTEGRITY_BUNDLE"
        ):
            raise HistoricalSignatureVerificationError(
                "Signature contains a subject type mismatch."
            )

        payload_service = CanonicalSignedPayloadService()
        payload = payload_service.generate(bundle)
        payload_digest = payload_service.digest(bundle)

        if signature.content_digest != payload_digest:
            raise HistoricalSignatureVerificationError(
                "Signature contains a content digest mismatch."
            )

        reconstruction = HistoricalRegistryReconstructionService()

        try:
            signing_snapshot = reconstruction.reconstruct(
                registry_id=registry_id,
                target_registry_version=signing_registry_version,
                snapshots=snapshots,
                version_records=version_records,
            )
        except HistoricalRegistryReconstructionError as error:
            raise HistoricalSignatureVerificationError(
                "Unable to resolve signing registry version."
            ) from error

        try:
            reconstruction.reconstruct(
                registry_id=registry_id,
                target_registry_version=verification_registry_version,
                snapshots=snapshots,
                version_records=version_records,
            )
        except HistoricalRegistryReconstructionError as error:
            raise HistoricalSignatureVerificationError(
                "Unable to resolve verification registry version."
            ) from error

        signing_material = next(
            (
                material
                for material in signing_snapshot.materials
                if material.key_id == signature.key_id
            ),
            None,
        )

        if signing_material is None:
            raise HistoricalSignatureVerificationError(
                "Signature key is absent from signing-time registry."
            )

        try:
            Ed25519SignatureVerifier().verify(
                message=payload,
                signature=signature,
                public_key_material=signing_material,
            )
        except Ed25519SignatureVerificationError as error:
            raise HistoricalSignatureVerificationError(
                "Historical signature mathematical verification failed."
            ) from error

        try:
            return SignatureVerificationReceiptService().create(
                receipt_id=receipt_id,
                verification_id=verification_id,
                signature_id=signature.signature_id,
                key_id=signing_material.key_id,
                subject_id=bundle.bundle_id,
                subject_type=signature.subject_type,
                content_digest=signature.content_digest,
                payload_digest=payload_digest,
                public_key_fingerprint=(
                    signing_material.public_key_fingerprint
                ),
                algorithm=signature.algorithm,
                signer_id=signature.signer_id,
                verifier_id=verifier_id,
                verified_at=verified_at,
                mathematical_verification=True,
                identity_match=True,
                content_match=True,
                key_valid=True,
            )
        except SignatureVerificationReceiptError as error:
            raise HistoricalSignatureVerificationError(
                "Historical verification receipt creation failed."
            ) from error

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
            raise HistoricalSignatureVerificationError(
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
            raise HistoricalSignatureVerificationError(
                f"{field_name} must not be empty."
            )