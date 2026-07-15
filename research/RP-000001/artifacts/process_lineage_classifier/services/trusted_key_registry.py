from models import PublicKeyMaterial
from services.public_key_fingerprint import (
    PublicKeyFingerprintError,
    PublicKeyFingerprintService,
)


class TrustedKeyRegistryError(ValueError):
    """Raised when trusted-key registry validation fails."""


class TrustedKeyRegistry:
    """Observer-only in-memory registry of trusted public-key material."""

    execution_requested = False
    side_effects_permitted = False

    def __init__(
        self,
        *,
        expected_owner_id: str | None = None,
        expected_issuer_id: str | None = None,
    ) -> None:
        if expected_owner_id is not None:
            self._require_non_empty(
                expected_owner_id,
                "expected_owner_id",
            )

        if expected_issuer_id is not None:
            self._require_non_empty(
                expected_issuer_id,
                "expected_issuer_id",
            )

        self._expected_owner_id = expected_owner_id
        self._expected_issuer_id = expected_issuer_id

        self._materials_by_key_id: dict[
            str,
            PublicKeyMaterial,
        ] = {}

        self._key_ids_by_fingerprint: dict[
            str,
            str,
        ] = {}

        self._key_ids_by_material_id: dict[
            str,
            str,
        ] = {}

        self._registration_order: list[str] = []

    def register(
        self,
        material: PublicKeyMaterial,
    ) -> bool:
        if not isinstance(material, PublicKeyMaterial):
            raise TypeError(
                "material must be a PublicKeyMaterial."
            )

        if material.revoked:
            raise TrustedKeyRegistryError(
                "Revoked public-key material cannot be registered."
            )

        self._validate_scope(material)
        self._validate_fingerprint(material)
        self._validate_uniqueness(material)

        self._materials_by_key_id[material.key_id] = material
        self._key_ids_by_fingerprint[
            material.public_key_fingerprint
        ] = material.key_id
        self._key_ids_by_material_id[
            material.material_id
        ] = material.key_id
        self._registration_order.append(material.key_id)

        return True

    def get(
        self,
        key_id: str,
    ) -> PublicKeyMaterial:
        self._require_non_empty(
            key_id,
            "key_id",
        )

        if key_id not in self._materials_by_key_id:
            raise TrustedKeyRegistryError(
                "Trusted-key registry contains an unknown key identity."
            )

        return self._materials_by_key_id[key_id]

    def contains(
        self,
        key_id: str,
    ) -> bool:
        self._require_non_empty(
            key_id,
            "key_id",
        )

        return key_id in self._materials_by_key_id

    def count(self) -> int:
        return len(self._materials_by_key_id)

    def list_key_ids(self) -> tuple[str, ...]:
        return tuple(self._registration_order)

    def list_materials(
        self,
    ) -> tuple[PublicKeyMaterial, ...]:
        return tuple(
            self._materials_by_key_id[key_id]
            for key_id in self._registration_order
        )

    def snapshot(
        self,
    ) -> tuple[PublicKeyMaterial, ...]:
        return self.list_materials()

    def _validate_scope(
        self,
        material: PublicKeyMaterial,
    ) -> None:
        if (
            self._expected_owner_id is not None
            and material.owner_id
            != self._expected_owner_id
        ):
            raise TrustedKeyRegistryError(
                "Public-key material contains an owner identity mismatch."
            )

        if (
            self._expected_issuer_id is not None
            and material.issuer_id
            != self._expected_issuer_id
        ):
            raise TrustedKeyRegistryError(
                "Public-key material contains an issuer identity mismatch."
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
            raise TrustedKeyRegistryError(
                "Public-key material fingerprint validation failed."
            ) from error

    def _validate_uniqueness(
        self,
        material: PublicKeyMaterial,
    ) -> None:
        if material.key_id in self._materials_by_key_id:
            raise TrustedKeyRegistryError(
                "Trusted-key registry contains a duplicate key identity."
            )

        if (
            material.public_key_fingerprint
            in self._key_ids_by_fingerprint
        ):
            raise TrustedKeyRegistryError(
                "Trusted-key registry contains a duplicate "
                "key fingerprint."
            )

        if material.material_id in self._key_ids_by_material_id:
            raise TrustedKeyRegistryError(
                "Trusted-key registry contains a duplicate "
                "material identity."
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
            raise TrustedKeyRegistryError(
                f"{field_name} must not be empty."
            )