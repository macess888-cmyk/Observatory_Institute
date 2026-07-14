# PROCESS LINEAGE CLASSIFIER — CHECKPOINT 004

**Research Program:** RP-000001 — Organized Understanding
**Artifact:** RA-000001 — Process Lineage Classifier Prototype
**Checkpoint:** 004
**Version:** 0.4.0
**Date:** 2026-07-14
**Status:** IMPLEMENTED — VALIDATED — READY TO FREEZE

---

## 1. Checkpoint Purpose

Checkpoint 004 extends the Process Lineage Classifier into interruption, resumption, rollback, temporal validity, lease validity, and concurrent-authority conflict.

This checkpoint implements:

* pause classification;
* resume classification;
* rollback classification;
* temporal freshness validation;
* lease-expiry validation;
* split-brain classification.

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

Checkpoint 004 introduces three transition families:

```text
PAUSE
RESUME
ROLLBACK
```

It also introduces three cross-cutting validation capabilities:

```text
TEMPORAL FRESHNESS
LEASE EXPIRY
SPLIT-BRAIN DETECTION
```

These capabilities assess whether a transition is not only structurally valid, but also temporally current and operationally admissible.

---

## 3. Vocabulary Extension

The following `EventType` values were added:

```text
PAUSE
RESUME
ROLLBACK
SPLIT_BRAIN
```

The following `TransitionStatus` values were added:

```text
PAUSED
RESUMED
ROLLED_BACK
SPLIT_BRAIN_DETECTED
```

The following status values are used by Checkpoint 004:

```text
BindingStatus.SUSPENDED
ContinuityStatus.CONFLICTED
LineageStatus.CONFLICTED
```

No previous checkpoint vocabulary was removed.

---

## 4. Architectural Invariants

Checkpoint 004 preserves:

```text
Runtime Present
        ≠
Execution Active
```

```text
Execution Resumed
        ≠
State Current
```

```text
Timestamp Present
        ≠
Timestamp Fresh
```

```text
Authority Claimed
        ≠
Authority Lease Valid
```

```text
Service Available
        ≠
Single Authority Holder
```

```text
Rollback Completed
        ≠
Rollback Target Verified
```

---

## 5. Pause Classifier

`PauseClassifier` classifies:

```text
Verified Pause
Unverified Pause
Pause With Active Authority Conflict
```

Implemented rules:

```text
PS-001 — Verified Pause
PS-002 — Unverified Pause
PS-003 — Authority Still Active
```

---

## 6. Verified Pause

A verified pause requires:

* current event type `PAUSE`;
* direct parent event reference;
* increasing event sequence;
* stable service identity;
* stable runtime identity;
* stable execution identity;
* stable state identity;
* stable host identity;
* stable address;
* parent-state reference;
* target authority role `NONE`;
* pause evidence;
* execution-suspension evidence;
* state-preservation evidence;
* authority-suspension evidence.

Expected classification:

```text
Service continuity: INTERRUPTED
Runtime continuity: CONTINUOUS
Execution continuity: INTERRUPTED
State continuity: CONTINUOUS
Authority continuity: INTERRUPTED
Availability continuity: INTERRUPTED
State lineage: LINEAR
Binding status: SUSPENDED
Conflict status: CLEAR
Operational status: PASS
Confidence: HIGH
```

---

## 7. Pause Semantics

Pause preserves the runtime while suspending execution.

```text
Runtime Continuity
        =
CONTINUOUS
```

```text
Execution Continuity
        =
INTERRUPTED
```

```text
State Continuity
        =
CONTINUOUS
```

The runtime remains identifiable, but it is not operationally active.

---

## 8. Unverified Pause

Where pause evidence is incomplete:

```text
Runtime continuity: CONTINUOUS
Execution continuity: UNVERIFIED
State continuity: UNVERIFIED
Authority continuity: UNVERIFIED
Availability continuity: UNKNOWN
State lineage: UNVERIFIED
Binding status: UNVERIFIED
Conflict status: UNKNOWN
Operational status: HOLD
Confidence: LOW
```

A declared pause does not establish that execution, state, and authority were safely suspended.

---

## 9. Authority Active During Pause

Where a paused runtime still claims authority:

```text
Runtime continuity: CONTINUOUS
Execution continuity: INTERRUPTED
State continuity: CONTINUOUS
Authority continuity: UNVERIFIED
Availability continuity: INTERRUPTED
Binding status: COLLIDING
Conflict status: COLLIDING
Operational status: HOLD
Confidence: MODERATE
```

This preserves:

```text
Execution Suspended
        ≠
Authority Suspended
```

---

## 10. Resume Classifier

`ResumeClassifier` classifies:

```text
Verified Resume
Unverified Resume
Resume With Authority Collision
Resume With Stale State
```

Implemented rules:

```text
RSU-001 — Verified Resume
RSU-002 — Unverified Resume
RSU-003 — Authority Collision
RSU-004 — Stale Resume
```

---

## 11. Verified Resume

A verified resume requires:

* source event type `PAUSE`;
* current event type `RESUME`;
* direct parent reference to the paused event;
* increasing event sequence;
* stable service identity;
* stable runtime identity;
* stable execution identity;
* stable host identity;
* stable address;
* paused source authority role `NONE`;
* resumed target authority role `PRIMARY`;
* preserved state identity;
* parent-state reference;
* resume evidence;
* execution-resume evidence;
* state-verification evidence;
* authority-restoration evidence;
* evidence that no other active `PRIMARY` exists.

Expected classification:

```text
Service continuity: CONDITIONALLY_CONTINUOUS
Runtime continuity: CONTINUOUS
Execution continuity: CONTINUOUS
State continuity: CONTINUOUS
Authority continuity: CONDITIONALLY_CONTINUOUS
Availability continuity: INTERRUPTED
State lineage: LINEAR
Binding status: REBOUND
Conflict status: CLEAR
Operational status: PASS
Confidence: HIGH
```

---

## 12. Resume Semantics

Resume restores operational execution after interruption.

```text
Pause Interval
        =
Availability Interruption
```

The resumed runtime and execution may remain identical to the paused identities.

```text
Paused Runtime
        =
Resumed Runtime
```

```text
Paused Execution Identity
        =
Resumed Execution Identity
```

This differs from revival, which requires new runtime and execution identities.

---

## 13. Unverified Resume

Where resume evidence is incomplete:

```text
Service continuity: UNVERIFIED
Runtime continuity: CONTINUOUS
Execution continuity: UNVERIFIED
State continuity: UNVERIFIED
Authority continuity: UNVERIFIED
Availability continuity: INTERRUPTED
State lineage: UNVERIFIED
Binding status: UNVERIFIED
Conflict status: UNKNOWN
Operational status: HOLD
Confidence: LOW
```

---

## 14. Resume Authority Collision

Where another active `PRIMARY` exists:

```text
Runtime continuity: CONTINUOUS
Execution continuity: CONTINUOUS
State continuity: CONTINUOUS
Authority continuity: UNVERIFIED
Binding status: COLLIDING
Conflict status: COLLIDING
Operational status: HOLD
Confidence: MODERATE
```

The resumed process cannot be admitted as exclusively authoritative.

---

## 15. Stale Resume

Where the resumed state differs from the paused state:

```text
Runtime continuity: CONTINUOUS
Execution continuity: CONTINUOUS
State continuity: DEGRADED
Authority continuity: CONDITIONALLY_CONTINUOUS
Availability continuity: INTERRUPTED
State lineage: DISCONTINUOUS
Binding status: REBOUND
Conflict status: CONFLICTED
Operational status: HOLD
Confidence: MODERATE
```

This preserves:

```text
Execution Successfully Resumed
        ≠
State Successfully Preserved
```

---

## 16. Rollback Classifier

`RollbackClassifier` classifies:

```text
Verified Rollback
Unverified Rollback
Rollback Target Conflict
```

Implemented rules:

```text
RK-001 — Verified Rollback
RK-002 — Unverified Rollback
RK-003 — Target-State Conflict
```

---

## 17. Verified Rollback

A verified rollback requires:

* current event type `ROLLBACK`;
* direct parent event reference;
* increasing event sequence;
* stable service identity;
* stable runtime identity;
* stable execution identity;
* stable authority role;
* changed state identity;
* reference to the pre-rollback state;
* reference to the restored target state;
* snapshot identity;
* rollback evidence;
* snapshot-verification evidence;
* target-state-verification evidence;
* authority-preservation evidence.

Expected classification:

```text
Service continuity: CONTINUOUS
Runtime continuity: CONTINUOUS
Execution continuity: CONTINUOUS
State continuity: DEGRADED
Authority continuity: CONTINUOUS
Availability continuity: CONTINUOUS
State lineage: RESTORED
Binding status: BOUND
Conflict status: CLEAR
Operational status: PASS
Confidence: HIGH
```

---

## 18. Rollback Semantics

Rollback intentionally replaces the current state with a prior state.

```text
Current State
        →
Earlier Verified State
```

State continuity is therefore marked:

```text
DEGRADED
```

This does not necessarily indicate failure.

It records that forward state history was intentionally abandoned.

---

## 19. Unverified Rollback

Where rollback evidence is incomplete:

```text
Runtime continuity: CONTINUOUS
Execution continuity: CONTINUOUS
State continuity: UNVERIFIED
Authority continuity: UNVERIFIED
Availability continuity: CONDITIONALLY_CONTINUOUS
State lineage: UNVERIFIED
Binding status: UNVERIFIED
Conflict status: UNKNOWN
Operational status: HOLD
Confidence: LOW
```

---

## 20. Rollback Target Conflict

Where the declared target state conflicts with supplied evidence:

```text
State continuity: UNVERIFIED
Authority continuity: CONTINUOUS
State lineage: CONFLICTED
Binding status: COLLIDING
Conflict status: CONFLICTED
Operational status: HOLD
Confidence: MODERATE
```

This preserves:

```text
Snapshot Exists
        ≠
Rollback Target Verified
```

---

## 21. Temporal Freshness Validator

`TemporalFreshnessValidator` validates:

* event age;
* future timestamp tolerance;
* transition timestamp order;
* transition sequence order;
* timezone awareness.

Implemented errors:

```text
TemporalFreshnessError
StaleEventError
FutureTimestampError
TemporalOrderError
```

---

## 22. Freshness Boundary

An event is accepted when:

```text
event timestamp
    ≥
now - maximum age
```

and:

```text
event timestamp
    ≤
now + future tolerance
```

The maximum-age boundary is inclusive.

The future-tolerance boundary is inclusive.

---

## 23. Stale Event Rejection

Where an event exceeds the maximum permitted age:

```text
Event Age
        >
Maximum Age
```

The validator raises:

```text
StaleEventError
```

A structurally valid event may still be operationally stale.

---

## 24. Future Timestamp Rejection

Where an event timestamp exceeds the permitted future tolerance:

```text
Event Timestamp
        >
Reference Time + Future Tolerance
```

The validator raises:

```text
FutureTimestampError
```

This protects against clock drift, malformed evidence, or premature event ordering.

---

## 25. Temporal Transition Ordering

For a valid transition:

```text
current timestamp
        >
previous timestamp
```

and:

```text
current sequence number
        >
previous sequence number
```

Equal or reversed timestamps are rejected.

Equal or reversed sequence numbers are rejected.

---

## 26. Timezone Requirement

All event timestamps and reference times must be timezone-aware.

Naive timestamps are rejected.

```text
Timestamp Without Timezone
        =
Temporally Ambiguous
```

---

## 27. Lease-Expiry Validator

`LeaseExpiryValidator` validates whether an event operates inside an active authority lease.

Implemented errors:

```text
LeaseValidationError
InvalidLeaseError
LeaseNotYetActiveError
ExpiredLeaseError
```

---

## 28. Valid Lease Interval

A lease is structurally valid only when:

```text
lease expiry
        >
lease start
```

Equal start and expiry values are invalid.

Expiry before start is invalid.

---

## 29. Active Lease Boundary

A lease is active when:

```text
lease start
        ≤
reference time
        <
lease expiry
```

The start boundary is inclusive.

The expiry boundary is exclusive.

At the exact expiry timestamp, the lease is expired.

---

## 30. Lease Not Yet Active

Where validation occurs before the lease start:

```text
reference time
        <
lease start
```

The validator raises:

```text
LeaseNotYetActiveError
```

---

## 31. Expired Lease

Where validation occurs at or after lease expiry:

```text
reference time
        ≥
lease expiry
```

The validator raises:

```text
ExpiredLeaseError
```

---

## 32. Expired Authority

Where an event claims `PRIMARY` after lease expiry:

```text
PRIMARY Claim
        +
Expired Lease
        =
Invalid Authority
```

The validator explicitly rejects the authority claim.

This preserves:

```text
Role Claim
        ≠
Current Authority
```

---

## 33. Split-Brain Classifier

`SplitBrainClassifier` classifies:

```text
Confirmed Split Brain
Unverified Split Brain
Clear Authority Topology
```

Implemented rules:

```text
SB-001 — Confirmed Split Brain
SB-002 — Unverified Split Brain
SB-003 — Clear Authority Topology
```

---

## 34. Confirmed Split Brain

A confirmed split-brain condition requires:

* at least two events;
* one shared service identity;
* distinct event identities;
* distinct runtime identities;
* distinct execution identities;
* increasing sequence numbers;
* multiple `PRIMARY` authority holders;
* active-primary evidence for every `PRIMARY`;
* valid-lease evidence for every `PRIMARY`.

Expected classification:

```text
Service continuity: UNVERIFIED
Runtime continuity: CONFLICTED
Execution continuity: CONFLICTED
State continuity: CONFLICTED
Authority continuity: CONFLICTED
Availability continuity: CONDITIONALLY_CONTINUOUS
State lineage: CONFLICTED
Binding status: COLLIDING
Conflict status: COLLIDING
Operational status: HOLD
Confidence: HIGH
```

---

## 35. Split-Brain Semantics

Split brain may preserve apparent availability.

```text
Multiple Active Runtimes
        =
Possible Availability
```

But authority and state become conflicted.

```text
Multiple PRIMARY Holders
        =
Authority Conflict
```

```text
Concurrent Divergent States
        =
Lineage Conflict
```

---

## 36. Unverified Split Brain

Where multiple `PRIMARY` roles are observed but active-authority or lease evidence is incomplete:

```text
Service continuity: UNVERIFIED
Runtime continuity: UNVERIFIED
Execution continuity: UNVERIFIED
State continuity: UNVERIFIED
Authority continuity: UNVERIFIED
Availability continuity: UNKNOWN
State lineage: UNVERIFIED
Binding status: UNVERIFIED
Conflict status: UNKNOWN
Operational status: HOLD
Confidence: LOW
```

The classifier does not infer a confirmed split brain without sufficient evidence.

---

## 37. Clear Authority Topology

Where only one runtime holds `PRIMARY`:

```text
Authority continuity: CONTINUOUS
Binding status: BOUND
Conflict status: CLEAR
Operational status: PASS
Confidence: HIGH
```

Other runtimes may exist as non-primary participants.

---

## 38. Split-Brain Structural Rejections

The classifier rejects:

* fewer than two events;
* non-tuple input;
* non-`ProcessEvent` members;
* mixed service identities;
* duplicate event identities;
* duplicate runtime identities;
* duplicate execution identities;
* non-increasing sequence numbers.

These conditions prevent invalid comparisons from being classified as authority topology.

---

## 39. Explainability

Checkpoint 004 preserves:

```text
Applied rules
Reasons
Missing evidence
Conflicts
Confidence
Operational status
Classifier version
```

Held temporal and authority outcomes explain whether the cause is:

* missing evidence;
* stale state;
* stale event;
* future timestamp;
* expired lease;
* authority collision;
* rollback conflict;
* split brain.

---

## 40. Validation Results

Checkpoint 004 test results:

```text
Pause classifier tests: 12 passed
Resume classifier tests: 13 passed
Rollback classifier tests: 13 passed
Temporal freshness validator tests: 14 passed
Lease-expiry validator tests: 14 passed
Split-brain classifier tests: 12 passed
```

Checkpoint 004 additions:

```text
78 PASSED
0 FAILED
```

Full prototype suite:

```text
275 PASSED
0 FAILED
```

---

## 41. Verified Behaviors

The following behaviors are verified:

```text
Verified pause → PASS
Unverified pause → HOLD
Authority active during pause → HOLD

Verified resume → PASS
Unverified resume → HOLD
Authority collision during resume → HOLD
Stale resumed state → HOLD

Verified rollback → PASS
Unverified rollback → HOLD
Rollback target conflict → HOLD

Fresh event → PASS
Stale event → REJECT
Future timestamp → REJECT
Temporal reversal → REJECT
Naive timestamp → REJECT

Active lease → PASS
Not-yet-active lease → REJECT
Expired lease → REJECT
Expired PRIMARY authority → REJECT

Confirmed split brain → HOLD
Unverified split brain → HOLD
Single PRIMARY topology → PASS
```

---

## 42. Preserved Structural Rejections

Checkpoint 004 rejects:

* wrong transition type;
* missing parent links;
* reversed event sequence;
* changed service identity where prohibited;
* changed runtime identity where prohibited;
* changed execution identity where prohibited;
* changed state identity where prohibited;
* invalid paused or resumed authority role;
* unchanged rollback state;
* missing rollback snapshot;
* invalid time interval;
* naive timestamps;
* duplicate split-brain identities;
* mixed-service split-brain input.

---

## 43. Checkpoint Compatibility

All Checkpoint 001, 002, and 003 capabilities remain operational.

```text
Address Change
Restart
Migration
Restore
Clone
Branch
Merge
Failover
Authority Transfer
Promotion
Demotion
Termination
Revival
Rebinding
```

Regression result:

```text
CHECKPOINT 001 CAPABILITIES: PRESERVED
CHECKPOINT 002 CAPABILITIES: PRESERVED
CHECKPOINT 003 CAPABILITIES: PRESERVED
```

---

## 44. Current Implementation Inventory

The classifier now supports:

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
```

Cross-cutting validators now include:

```text
Structural Transition Validation
Lineage Graph Validation
Temporal Freshness Validation
Lease Expiry Validation
```

---

## 45. Operational Outcomes

### PASS

Evidence establishes a valid transition, valid authority, and acceptable temporal state.

### HOLD

Evidence is incomplete, state is stale, authority is conflicted, rollback evidence conflicts, or split brain is detected.

### REJECT

The transition, timestamp, lease, or comparison structure is invalid.

---

## 46. Checkpoint Determination

```text
CHECKPOINT 004: PASS
PAUSE CLASSIFIER: IMPLEMENTED
RESUME CLASSIFIER: IMPLEMENTED
ROLLBACK CLASSIFIER: IMPLEMENTED
TEMPORAL FRESHNESS VALIDATOR: IMPLEMENTED
LEASE EXPIRY VALIDATOR: IMPLEMENTED
SPLIT-BRAIN CLASSIFIER: IMPLEMENTED
STALE EVENT REJECTION: VERIFIED
EXPIRED AUTHORITY REJECTION: VERIFIED
AUTHORITY COLLISION → HOLD: VERIFIED
ROLLBACK CONFLICT → HOLD: VERIFIED
TESTS: 275 PASSED
FAILURES: 0
SIDE EFFECTS: NONE
READY TO FREEZE: YES
```

---

## 47. Remaining Freeze Steps

Before freezing Checkpoint 004:

```text
Return to repository root
Inspect Git status
Stage changed files
Review staged diff
Run full suite once more
Run git diff --cached --check
Commit
Push
Verify clean working tree
```

---

## 48. Next Capability Boundary

Checkpoint 005 may consider:

* binding lease integration;
* temporal authority reconciliation;
* concurrent event windows;
* quorum or witness evidence;
* split-brain recovery;
* authority convergence;
* lineage reconciliation;
* rollback recovery verification.

These capabilities are not included in Checkpoint 004.

---

## 49. Final Checkpoint Statement

Checkpoint 004 demonstrates that process continuity must be assessed across operational state, temporal validity, authority leases, and concurrent authority topology.

The implementation preserves:

```text
Paused
        ≠
Terminated

Resumed
        ≠
State Current

Rollback
        ≠
Target Verified

PRIMARY
        ≠
Lease Valid

Available
        ≠
Governable
```

The governing invariant remains:

```text
No proof
    ↓
No temporal or authority admission
    ↓
HOLD
```

---

End of PROCESS LINEAGE CLASSIFIER CHECKPOINT 004
