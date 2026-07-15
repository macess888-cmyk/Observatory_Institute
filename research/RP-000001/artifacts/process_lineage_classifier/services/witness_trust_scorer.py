from enums import WitnessTrustLevel
from models import WitnessTrustProfile, WitnessTrustScore


class WitnessTrustScoringError(ValueError):
    """Raised when a witness trust profile cannot be scored."""


class WitnessTrustScorer:
    """Produces a deterministic trust score from witness history."""

    HIGH_TRUST_RULE = "WTS-001"
    MODERATE_TRUST_RULE = "WTS-002"
    LOW_TRUST_RULE = "WTS-003"
    UNTRUSTED_RULE = "WTS-004"

    VERIFIED_WEIGHT = 5
    INDEPENDENT_CONFIRMATION_WEIGHT = 3
    CONTRADICTION_PENALTY = 5
    STALE_PENALTY = 2

    def score(
        self,
        profile: WitnessTrustProfile,
    ) -> WitnessTrustScore:
        if not isinstance(profile, WitnessTrustProfile):
            raise TypeError(
                "profile must be a WitnessTrustProfile."
            )

        disqualifying_failures = (
            self._find_disqualifying_failures(profile)
        )

        if disqualifying_failures:
            return self._untrusted_result(
                profile,
                disqualifying_failures,
            )

        raw_score = (
            profile.verified_observations
            * self.VERIFIED_WEIGHT
            + profile.independent_confirmations
            * self.INDEPENDENT_CONFIRMATION_WEIGHT
            - profile.contradicted_observations
            * self.CONTRADICTION_PENALTY
            - profile.stale_observations
            * self.STALE_PENALTY
        )

        normalized_score = max(0, min(100, raw_score))

        if normalized_score >= 80:
            return self._high_result(
                profile,
                normalized_score,
            )

        if normalized_score >= 50:
            return self._moderate_result(
                profile,
                normalized_score,
            )

        if normalized_score >= 1:
            return self._low_result(
                profile,
                normalized_score,
            )

        return self._untrusted_result(
            profile,
            (),
        )

    def _high_result(
        self,
        profile: WitnessTrustProfile,
        score: int,
    ) -> WitnessTrustScore:
        return self._build_result(
            profile,
            level=WitnessTrustLevel.HIGH,
            score=score,
            applied_rule=self.HIGH_TRUST_RULE,
            reasons=(
                "Verified observations strongly support the witness source.",
                "Independent confirmations are substantial.",
                "Contradictions and stale observations remain limited.",
                "No disqualifying provenance or signature failures exist.",
            ),
        )

    def _moderate_result(
        self,
        profile: WitnessTrustProfile,
        score: int,
    ) -> WitnessTrustScore:
        return self._build_result(
            profile,
            level=WitnessTrustLevel.MODERATE,
            score=score,
            applied_rule=self.MODERATE_TRUST_RULE,
            reasons=(
                "The witness source has meaningful verified history.",
                "Independent confirmation exists.",
                "Contradictions or stale observations reduce confidence.",
                "No disqualifying provenance or signature failures exist.",
            ),
        )

    def _low_result(
        self,
        profile: WitnessTrustProfile,
        score: int,
    ) -> WitnessTrustScore:
        return self._build_result(
            profile,
            level=WitnessTrustLevel.LOW,
            score=score,
            applied_rule=self.LOW_TRUST_RULE,
            reasons=(
                "The witness source has limited verified history.",
                "Contradictions or stale observations materially reduce trust.",
                "Independent confirmation remains insufficient for higher trust.",
                "The source is not disqualified but should be treated cautiously.",
            ),
        )

    def _untrusted_result(
        self,
        profile: WitnessTrustProfile,
        disqualifying_failures: tuple[str, ...],
    ) -> WitnessTrustScore:
        reasons = (
            (
                "Signature or provenance failures disqualify the witness source.",
                "The source cannot contribute trusted evidence.",
            )
            if disqualifying_failures
            else (
                "The calculated trust score did not exceed zero.",
                "Observed failures outweigh verified evidence.",
            )
        )

        return self._build_result(
            profile,
            level=WitnessTrustLevel.UNTRUSTED,
            score=0,
            applied_rule=self.UNTRUSTED_RULE,
            reasons=reasons,
            disqualifying_failures=disqualifying_failures,
        )

    def _build_result(
        self,
        profile: WitnessTrustProfile,
        *,
        level: WitnessTrustLevel,
        score: int,
        applied_rule: str,
        reasons: tuple[str, ...],
        disqualifying_failures: tuple[str, ...] = (),
    ) -> WitnessTrustScore:
        return WitnessTrustScore(
            source_id=profile.source_id,
            level=level,
            score=score,
            verified_observations=profile.verified_observations,
            contradicted_observations=(
                profile.contradicted_observations
            ),
            stale_observations=profile.stale_observations,
            signature_failures=profile.signature_failures,
            provenance_failures=profile.provenance_failures,
            independent_confirmations=(
                profile.independent_confirmations
            ),
            disqualifying_failures=disqualifying_failures,
            applied_rules=(applied_rule,),
            reasons=reasons,
        )

    @staticmethod
    def _find_disqualifying_failures(
        profile: WitnessTrustProfile,
    ) -> tuple[str, ...]:
        failures: list[str] = []

        if profile.signature_failures > 0:
            failures.append("signature failure")

        if profile.provenance_failures > 0:
            failures.append("provenance failure")

        return tuple(failures)