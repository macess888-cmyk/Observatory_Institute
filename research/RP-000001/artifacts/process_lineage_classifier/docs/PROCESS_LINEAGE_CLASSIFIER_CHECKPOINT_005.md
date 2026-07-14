# PROCESS LINEAGE CLASSIFIER — CHECKPOINT 005

**Research Program:** RP-000001 — Organized Understanding
**Artifact:** RA-000001 — Process Lineage Classifier Prototype
**Checkpoint:** 005
**Version:** 0.5.0
**Date:** 2026-07-14
**Status:** IMPLEMENTED — VALIDATED — READY TO FREEZE

---

## 1. Checkpoint Purpose

Checkpoint 005 extends the Process Lineage Classifier into independent witness validation, concurrent event analysis, authority convergence, split-brain recovery, lineage reconciliation, and rollback recovery.

This checkpoint implements:

* witness-evidence validation;
* concurrent event-window validation;
* authority-convergence classification;
* split-brain recovery classification;
* lineage-reconciliation classification;
* rollback-recovery classification.

The implementation remains:

```text
OBSERVER-ONLY
DETERMINISTIC
TEST-FIRST
IMMUTABLE
EXPLAINABLE
NO SIDE EFFECTS
UNKNOWN → HOLD
```

---

## 2. Checkpoint Boundary

Checkpoint 005 introduces four recovery and reconciliation transition families:

```text
AUTHORITY_CONVERGENCE
SPLIT_BRAIN_RECOVERY
LINEAGE_RECONCILIATION
ROLLBACK_RECOVERY
```

It also introduces two cross-cutting validation capabilities:

```text
WITNESS EVIDENCE VALIDATION
CONCURRENT EVENT-WINDOW VALIDATION
```

These capabilities extend the prototype beyond individual event transitions into multi-source, concurrent, and post-conflict assessment.

---

## 3. Vocabulary Extension

The following `EventType` values were added:

```text
AUTHORITY_CONVERGENCE
SPLIT_BRAIN_RECOVERY
LINEAGE_RECONCILIATION
ROLLBACK_RECOVERY
```

The following `TransitionStatus` values were added:

```text
AUTHORITY_CONVERGED
SPLIT_BRAIN_RECOVERED
LINEAGE_RECONCILED
ROLLBACK_RECOVERED
```

The following lineage status is used:

```text
LineageStatus.RECONCILED
```

No previous vocabulary was removed.

---

## 4. New Immutable Model

Checkpoint 005 introduces:

```text
WitnessEvidence
```

The model records:

```text
witness_id
source_id
subject_event_id
claim
observed_at
provenance_id
signature_id
```

The model is:

```text
FROZEN
SLOTTED
TIMEZONE-AWARE
PROVENANCE-BEARING
SIGNATURE-BEARING
```

---

## 5. Architectural Invariants

Checkpoint 005 preserves:

```text
Claimant Statement
        ≠
Independent Witness Evidence
```

```text
Multiple Witness Records
        ≠
Multiple Independent Sources
```

```text
Concurrent Events
        ≠
Conflicting Events
```

```text
Single PRIMARY
        ≠
Verified Authority Convergence
```

```text
Authority Recovery
        ≠
State Recovery
```

```text
Merged State
        ≠
Reconciled Lineage
```

```text
Forward State Created
        ≠
Rollback Recovery Verified
```

---

## 6. Witness-Evidence Validator

`WitnessEvidenceValidator` validates:

* independent witness quorum;
* witness identity uniqueness;
* source identity independence;
* claim consistency;
* subject-event alignment;
* provenance presence;
* signature presence;
* observation freshness;
* future timestamp rejection;
* self-witness exclusion.

Implemented errors:

```text
WitnessEvidenceValidationError
InvalidWitnessEvidenceError
DuplicateWitnessError
ConflictingWitnessError
InsufficientWitnessesError
```

---

## 7. Independent Witness Quorum

A valid witness quorum requires:

* tuple input;
* only `WitnessEvidence` records;
* unique witness identities;
* unique independent source identities;
* matching subject event;
* matching required claim;
* valid provenance;
* valid signature;
* fresh observation timestamps;
* minimum independent witness count.

Expected result:

```text
Independent quorum established → PASS
```

---

## 8. Self-Witnessing Boundary

Witnesses originating from the claimant source are excluded from the independent quorum count.

```text
Self-Witness
        ≠
Independent Witness
```

Self-witness records may be present, but they cannot satisfy quorum.

```text
Self-witnessing only → INSUFFICIENT
```

---

## 9. Duplicate Witness and Source Rejection

The validator rejects:

```text
Duplicate witness identity
Duplicate independent source identity
```

Multiple records from the same independent source do not increase quorum strength.

```text
Record Count
        ≠
Source Independence
```

---

## 10. Witness Claim Conflict

Where witnesses provide inconsistent claims:

```text
PRIMARY_DEACTIVATED
        ≠
PRIMARY_ACTIVE
```

The validator raises:

```text
ConflictingWitnessError
```

A quorum cannot be established from mutually incompatible claims.

---

## 11. Witness Provenance and Signature

Every witness record requires:

```text
provenance_id
signature_id
```

Missing values cause:

```text
InvalidWitnessEvidenceError
```

This preserves:

```text
Witness Statement
        ≠
Verifiable Witness Evidence
```

---

## 12. Witness Freshness

Witness evidence is valid only when:

```text
observed_at
    ≥
now - maximum_age
```

and:

```text
observed_at
    ≤
now
```

Stale or future observations are rejected.

---

## 13. Concurrent Event-Window Validator

`ConcurrentEventWindowValidator` validates:

* event-set structure;
* shared service identity;
* unique event identity;
* unique runtime identity;
* unique execution identity;
* timezone-aware timestamps;
* maximum concurrency window;
* concurrent authority overlap.

Implemented errors:

```text
ConcurrentEventWindowError
InvalidConcurrentWindowError
ConcurrentEventConflictError
```

---

## 14. Concurrent Window Boundary

Events are considered inside one concurrent window when:

```text
latest timestamp - earliest timestamp
        ≤
maximum window
```

The exact maximum-window boundary is accepted.

Events beyond that boundary are rejected.

---

## 15. Concurrent Authority Validation

Within a validated concurrent window:

```text
One PRIMARY → PASS
More than one PRIMARY → CONFLICT
```

Multiple `PRIMARY` roles raise:

```text
ConcurrentEventConflictError
```

This does not itself perform full split-brain classification.

It establishes that conflicting authority exists inside one temporal window.

---

## 16. Concurrent Event Structural Rejections

The validator rejects:

* non-tuple input;
* fewer than two events;
* non-`ProcessEvent` members;
* mixed service identities;
* duplicate event identities;
* duplicate runtime identities;
* duplicate execution identities;
* timezone-naive timestamps;
* invalid maximum-window configuration.

---

## 17. Authority-Convergence Classifier

`AuthorityConvergenceClassifier` classifies:

```text
Verified Authority Convergence
Unverified Authority Convergence
Authority Conflict
State Divergence
```

Implemented rules:

```text
ACV-001 — Verified Convergence
ACV-002 — Unverified Convergence
ACV-003 — Authority Conflict
ACV-004 — State Divergence
```

---

## 18. Verified Authority Convergence

Verified convergence requires:

* at least two events;
* shared service identity;
* unique event, runtime, and execution identities;
* increasing sequence numbers;
* exactly one `PRIMARY`;
* authority-grant evidence for the elected `PRIMARY`;
* quorum-confirmation evidence;
* authority-revocation evidence for a former authority holder;
* convergence acknowledgement from every observed runtime;
* no state-divergence evidence.

Expected classification:

```text
Service continuity: CONTINUOUS
Runtime continuity: CONDITIONALLY_CONTINUOUS
Execution continuity: CONDITIONALLY_CONTINUOUS
State continuity: CONDITIONALLY_CONTINUOUS
Authority continuity: CONTINUOUS
Availability continuity: CONTINUOUS
State lineage: RECONCILED
Binding status: BOUND
Conflict status: CLEAR
Operational status: PASS
Confidence: HIGH
```

---

## 19. Incomplete Authority Convergence

Where exactly one `PRIMARY` exists but convergence evidence is incomplete:

```text
Authority continuity: UNVERIFIED
State lineage: UNVERIFIED
Binding status: UNVERIFIED
Conflict status: UNKNOWN
Operational status: HOLD
Confidence: LOW
```

This preserves:

```text
Single PRIMARY Observed
        ≠
Authority Convergence Verified
```

---

## 20. Authority Conflict During Convergence

Where multiple `PRIMARY` holders remain:

```text
Runtime continuity: CONFLICTED
Execution continuity: CONFLICTED
State continuity: CONFLICTED
Authority continuity: CONFLICTED
State lineage: CONFLICTED
Binding status: COLLIDING
Conflict status: COLLIDING
Operational status: HOLD
Confidence: HIGH
```

---

## 21. State Divergence After Authority Convergence

Authority may converge while state remains divergent.

```text
Authority Converged
        ≠
State Reconciled
```

Expected classification:

```text
Authority continuity: CONDITIONALLY_CONTINUOUS
State continuity: CONFLICTED
State lineage: CONFLICTED
Conflict status: CONFLICTED
Operational status: HOLD
Confidence: MODERATE
```

---

## 22. Split-Brain Recovery Classifier

`SplitBrainRecoveryClassifier` classifies:

```text
Verified Split-Brain Recovery
Unverified Split-Brain Recovery
Persistent Authority Conflict
Persistent State Divergence
```

Implemented rules:

```text
SBR-001 — Verified Recovery
SBR-002 — Unverified Recovery
SBR-003 — Authority Conflict
SBR-004 — State Divergence
```

---

## 23. Verified Split-Brain Recovery

Verified recovery requires:

* one shared service identity;
* unique event, runtime, and execution identities;
* increasing sequences;
* exactly one recovered `PRIMARY`;
* authority-grant evidence;
* quorum-confirmation evidence;
* authority-revocation evidence;
* isolation evidence for the former authority holder;
* state-reconciliation evidence;
* recovery acknowledgement from all observed runtimes;
* no state-divergence evidence.

Expected classification:

```text
Service continuity: CONDITIONALLY_CONTINUOUS
Runtime continuity: CONDITIONALLY_CONTINUOUS
Execution continuity: CONDITIONALLY_CONTINUOUS
State continuity: CONDITIONALLY_CONTINUOUS
Authority continuity: CONTINUOUS
Availability continuity: CONDITIONALLY_CONTINUOUS
State lineage: RECONCILED
Binding status: REBOUND
Conflict status: CLEAR
Operational status: PASS
Confidence: HIGH
```

---

## 24. Split-Brain Recovery Semantics

Recovery requires more than selecting one authority holder.

```text
Select One PRIMARY
        ≠
Recover From Split Brain
```

Verified recovery also requires:

```text
Former PRIMARY isolated
Authority revoked
State reconciled
Quorum confirmed
Participants acknowledged recovery
```

---

## 25. Incomplete Split-Brain Recovery

Where one `PRIMARY` remains but evidence is incomplete:

```text
Runtime continuity: UNVERIFIED
Execution continuity: UNVERIFIED
State continuity: UNVERIFIED
Authority continuity: UNVERIFIED
State lineage: UNVERIFIED
Binding status: UNVERIFIED
Operational status: HOLD
Confidence: LOW
```

---

## 26. Persistent Authority Conflict

Where multiple `PRIMARY` holders remain:

```text
Authority continuity: CONFLICTED
State continuity: CONFLICTED
Binding status: COLLIDING
Conflict status: COLLIDING
Operational status: HOLD
Confidence: HIGH
```

---

## 27. Persistent State Divergence

Where authority converges but state remains divergent:

```text
State continuity: CONFLICTED
State lineage: CONFLICTED
Conflict status: CONFLICTED
Operational status: HOLD
Confidence: MODERATE
```

This preserves:

```text
Authority Recovery
        ≠
State Recovery
```

---

## 28. Lineage-Reconciliation Classifier

`LineageReconciliationClassifier` classifies:

```text
Verified Lineage Reconciliation
Unverified Reconciliation
Unresolved Lineage Conflict
Missing Parent-State Coverage
```

Implemented rules:

```text
LR-001 — Verified Reconciliation
LR-002 — Unverified Reconciliation
LR-003 — Unresolved Conflict
LR-004 — Missing Parent State
```

---

## 29. Verified Lineage Reconciliation

Verified reconciliation requires:

* at least three events;
* one shared service identity;
* unique event, runtime, and execution identities;
* increasing sequence numbers;
* multiple parent events;
* explicit reference to every parent state;
* parent-state verification evidence;
* lineage-reconciliation evidence;
* state-merge verification evidence;
* conflict-resolution evidence;
* quorum-confirmation evidence;
* lineage acknowledgement from every event;
* no unresolved-conflict evidence.

Expected classification:

```text
Service continuity: CONDITIONALLY_CONTINUOUS
Runtime continuity: CONDITIONALLY_CONTINUOUS
Execution continuity: CONDITIONALLY_CONTINUOUS
State continuity: CONDITIONALLY_CONTINUOUS
Authority continuity: CONTINUOUS
Availability continuity: CONTINUOUS
State lineage: RECONCILED
Binding status: REBOUND
Conflict status: CLEAR
Operational status: PASS
Confidence: HIGH
```

---

## 30. Parent-State Coverage

Every source state must be referenced by the reconciled event.

```text
Observed Parent States
        =
Referenced Parent States
```

Missing coverage produces:

```text
State continuity: UNVERIFIED
State lineage: UNVERIFIED
Operational status: HOLD
```

This preserves:

```text
Some Parent States Referenced
        ≠
Complete Lineage Reconciliation
```

---

## 31. Unverified Lineage Reconciliation

Where parent-state coverage is complete but required evidence is incomplete:

```text
State continuity: UNVERIFIED
State lineage: UNVERIFIED
Binding status: UNVERIFIED
Conflict status: UNKNOWN
Operational status: HOLD
Confidence: LOW
```

---

## 32. Unresolved Lineage Conflict

Where reconciliation is declared but unresolved-conflict evidence remains:

```text
State continuity: CONFLICTED
State lineage: CONFLICTED
Binding status: COLLIDING
Conflict status: CONFLICTED
Operational status: HOLD
Confidence: MODERATE
```

This preserves:

```text
Merged State Produced
        ≠
Conflict Resolved
```

---

## 33. Rollback-Recovery Classifier

`RollbackRecoveryClassifier` classifies:

```text
Verified Rollback Recovery
Unverified Rollback Recovery
Integrity Conflict
Stale Recovery State
```

Implemented rules:

```text
RKR-001 — Verified Recovery
RKR-002 — Unverified Recovery
RKR-003 — Integrity Conflict
RKR-004 — Stale Recovery
```

---

## 34. Verified Rollback Recovery

Verified rollback recovery requires:

* current event type `ROLLBACK_RECOVERY`;
* direct parent reference to the rollback event;
* increasing event sequence;
* stable service identity;
* stable runtime identity;
* stable execution identity;
* stable host identity;
* stable address;
* stable authority role;
* parent-state reference to the rollback state;
* new forward state identity;
* recovery snapshot identity;
* rollback-recovery evidence;
* forward-state verification evidence;
* integrity-check evidence;
* authority-preservation evidence;
* recovery-completion evidence.

Expected classification:

```text
Service continuity: CONTINUOUS
Runtime continuity: CONTINUOUS
Execution continuity: CONTINUOUS
State continuity: CONDITIONALLY_CONTINUOUS
Authority continuity: CONTINUOUS
Availability continuity: CONTINUOUS
State lineage: RECONCILED
Binding status: BOUND
Conflict status: CLEAR
Operational status: PASS
Confidence: HIGH
```

---

## 35. Rollback-Recovery Semantics

Rollback recovery advances from a known rollback baseline into a new verified forward state.

```text
Rollback State
        →
Verified Forward State
```

This differs from rollback itself:

```text
Rollback
        =
Move Backward to Prior State
```

```text
Rollback Recovery
        =
Advance Forward From Rollback Baseline
```

---

## 36. Unverified Rollback Recovery

Where recovery evidence is incomplete:

```text
Runtime continuity: CONTINUOUS
Execution continuity: CONTINUOUS
State continuity: UNVERIFIED
Authority continuity: UNVERIFIED
State lineage: UNVERIFIED
Binding status: UNVERIFIED
Operational status: HOLD
Confidence: LOW
```

---

## 37. Rollback-Recovery Integrity Conflict

Where integrity evidence contradicts the recovered state:

```text
State continuity: CONFLICTED
State lineage: CONFLICTED
Binding status: COLLIDING
Conflict status: CONFLICTED
Operational status: HOLD
Confidence: MODERATE
```

This preserves:

```text
Forward State Exists
        ≠
Forward State Integrity Verified
```

---

## 38. Stale Rollback-Recovery State

Where recovery produces an older-than-required state:

```text
State continuity: DEGRADED
State lineage: DISCONTINUOUS
Conflict status: CONFLICTED
Operational status: HOLD
Confidence: MODERATE
```

Runtime and execution continuity may remain intact while state recovery remains invalid.

---

## 39. Explainability

Checkpoint 005 preserves:

```text
Applied rules
Reasons
Missing evidence
Conflicts
Confidence
Operational status
Classifier version
```

Each recovery or reconciliation outcome explains:

* which authority holder was selected;
* whether quorum existed;
* whether former authority was revoked;
* whether isolation occurred;
* whether parent states were covered;
* whether state conflict was resolved;
* whether integrity checks passed;
* whether evidence remained incomplete.

---

## 40. Validation Results

Checkpoint 005 test results:

```text
Witness-evidence validator tests: 16 passed
Concurrent event-window validator tests: 14 passed
Authority-convergence classifier tests: 13 passed
Split-brain recovery classifier tests: 13 passed
Lineage-reconciliation classifier tests: 13 passed
Rollback-recovery classifier tests: 14 passed
```

Checkpoint 005 additions:

```text
83 PASSED
0 FAILED
```

Full prototype suite:

```text
358 PASSED
0 FAILED
```

---

## 41. Verified Behaviors

```text
Independent witness quorum → PASS
Insufficient independent witnesses → REJECT
Duplicate witness identity → REJECT
Duplicate independent source → REJECT
Conflicting witness claims → REJECT
Missing provenance or signature → REJECT
Stale or future witness evidence → REJECT

Concurrent events inside window → PASS
Events outside window → REJECT
Multiple PRIMARY holders inside window → REJECT
Single PRIMARY inside window → PASS

Verified authority convergence → PASS
Incomplete convergence evidence → HOLD
Multiple PRIMARY holders remain → HOLD
State divergence after convergence → HOLD

Verified split-brain recovery → PASS
Incomplete recovery evidence → HOLD
Persistent multiple PRIMARY holders → HOLD
Persistent state divergence → HOLD

Verified lineage reconciliation → PASS
Incomplete reconciliation evidence → HOLD
Unresolved lineage conflict → HOLD
Missing parent-state reference → HOLD

Verified rollback recovery → PASS
Incomplete rollback-recovery evidence → HOLD
Integrity conflict → HOLD
Stale recovery state → HOLD
```

---

## 42. Preserved Structural Rejections

Checkpoint 005 rejects:

* non-tuple collections where tuples are required;
* insufficient event counts;
* non-model collection members;
* mixed service identities;
* duplicate event identities;
* duplicate runtime identities;
* duplicate execution identities;
* non-increasing sequence numbers;
* missing parent-event references;
* missing parent-state references;
* missing snapshots;
* changed protected identities;
* invalid authority roles;
* invalid witness provenance;
* invalid witness signatures;
* stale witness records;
* future witness records.

---

## 43. Checkpoint Compatibility

All previous checkpoint capabilities remain operational.

```text
CHECKPOINT 001 CAPABILITIES: PRESERVED
CHECKPOINT 002 CAPABILITIES: PRESERVED
CHECKPOINT 003 CAPABILITIES: PRESERVED
CHECKPOINT 004 CAPABILITIES: PRESERVED
```

Regression result:

```text
358 PASSED
0 FAILED
```

---

## 44. Current Implementation Inventory

Transition and classification families now include:

```text
ADDRESS_CHANGE
RESTART
MIGRATE
RESTORE
CLONE
BRANCH
MERGE
FAILOVER
AUTHORITY_TRANSFER
PROMOTE
DEMOTE
TERMINATE
REVIVE
REBIND
PAUSE
RESUME
ROLLBACK
SPLIT_BRAIN
AUTHORITY_CONVERGENCE
SPLIT_BRAIN_RECOVERY
LINEAGE_RECONCILIATION
ROLLBACK_RECOVERY
```

Cross-cutting validators include:

```text
Structural Transition Validation
Lineage Graph Validation
Temporal Freshness Validation
Lease Expiry Validation
Witness Evidence Validation
Concurrent Event-Window Validation
```

---

## 45. Operational Outcomes

### PASS

Evidence establishes a valid transition, independent support, temporal admissibility, authority resolution, and state reconciliation.

### HOLD

Evidence is incomplete, authority remains conflicted, state remains divergent, lineage remains unresolved, or integrity cannot be established.

### REJECT

The evidence, timing, identity, event set, parent structure, or comparison structure is invalid.

---

## 46. Checkpoint Determination

```text
CHECKPOINT 005: PASS
WITNESS EVIDENCE VALIDATOR: IMPLEMENTED
CONCURRENT EVENT-WINDOW VALIDATOR: IMPLEMENTED
AUTHORITY CONVERGENCE CLASSIFIER: IMPLEMENTED
SPLIT-BRAIN RECOVERY CLASSIFIER: IMPLEMENTED
LINEAGE RECONCILIATION CLASSIFIER: IMPLEMENTED
ROLLBACK RECOVERY CLASSIFIER: IMPLEMENTED
INDEPENDENT QUORUM VALIDATION: VERIFIED
AUTHORITY CONVERGENCE: VERIFIED
STATE RECONCILIATION: VERIFIED
RECOVERY INTEGRITY: VERIFIED
TESTS: 358 PASSED
FAILURES: 0
SIDE EFFECTS: NONE
READY TO FREEZE: YES
```

---

## 47. Remaining Freeze Steps

```text
Return to repository root
Inspect Git status
Remove accidental files if present
Stage Checkpoint 005 files
Review staged diff
Run full suite once more
Run git diff --cached --check
Commit
Push
Verify clean working tree
```

---

## 48. Next Capability Boundary

Checkpoint 006 may consider:

* integrated recovery orchestration;
* authority and lineage recovery plans;
* evidence-weight scoring;
* witness trust levels;
* quorum-policy models;
* temporal quorum expiry;
* reconciliation receipts;
* recovery audit trails.

These capabilities are not included in Checkpoint 005.

---

## 49. Final Checkpoint Statement

Checkpoint 005 demonstrates that recovery cannot be established by a single declaration, a single authority holder, or a newly produced state.

The implementation preserves:

```text
Witness Count
        ≠
Independent Quorum

Single PRIMARY
        ≠
Verified Convergence

Authority Recovery
        ≠
State Recovery

Merged State
        ≠
Reconciled Lineage

Forward State
        ≠
Verified Recovery
```

The governing invariant remains:

```text
No independent proof
        ↓
No convergence or recovery admission
        ↓
HOLD
```

---

End of PROCESS LINEAGE CLASSIFIER CHECKPOINT 005
