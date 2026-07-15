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
from services.signature_verification_receipt_service import (
    SignatureVerificationReceiptError,
    SignatureVerificationReceiptService,
)
from services.trusted_key_registry import (
    TrustedKeyRegistry,
    TrustedKeyRegistryError,
)


class TrustedSignatureVerificationError(ValueError):
    """Raised when trusted signature verification fails."""


class TrustedSignatureVerificationService:
    """Verifies a signed recovery bundle using trusted key material."""

    def verify(
        self,
        *,
        bundle: RecoveryIntegrityBundle,
        signature: DetachedSignature,
        registry: TrustedKeyRegistry,
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

        if not isinstance(registry, TrustedKeyRegistry):
            raise TypeError(
                "registry must be a TrustedKeyRegistry."
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

        self._validate_datetime(
            verified_at,
            "verified_at",
        )

        if verified_at < signature.signed_at:
            raise TrustedSignatureVerificationError(
                "Verification cannot occur before signature creation."
            )

        self._validate_subject_relationship(
            bundle=bundle,
            signature=signature,
        )

        payload_service = CanonicalSignedPayloadService()
        payload = payload_service.generate(bundle)
        payload_digest = payload_service.digest(bundle)

        if signature.content_digest != payload_digest:
            raise TrustedSignatureVerificationError(
                "Signature contains a content digest mismatch."
            )

        try:
            public_key_material = registry.get(
                signature.key_id
            )
        except TrustedKeyRegistryError as error:
            raise TrustedSignatureVerificationError(
                "Signature references an unknown trusted key."
            ) from error

        try:
            Ed25519SignatureVerifier().verify(
                message=payload,
                signature=signature,
                public_key_material=public_key_material,
            )
        except Ed25519SignatureVerificationError as error:
            message = str(error)

            if "revoked" in message.lower():
                raise TrustedSignatureVerificationError(
                    "Trusted public-key material has been revoked."
                ) from error

            raise TrustedSignatureVerificationError(
                "Trusted signature mathematical verification failed."
            ) from error

        try:
            return SignatureVerificationReceiptService().create(
                receipt_id=receipt_id,
                verification_id=verification_id,
                signature_id=signature.signature_id,
                key_id=public_key_material.key_id,
                subject_id=bundle.bundle_id,
                subject_type=signature.subject_type,
                content_digest=signature.content_digest,
                payload_digest=payload_digest,
                public_key_fingerprint=(
                    public_key_material.public_key_fingerprint
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
            raise TrustedSignatureVerificationError(
                "Signature-verification receipt creation failed."
            ) from error

    @staticmethod
    def _validate_subject_relationship(
        *,
        bundle: RecoveryIntegrityBundle,
        signature: DetachedSignature,
    ) -> None:
        if signature.subject_id != bundle.bundle_id:
            raise TrustedSignatureVerificationError(
                "Signature contains a subject identity mismatch."
            )

        if (
            signature.subject_type
            != "RECOVERY_INTEGRITY_BUNDLE"
        ):
            raise TrustedSignatureVerificationError(
                "Signature contains a subject type mismatch."
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
            raise TrustedSignatureVerificationError(
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
            raise TrustedSignatureVerificationError(
                f"{field_name} must not be empty."
            )