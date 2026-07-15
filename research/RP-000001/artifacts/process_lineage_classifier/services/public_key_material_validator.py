from models import PublicKeyMaterial


class PublicKeyMaterialError(ValueError):
    """Raised when public-key material fails validation."""


class PublicKeyMaterialValidator:
    """Validates public-key material identity and reference alignment."""

    def validate(
        self,
        material: PublicKeyMaterial,
        *,
        expected_key_id: str | None = None,
        expected_owner_id: str | None = None,
        expected_algorithm: str | None = None,
        expected_encoding: str | None = None,
        expected_fingerprint: str | None = None,
        expected_issuer_id: str | None = None,
    ) -> bool:
        if not isinstance(material, PublicKeyMaterial):
            raise TypeError(
                "material must be a PublicKeyMaterial."
            )

        if material.revoked:
            raise PublicKeyMaterialError(
                "Public-key material has been revoked."
            )

        expected_values = (
            expected_key_id,
            expected_owner_id,
            expected_algorithm,
            expected_encoding,
            expected_fingerprint,
            expected_issuer_id,
        )

        if all(value is None for value in expected_values):
            return True

        if any(value is None for value in expected_values):
            raise PublicKeyMaterialError(
                "Public-key material validation requires a complete "
                "expected reference set."
            )

        self._require_non_empty(
            expected_key_id,
            "expected_key_id",
        )
        self._require_non_empty(
            expected_owner_id,
            "expected_owner_id",
        )
        self._require_non_empty(
            expected_algorithm,
            "expected_algorithm",
        )
        self._require_non_empty(
            expected_encoding,
            "expected_encoding",
        )
        self._require_fingerprint(
            expected_fingerprint,
            "expected_fingerprint",
        )
        self._require_non_empty(
            expected_issuer_id,
            "expected_issuer_id",
        )

        comparisons = (
            (
                material.key_id,
                expected_key_id,
                "key identity",
            ),
            (
                material.owner_id,
                expected_owner_id,
                "owner identity",
            ),
            (
                material.algorithm,
                expected_algorithm,
                "algorithm",
            ),
            (
                material.encoding,
                expected_encoding,
                "encoding",
            ),
            (
                material.public_key_fingerprint,
                expected_fingerprint,
                "fingerprint",
            ),
            (
                material.issuer_id,
                expected_issuer_id,
                "issuer identity",
            ),
        )

        for actual, expected, label in comparisons:
            if actual != expected:
                raise PublicKeyMaterialError(
                    f"Public-key material contains a {label} mismatch."
                )

        return True

    @staticmethod
    def _require_non_empty(
        value: str | None,
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

    @staticmethod
    def _require_fingerprint(
        value: str | None,
        field_name: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        prefix = "sha256:"

        if not value.startswith(prefix):
            raise ValueError(
                f"{field_name} must use the sha256 prefix."
            )

        fingerprint_value = value.removeprefix(prefix)

        if len(fingerprint_value) != 64:
            raise ValueError(
                f"{field_name} must contain 64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in fingerprint_value
        ):
            raise ValueError(
                f"{field_name} must contain only lowercase "
                "hexadecimal characters."
            )