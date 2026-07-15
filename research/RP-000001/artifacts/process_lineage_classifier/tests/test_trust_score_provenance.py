from datetime import datetime, timedelta, timezone

import pytest

from enums import WitnessTrustLevel
from models import (
    TrustScoreProvenance,
    WitnessTrustProfile,
    WitnessTrustScore,
)
from services.trust_score_provenance_validator import (
    TrustScoreProvenanceError,
    TrustScoreProvenanceValidator,
)


GENERATED_AT = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def make_profile(
    *,
    source_id: str = "SOURCE-A",
) -> WitnessTrustProfile:
    return WitnessTrustProfile(
        source_id=source_id,
        verified_observations=20,
        contradicted_observations=1,
        stale_observations=1,
        signature_failures=0,
        provenance_failures=0,
        independent_confirmations=15,
    )


def make_score(
    *,
    source_id: str = "SOURCE-A",
    level: WitnessTrustLevel = WitnessTrustLevel.HIGH,
    score: int = 100,
) -> WitnessTrustScore:
    return WitnessTrustScore(
        source_id=source_id,
        level=level,
        score=score,
        verified_observations=20,
        contradicted_observations=1,
        stale_observations=1,
        signature_failures=0,
        provenance_failures=0,
        independent_confirmations=15,
        disqualifying_failures=(),
        applied_rules=("WTS-001",),
        reasons=("Witness source has strong verified history.",),
    )


def make_provenance(
    *,
    provenance_id: str = "TSP-001",
    source_id: str = "SOURCE-A",
    profile_id: str = "WTP-SOURCE-A",
    scorer_version: str = "1.0.0",
    scoring_policy_id: str = "WTS-POLICY-001",
    scoring_policy_hash: str = "sha256:trust-policy-hash-001",
    generated_at: datetime = GENERATED_AT,
    issuer_id: str = "PROCESS-LINEAGE-CLASSIFIER",
) -> TrustScoreProvenance:
    return TrustScoreProvenance(
        provenance_id=provenance_id,
        source_id=source_id,
        profile_id=profile_id,
        scorer_version=scorer_version,
        scoring_policy_id=scoring_policy_id,
        scoring_policy_hash=scoring_policy_hash,
        generated_at=generated_at,
        issuer_id=issuer_id,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_validator_accepts_matching_trust_score_provenance() -> None:
    assert (
        TrustScoreProvenanceValidator().validate(
            make_provenance(),
            make_profile(),
            make_score(),
            expected_profile_id="WTP-SOURCE-A",
            expected_scorer_version="1.0.0",
            expected_policy_id="WTS-POLICY-001",
            expected_policy_hash="sha256:trust-policy-hash-001",
            now=GENERATED_AT,
        )
        is True
    )


def test_validator_accepts_provenance_before_reference_time() -> None:
    provenance = make_provenance(
        generated_at=GENERATED_AT - timedelta(seconds=1),
    )

    assert (
        TrustScoreProvenanceValidator().validate(
            provenance,
            make_profile(),
            make_score(),
            expected_profile_id="WTP-SOURCE-A",
            expected_scorer_version="1.0.0",
            expected_policy_id="WTS-POLICY-001",
            expected_policy_hash="sha256:trust-policy-hash-001",
            now=GENERATED_AT,
        )
        is True
    )


def test_validator_rejects_non_provenance_input() -> None:
    with pytest.raises(TypeError, match="TrustScoreProvenance"):
        TrustScoreProvenanceValidator().validate(
            "TSP-001",  # type: ignore[arg-type]
            make_profile(),
            make_score(),
            expected_profile_id="WTP-SOURCE-A",
            expected_scorer_version="1.0.0",
            expected_policy_id="WTS-POLICY-001",
            expected_policy_hash="sha256:trust-policy-hash-001",
            now=GENERATED_AT,
        )


def test_validator_rejects_non_profile_input() -> None:
    with pytest.raises(TypeError, match="WitnessTrustProfile"):
        TrustScoreProvenanceValidator().validate(
            make_provenance(),
            "SOURCE-A",  # type: ignore[arg-type]
            make_score(),
            expected_profile_id="WTP-SOURCE-A",
            expected_scorer_version="1.0.0",
            expected_policy_id="WTS-POLICY-001",
            expected_policy_hash="sha256:trust-policy-hash-001",
            now=GENERATED_AT,
        )


def test_validator_rejects_non_score_input() -> None:
    with pytest.raises(TypeError, match="WitnessTrustScore"):
        TrustScoreProvenanceValidator().validate(
            make_provenance(),
            make_profile(),
            100,  # type: ignore[arg-type]
            expected_profile_id="WTP-SOURCE-A",
            expected_scorer_version="1.0.0",
            expected_policy_id="WTS-POLICY-001",
            expected_policy_hash="sha256:trust-policy-hash-001",
            now=GENERATED_AT,
        )


def test_validator_rejects_source_identity_mismatch() -> None:
    with pytest.raises(
        TrustScoreProvenanceError,
        match="source identity",
    ):
        TrustScoreProvenanceValidator().validate(
            make_provenance(source_id="SOURCE-A"),
            make_profile(source_id="SOURCE-B"),
            make_score(source_id="SOURCE-A"),
            expected_profile_id="WTP-SOURCE-A",
            expected_scorer_version="1.0.0",
            expected_policy_id="WTS-POLICY-001",
            expected_policy_hash="sha256:trust-policy-hash-001",
            now=GENERATED_AT,
        )


def test_validator_rejects_score_source_mismatch() -> None:
    with pytest.raises(
        TrustScoreProvenanceError,
        match="score source",
    ):
        TrustScoreProvenanceValidator().validate(
            make_provenance(),
            make_profile(),
            make_score(source_id="SOURCE-B"),
            expected_profile_id="WTP-SOURCE-A",
            expected_scorer_version="1.0.0",
            expected_policy_id="WTS-POLICY-001",
            expected_policy_hash="sha256:trust-policy-hash-001",
            now=GENERATED_AT,
        )


def test_validator_rejects_profile_identity_mismatch() -> None:
    with pytest.raises(
        TrustScoreProvenanceError,
        match="profile identity",
    ):
        TrustScoreProvenanceValidator().validate(
            make_provenance(profile_id="WTP-SOURCE-A"),
            make_profile(),
            make_score(),
            expected_profile_id="WTP-SOURCE-B",
            expected_scorer_version="1.0.0",
            expected_policy_id="WTS-POLICY-001",
            expected_policy_hash="sha256:trust-policy-hash-001",
            now=GENERATED_AT,
        )


def test_validator_rejects_scorer_version_mismatch() -> None:
    with pytest.raises(
        TrustScoreProvenanceError,
        match="scorer version",
    ):
        TrustScoreProvenanceValidator().validate(
            make_provenance(scorer_version="1.0.0"),
            make_profile(),
            make_score(),
            expected_profile_id="WTP-SOURCE-A",
            expected_scorer_version="2.0.0",
            expected_policy_id="WTS-POLICY-001",
            expected_policy_hash="sha256:trust-policy-hash-001",
            now=GENERATED_AT,
        )


def test_validator_rejects_policy_identity_mismatch() -> None:
    with pytest.raises(
        TrustScoreProvenanceError,
        match="policy identity",
    ):
        TrustScoreProvenanceValidator().validate(
            make_provenance(scoring_policy_id="WTS-POLICY-001"),
            make_profile(),
            make_score(),
            expected_profile_id="WTP-SOURCE-A",
            expected_scorer_version="1.0.0",
            expected_policy_id="WTS-POLICY-999",
            expected_policy_hash="sha256:trust-policy-hash-001",
            now=GENERATED_AT,
        )


def test_validator_rejects_policy_hash_mismatch() -> None:
    with pytest.raises(
        TrustScoreProvenanceError,
        match="policy hash",
    ):
        TrustScoreProvenanceValidator().validate(
            make_provenance(),
            make_profile(),
            make_score(),
            expected_profile_id="WTP-SOURCE-A",
            expected_scorer_version="1.0.0",
            expected_policy_id="WTS-POLICY-001",
            expected_policy_hash="sha256:trust-policy-hash-999",
            now=GENERATED_AT,
        )


def test_validator_rejects_future_provenance() -> None:
    with pytest.raises(
        TrustScoreProvenanceError,
        match="future",
    ):
        TrustScoreProvenanceValidator().validate(
            make_provenance(
                generated_at=GENERATED_AT + timedelta(seconds=1),
            ),
            make_profile(),
            make_score(),
            expected_profile_id="WTP-SOURCE-A",
            expected_scorer_version="1.0.0",
            expected_policy_id="WTS-POLICY-001",
            expected_policy_hash="sha256:trust-policy-hash-001",
            now=GENERATED_AT,
        )


def test_provenance_is_immutable() -> None:
    provenance = make_provenance()

    with pytest.raises((AttributeError, TypeError)):
        provenance.scorer_version = "2.0.0"  # type: ignore[misc]


def test_provenance_rejects_empty_provenance_id() -> None:
    with pytest.raises(ValueError, match="provenance_id"):
        make_provenance(provenance_id="")


def test_provenance_rejects_empty_scorer_version() -> None:
    with pytest.raises(ValueError, match="scorer_version"):
        make_provenance(scorer_version="")


def test_provenance_rejects_empty_policy_hash() -> None:
    with pytest.raises(ValueError, match="scoring_policy_hash"):
        make_provenance(scoring_policy_hash="")


def test_provenance_rejects_naive_generated_at() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        make_provenance(
            generated_at=datetime(2026, 7, 14, 12, 0),
        )


def test_validator_rejects_naive_reference_time() -> None:
    with pytest.raises(TypeError, match="timezone-aware"):
        TrustScoreProvenanceValidator().validate(
            make_provenance(),
            make_profile(),
            make_score(),
            expected_profile_id="WTP-SOURCE-A",
            expected_scorer_version="1.0.0",
            expected_policy_id="WTS-POLICY-001",
            expected_policy_hash="sha256:trust-policy-hash-001",
            now=datetime(2026, 7, 14, 12, 0),
        )


def test_provenance_preserves_observer_only_boundary() -> None:
    provenance = make_provenance()

    assert provenance.execution_requested is False
    assert provenance.side_effects_permitted is False