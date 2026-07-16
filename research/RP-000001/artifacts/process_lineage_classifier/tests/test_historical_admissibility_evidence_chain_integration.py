from dataclasses import FrozenInstanceError

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

from services.historical_admissibility_evidence_provenance_service import (
    HistoricalAdmissibilityEvidenceProvenanceService,
)
from services.historical_admissibility_evidence_provenance_hasher import (
    HistoricalAdmissibilityEvidenceProvenanceHasher,
)
from services.historical_admissibility_evidence_provenance_validator import (
    HistoricalAdmissibilityEvidenceProvenanceValidator,
)
from services.historical_admissibility_evidence_provenance_manifest_service import (
    HistoricalAdmissibilityEvidenceProvenanceManifestService,
)
from services.historical_admissibility_evidence_provenance_manifest_hasher import (
    HistoricalAdmissibilityEvidenceProvenanceManifestHasher,
)
from services.historical_admissibility_evidence_provenance_manifest_validator import (
    HistoricalAdmissibilityEvidenceProvenanceManifestValidator,
)

from services.historical_admissibility_evidence_trust_assessment_service import (
    HistoricalAdmissibilityEvidenceTrustAssessmentService,
)
from services.historical_admissibility_evidence_trust_assessment_hasher import (
    HistoricalAdmissibilityEvidenceTrustAssessmentHasher,
)
from services.historical_admissibility_evidence_trust_assessment_validator import (
    HistoricalAdmissibilityEvidenceTrustAssessmentValidator,
)
from services.historical_admissibility_evidence_trust_receipt_service import (
    HistoricalAdmissibilityEvidenceTrustReceiptService,
)
from services.historical_admissibility_evidence_trust_receipt_hasher import (
    HistoricalAdmissibilityEvidenceTrustReceiptHasher,
)
from services.historical_admissibility_evidence_trust_receipt_validator import (
    HistoricalAdmissibilityEvidenceTrustReceiptValidator,
)

from services.historical_admissibility_evidence_admission_assessment_service import (
    HistoricalAdmissibilityEvidenceAdmissionAssessmentService,
)
from services.historical_admissibility_evidence_admission_assessment_hasher import (
    HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher,
)
from services.historical_admissibility_evidence_admission_assessment_validator import (
    HistoricalAdmissibilityEvidenceAdmissionAssessmentValidator,
)
from services.historical_admissibility_evidence_admission_receipt_service import (
    HistoricalAdmissibilityEvidenceAdmissionReceiptService,
)
from services.historical_admissibility_evidence_admission_receipt_hasher import (
    HistoricalAdmissibilityEvidenceAdmissionReceiptHasher,
)
from services.historical_admissibility_evidence_admission_receipt_validator import (
    HistoricalAdmissibilityEvidenceAdmissionReceiptValidator,
)

from services.historical_admissibility_evidence_package_service import (
    HistoricalAdmissibilityEvidencePackageService,
)
from services.historical_admissibility_evidence_package_hasher import (
    HistoricalAdmissibilityEvidencePackageHasher,
)
from services.historical_admissibility_evidence_package_validator import (
    HistoricalAdmissibilityEvidencePackageValidator,
)
from services.historical_admissibility_evidence_package_receipt_service import (
    HistoricalAdmissibilityEvidencePackageReceiptService,
)
from services.historical_admissibility_evidence_package_receipt_hasher import (
    HistoricalAdmissibilityEvidencePackageReceiptHasher,
)
from services.historical_admissibility_evidence_package_receipt_validator import (
    HistoricalAdmissibilityEvidencePackageReceiptValidator,
)


def build_chain(
    *,
    trust_status: str = "PASS",
    confidence_level: str = "HIGH",
    admission_status: str = "PASS",
    package_status: str = "PASS",
) -> dict[str, object]:
    bundle = HistoricalSignatureAdmissibilityBundle(
        bundle_id="HSAB-000001",
        receipt_id="HSAR-000001",
        receipt_hash="a" * 64,
        assessment_hash="b" * 64,
        signature_id="SIG-000001",
        key_id="KEY-000001",
        admissibility_status="PASS",
        policy_version="historical-signature-admissibility-v1",
        exported_at="2026-07-16T18:00:00Z",
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )
    bundle_hash = (
        HistoricalSignatureAdmissibilityBundleHasher()
        .hash_bundle(bundle)
    )

    provenance = (
        HistoricalAdmissibilityEvidenceProvenanceService()
        .create_provenance(
            provenance_id="HAEP-000001",
            bundle=bundle,
            evidence_id="EVD-000001",
            evidence_type="KEY_COMPROMISE_EVENT",
            source_system="historical-key-registry",
            source_reference=(
                "registry://keys/KEY-000001/events/KCE-000001"
            ),
            source_hash="c" * 64,
            observed_at="2026-07-16T18:30:00Z",
            collected_at="2026-07-16T18:35:00Z",
        )
    )
    provenance_hash = (
        HistoricalAdmissibilityEvidenceProvenanceHasher()
        .hash_provenance(provenance)
    )

    manifest = (
        HistoricalAdmissibilityEvidenceProvenanceManifestService()
        .create_manifest(
            manifest_id="HAEPM-000001",
            provenance_records=(provenance,),
            assembled_at="2026-07-16T19:00:00Z",
        )
    )
    manifest_hash = (
        HistoricalAdmissibilityEvidenceProvenanceManifestHasher()
        .hash_manifest(manifest)
    )

    trust_assessment = (
        HistoricalAdmissibilityEvidenceTrustAssessmentService()
        .assess(
            assessment_id="HAETA-000001",
            manifest=manifest,
            manifest_hash=manifest_hash,
            trust_status=trust_status,
            confidence_level=confidence_level,
            rationale=(
                "Manifest integrity is confirmed under the applied "
                "observer-only trust policy."
            ),
            policy_version="historical-evidence-trust-v1",
            assessed_at="2026-07-16T20:00:00Z",
        )
    )
    trust_assessment_hash = (
        HistoricalAdmissibilityEvidenceTrustAssessmentHasher()
        .hash_assessment(trust_assessment)
    )

    trust_receipt = (
        HistoricalAdmissibilityEvidenceTrustReceiptService()
        .create_receipt(
            receipt_id="HAETR-000001",
            assessment=trust_assessment,
            assessment_hash=trust_assessment_hash,
            recorded_at="2026-07-16T20:30:00Z",
        )
    )
    trust_receipt_hash = (
        HistoricalAdmissibilityEvidenceTrustReceiptHasher()
        .hash_receipt(trust_receipt)
    )

    admission_assessment = (
        HistoricalAdmissibilityEvidenceAdmissionAssessmentService()
        .assess(
            assessment_id="HAEAA-000001",
            trust_receipt=trust_receipt,
            trust_receipt_hash=trust_receipt_hash,
            admission_status=admission_status,
            rationale=(
                "The supplied evidence chain was evaluated under the "
                "historical evidence admission policy."
            ),
            policy_version="historical-evidence-admission-v1",
            assessed_at="2026-07-16T21:00:00Z",
        )
    )
    admission_assessment_hash = (
        HistoricalAdmissibilityEvidenceAdmissionAssessmentHasher()
        .hash_assessment(admission_assessment)
    )

    admission_receipt = (
        HistoricalAdmissibilityEvidenceAdmissionReceiptService()
        .create_receipt(
            receipt_id="HAEAR-000001",
            assessment=admission_assessment,
            assessment_hash=admission_assessment_hash,
            recorded_at="2026-07-16T21:30:00Z",
        )
    )
    admission_receipt_hash = (
        HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()
        .hash_receipt(admission_receipt)
    )

    package = HistoricalAdmissibilityEvidencePackageService().assemble(
        package_id="HAEPKG-000001",
        admissibility_bundle=bundle,
        admissibility_bundle_hash=bundle_hash,
        provenance_manifest=manifest,
        provenance_manifest_hash=manifest_hash,
        trust_receipt=trust_receipt,
        trust_receipt_hash=trust_receipt_hash,
        admission_receipt=admission_receipt,
        admission_receipt_hash=admission_receipt_hash,
        package_version="historical-evidence-package-v1",
        assembled_at="2026-07-16T22:00:00Z",
    )
    package_hash = (
        HistoricalAdmissibilityEvidencePackageHasher()
        .hash_package(package)
    )

    package_receipt = (
        HistoricalAdmissibilityEvidencePackageReceiptService()
        .create_receipt(
            receipt_id="HAEPKGR-000001",
            package=package,
            package_hash=package_hash,
            package_status=package_status,
            recorded_at="2026-07-16T22:30:00Z",
        )
    )
    package_receipt_hash = (
        HistoricalAdmissibilityEvidencePackageReceiptHasher()
        .hash_receipt(package_receipt)
    )

    return {
        "bundle": bundle,
        "bundle_hash": bundle_hash,
        "provenance": provenance,
        "provenance_hash": provenance_hash,
        "manifest": manifest,
        "manifest_hash": manifest_hash,
        "trust_assessment": trust_assessment,
        "trust_assessment_hash": trust_assessment_hash,
        "trust_receipt": trust_receipt,
        "trust_receipt_hash": trust_receipt_hash,
        "admission_assessment": admission_assessment,
        "admission_assessment_hash": admission_assessment_hash,
        "admission_receipt": admission_receipt,
        "admission_receipt_hash": admission_receipt_hash,
        "package": package,
        "package_hash": package_hash,
        "package_receipt": package_receipt,
        "package_receipt_hash": package_receipt_hash,
    }


def test_complete_chain_binds_each_downstream_identifier() -> None:
    chain = build_chain()

    bundle = chain["bundle"]
    provenance = chain["provenance"]
    manifest = chain["manifest"]
    trust_assessment = chain["trust_assessment"]
    trust_receipt = chain["trust_receipt"]
    admission_assessment = chain["admission_assessment"]
    admission_receipt = chain["admission_receipt"]
    package = chain["package"]
    package_receipt = chain["package_receipt"]

    assert provenance.bundle_id == bundle.bundle_id
    assert manifest.bundle_id == bundle.bundle_id
    assert trust_assessment.manifest_id == manifest.manifest_id
    assert trust_receipt.manifest_id == manifest.manifest_id
    assert trust_receipt.assessment_id == trust_assessment.assessment_id
    assert (
        admission_assessment.trust_receipt_id
        == trust_receipt.receipt_id
    )
    assert (
        admission_receipt.trust_receipt_id
        == trust_receipt.receipt_id
    )
    assert (
        admission_receipt.assessment_id
        == admission_assessment.assessment_id
    )
    assert package.admissibility_bundle_id == bundle.bundle_id
    assert package.provenance_manifest_id == manifest.manifest_id
    assert package.trust_receipt_id == trust_receipt.receipt_id
    assert package.admission_receipt_id == admission_receipt.receipt_id
    assert package_receipt.package_id == package.package_id


def test_complete_chain_preserves_all_referenced_hashes() -> None:
    chain = build_chain()

    assert chain["provenance_hash"] in chain["manifest"].provenance_hashes

    assert (
        chain["trust_assessment"].manifest_hash
        == chain["manifest_hash"]
    )
    assert (
        chain["trust_receipt"].assessment_hash
        == chain["trust_assessment_hash"]
    )
    assert (
        chain["trust_receipt"].manifest_hash
        == chain["manifest_hash"]
    )
    assert (
        chain["admission_assessment"].trust_receipt_hash
        == chain["trust_receipt_hash"]
    )
    assert (
        chain["admission_receipt"].assessment_hash
        == chain["admission_assessment_hash"]
    )
    assert (
        chain["admission_receipt"].trust_receipt_hash
        == chain["trust_receipt_hash"]
    )
    assert (
        chain["package"].admissibility_bundle_hash
        == chain["bundle_hash"]
    )
    assert (
        chain["package"].provenance_manifest_hash
        == chain["manifest_hash"]
    )
    assert (
        chain["package"].trust_receipt_hash
        == chain["trust_receipt_hash"]
    )
    assert (
        chain["package"].admission_receipt_hash
        == chain["admission_receipt_hash"]
    )
    assert (
        chain["package_receipt"].package_hash
        == chain["package_hash"]
    )


def test_every_chain_hash_is_independently_validatable() -> None:
    chain = build_chain()

    assert HistoricalSignatureAdmissibilityBundleValidator().validate(
        bundle=chain["bundle"],
        expected_hash=chain["bundle_hash"],
    )

    assert HistoricalAdmissibilityEvidenceProvenanceValidator().validate(
        provenance=chain["provenance"],
        expected_hash=chain["provenance_hash"],
    )

    assert (
        HistoricalAdmissibilityEvidenceProvenanceManifestValidator()
        .validate(
            manifest=chain["manifest"],
            expected_hash=chain["manifest_hash"],
        )
    )

    assert HistoricalAdmissibilityEvidenceTrustAssessmentValidator().validate(
        assessment=chain["trust_assessment"],
        expected_hash=chain["trust_assessment_hash"],
    )

    assert HistoricalAdmissibilityEvidenceTrustReceiptValidator().validate(
        receipt=chain["trust_receipt"],
        expected_hash=chain["trust_receipt_hash"],
    )

    assert (
        HistoricalAdmissibilityEvidenceAdmissionAssessmentValidator()
        .validate(
            assessment=chain["admission_assessment"],
            expected_hash=chain["admission_assessment_hash"],
        )
    )

    assert HistoricalAdmissibilityEvidenceAdmissionReceiptValidator().validate(
        receipt=chain["admission_receipt"],
        expected_hash=chain["admission_receipt_hash"],
    )

    assert HistoricalAdmissibilityEvidencePackageValidator().validate(
        package=chain["package"],
        expected_hash=chain["package_hash"],
    )

    assert HistoricalAdmissibilityEvidencePackageReceiptValidator().validate(
        receipt=chain["package_receipt"],
        expected_hash=chain["package_receipt_hash"],
    )


@pytest.mark.parametrize(
    "status_field, expected_status",
    [
        ("trust_status", "PASS"),
        ("admission_status", "PASS"),
        ("package_status", "PASS"),
    ],
)
def test_pass_status_never_grants_authority(
    status_field: str,
    expected_status: str,
) -> None:
    chain = build_chain()

    objects = (
        chain["trust_assessment"],
        chain["trust_receipt"],
        chain["admission_assessment"],
        chain["admission_receipt"],
        chain["package"],
        chain["package_receipt"],
    )

    matching_objects = [
        artifact
        for artifact in objects
        if hasattr(artifact, status_field)
    ]

    assert matching_objects
    assert all(
        getattr(artifact, status_field) == expected_status
        for artifact in matching_objects
    )

    for artifact in objects:
        if hasattr(artifact, "trust_established"):
            assert artifact.trust_established is False

        if hasattr(artifact, "evidence_admitted"):
            assert artifact.evidence_admitted is False

        assert artifact.authorization_granted is False
        assert artifact.execution_requested is False
        assert artifact.side_effects_permitted is False


@pytest.mark.parametrize(
    "trust_status, admission_status, package_status",
    [
        ("HOLD", "HOLD", "HOLD"),
        ("REJECT", "REJECT", "REJECT"),
    ],
)
def test_hold_and_reject_statuses_are_preserved_end_to_end(
    trust_status: str,
    admission_status: str,
    package_status: str,
) -> None:
    chain = build_chain(
        trust_status=trust_status,
        admission_status=admission_status,
        package_status=package_status,
    )

    assert chain["trust_assessment"].trust_status == trust_status
    assert chain["trust_receipt"].trust_status == trust_status
    assert (
        chain["admission_assessment"].admission_status
        == admission_status
    )
    assert (
        chain["admission_receipt"].admission_status
        == admission_status
    )
    assert chain["package_receipt"].package_status == package_status

    assert chain["package"].evidence_admitted is False
    assert chain["package_receipt"].evidence_admitted is False


def test_complete_chain_is_deterministically_reproducible() -> None:
    first = build_chain()
    second = build_chain()

    hash_names = (
        "bundle_hash",
        "provenance_hash",
        "manifest_hash",
        "trust_assessment_hash",
        "trust_receipt_hash",
        "admission_assessment_hash",
        "admission_receipt_hash",
        "package_hash",
        "package_receipt_hash",
    )

    for hash_name in hash_names:
        assert first[hash_name] == second[hash_name]

    assert first["package"] == second["package"]
    assert first["package_receipt"] == second["package_receipt"]


def test_complete_chain_models_remain_immutable() -> None:
    chain = build_chain()

    with pytest.raises(FrozenInstanceError):
        chain["package"].package_version = "changed"  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        chain["package_receipt"].package_status = "HOLD"  # type: ignore[misc]


def test_complete_chain_preserves_observer_only_invariants() -> None:
    chain = build_chain()

    artifacts = (
        chain["bundle"],
        chain["provenance"],
        chain["manifest"],
        chain["trust_assessment"],
        chain["trust_receipt"],
        chain["admission_assessment"],
        chain["admission_receipt"],
        chain["package"],
        chain["package_receipt"],
    )

    for artifact in artifacts:
        if hasattr(artifact, "trust_established"):
            assert artifact.trust_established is False

        if hasattr(artifact, "evidence_admitted"):
            assert artifact.evidence_admitted is False

        assert artifact.authorization_granted is False
        assert artifact.execution_requested is False
        assert artifact.side_effects_permitted is False