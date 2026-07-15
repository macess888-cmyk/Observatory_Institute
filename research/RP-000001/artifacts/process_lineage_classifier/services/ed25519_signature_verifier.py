from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)

from models import (
    DetachedSignature,
    PublicKeyMaterial,
)
from services.public_key_fingerprint import (
    PublicKeyFingerprintError,
    PublicKeyFingerprintService,
)


class Ed25519SignatureVerificationError(ValueError):
    """Raised when mathematical Ed25519 verification fails."""


class Ed25519SignatureVerifier:
    """Performs observer-only mathematical Ed25519 verification."""

    def verify(
        self,
        *,
        message: bytes,
        signature: DetachedSignature,
        public_key_material: PublicKeyMaterial,
    ) -> bool:
        if not isinstance(message, bytes):
            raise TypeError(
                "message must be bytes."
            )

        if not message:
            raise Ed25519SignatureVerificationError(
                "message must not be empty."
            )

        if not isinstance(signature, DetachedSignature):
            raise TypeError(
                "signature must be a DetachedSignature."
            )

        if not isinstance(
            public_key_material,
            PublicKeyMaterial,
        ):
            raise TypeError(
                "public_key_material must be a PublicKeyMaterial."
            )

        self._validate_relationships(
            signature=signature,
            material=public_key_material,
        )

        self._validate_temporal_state(
            signature=signature,
            material=public_key_material,
        )

        self._validate_fingerprint(
            public_key_material,
        )

        public_key_bytes = self._extract_public_key(
            public_key_material.public_key_value
        )
        signature_bytes = self._extract_signature(
            signature.signature_value
        )

        try:
            public_key = Ed25519PublicKey.from_public_bytes(
                public_key_bytes
            )
            public_key.verify(
                signature_bytes,
                message,
            )
        except (
            InvalidSignature,
            ValueError,
        ) as error:
            raise Ed25519SignatureVerificationError(
                "Ed25519 mathematical verification failed."
            ) from error

        return True

    @staticmethod
    def _validate_relationships(
        *,
        signature: DetachedSignature,
        material: PublicKeyMaterial,
    ) -> None:
        if signature.key_id != material.key_id:
            raise Ed25519SignatureVerificationError(
                "Signature contains a key identity mismatch."
            )

        if signature.signer_id != material.owner_id:
            raise Ed25519SignatureVerificationError(
                "Signature contains a signer identity mismatch."
            )

        if signature.algorithm != material.algorithm:
            raise Ed25519SignatureVerificationError(
                "Signature and public-key material contain "
                "an algorithm mismatch."
            )

        if signature.algorithm != "ED25519":
            raise Ed25519SignatureVerificationError(
                "Only ED25519 signatures are supported."
            )

    @staticmethod
    def _validate_temporal_state(
        *,
        signature: DetachedSignature,
        material: PublicKeyMaterial,
    ) -> None:
        if material.revoked:
            raise Ed25519SignatureVerificationError(
                "Public-key material has been revoked."
            )

        if signature.signed_at < material.valid_from:
            raise Ed25519SignatureVerificationError(
                "Signature was created before key validity began."
            )

        if signature.signed_at > material.valid_until:
            raise Ed25519SignatureVerificationError(
                "Signature was created after key validity ended."
            )

    @staticmethod
    def _validate_fingerprint(
        material: PublicKeyMaterial,
    ) -> None:
        try:
            PublicKeyFingerprintService().validate_material(
                material
            )
        except PublicKeyFingerprintError as error:
            raise Ed25519SignatureVerificationError(
                "Public-key fingerprint validation failed."
            ) from error

    @staticmethod
    def _extract_public_key(
        public_key_value: str,
    ) -> bytes:
        prefix = "ed25519:"

        if not public_key_value.startswith(prefix):
            raise Ed25519SignatureVerificationError(
                "public_key_value must use the ed25519 prefix."
            )

        encoded_key = public_key_value.removeprefix(prefix)

        if len(encoded_key) != 64:
            raise Ed25519SignatureVerificationError(
                "public_key_value must contain "
                "64 hexadecimal characters."
            )

        try:
            return bytes.fromhex(encoded_key)
        except ValueError as error:
            raise Ed25519SignatureVerificationError(
                "public_key_value must contain valid hexadecimal."
            ) from error

    @staticmethod
    def _extract_signature(
        signature_value: str,
    ) -> bytes:
        prefix = "ed25519:"

        if not signature_value.startswith(prefix):
            raise Ed25519SignatureVerificationError(
                "signature_value must use the ed25519 prefix."
            )

        encoded_signature = signature_value.removeprefix(
            prefix
        )

        if len(encoded_signature) != 128:
            raise Ed25519SignatureVerificationError(
                "signature_value must contain "
                "128 hexadecimal characters."
            )

        try:
            return bytes.fromhex(encoded_signature)
        except ValueError as error:
            raise Ed25519SignatureVerificationError(
                "signature_value must contain valid hexadecimal."
            ) from error