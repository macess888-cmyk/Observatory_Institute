import pytest

from enums import WitnessTrustLevel
from models import WitnessTrustProfile
from services.witness_trust_scorer import (
    WitnessTrustScorer,
    WitnessTrustScoringError,
)


def make_profile(
    *,
    source_id: str = "SOURCE-A",
    verified_observations: int = 20,
    contradicted_observations: int = 1,
    stale_observations: int = 1,
    signature_failures: int = 0,
    provenance_failures: int = 0,
    independent_confirmations: int = 15,
) -> WitnessTrustProfile:
    return WitnessTrustProfile(
        source_id=source_id,
        verified_observations=verified_observations,
        contradicted_observations=contradicted_observations,
        stale_observations=stale_observations,
        signature_failures=signature_failures,
        provenance_failures=provenance_failures,
        independent_confirmations=independent_confirmations,
    )


def test_scorer_returns_high_trust() -> None:
    profile = make_profile()

    result = WitnessTrustScorer().score(profile)

    assert result.source_id == "SOURCE-A"
    assert result.level is WitnessTrustLevel.HIGH
    assert result.score >= 80
    assert result.verified_observations == 20
    assert result.independent_confirmations == 15
    assert result.disqualifying_failures == ()
    assert "WTS-001" in result.applied_rules


def test_scorer_returns_moderate_trust() -> None:
    profile = make_profile(
        verified_observations=10,
        contradicted_observations=2,
        stale_observations=2,
        independent_confirmations=5,
    )

    result = WitnessTrustScorer().score(profile)

    assert result.level is WitnessTrustLevel.MODERATE
    assert 50 <= result.score < 80
    assert "WTS-002" in result.applied_rules


def test_scorer_returns_low_trust() -> None:
    profile = make_profile(
        verified_observations=4,
        contradicted_observations=3,
        stale_observations=2,
        independent_confirmations=1,
    )

    result = WitnessTrustScorer().score(profile)

    assert result.level is WitnessTrustLevel.LOW
    assert 1 <= result.score < 50
    assert "WTS-003" in result.applied_rules


def test_scorer_returns_untrusted_for_signature_failure() -> None:
    profile = make_profile(
        signature_failures=1,
    )

    result = WitnessTrustScorer().score(profile)

    assert result.level is WitnessTrustLevel.UNTRUSTED
    assert result.score == 0
    assert "signature failure" in result.disqualifying_failures
    assert "WTS-004" in result.applied_rules


def test_scorer_returns_untrusted_for_provenance_failure() -> None:
    profile = make_profile(
        provenance_failures=1,
    )

    result = WitnessTrustScorer().score(profile)

    assert result.level is WitnessTrustLevel.UNTRUSTED
    assert result.score == 0
    assert "provenance failure" in result.disqualifying_failures
    assert "WTS-004" in result.applied_rules


def test_scorer_returns_untrusted_for_multiple_disqualifying_failures() -> None:
    profile = make_profile(
        signature_failures=2,
        provenance_failures=3,
    )

    result = WitnessTrustScorer().score(profile)

    assert result.level is WitnessTrustLevel.UNTRUSTED
    assert result.score == 0
    assert result.disqualifying_failures == (
        "signature failure",
        "provenance failure",
    )


def test_scorer_caps_score_at_one_hundred() -> None:
    profile = make_profile(
        verified_observations=100,
        contradicted_observations=0,
        stale_observations=0,
        independent_confirmations=100,
    )

    result = WitnessTrustScorer().score(profile)

    assert result.score == 100
    assert result.level is WitnessTrustLevel.HIGH


def test_scorer_never_returns_negative_score() -> None:
    profile = make_profile(
        verified_observations=0,
        contradicted_observations=100,
        stale_observations=100,
        independent_confirmations=0,
    )

    result = WitnessTrustScorer().score(profile)

    assert result.score == 0
    assert result.level is WitnessTrustLevel.UNTRUSTED


def test_scorer_is_deterministic() -> None:
    profile = make_profile()

    first = WitnessTrustScorer().score(profile)
    second = WitnessTrustScorer().score(profile)

    assert first == second


def test_scorer_does_not_mutate_profile() -> None:
    profile = make_profile()
    original = profile

    WitnessTrustScorer().score(profile)

    assert profile == original


def test_scorer_requires_witness_trust_profile() -> None:
    with pytest.raises(
        TypeError,
        match="WitnessTrustProfile",
    ):
        WitnessTrustScorer().score(
            "SOURCE-A"  # type: ignore[arg-type]
        )


def test_profile_rejects_negative_verified_observations() -> None:
    with pytest.raises(
        ValueError,
        match="verified_observations",
    ):
        make_profile(
            verified_observations=-1,
        )


def test_profile_rejects_negative_failure_count() -> None:
    with pytest.raises(
        ValueError,
        match="signature_failures",
    ):
        make_profile(
            signature_failures=-1,
        )


def test_profile_rejects_empty_source_identity() -> None:
    with pytest.raises(
        ValueError,
        match="source_id",
    ):
        make_profile(
            source_id="",
        )