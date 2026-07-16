import pytest

from models.historical_signature_admissibility_bundle import (
    HistoricalSignatureAdmissibilityBundle,
)
from services.historical_signature_admissibility_bundle_hasher import (
    HistoricalSignatureAdmissibilityBundleHasher,
)
from services.historical_signature_admissibility_bundle_validator import (
    HistoricalSignatureAdmissibilityBundleValidator,
)


def make_bundle(
    *,
    bundle_id: str = "HSAB-000001",
    receipt_id: str = "HSAR-000001",
    receipt_hash: str = "a" * 64,
    assessment_hash: str = "b" * 64,
    signature_id: str = "SIG-000001",
    key_id: str = "KEY-000001",
    admissibility_status: str = "PASS",
    policy_version: str = "historical-signature-admissibility-v1",
    exported_at: str = "2026-07-16T18:00:00Z",
) -> HistoricalSignatureAdmissibilityBundle:
    return HistoricalSignatureAdmissibilityBundle(
        bundle_id=bundle_id,
        receipt_id=receipt_id,
        receipt_hash=receipt_hash,
        assessment_hash=assessment_hash,
        signature_id=signature_id,
        key_id=key_id,
        admissibility_status=admissibility_status,
        policy_version=policy_version,
        exported_at=exported_at,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_matching_bundle_hash() -> None:
    bundle = make_bundle()
    expected_hash = (
        HistoricalSignatureAdmissibilityBundleHasher()
        .hash_bundle(bundle)
    )

    validator = HistoricalSignatureAdmissibilityBundleValidator()

    assert validator.validate(
        bundle=bundle,
        expected_hash=expected_hash,
    ) is True


def test_validator_rejects_non_matching_bundle_hash() -> None:
    validator = HistoricalSignatureAdmissibilityBundleValidator()

    assert validator.validate(
        bundle=make_bundle(),
        expected_hash="c" * 64,
    ) is False


def test_validator_detects_modified_bundle() -> None:
    original = make_bundle()
    expected_hash = (
        HistoricalSignatureAdmissibilityBundleHasher()
        .hash_bundle(original)
    )

    modified = make_bundle(
        admissibility_status="HOLD",
    )

    validator = HistoricalSignatureAdmissibilityBundleValidator()

    assert validator.validate(
        bundle=modified,
        expected_hash=expected_hash,
    ) is False


@pytest.mark.parametrize(
    "status",
    ["PASS", "HOLD", "REJECT"],
)
def test_validator_supports_all_admissibility_statuses(
    status: str,
) -> None:
    bundle = make_bundle(
        admissibility_status=status,
    )
    expected_hash = (
        HistoricalSignatureAdmissibilityBundleHasher()
        .hash_bundle(bundle)
    )

    validator = HistoricalSignatureAdmissibilityBundleValidator()

    assert validator.validate(
        bundle=bundle,
        expected_hash=expected_hash,
    ) is True


def test_validator_rejects_none_bundle() -> None:
    validator = HistoricalSignatureAdmissibilityBundleValidator()

    with pytest.raises(ValueError):
        validator.validate(
            bundle=None,
            expected_hash="a" * 64,
        )


@pytest.mark.parametrize(
    "expected_hash",
    [
        None,
        "",
        " ",
        "abc",
        "g" * 64,
        "a" * 63,
        "a" * 65,
    ],
)
def test_validator_rejects_invalid_expected_hash(
    expected_hash: str | None,
) -> None:
    validator = HistoricalSignatureAdmissibilityBundleValidator()

    with pytest.raises(ValueError):
        validator.validate(
            bundle=make_bundle(),
            expected_hash=expected_hash,
        )


def test_validator_accepts_uppercase_expected_hash() -> None:
    bundle = make_bundle()
    expected_hash = (
        HistoricalSignatureAdmissibilityBundleHasher()
        .hash_bundle(bundle)
        .upper()
    )

    validator = HistoricalSignatureAdmissibilityBundleValidator()

    assert validator.validate(
        bundle=bundle,
        expected_hash=expected_hash,
    ) is True


def test_validator_does_not_mutate_bundle() -> None:
    bundle = make_bundle()
    original = bundle

    expected_hash = (
        HistoricalSignatureAdmissibilityBundleHasher()
        .hash_bundle(bundle)
    )

    HistoricalSignatureAdmissibilityBundleValidator().validate(
        bundle=bundle,
        expected_hash=expected_hash,
    )

    assert bundle == original
    assert bundle.authorization_granted is False
    assert bundle.execution_requested is False
    assert bundle.side_effects_permitted is False


def test_successful_validation_does_not_grant_authority() -> None:
    bundle = make_bundle()
    expected_hash = (
        HistoricalSignatureAdmissibilityBundleHasher()
        .hash_bundle(bundle)
    )

    validator = HistoricalSignatureAdmissibilityBundleValidator()

    assert validator.validate(
        bundle=bundle,
        expected_hash=expected_hash,
    ) is True

    assert bundle.authorization_granted is False
    assert bundle.execution_requested is False
    assert bundle.side_effects_permitted is False