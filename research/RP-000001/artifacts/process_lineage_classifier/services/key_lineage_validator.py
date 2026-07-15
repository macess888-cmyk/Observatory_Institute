from models import (
    KeyRevocationRecord,
    KeyRotationRecord,
    SigningKeyIdentity,
)


class KeyLineageError(ValueError):
    """Raised when signing-key lineage fails validation."""


class KeyLineageValidator:
    """Validates key identities, rotations, and revocations as one lineage."""

    def validate(
        self,
        *,
        keys: tuple[SigningKeyIdentity, ...],
        rotations: tuple[KeyRotationRecord, ...],
        revocations: tuple[KeyRevocationRecord, ...],
        expected_owner_id: str,
        expected_algorithm: str,
    ) -> bool:
        self._validate_collections(
            keys=keys,
            rotations=rotations,
            revocations=revocations,
        )
        self._require_non_empty(
            expected_owner_id,
            "expected_owner_id",
        )
        self._require_non_empty(
            expected_algorithm,
            "expected_algorithm",
        )

        self._validate_key_uniqueness(keys)
        self._validate_key_identity_scope(
            keys=keys,
            expected_owner_id=expected_owner_id,
            expected_algorithm=expected_algorithm,
        )
        self._validate_record_counts(
            keys=keys,
            rotations=rotations,
            revocations=revocations,
        )
        self._validate_rotations(
            keys=keys,
            rotations=rotations,
            expected_owner_id=expected_owner_id,
            expected_algorithm=expected_algorithm,
        )
        self._validate_revocations(
            keys=keys,
            rotations=rotations,
            revocations=revocations,
            expected_owner_id=expected_owner_id,
            expected_algorithm=expected_algorithm,
        )
        self._validate_key_states(keys)

        return True

    @staticmethod
    def _validate_collections(
        *,
        keys: tuple[SigningKeyIdentity, ...],
        rotations: tuple[KeyRotationRecord, ...],
        revocations: tuple[KeyRevocationRecord, ...],
    ) -> None:
        if not isinstance(keys, tuple):
            raise TypeError("keys must be a tuple.")

        if not isinstance(rotations, tuple):
            raise TypeError("rotations must be a tuple.")

        if not isinstance(revocations, tuple):
            raise TypeError("revocations must be a tuple.")

        if not keys:
            raise KeyLineageError(
                "Key lineage must contain at least one key."
            )

        if any(
            not isinstance(key, SigningKeyIdentity)
            for key in keys
        ):
            raise TypeError(
                "keys must contain only SigningKeyIdentity instances."
            )

        if any(
            not isinstance(record, KeyRotationRecord)
            for record in rotations
        ):
            raise TypeError(
                "rotations must contain only KeyRotationRecord instances."
            )

        if any(
            not isinstance(record, KeyRevocationRecord)
            for record in revocations
        ):
            raise TypeError(
                "revocations must contain only "
                "KeyRevocationRecord instances."
            )

    @staticmethod
    def _validate_key_uniqueness(
        keys: tuple[SigningKeyIdentity, ...],
    ) -> None:
        key_ids = tuple(key.key_id for key in keys)
        fingerprints = tuple(
            key.public_key_fingerprint
            for key in keys
        )

        if len(set(key_ids)) != len(key_ids):
            raise KeyLineageError(
                "Key lineage contains a duplicate key identity."
            )

        if len(set(fingerprints)) != len(fingerprints):
            raise KeyLineageError(
                "Key lineage contains a duplicate key fingerprint."
            )

    @staticmethod
    def _validate_key_identity_scope(
        *,
        keys: tuple[SigningKeyIdentity, ...],
        expected_owner_id: str,
        expected_algorithm: str,
    ) -> None:
        for key in keys:
            if key.owner_id != expected_owner_id:
                raise KeyLineageError(
                    "Key lineage contains an owner identity mismatch."
                )

            if key.algorithm != expected_algorithm:
                raise KeyLineageError(
                    "Key lineage contains an algorithm mismatch."
                )

    @staticmethod
    def _validate_record_counts(
        *,
        keys: tuple[SigningKeyIdentity, ...],
        rotations: tuple[KeyRotationRecord, ...],
        revocations: tuple[KeyRevocationRecord, ...],
    ) -> None:
        expected_transition_count = len(keys) - 1

        if len(rotations) != expected_transition_count:
            raise KeyLineageError(
                "Key lineage rotation count must equal key count minus one."
            )

        if len(revocations) != expected_transition_count:
            raise KeyLineageError(
                "Key lineage revocation count must equal key count minus one."
            )

    @staticmethod
    def _validate_rotations(
        *,
        keys: tuple[SigningKeyIdentity, ...],
        rotations: tuple[KeyRotationRecord, ...],
        expected_owner_id: str,
        expected_algorithm: str,
    ) -> None:
        for index, rotation in enumerate(rotations):
            previous_key = keys[index]
            new_key = keys[index + 1]

            if rotation.owner_id != expected_owner_id:
                raise KeyLineageError(
                    "Key rotation contains an owner identity mismatch."
                )

            if rotation.algorithm != expected_algorithm:
                raise KeyLineageError(
                    "Key rotation contains an algorithm mismatch."
                )

            if rotation.previous_key_id != previous_key.key_id:
                raise KeyLineageError(
                    "Key rotation contains a previous key identity mismatch."
                )

            if (
                rotation.previous_key_fingerprint
                != previous_key.public_key_fingerprint
            ):
                raise KeyLineageError(
                    "Key rotation contains a previous key fingerprint "
                    "mismatch."
                )

            if rotation.new_key_id != new_key.key_id:
                raise KeyLineageError(
                    "Key rotation contains a new key identity mismatch."
                )

            if (
                rotation.new_key_fingerprint
                != new_key.public_key_fingerprint
            ):
                raise KeyLineageError(
                    "Key rotation contains a new key fingerprint mismatch."
                )

            if rotation.rotated_at < new_key.created_at:
                raise KeyLineageError(
                    "Key rotation cannot occur before new key creation."
                )

    @staticmethod
    def _validate_revocations(
        *,
        keys: tuple[SigningKeyIdentity, ...],
        rotations: tuple[KeyRotationRecord, ...],
        revocations: tuple[KeyRevocationRecord, ...],
        expected_owner_id: str,
        expected_algorithm: str,
    ) -> None:
        for index, revocation in enumerate(revocations):
            retired_key = keys[index]
            rotation = rotations[index]

            if revocation.owner_id != expected_owner_id:
                raise KeyLineageError(
                    "Key revocation contains an owner identity mismatch."
                )

            if revocation.algorithm != expected_algorithm:
                raise KeyLineageError(
                    "Key revocation contains an algorithm mismatch."
                )

            if revocation.key_id != retired_key.key_id:
                raise KeyLineageError(
                    "Key lineage contains a revocation key identity "
                    "mismatch."
                )

            if (
                revocation.key_fingerprint
                != retired_key.public_key_fingerprint
            ):
                raise KeyLineageError(
                    "Key lineage contains a revocation key fingerprint "
                    "mismatch."
                )

            if revocation.revoked_at < rotation.rotated_at:
                raise KeyLineageError(
                    "Key revocation cannot occur before rotation."
                )

            if revocation.permanent is not True:
                raise KeyLineageError(
                    "Key lineage requires permanent revocation records."
                )

    @staticmethod
    def _validate_key_states(
        keys: tuple[SigningKeyIdentity, ...],
    ) -> None:
        retired_keys = keys[:-1]
        active_key = keys[-1]

        if any(key.revoked is not True for key in retired_keys):
            raise KeyLineageError(
                "Every retired key must be marked revoked."
            )

        if active_key.revoked is not False:
            raise KeyLineageError(
                "The active key must not be revoked."
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