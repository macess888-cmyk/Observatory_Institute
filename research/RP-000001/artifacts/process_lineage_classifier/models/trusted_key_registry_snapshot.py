from dataclasses import dataclass
from datetime import datetime

from models.public_key_material import PublicKeyMaterial


@dataclass(frozen=True, slots=True)
class TrustedKeyRegistrySnapshot:
    """Immutable observer-only snapshot of trusted registry state."""

    snapshot_id: str
    registry_id: str
    registry_version: str

    materials: tuple[PublicKeyMaterial, ...]

    captured_at: datetime

    owner_id: str
    issuer_id: str

    execution_requested: bool = False
    side_effects_permitted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("snapshot_id", self.snapshot_id),
            ("registry_id", self.registry_id),
            ("registry_version", self.registry_version),
            ("owner_id", self.owner_id),
            ("issuer_id", self.issuer_id),
        ):
            self._require_non_empty(value, field_name)

        if not isinstance(self.materials, tuple):
            raise TypeError(
                "materials must be a tuple."
            )

        if not self.materials:
            raise ValueError(
                "materials must not be empty."
            )

        key_ids: set[str] = set()
        material_ids: set[str] = set()
        fingerprints: set[str] = set()

        for material in self.materials:
            if not isinstance(material, PublicKeyMaterial):
                raise TypeError(
                    "materials must contain only PublicKeyMaterial."
                )

            if material.key_id in key_ids:
                raise ValueError(
                    "materials contain a duplicate key identity."
                )

            if material.material_id in material_ids:
                raise ValueError(
                    "materials contain a duplicate material identity."
                )

            if (
                material.public_key_fingerprint
                in fingerprints
            ):
                raise ValueError(
                    "materials contain a duplicate fingerprint."
                )

            if material.owner_id != self.owner_id:
                raise ValueError(
                    "material owner identity does not match snapshot."
                )

            if material.issuer_id != self.issuer_id:
                raise ValueError(
                    "material issuer identity does not match snapshot."
                )

            key_ids.add(material.key_id)
            material_ids.add(material.material_id)
            fingerprints.add(
                material.public_key_fingerprint
            )

        self._validate_datetime(
            self.captured_at,
            "captured_at",
        )

        if any(
            self.captured_at < material.created_at
            for material in self.materials
        ):
            raise ValueError(
                "captured_at cannot be before material creation."
            )

        if self.execution_requested is not False:
            raise ValueError(
                "TrustedKeyRegistrySnapshot must remain observer-only."
            )

        if self.side_effects_permitted is not False:
            raise ValueError(
                "TrustedKeyRegistrySnapshot must not permit side effects."
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