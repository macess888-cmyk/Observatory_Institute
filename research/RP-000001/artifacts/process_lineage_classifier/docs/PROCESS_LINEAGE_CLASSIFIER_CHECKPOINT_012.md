# PROCESS LINEAGE CLASSIFIER — CHECKPOINT 012

**Research Program:** RP-000001 — Organized Understanding
**Artifact:** RA-000001 — Process Lineage Classifier Prototype
**Checkpoint:** 012
**Version:** 0.12.0
**Date:** 2026-07-16
**Status:** IMPLEMENTED — VALIDATED — READY TO FREEZE

---

## 1. Checkpoint Purpose

Checkpoint 012 extends the Process Lineage Classifier from historical trusted-key registry reconstruction into time-aware historical signature verification, compromise analysis, and evidence-bound admissibility classification.

This checkpoint implements:

* historical signature verification;
* explicit signing-time and verification-time registry bindings;
* immutable historical verification receipts;
* deterministic historical verification receipt hashing;
* confirmed key-compromise event records;
* deterministic key-compromise event hashing;
* historical signature compromise timing assessment;
* deterministic compromise-assessment hashing;
* historical signature admissibility classification;
* deterministic admissibility-assessment hashing.

Checkpoint 012 establishes the ability to determine:

```text
Whether a signature was mathematically valid,
whether its key was trusted when signing occurred,
whether a later compromise affected the signing time,
and whether the available evidence supports
PASS, HOLD, or REJECT.
```

The checkpoint remains:

```text
OBSERVER-ONLY
DETERMINISTIC
IMMUTABLE
TIME-AWARE
REGISTRY-BOUND
EVIDENCE-BOUND
NON-RETROACTIVE
NO AUTHORIZATION
NO EXECUTION
NO SIDE EFFECTS
UNKNOWN → HOLD
```

---

## 2. Checkpoint Boundary

Checkpoint 012 evaluates historical signature evidence.

It does not:

* grant signer authority;
* authorize execution;
* mutate trusted-key registries;
* revoke keys;
* invalidate signatures automatically;
* infer an unknown compromise start time;
* treat compromise detection as compromise inception;
* establish legal admissibility;
* establish institutional approval;
* perform external trust resolution;
* execute recovery activity;
* permit side effects.

The checkpoint establishes:

```text
Historical Registry State
        ↓
Signing-Time Key Presence
        ↓
Canonical Payload Verification
        ↓
Mathematical Signature Verification
        ↓
Historical Verification Receipt
        ↓
Compromise Event
        ↓
Compromise Timing Assessment
        ↓
Historical Admissibility Assessment
```

---

## 3. Governing Distinctions

Checkpoint 012 preserves:

```text
Key Trusted at Signing Time
        ≠
Key Trusted at Verification Time
```

```text
Key Removed Later
        ≠
Signature Invalid Earlier
```

```text
Compromise Effective Time
        ≠
Compromise Detection Time
```

```text
Compromise Detection
        ≠
Automatic Retroactive Invalidation
```

```text
Mathematical Verification
        ≠
Authorization
```

```text
Historical Validity
        ≠
Current Trust
```

```text
Admissibility PASS
        ≠
Execution Permission
```

```text
Missing Evidence
        ≠
Negative Evidence
```

```text
UNKNOWN
        →
HOLD
```

---

## 4. New Model

Checkpoint 012 introduces:

```text
HistoricalSignatureVerificationReceipt
KeyCompromiseEvent
```

It also introduces two immutable service-layer evidence models:

```text
HistoricalSignatureCompromiseAssessment
HistoricalSignatureAdmissibilityAssessment
```

All are:

```text
FROZEN
SLOTTED
VALIDATED
OBSERVER-ONLY
SIDE-EFFECT FREE
```

---

## 5. New Services

Checkpoint 012 introduces:

```text
HistoricalSignatureVerificationService
HistoricalSignatureVerificationReceiptService
HistoricalSignatureVerificationReceiptHasher
KeyCompromiseEventValidator
KeyCompromiseEventHasher
HistoricalSignatureCompromiseAssessmentService
HistoricalSignatureCompromiseAssessmentHasher
HistoricalSignatureAdmissibilityService
HistoricalSignatureAdmissibilityAssessmentHasher
```

---

## 6. Historical Signature Verification

`HistoricalSignatureVerificationService` verifies a detached signature against a reconstructed trusted-key registry state.

Inputs include:

```text
RecoveryIntegrityBundle
DetachedSignature
registry_id
signing_registry_version
verification_registry_version
registry snapshots
registry version records
receipt identity
verification identity
verifier identity
verification time
```

---

## 7. Historical Verification Sequence

```text
Validate Bundle
        ↓
Validate Detached Signature
        ↓
Validate Registry References
        ↓
Validate Verification Time
        ↓
Validate Subject Identity
        ↓
Generate Canonical Payload
        ↓
Recalculate Payload Digest
        ↓
Reconstruct Signing-Time Registry
        ↓
Reconstruct Verification-Time Registry
        ↓
Resolve Signing Key from Historical Snapshot
        ↓
Verify Ed25519 Signature
        ↓
Create Verification Receipt
```

---

## 8. Signing-Time Registry Boundary

The service reconstructs:

```text
signing_registry_version
```

and requires the signature key to exist in that snapshot.

```text
Key Present at Signing Time
        →
Historical Trust Evidence Available
```

```text
Key Absent at Signing Time
        →
REJECT
```

---

## 9. Verification-Time Registry Boundary

The service also reconstructs:

```text
verification_registry_version
```

The signature key may be absent from the verification-time registry without invalidating a signature created while the key was historically trusted.

```text
Present at Signing Time
        +
Absent at Verification Time
        ≠
Historical Invalidity
```

---

## 10. Historical Signature Rejections

The service rejects:

* non-bundle input;
* non-signature input;
* empty registry identity;
* empty signing registry version;
* empty verification registry version;
* empty receipt identity;
* empty verification identity;
* empty verifier identity;
* non-tuple snapshots;
* non-tuple version records;
* timezone-naive verification time;
* verification before signature creation;
* signature subject mismatch;
* signature subject-type mismatch;
* content-digest mismatch;
* unknown signing registry version;
* unknown verification registry version;
* signing key absent from historical registry;
* mathematical signature verification failure;
* verification receipt construction failure.

---

## 11. Historical Verification Invariant

```text
Historical Signature Verification
        =
Canonical Payload Match
        +
Signing-Time Key Presence
        +
Historical Registry Binding
        +
Mathematical Signature Verification
```

```text
Historical Signature Verification
        ≠
Signer Authorization
```

---

## 12. Historical Signature Verification Receipt

`HistoricalSignatureVerificationReceipt` records complete signing-time and verification-time trust evidence.

Fields include:

```text
receipt_id
verification_id
signature_id
key_id
subject_id
subject_type
content_digest
payload_digest
public_key_fingerprint
algorithm
signer_id
verifier_id
registry_id
signing_registry_version
signing_snapshot_id
signing_snapshot_digest
verification_registry_version
verification_snapshot_id
verification_snapshot_digest
signed_at
verified_at
mathematical_verification
identity_match
content_match
signing_time_key_present
verification_time_key_present
key_valid_at_signing
verified
execution_requested
side_effects_permitted
```

---

## 13. Required Verification Components

A verified receipt requires:

```text
mathematical_verification = True
identity_match = True
content_match = True
signing_time_key_present = True
key_valid_at_signing = True
```

`verification_time_key_present` may be:

```text
True
```

or:

```text
False
```

without changing historical verification success.

---

## 14. Verification Receipt Boundary

```text
signing_time_key_present = True
verification_time_key_present = False
verified = True
```

is valid.

This preserves:

```text
Key Removed Later
        ≠
Signature Invalid Earlier
```

---

## 15. Verification Receipt Rejections

The model or service rejects:

* empty identities;
* malformed content digest;
* malformed payload digest;
* malformed fingerprint;
* malformed snapshot digests;
* unsupported signature algorithm;
* timezone-naive signing time;
* timezone-naive verification time;
* verification before signing;
* non-Boolean verification components;
* failed required verification components;
* inconsistent verified state;
* observer-only violations.

---

## 16. Historical Verification Receipt Hashing

`HistoricalSignatureVerificationReceiptHasher` creates a deterministic SHA-256 digest of complete receipt state.

Output:

```text
sha256:<64 lowercase hexadecimal characters>
```

---

## 17. Historical Verification Canonical Field Order

```text
receipt_id
verification_id
signature_id
key_id
subject_id
subject_type
content_digest
payload_digest
public_key_fingerprint
algorithm
signer_id
verifier_id
registry_id
signing_registry_version
signing_snapshot_id
signing_snapshot_digest
verification_registry_version
verification_snapshot_id
verification_snapshot_digest
signed_at
verified_at
mathematical_verification
identity_match
content_match
signing_time_key_present
verification_time_key_present
key_valid_at_signing
verified
execution_requested
side_effects_permitted
```

---

## 18. Verification Receipt Hash Determinism

```text
Equivalent Historical Receipt
        →
Identical Canonical Bytes
        →
Identical Hash
```

```text
Registry Version Change
        →
Different Hash
```

```text
Snapshot Identity Change
        →
Different Hash
```

```text
Verification-Time Key Presence Change
        →
Different Hash
```

---

## 19. Verification Receipt Hash Rejections

The hasher rejects:

* non-receipt input;
* malformed expected digest;
* receipt hash mismatch.

---

## 20. Key Compromise Event

`KeyCompromiseEvent` records confirmed evidence that a key may no longer be trustworthy from a declared effective time.

Fields include:

```text
event_id
key_id
material_id
public_key_fingerprint
owner_id
issuer_id
compromise_type
evidence_digest
detected_at
effective_at
recorded_at
reported_by
description
confirmed
historical_signatures_invalidated
execution_requested
side_effects_permitted
```

---

## 21. Supported Compromise Types

Checkpoint 012 supports:

```text
PRIVATE_KEY_EXPOSURE
UNAUTHORIZED_KEY_USE
KEY_MATERIAL_LOSS
UNKNOWN_COMPROMISE
```

Other compromise types are rejected.

---

## 22. Compromise Time Semantics

The event distinguishes:

```text
effective_at
```

The declared time from which compromise evidence is considered applicable.

```text
detected_at
```

The time compromise evidence was discovered.

```text
recorded_at
```

The time the event was formally recorded.

Required temporal order:

```text
effective_at
        ≤
detected_at
        ≤
recorded_at
```

---

## 23. Compromise Timing Boundary

```text
Effective Compromise Time
        ≠
Detection Time
```

A signature created before detection but after the effective compromise time remains exposed.

```text
signed_at < detected_at
```

does not prove pre-compromise validity.

The relevant comparison is:

```text
signed_at
        vs
effective_at
```

---

## 24. Non-Retroactive Event Boundary

Checkpoint 012 enforces:

```text
historical_signatures_invalidated = False
```

A compromise event records evidence.

It does not automatically invalidate every historical signature.

---

## 25. Key Compromise Event Rejections

The model or validator rejects:

* empty event identity;
* empty key identity;
* empty material identity;
* malformed fingerprint;
* empty owner identity;
* empty issuer identity;
* unsupported compromise type;
* malformed evidence digest;
* timezone-naive event times;
* detection before effective time;
* recording before detection;
* empty reporter identity;
* empty description;
* non-Boolean confirmation;
* unconfirmed event during validation;
* non-Boolean historical invalidation state;
* automatic historical invalidation claim;
* reference mismatch;
* partial expected-reference set;
* observer-only violations.

---

## 26. Key Compromise Event Validation

`KeyCompromiseEventValidator` may bind expected:

```text
key_id
material_id
owner_id
issuer_id
public_key_fingerprint
```

Expected references must be complete or absent.

---

## 27. Key Compromise Event Hashing

`KeyCompromiseEventHasher` creates a deterministic digest of complete compromise evidence.

---

## 28. Key Compromise Canonical Field Order

```text
event_id
key_id
material_id
public_key_fingerprint
owner_id
issuer_id
compromise_type
evidence_digest
detected_at
effective_at
recorded_at
reported_by
description
confirmed
historical_signatures_invalidated
execution_requested
side_effects_permitted
```

---

## 29. Key Compromise Hash Determinism

```text
Equivalent Compromise Event
        →
Identical Hash
```

```text
Effective-Time Change
        →
Different Hash
```

```text
Detection-Time Change
        →
Different Hash
```

```text
Recorded-Time Change
        →
Different Hash
```

```text
Evidence Change
        →
Different Hash
```

---

## 30. Historical Signature Compromise Assessment

`HistoricalSignatureCompromiseAssessmentService` compares a verified historical signature receipt against a confirmed compromise event.

Output:

```text
HistoricalSignatureCompromiseAssessment
```

---

## 31. Compromise Assessment Inputs

```text
assessment_id
HistoricalSignatureVerificationReceipt
KeyCompromiseEvent
assessed_by
assessed_at
```

---

## 32. Compromise Assessment Sequence

```text
Validate Assessment Identity
        ↓
Validate Historical Verification Receipt
        ↓
Validate Confirmed Compromise Event
        ↓
Validate Key Identity Binding
        ↓
Validate Fingerprint Binding
        ↓
Validate Assessment Time
        ↓
Compare signed_at with effective_at
        ↓
Classify Timing
        ↓
Preserve or Withhold Historical Validity
```

---

## 33. Compromise Timing Classifications

### PRE_COMPROMISE_VALID

```text
signed_at
        <
compromise_effective_at
```

Produces:

```text
signature_precedes_compromise = True
signature_at_or_after_compromise = False
historical_validity_preserved = True
status = PRE_COMPROMISE_VALID
```

### AT_OR_AFTER_COMPROMISE

```text
signed_at
        ≥
compromise_effective_at
```

Produces:

```text
signature_precedes_compromise = False
signature_at_or_after_compromise = True
historical_validity_preserved = False
status = AT_OR_AFTER_COMPROMISE
```

---

## 34. Exact Effective-Time Boundary

A signature created exactly at the effective compromise time is classified:

```text
AT_OR_AFTER_COMPROMISE
```

---

## 35. Compromise Assessment Rejections

The service rejects:

* empty assessment identity;
* empty assessor identity;
* non-receipt input;
* non-compromise-event input;
* unverified receipt;
* unconfirmed compromise event;
* key identity mismatch;
* fingerprint mismatch;
* timezone-naive assessment time;
* assessment before compromise recording;
* observer-only violations.

---

## 36. Compromise Assessment Invariant

```text
Historical Compromise Assessment
        =
Verified Historical Signature
        +
Confirmed Compromise Evidence
        +
Effective-Time Comparison
```

```text
Compromise Detected Later
        ≠
Automatic Retroactive Invalidation
```

---

## 37. Compromise Assessment Hashing

`HistoricalSignatureCompromiseAssessmentHasher` hashes complete compromise-timing classification evidence.

---

## 38. Compromise Assessment Canonical Field Order

```text
assessment_id
receipt_id
verification_id
signature_id
key_id
material_id
public_key_fingerprint
compromise_event_id
compromise_type
signed_at
compromise_effective_at
compromise_detected_at
compromise_recorded_at
assessed_at
assessed_by
signature_precedes_compromise
signature_at_or_after_compromise
historical_validity_preserved
automatic_retroactive_invalidation
status
execution_requested
side_effects_permitted
```

---

## 39. Compromise Assessment Hash Determinism

```text
Equivalent Assessment
        →
Identical Hash
```

```text
Timing Change
        →
Different Hash
```

```text
Classification Change
        →
Different Hash
```

```text
Status Change
        →
Different Hash
```

---

## 40. Historical Signature Admissibility

`HistoricalSignatureAdmissibilityService` combines verification evidence and compromise timing evidence.

It produces:

```text
HistoricalSignatureAdmissibilityAssessment
```

---

## 41. Admissibility Inputs

```text
admissibility_id
HistoricalSignatureVerificationReceipt | None
HistoricalSignatureCompromiseAssessment | None
assessed_by
assessed_at
```

---

## 42. Admissibility Outcomes

Checkpoint 012 supports:

```text
PASS
HOLD
REJECT
```

---

## 43. PASS

PASS requires:

```text
Verified historical signature receipt
        +
Compromise assessment available
        +
historical_validity_preserved = True
```

Produces:

```text
outcome = PASS
admissible = True
hold_required = False
rejected = False
authorization_granted = False
```

---

## 44. HOLD

HOLD occurs when required evidence is missing.

Examples:

```text
Verification Receipt Missing
```

or:

```text
Compromise Assessment Missing
```

Produces:

```text
outcome = HOLD
admissible = False
hold_required = True
rejected = False
authorization_granted = False
```

---

## 45. REJECT

REJECT occurs when:

```text
historical_validity_preserved = False
```

Produces:

```text
outcome = REJECT
admissible = False
hold_required = False
rejected = True
authorization_granted = False
```

---

## 46. Admissibility Reference Binding

When both evidence objects are present, the service requires matching:

```text
receipt_id
signature_id
key_id
public_key_fingerprint
```

A mismatch is rejected.

---

## 47. Admissibility Rejections

The service rejects:

* empty admissibility identity;
* empty assessor identity;
* non-receipt input;
* non-compromise-assessment input;
* unverified receipt;
* assessment before verification;
* receipt identity mismatch;
* signature identity mismatch;
* key identity mismatch;
* fingerprint mismatch;
* timezone-naive assessment time;
* observer-only violations.

---

## 48. Admissibility Boundary

```text
PASS
        ≠
Authorization
```

```text
PASS
        ≠
Execution
```

```text
PASS
        ≠
Side-Effect Permission
```

The service enforces:

```text
authorization_granted = False
execution_requested = False
side_effects_permitted = False
```

---

## 49. Unknown-to-Hold Boundary

```text
Missing Verification Evidence
        →
HOLD
```

```text
Missing Compromise Evidence
        →
HOLD
```

```text
Unknown
        ≠
Reject
```

```text
UNKNOWN
        →
HOLD
```

---

## 50. Admissibility Assessment Hashing

`HistoricalSignatureAdmissibilityAssessmentHasher` hashes complete PASS, HOLD, or REJECT evidence.

---

## 51. Admissibility Canonical Field Order

```text
admissibility_id
receipt_id
verification_id
signature_id
key_id
public_key_fingerprint
compromise_assessment_id
compromise_event_id
assessed_by
assessed_at
verification_evidence_available
compromise_evidence_available
historical_validity_preserved
outcome
admissible
hold_required
rejected
authorization_granted
execution_requested
side_effects_permitted
```

---

## 52. Admissibility Hash Determinism

```text
Equivalent Assessment
        →
Identical Hash
```

```text
Outcome Change
        →
Different Hash
```

```text
Missing Evidence
        →
Different Hash
```

```text
Assessment-Time Change
        →
Different Hash
```

---

## 53. Complete Checkpoint 012 Architecture

```text
HistoricalRegistryReconstructionService
        ↓
HistoricalSignatureVerificationService
        ↓
HistoricalSignatureVerificationReceipt
        ↓
HistoricalSignatureVerificationReceiptHasher
        ↓
KeyCompromiseEvent
        ↓
KeyCompromiseEventValidator
        ↓
KeyCompromiseEventHasher
        ↓
HistoricalSignatureCompromiseAssessmentService
        ↓
HistoricalSignatureCompromiseAssessmentHasher
        ↓
HistoricalSignatureAdmissibilityService
        ↓
HistoricalSignatureAdmissibilityAssessmentHasher
```

---

## 54. Checkpoint 011 to 012 Transition

Checkpoint 011 established:

```text
Historical Trusted-Key Registry Reconstruction
```

Checkpoint 012 adds:

```text
Historical Signature Verification
        ↓
Compromise Effective-Time Analysis
        ↓
Historical Admissibility Classification
```

---

## 55. Complete Historical Trust Flow

```text
Detached Signature
        ↓
Canonical Signed Payload
        ↓
Signing-Time Registry Version
        ↓
Historical Registry Reconstruction
        ↓
Signing-Time Key Presence
        ↓
Mathematical Verification
        ↓
Historical Verification Receipt
        ↓
Compromise Event
        ↓
Effective-Time Comparison
        ↓
Compromise Assessment
        ↓
PASS / HOLD / REJECT
```

---

## 56. Checkpoint 012 Test Results

Checkpoint-specific tests:

```text
Historical signature verification: 14 passed
Historical verification receipt: 40 passed
Historical verification receipt hasher: 28 passed
Key compromise event: 37 passed
Key compromise event hasher: 28 passed
Historical compromise assessment: 18 passed
Historical compromise assessment hasher: 34 passed
Historical signature admissibility: 19 passed
Historical admissibility hasher: 34 passed
```

Checkpoint 012 additions:

```text
252 PASSED
0 FAILED
```

Full prototype suite:

```text
1650 PASSED
0 FAILED
```

---

## 57. Verified Behaviors

```text
Signing-time key present → PASS verification
Verification-time key absent → historical verification preserved
Signing-time key absent → REJECT
Unknown signing registry version → REJECT
Unknown verification registry version → REJECT
Modified payload → REJECT
Modified signature → REJECT
Verification before signing → REJECT

Equivalent historical receipt → identical hash
Historical receipt change → different hash

Confirmed compromise event → PASS validation
Unconfirmed compromise event → REJECT
Detection before effective time → REJECT
Recording before detection → REJECT
Automatic historical invalidation → REJECT

Equivalent compromise event → identical hash
Compromise timing change → different hash

Signature before effective compromise → PRE_COMPROMISE_VALID
Signature at effective compromise → AT_OR_AFTER_COMPROMISE
Signature after effective compromise → AT_OR_AFTER_COMPROMISE
Detection time used as validity boundary → NEVER

Verified + pre-compromise → PASS
Verified + at/after compromise → REJECT
Missing verification evidence → HOLD
Missing compromise evidence → HOLD

PASS grants authorization → NEVER
PASS requests execution → NEVER
PASS permits side effects → NEVER
```

---

## 58. Previous Checkpoint Compatibility

```text
CHECKPOINT 001 CAPABILITIES: PRESERVED
CHECKPOINT 002 CAPABILITIES: PRESERVED
CHECKPOINT 003 CAPABILITIES: PRESERVED
CHECKPOINT 004 CAPABILITIES: PRESERVED
CHECKPOINT 005 CAPABILITIES: PRESERVED
CHECKPOINT 006 CAPABILITIES: PRESERVED
CHECKPOINT 007 CAPABILITIES: PRESERVED
CHECKPOINT 008 CAPABILITIES: PRESERVED
CHECKPOINT 009 CAPABILITIES: PRESERVED
CHECKPOINT 010 CAPABILITIES: PRESERVED
CHECKPOINT 011 CAPABILITIES: PRESERVED
```

Regression result:

```text
1650 PASSED
0 FAILED
```

---

## 59. Operational Outcomes

### PASS

A historical verification receipt is valid, the signing key was trusted at signing time, mathematical verification succeeded, compromise evidence is available, and the signature predates the effective compromise time.

### HOLD

Required historical verification evidence or compromise evidence is unavailable.

### REJECT

The signature was created at or after the confirmed effective compromise time, or an identity, digest, registry, timing, mathematical, evidence-binding, or observer-only invariant failed.

---

## 60. Checkpoint Determination

```text
CHECKPOINT 012: PASS

HISTORICAL SIGNATURE VERIFICATION: IMPLEMENTED
SIGNING-TIME TRUST RESOLUTION: IMPLEMENTED
VERIFICATION-TIME TRUST RESOLUTION: IMPLEMENTED

HISTORICAL VERIFICATION RECEIPT: IMPLEMENTED
HISTORICAL RECEIPT HASHING: IMPLEMENTED

KEY COMPROMISE EVENT MODEL: IMPLEMENTED
KEY COMPROMISE VALIDATION: IMPLEMENTED
KEY COMPROMISE HASHING: IMPLEMENTED

COMPROMISE EFFECTIVE-TIME ASSESSMENT: IMPLEMENTED
COMPROMISE ASSESSMENT HASHING: IMPLEMENTED

HISTORICAL SIGNATURE ADMISSIBILITY: IMPLEMENTED
ADMISSIBILITY ASSESSMENT HASHING: IMPLEMENTED

PASS / HOLD / REJECT: VERIFIED
UNKNOWN → HOLD: VERIFIED
NON-RETROACTIVE BOUNDARY: VERIFIED
NO-AUTHORIZATION BOUNDARY: VERIFIED
OBSERVER-ONLY BOUNDARY: VERIFIED

AUTHORIZATION: NONE
EXECUTION: NONE
SIDE EFFECTS: NONE

TESTS: 1650 PASSED
FAILURES: 0
READY TO FREEZE: YES
```

---

## 61. Remaining Freeze Steps

```text
Save Checkpoint 012 document
Return to repository root
Inspect Git status
Stage Checkpoint 012 files
Review staged file list
Review staged diff statistics
Run full test suite once more
Run git diff --cached --check
Commit
Push
Verify synchronized repository
Verify clean working tree
```

---

## 62. Next Capability Boundary

Checkpoint 013 may consider:

```text
compromise confidence levels
compromise evidence provenance
multiple compromise events per key
compromise-event supersession
compromise-event correction
compromise uncertainty windows
earliest-known compromise time
latest-possible compromise time
partial compromise evidence
independently re-establishable compromise state
irreversibly lost compromise state
historical verification bundles
portable historical evidence packages
cross-institution historical verification
issuer compromise events
registry authority compromise
signature-policy-at-signing-time
signature-policy-at-verification-time
admissibility policy version binding
multi-signature historical verification
quorum signature verification
threshold-signature history
historical verification audit chain
historical admissibility receipt
admissibility receipt hashing
admissibility evidence export
```

These capabilities are not included in Checkpoint 012.

---

## 63. Final Checkpoint Statement

Checkpoint 012 demonstrates that a signature can be evaluated against the trusted-key registry state that existed when signing occurred, compared against later compromise evidence using an explicit effective time, and classified as PASS, HOLD, or REJECT without collapsing later discovery into automatic retroactive invalidity.

The governing reductions remain:

```text
Key Trusted Then
        ≠
Key Trusted Now
```

```text
Key Removed Now
        ≠
Signature Invalid Then
```

```text
Compromise Detected Later
        ≠
Compromise Began at Detection
```

```text
Compromise Event
        ≠
Automatic Historical Invalidation
```

```text
Mathematical Verification
        ≠
Authorization
```

```text
Admissibility PASS
        ≠
Execution Permission
```

```text
Missing Evidence
        →
HOLD
```

The final invariant is:

```text
No Historical Registry
        ↓
No Signing-Time Key Resolution
        ↓
No Historical Verification
        ↓
No Compromise Timing Assessment
        ↓
No Admissibility Determination
        ↓
UNKNOWN → HOLD
```

---

End of PROCESS LINEAGE CLASSIFIER CHECKPOINT 012
