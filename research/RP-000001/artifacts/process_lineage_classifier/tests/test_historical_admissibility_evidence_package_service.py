import pytest

from models.historical_admissibility_evidence_package import (
    HistoricalAdmissibilityEvidencePackage,
)
from models.historical_admissibility_evidence_admission_receipt import (
    HistoricalAdmissibilityEvidenceAdmissionReceipt,
)
from models.historical_admissibility_evidence_provenance_manifest import (
    HistoricalAdmissibilityEvidenceProvenanceManifest,
)
from models.historical_admissibility_evidence_trust_receipt import (
    HistoricalAdmissibilityEvidenceTrustReceipt,
)
from models.historical_signature_admissibility_bundle import (
    HistoricalSignatureAdmissibilityBundle,
)
from services.historical_admissibility_evidence_admission_receipt_hasher import (
    HistoricalAdmissibilityEvidenceAdmissionReceiptHasher,
)
from services.historical_admissibility_evidence_package_service import (
    HistoricalAdmissibilityEvidencePackageService,
)
from services.historical_admissibility_evidence_provenance_manifest_hasher import (
    HistoricalAdmissibilityEvidenceProvenanceManifestHasher,
)
from services.historical_admissibility_evidence_trust_receipt_hasher import (
    HistoricalAdmissibilityEvidenceTrustReceiptHasher,
)
from services.historical_signature_admissibility_bundle_hasher import (
    HistoricalSignatureAdmissibilityBundleHasher,
)


def make_bundle() -> HistoricalSignatureAdmissibilityBundle:
    return HistoricalSignatureAdmissibilityBundle(
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


def make_manifest() -> HistoricalAdmissibilityEvidenceProvenanceManifest:
    return HistoricalAdmissibilityEvidenceProvenanceManifest(
        manifest_id="HAEPM-000001",
        bundle_id="HSAB-000001",
        provenance_hashes=("c" * 64,),
        record_count=1,
        assembled_at="2026-07-16T19:00:00Z",
        trust_established=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_trust_receipt() -> HistoricalAdmissibilityEvidenceTrustReceipt:
    return HistoricalAdmissibilityEvidenceTrustReceipt(
        receipt_id="HAETR-000001",
        assessment_id="HAETA-000001",
        assessment_hash="d" * 64,
        manifest_id="HAEPM-000001",
        manifest_hash=(
            HistoricalAdmissibilityEvidenceProvenanceManifestHasher()
            .hash_manifest(make_manifest())
        ),
        trust_status="PASS",
        confidence_level="HIGH",
        policy_version="historical-evidence-trust-v1",
        recorded_at="2026-07-16T20:30:00Z",
        trust_established=False,
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def make_admission_receipt() -> HistoricalAdmissibilityEvidenceAdmissionReceipt:
    trust_receipt = make_trust_receipt()

    return HistoricalAdmissibilityEvidenceAdmissionReceipt(
        receipt_id="HAEAR-000001",
        assessment_id="HAEAA-000001",
        assessment_hash="e" * 64,
        trust_receipt_id=trust_receipt.receipt_id,
        trust_receipt_hash=(
            HistoricalAdmissibilityEvidenceTrustReceiptHasher()
            .hash_receipt(trust_receipt)
        ),
        admission_status="PASS",
        policy_version="historical-evidence-admission-v1",
        recorded_at="2026-07-16T21:30:00Z",
        evidence_admitted=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )


def test_service_assembles_package_from_validated_chain() -> None:
    bundle = make_bundle()
    manifest = make_manifest()
    trust_receipt = make_trust_receipt()
    admission_receipt = make_admission_receipt()

    package = HistoricalAdmissibilityEvidencePackageService().assemble(
        package_id="HAEPKG-000001",
        admissibility_bundle=bundle,
        admissibility_bundle_hash=(
            HistoricalSignatureAdmissibilityBundleHasher()
            .hash_bundle(bundle)
        ),
        provenance_manifest=manifest,
        provenance_manifest_hash=(
            HistoricalAdmissibilityEvidenceProvenanceManifestHasher()
            .hash_manifest(manifest)
        ),
        trust_receipt=trust_receipt,
        trust_receipt_hash=(
            HistoricalAdmissibilityEvidenceTrustReceiptHasher()
            .hash_receipt(trust_receipt)
        ),
        admission_receipt=admission_receipt,
        admission_receipt_hash=(
            HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()
            .hash_receipt(admission_receipt)
        ),
        package_version="historical-evidence-package-v1",
        assembled_at="2026-07-16T22:00:00Z",
    )

    assert isinstance(package, HistoricalAdmissibilityEvidencePackage)
    assert package.package_id == "HAEPKG-000001"
    assert package.admissibility_bundle_id == "HSAB-000001"
    assert package.provenance_manifest_id == "HAEPM-000001"
    assert package.trust_receipt_id == "HAETR-000001"
    assert package.admission_receipt_id == "HAEAR-000001"


@pytest.mark.parametrize(
    "field_name",
    [
        "admissibility_bundle",
        "provenance_manifest",
        "trust_receipt",
        "admission_receipt",
    ],
)
def test_service_rejects_missing_chain_component(
    field_name: str,
) -> None:
    bundle = make_bundle()
    manifest = make_manifest()
    trust_receipt = make_trust_receipt()
    admission_receipt = make_admission_receipt()

    values = {
        "package_id": "HAEPKG-000001",
        "admissibility_bundle": bundle,
        "admissibility_bundle_hash": (
            HistoricalSignatureAdmissibilityBundleHasher()
            .hash_bundle(bundle)
        ),
        "provenance_manifest": manifest,
        "provenance_manifest_hash": (
            HistoricalAdmissibilityEvidenceProvenanceManifestHasher()
            .hash_manifest(manifest)
        ),
        "trust_receipt": trust_receipt,
        "trust_receipt_hash": (
            HistoricalAdmissibilityEvidenceTrustReceiptHasher()
            .hash_receipt(trust_receipt)
        ),
        "admission_receipt": admission_receipt,
        "admission_receipt_hash": (
            HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()
            .hash_receipt(admission_receipt)
        ),
        "package_version": "historical-evidence-package-v1",
        "assembled_at": "2026-07-16T22:00:00Z",
    }
    values[field_name] = None

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidencePackageService().assemble(**values)


def test_service_rejects_cross_chain_identifier_mismatch() -> None:
    bundle = make_bundle()

    mismatched_manifest = HistoricalAdmissibilityEvidenceProvenanceManifest(
        manifest_id="HAEPM-000001",
        bundle_id="HSAB-999999",
        provenance_hashes=("c" * 64,),
        record_count=1,
        assembled_at="2026-07-16T19:00:00Z",
        trust_established=False,
        authorization_granted=False,
        execution_requested=False,
        side_effects_permitted=False,
    )

    trust_receipt = make_trust_receipt()
    admission_receipt = make_admission_receipt()

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidencePackageService().assemble(
            package_id="HAEPKG-000001",
            admissibility_bundle=bundle,
            admissibility_bundle_hash=(
                HistoricalSignatureAdmissibilityBundleHasher()
                .hash_bundle(bundle)
            ),
            provenance_manifest=mismatched_manifest,
            provenance_manifest_hash=(
                HistoricalAdmissibilityEvidenceProvenanceManifestHasher()
                .hash_manifest(mismatched_manifest)
            ),
            trust_receipt=trust_receipt,
            trust_receipt_hash=(
                HistoricalAdmissibilityEvidenceTrustReceiptHasher()
                .hash_receipt(trust_receipt)
            ),
            admission_receipt=admission_receipt,
            admission_receipt_hash=(
                HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()
                .hash_receipt(admission_receipt)
            ),
            package_version="historical-evidence-package-v1",
            assembled_at="2026-07-16T22:00:00Z",
        )


def test_service_rejects_non_matching_component_hash() -> None:
    bundle = make_bundle()
    manifest = make_manifest()
    trust_receipt = make_trust_receipt()
    admission_receipt = make_admission_receipt()

    with pytest.raises(ValueError):
        HistoricalAdmissibilityEvidencePackageService().assemble(
            package_id="HAEPKG-000001",
            admissibility_bundle=bundle,
            admissibility_bundle_hash="f" * 64,
            provenance_manifest=manifest,
            provenance_manifest_hash=(
                HistoricalAdmissibilityEvidenceProvenanceManifestHasher()
                .hash_manifest(manifest)
            ),
            trust_receipt=trust_receipt,
            trust_receipt_hash=(
                HistoricalAdmissibilityEvidenceTrustReceiptHasher()
                .hash_receipt(trust_receipt)
            ),
            admission_receipt=admission_receipt,
            admission_receipt_hash=(
                HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()
                .hash_receipt(admission_receipt)
            ),
            package_version="historical-evidence-package-v1",
            assembled_at="2026-07-16T22:00:00Z",
        )


def test_service_preserves_observer_only_invariants() -> None:
    bundle = make_bundle()
    manifest = make_manifest()
    trust_receipt = make_trust_receipt()
    admission_receipt = make_admission_receipt()

    package = HistoricalAdmissibilityEvidencePackageService().assemble(
        package_id="HAEPKG-000001",
        admissibility_bundle=bundle,
        admissibility_bundle_hash=(
            HistoricalSignatureAdmissibilityBundleHasher()
            .hash_bundle(bundle)
        ),
        provenance_manifest=manifest,
        provenance_manifest_hash=(
            HistoricalAdmissibilityEvidenceProvenanceManifestHasher()
            .hash_manifest(manifest)
        ),
        trust_receipt=trust_receipt,
        trust_receipt_hash=(
            HistoricalAdmissibilityEvidenceTrustReceiptHasher()
            .hash_receipt(trust_receipt)
        ),
        admission_receipt=admission_receipt,
        admission_receipt_hash=(
            HistoricalAdmissibilityEvidenceAdmissionReceiptHasher()
            .hash_receipt(admission_receipt)
        ),
        package_version="historical-evidence-package-v1",
        assembled_at="2026-07-16T22:00:00Z",
    )

    assert package.evidence_admitted is False
    assert package.authorization_granted is False
    assert package.execution_requested is False
    assert package.side_effects_permitted is False