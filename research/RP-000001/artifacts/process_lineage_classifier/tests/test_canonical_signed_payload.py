import hashlib
import json
from datetime import datetime, timezone

import pytest

from models import RecoveryIntegrityBundle
from services.canonical_signed_payload import (
    CanonicalSignedPayloadError,
    CanonicalSignedPayloadService,
)


CREATED_AT = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)

RECONCILIATION_RECEIPT_DIGEST = "sha256:" + ("1" * 64)
AUDIT_ROOT_DIGEST = "sha256:" + ("2" * 64)
REPLAY_MANIFEST_DIGEST = "sha256:" + ("3" * 64)
VERIFICATION_RECEIPT_DIGEST = "sha256:" + ("4" * 64)
POLICY_DIGEST = "sha256:" + ("5" * 64)
TRUST_DIGEST_001 = "sha256:" + ("6" * 64)
TRUST_DIGEST_002 = "sha256:" + ("7" * 64)


def make_bundle(
    *,
    bundle_id: str = "RIB-001",
    subject_id: str = "RECOVERY-001",
    original_decision_id: str = "RD-001",
    trust_provenance_ids: tuple[str, ...] = (
        "TSP-001",
        "TSP-002",
    ),
    trust_digests: tuple[str, ...] = (
        TRUST_DIGEST_001,
        TRUST_DIGEST_002,
    ),
) -> RecoveryIntegrityBundle:
    return RecoveryIntegrityBundle(
        bundle_id=bundle_id,
        subject_id=subject_id,
        original_decision_id=original_decision_id,
        reconciliation_receipt_id="RCP-001",
        reconciliation_receipt_digest=RECONCILIATION_RECEIPT_DIGEST,
        audit_chain_id="AHC-001",
        audit_root_digest=AUDIT_ROOT_DIGEST,
        replay_manifest_id="RIM-001",
        replay_manifest_digest=REPLAY_MANIFEST_DIGEST,
        verification_receipt_id="RVR-001",
        verification_receipt_digest=VERIFICATION_RECEIPT_DIGEST,
        policy_binding_id="PVB-001",
        policy_digest=POLICY_DIGEST,
        trust_provenance_ids=trust_provenance_ids,
        trust_digests=trust_digests,
        created_at=CREATED_AT,
        issuer_id="PROCESS-LINEAGE-CLASSIFIER",
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_service_generates_canonical_payload_bytes() -> None:
    bundle = make_bundle()

    payload = CanonicalSignedPayloadService().generate(bundle)

    assert isinstance(payload, bytes)

    decoded = json.loads(payload.decode("utf-8"))

    assert decoded["bundle_id"] == "RIB-001"
    assert decoded["subject_id"] == "RECOVERY-001"
    assert decoded["original_decision_id"] == "RD-001"
    assert decoded["execution_requested"] is False
    assert decoded["side_effects_permitted"] is False


def test_service_uses_expected_field_order() -> None:
    payload_text = (
        CanonicalSignedPayloadService()
        .generate(make_bundle())
        .decode("utf-8")
    )

    expected_order = (
        '"bundle_id"',
        '"subject_id"',
        '"original_decision_id"',
        '"reconciliation_receipt_id"',
        '"reconciliation_receipt_digest"',
        '"audit_chain_id"',
        '"audit_root_digest"',
        '"replay_manifest_id"',
        '"replay_manifest_digest"',
        '"verification_receipt_id"',
        '"verification_receipt_digest"',
        '"policy_binding_id"',
        '"policy_digest"',
        '"trust_provenance_ids"',
        '"trust_digests"',
        '"created_at"',
        '"issuer_id"',
        '"execution_requested"',
        '"side_effects_permitted"',
    )

    positions = tuple(
        payload_text.index(field_name)
        for field_name in expected_order
    )

    assert positions == tuple(sorted(positions))


def test_service_is_deterministic() -> None:
    service = CanonicalSignedPayloadService()
    bundle = make_bundle()

    first = service.generate(bundle)
    second = service.generate(bundle)

    assert first == second


def test_equivalent_bundles_produce_identical_payloads() -> None:
    service = CanonicalSignedPayloadService()

    assert service.generate(make_bundle()) == service.generate(
        make_bundle()
    )


def test_bundle_change_produces_different_payload() -> None:
    service = CanonicalSignedPayloadService()

    first = service.generate(make_bundle())
    second = service.generate(
        make_bundle(subject_id="RECOVERY-999")
    )

    assert first != second


def test_trust_order_is_preserved() -> None:
    payload = CanonicalSignedPayloadService().generate(
        make_bundle(
            trust_provenance_ids=("TSP-002", "TSP-001"),
            trust_digests=(
                TRUST_DIGEST_002,
                TRUST_DIGEST_001,
            ),
        )
    )

    decoded = json.loads(payload.decode("utf-8"))

    assert decoded["trust_provenance_ids"] == [
        "TSP-002",
        "TSP-001",
    ]
    assert decoded["trust_digests"] == [
        TRUST_DIGEST_002,
        TRUST_DIGEST_001,
    ]


def test_timestamp_is_iso_8601() -> None:
    payload = CanonicalSignedPayloadService().generate(
        make_bundle()
    )

    decoded = json.loads(payload.decode("utf-8"))

    assert decoded["created_at"] == CREATED_AT.isoformat()


def test_payload_has_no_extra_whitespace() -> None:
    payload_text = (
        CanonicalSignedPayloadService()
        .generate(make_bundle())
        .decode("utf-8")
    )

    assert ": " not in payload_text
    assert ", " not in payload_text
    assert "\n" not in payload_text


def test_payload_uses_utf8() -> None:
    payload = CanonicalSignedPayloadService().generate(
        make_bundle()
    )

    assert payload.decode("utf-8").encode("utf-8") == payload


def test_service_rejects_non_bundle_input() -> None:
    with pytest.raises(
        TypeError,
        match="RecoveryIntegrityBundle",
    ):
        CanonicalSignedPayloadService().generate(
            "RIB-001"  # type: ignore[arg-type]
        )


def test_service_generates_expected_sha256_digest() -> None:
    service = CanonicalSignedPayloadService()
    payload = service.generate(make_bundle())

    expected = "sha256:" + hashlib.sha256(
        payload
    ).hexdigest()

    assert service.digest(make_bundle()) == expected


def test_digest_is_deterministic() -> None:
    service = CanonicalSignedPayloadService()
    bundle = make_bundle()

    assert service.digest(bundle) == service.digest(bundle)


def test_changed_bundle_changes_digest() -> None:
    service = CanonicalSignedPayloadService()

    first = service.digest(make_bundle())
    second = service.digest(
        make_bundle(original_decision_id="RD-999")
    )

    assert first != second


def test_validate_digest_accepts_matching_digest() -> None:
    service = CanonicalSignedPayloadService()
    bundle = make_bundle()
    digest = service.digest(bundle)

    assert service.validate_digest(
        bundle,
        digest,
    ) is True


def test_validate_digest_rejects_mismatch() -> None:
    with pytest.raises(
        CanonicalSignedPayloadError,
        match="digest mismatch",
    ):
        CanonicalSignedPayloadService().validate_digest(
            make_bundle(),
            "sha256:" + ("9" * 64),
        )


@pytest.mark.parametrize(
    "digest",
    [
        "md5:invalid",
        "sha256:abc",
        "sha256:" + ("z" * 64),
        "sha256:" + ("A" * 64),
    ],
)
def test_validate_digest_rejects_invalid_digest(
    digest: str,
) -> None:
    with pytest.raises(
        CanonicalSignedPayloadError,
        match="expected_digest",
    ):
        CanonicalSignedPayloadService().validate_digest(
            make_bundle(),
            digest,
        )


def test_service_does_not_mutate_bundle() -> None:
    bundle = make_bundle()
    original = bundle

    CanonicalSignedPayloadService().generate(bundle)

    assert bundle == original


def test_bundle_preserves_observer_only_boundary() -> None:
    bundle = make_bundle()

    assert bundle.execution_requested is False
    assert bundle.side_effects_permitted is False