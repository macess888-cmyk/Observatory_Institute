from models import DetachedSignature


class DetachedSignatureError(ValueError):
    """Raised when a detached signature fails validation."""


class DetachedSignatureValidator:
    """Validates detached-signature identity and content references."""

    def validate(
        self,
        signature: DetachedSignature,
        *,
        expected_key_id: str | None = None,
        expected_subject_id: str | None = None,
        expected_subject_type: str | None = None,
        expected_content_digest: str | None = None,
        expected_signer_id: str | None = None,
    ) -> bool:
        if not isinstance(signature, DetachedSignature):
            raise TypeError(
                "signature must be a DetachedSignature."
            )

        expected_values = (
            expected_key_id,
            expected_subject_id,
            expected_subject_type,
            expected_content_digest,
            expected_signer_id,
        )

        if all(value is None for value in expected_values):
            return True

        if any(value is None for value in expected_values):
            raise DetachedSignatureError(
                "Detached-signature validation requires a complete "
                "expected reference set."
            )

        self._require_non_empty(
            expected_key_id,
            "expected_key_id",
        )
        self._require_non_empty(
            expected_subject_id,
            "expected_subject_id",
        )
        self._require_non_empty(
            expected_subject_type,
            "expected_subject_type",
        )
        self._require_digest(
            expected_content_digest,
            "expected_content_digest",
        )
        self._require_non_empty(
            expected_signer_id,
            "expected_signer_id",
        )

        comparisons = (
            (
                signature.key_id,
                expected_key_id,
                "key identity",
            ),
            (
                signature.subject_id,
                expected_subject_id,
                "subject identity",
            ),
            (
                signature.subject_type,
                expected_subject_type,
                "subject type",
            ),
            (
                signature.content_digest,
                expected_content_digest,
                "content digest",
            ),
            (
                signature.signer_id,
                expected_signer_id,
                "signer identity",
            ),
        )

        for actual, expected, label in comparisons:
            if actual != expected:
                raise DetachedSignatureError(
                    f"Detached signature contains a {label} mismatch."
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
    def _require_digest(
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

        digest_value = value.removeprefix(prefix)

        if len(digest_value) != 64:
            raise ValueError(
                f"{field_name} must contain 64 hexadecimal characters."
            )

        if any(
            character not in "0123456789abcdef"
            for character in digest_value
        ):
            raise ValueError(
                f"{field_name} must contain only lowercase "
                "hexadecimal characters."
            )