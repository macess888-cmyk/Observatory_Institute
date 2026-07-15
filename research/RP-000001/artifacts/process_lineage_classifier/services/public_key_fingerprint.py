import hashlib

from models import PublicKeyMaterial


class PublicKeyFingerprintError(ValueError):
    """Raised when public-key fingerprint generation or validation fails."""


class PublicKeyFingerprintService:
    """Generates and validates deterministic SHA-256 public-key fingerprints."""

    def generate(
        self,
        public_key_value: str,
    ) -> str:
        encoded_key = self._extract_public_key_bytes(
            public_key_value
        )

        digest = hashlib.sha256(encoded_key).hexdigest()

        return f"sha256:{digest}"

    def validate(
        self,
        public_key_value: str,
        expected_fingerprint: str,
    ) -> bool:
        self._validate_fingerprint(
            expected_fingerprint,
            "expected_fingerprint",
        )

        actual_fingerprint = self.generate(
            public_key_value
        )

        if actual_fingerprint != expected_fingerprint:
            raise PublicKeyFingerprintError(
                "Public-key fingerprint mismatch."
            )

        return True

    def validate_material(
        self,
        material: PublicKeyMaterial,
    ) -> bool:
        if not isinstance(material, PublicKeyMaterial):
            raise TypeError(
                "material must be a PublicKeyMaterial."
            )

        return self.validate(
            material.public_key_value,
            material.public_key_fingerprint,
        )

    @staticmethod
    def _extract_public_key_bytes(
        public_key_value: str,
    ) -> bytes:
        if not isinstance(public_key_value, str):
            raise TypeError(
                "public_key_value must be a string."
            )

        if not public_key_value.strip():
            raise PublicKeyFingerprintError(
                "public_key_value must not be empty."
            )

        prefix = "ed25519:"

        if not public_key_value.startswith(prefix):
            raise PublicKeyFingerprintError(
                "public_key_value must use the ed25519 prefix."
            )

        encoded_key = public_key_value.removeprefix(prefix)

        if len(encoded_key) != 64:
            raise PublicKeyFingerprintError(
                "public_key_value must contain "
                "64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in encoded_key
        ):
            raise PublicKeyFingerprintError(
                "public_key_value must contain only lowercase "
                "hexadecimal characters."
            )

        return bytes.fromhex(encoded_key)

    @staticmethod
    def _validate_fingerprint(
        fingerprint: str,
        field_name: str,
    ) -> None:
        if not isinstance(fingerprint, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        prefix = "sha256:"

        if not fingerprint.startswith(prefix):
            raise PublicKeyFingerprintError(
                f"{field_name} must use the sha256 prefix."
            )

        digest = fingerprint.removeprefix(prefix)

        if len(digest) != 64:
            raise PublicKeyFingerprintError(
                f"{field_name} must contain "
                "64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest
        ):
            raise PublicKeyFingerprintError(
                f"{field_name} must contain only lowercase "
                "hexadecimal characters."
            )