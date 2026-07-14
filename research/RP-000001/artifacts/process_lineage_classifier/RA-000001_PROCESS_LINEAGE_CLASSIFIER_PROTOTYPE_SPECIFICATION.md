# RA-000001

# Process Lineage Classifier Prototype Specification

**Research Program:** RP-000001 — Organized Understanding
**Research Question:** RQ-000001 — Irreducible Structures of Organized Understanding
**Related Model:** RM-000001 — Minimum Distinguishability, Identity, Binding Integrity, and Continuity Model, Version 0.4
**Supporting Observation:** ROB-000011 — Executable Process Lineage and Continuity Classification
**Supporting Review:** RR-000011 — Research Review of Executable Process Lineage and Continuity Classification
**Artifact Type:** Research Prototype Specification
**Version:** 0.1
**Status:** PROPOSED — IMPLEMENTATION READY
**Date:** 2026-07-14

---

## 1. Specification Purpose

This specification defines the first executable prototype for classifying process identity, lineage, binding integrity, and continuity transitions.

The prototype will classify structured process events involving:

* start;
* address change;
* restart;
* migration;
* restoration;
* cloning;
* branching;
* merging.

The prototype will remain:

```text
OBSERVER-ONLY
DETERMINISTIC
TEST-FIRST
IMMUTABLE
EXPLAINABLE
NO SIDE EFFECTS
UNKNOWN → HOLD
```

The prototype will not control, restart, migrate, terminate, or modify real processes.

---

## 2. Prototype Objective

The prototype must determine whether supplied event records support continuity claims across separate identity layers.

It must not produce a single binary result such as:

```text
same_process = true
```

Instead, it must classify:

```text
Service Continuity
Runtime Continuity
Execution Continuity
State Continuity
State Lineage
Authority Continuity
Availability Continuity
Binding Integrity
Operational Status
```

---

## 3. Core Research Principle

The prototype implements the four-threshold model:

```text
D = Distinguishability
I = Identity
B = Binding Integrity
C = Continuity
```

A classification may be admitted only where the required evidence satisfies:

```text
D ≥ Tᴅ
I ≥ Tᵢ
B ≥ Tᵦ
C ≥ T꜀
```

Where evidence is insufficient:

```text
UNKNOWN → HOLD
```

---

## 4. Prototype Boundary

Version 0.1 will support:

```text
START
ADDRESS_CHANGE
RESTART
MIGRATE
RESTORE
CLONE
BRANCH
MERGE
```

Version 0.1 will validate but not yet fully classify:

```text
PROMOTE
DEMOTE
FAILOVER
TERMINATE
REVIVE
REBIND
```

Unsupported events must return:

```text
UNKNOWN_EVENT
```

and:

```text
operational_status = HOLD
```

---

## 5. Non-Goals

Version 0.1 will not:

* connect to operating systems;
* inspect live processes;
* migrate workloads;
* restart services;
* write to external systems;
* resolve distributed consensus;
* reconcile split-brain states automatically;
* assign blame;
* infer human identity;
* make legal determinations;
* calculate probabilistic confidence;
* modify historical records;
* provide a graphical user interface.

---

## 6. Repository Location

The prototype should be created under:

```text
research/RP-000001/artifacts/process_lineage_classifier/
```

Recommended structure:

```text
process_lineage_classifier/
├── README.md
├── models/
│   ├── __init__.py
│   ├── process_event.py
│   ├── process_state.py
│   ├── transition_evidence.py
│   ├── continuity_classification.py
│   └── binding_assessment.py
├── enums/
│   ├── __init__.py
│   ├── event_type.py
│   ├── continuity_status.py
│   ├── transition_status.py
│   ├── lineage_status.py
│   ├── binding_status.py
│   ├── conflict_status.py
│   ├── operational_status.py
│   └── confidence_level.py
├── services/
│   ├── __init__.py
│   ├── transition_validator.py
│   ├── lineage_graph_validator.py
│   ├── binding_classifier.py
│   ├── continuity_classifier.py
│   └── classification_explainer.py
├── tests/
│   ├── __init__.py
│   ├── test_address_change.py
│   ├── test_restart.py
│   ├── test_migration.py
│   ├── test_restore.py
│   ├── test_clone.py
│   ├── test_branch.py
│   ├── test_merge.py
│   └── test_invalid_transitions.py
└── docs/
    └── PROCESS_LINEAGE_CLASSIFIER_CHECKPOINT_001.md
```

---

## 7. Architectural Separation

The prototype must preserve these boundaries:

```text
Models
    ≠
Validation
    ≠
Binding Classification
    ≠
Continuity Classification
    ≠
Explanation
```

### Models

Represent immutable facts supplied to the classifier.

### Validation

Determines whether the records are structurally admissible.

### Binding Classification

Determines whether identifiers remain correctly associated with targets.

### Continuity Classification

Determines how identity layers persist or change.

### Explanation

Reports applied rules, evidence, missing information, and reasons.

---

## 8. Immutable Model Requirement

All core models must be immutable.

Recommended Python approach:

```python
@dataclass(frozen=True)
```

No service may mutate an input event or state.

Corrections must be represented as new records.

---

## 9. EventType Enum

The initial enum must contain:

```text
START
ADDRESS_CHANGE
RESTART
MIGRATE
RESTORE
CLONE
BRANCH
MERGE
UNKNOWN_EVENT
```

Deferred values may be reserved for later versions:

```text
CHECKPOINT
PROMOTE
DEMOTE
FAILOVER
TERMINATE
REVIVE
REBIND
PAUSE
RESUME
ROLLBACK
```

---

## 10. ContinuityStatus Enum

Continuity status must describe persistence across time.

```text
CONTINUOUS
CONDITIONALLY_CONTINUOUS
DEGRADED
INTERRUPTED
TERMINATED
UNVERIFIED
UNKNOWN
```

This enum must not contain transition names such as `RESTARTED` or `MIGRATED`.

---

## 11. TransitionStatus Enum

Transition status must describe the event outcome.

```text
STARTED
ADDRESS_REBOUND
RESTARTED
MIGRATED
RESTORED
CLONED
BRANCHED
MERGED
REPLACED
NEW_ROOT
UNKNOWN
```

---

## 12. LineageStatus Enum

Lineage status must describe derivation structure.

```text
LINEAR
RESTORED
SHARED_PARENT
BRANCHED
MERGED
NEW_ROOT
DISCONTINUOUS
UNVERIFIED
UNKNOWN
```

---

## 13. BindingStatus Enum

Binding status must contain:

```text
BOUND
CONDITIONALLY_BOUND
REBOUND
COLLIDING
EXPIRED
UNVERIFIED
INVALID
UNKNOWN
```

---

## 14. ConflictStatus Enum

Conflict status must contain:

```text
CLEAR
CONFLICTED
COLLIDING
UNKNOWN
```

---

## 15. OperationalStatus Enum

Operational status must contain:

```text
PASS
HOLD
FAIL
```

### PASS

Required evidence is sufficient and no invalid condition is present.

### HOLD

Evidence is incomplete, unsupported, ambiguous, or conflicted.

### FAIL

A structural or semantic violation is established.

---

## 16. ConfidenceLevel Enum

Initial confidence levels:

```text
HIGH
MODERATE
LOW
UNKNOWN
```

Confidence must derive from evidence completeness.

The prototype must not calculate arbitrary numeric confidence.

---

## 17. ProcessEvent Model

Required fields:

```text
event_id
event_type
timestamp
sequence_number
service_id
runtime_id
execution_id
state_id
host_id
address
authority_role
parent_event_ids
parent_state_ids
evidence_ids
```

Recommended optional fields:

```text
migration_id
snapshot_id
branch_id
merge_id
notes
```

### Required Properties

* `event_id` must be unique.
* `event_type` must be valid.
* `sequence_number` must be non-negative.
* identifiers must not be empty when required.
* parent fields must be immutable tuples.
* evidence fields must be immutable tuples.

---

## 18. ProcessState Model

Required fields:

```text
service_id
runtime_id
execution_id
state_id
host_id
address
authority_role
is_active
```

Optional fields:

```text
state_hash
code_version
environment_id
```

The model represents one declared state at one event boundary.

---

## 19. TransitionEvidence Model

Required fields:

```text
evidence_id
evidence_type
source_event_id
target_event_id
is_verified
```

Optional fields:

```text
checksum
source
method
notes
```

Candidate evidence types:

```text
PARENT_LINK
STATE_HASH
MIGRATION_TRANSACTION
SOURCE_DEACTIVATION
SNAPSHOT_PARENT
AUTHORITY_TRANSFER
ADDRESS_REBIND
```

---

## 20. BindingAssessment Model

Required fields:

```text
binding_status
reference_type
reference_value
target_type
target_value
reasons
missing_evidence
```

The model must remain separate from continuity classification.

---

## 21. ContinuityClassification Model

Required fields:

```text
transition_id
event_type
service_continuity
runtime_continuity
execution_continuity
state_continuity
state_lineage
authority_continuity
availability_continuity
binding_status
conflict_status
transition_status
operational_status
confidence
applied_rules
reasons
missing_evidence
conflicts
```

All collection fields must be immutable tuples.

---

## 22. Validation Order

The prototype must apply validation in this order:

```text
1. Record structure
2. Identifier presence
3. Event-type validity
4. Parent existence
5. Sequence ordering
6. Duplicate detection
7. Lineage-cycle detection
8. Authority collision detection
9. Branch and merge constraints
10. Transition-specific evidence
```

Classification must not proceed optimistically after a validation failure.

---

## 23. Structural Validation Rules

### Rule SV-001 — Unique Event Identity

Every `event_id` must be unique.

Violation:

```text
operational_status = FAIL
```

### Rule SV-002 — Parent Existence

Every parent event and parent state must exist.

Violation:

```text
operational_status = HOLD
```

unless the record explicitly declares a new root.

### Rule SV-003 — Sequence Ordering

A child event sequence must be greater than its parent sequence.

Violation:

```text
operational_status = FAIL
```

### Rule SV-004 — No Self-Ancestry

An event, runtime, execution, or state cannot be its own ancestor.

Violation:

```text
operational_status = FAIL
```

### Rule SV-005 — No Derivation Cycles

The lineage derivation graph must be acyclic.

Violation:

```text
operational_status = FAIL
```

---

## 24. Branch Validation Rules

### Rule BR-001

A branch must have one parent and at least two distinct child lineages.

### Rule BR-002

Branch children must have distinct runtime or execution identities.

### Rule BR-003

Shared parentage must remain visible.

Failure to preserve shared parentage:

```text
operational_status = HOLD
```

---

## 25. Merge Validation Rules

### Rule MG-001

A merge must reference at least two distinct parent states.

### Rule MG-002

The merged state must have a new state identity.

### Rule MG-003

All parent lineages must remain preserved.

Invalid merge structure:

```text
operational_status = FAIL
```

---

## 26. Authority Validation Rules

### Rule AU-001

Only one active runtime may hold an exclusive authority role within the same scope.

### Rule AU-002

Overlapping exclusive roles create:

```text
binding_status = COLLIDING
conflict_status = COLLIDING
operational_status = HOLD
```

or `FAIL` when the supplied records establish an invalid state.

### Rule AU-003

Authority transfer must include explicit transfer evidence.

---

## 27. Address-Change Classification

Required conditions:

* same service ID;
* same runtime ID;
* same execution ID;
* valid parent link;
* new address;
* no other conflicting transition.

Expected result:

```text
service_continuity = CONTINUOUS
runtime_continuity = CONTINUOUS
execution_continuity = CONTINUOUS
state_continuity = CONTINUOUS
state_lineage = LINEAR
binding_status = REBOUND
transition_status = ADDRESS_REBOUND
operational_status = PASS
```

---

## 28. Restart Classification

Required conditions:

* event type `RESTART`;
* same service ID;
* different runtime ID;
* different execution ID;
* valid prior termination or replacement evidence.

Expected result:

```text
service_continuity = CONTINUOUS
runtime_continuity = TERMINATED
execution_continuity = TERMINATED
transition_status = RESTARTED
```

State results depend on restoration evidence.

---

## 29. Warm Restart Classification

Where the latest verified state is restored:

```text
state_continuity = CONDITIONALLY_CONTINUOUS
state_lineage = RESTORED
binding_status = BOUND
operational_status = PASS
```

The classifier must explain:

```text
State lineage preserved through verified restore.
Execution continuity terminated at restart.
```

---

## 30. Cold Restart Classification

Where no prior state is inherited:

```text
state_continuity = INTERRUPTED
state_lineage = NEW_ROOT
transition_status = RESTARTED
```

The classifier must not use `SUCCEEDED` for state lineage.

---

## 31. Migration Classification

Required migration evidence:

* migration ID;
* source event;
* destination event;
* state-transfer evidence;
* source deactivation;
* no simultaneous duplicate execution;
* valid parent link.

Expected result:

```text
service_continuity = CONTINUOUS
runtime_continuity = CONDITIONALLY_CONTINUOUS
execution_continuity = CONDITIONALLY_CONTINUOUS
state_continuity = CONTINUOUS
state_lineage = LINEAR
binding_status = REBOUND
transition_status = MIGRATED
operational_status = PASS
```

---

## 32. Unverified Migration Classification

Where migration is claimed but required evidence is absent:

```text
runtime_continuity = UNVERIFIED
execution_continuity = UNKNOWN
state_continuity = UNVERIFIED
state_lineage = UNVERIFIED
operational_status = HOLD
confidence = LOW
```

The classifier must not infer continuity from matching names or state alone.

---

## 33. Restore Classification

Required conditions:

* event type `RESTORE`;
* valid snapshot parent;
* verified state evidence;
* new runtime identity;
* new execution identity.

Expected result:

```text
service_continuity = CONTINUOUS
runtime_continuity = TERMINATED
execution_continuity = TERMINATED
state_continuity = CONDITIONALLY_CONTINUOUS
state_lineage = RESTORED
transition_status = RESTORED
operational_status = PASS
```

---

## 34. Clone Classification

Required conditions:

* multiple active children;
* shared state parent;
* distinct runtime IDs;
* distinct execution IDs.

Expected result:

```text
runtime_continuity = TERMINATED
execution_continuity = TERMINATED
state_lineage = SHARED_PARENT
transition_status = CLONED
conflict_status = CLEAR
operational_status = PASS
```

If clones claim one exclusive authority role:

```text
binding_status = COLLIDING
conflict_status = COLLIDING
operational_status = HOLD
```

---

## 35. Branch Classification

Required conditions:

* one parent lineage;
* two or more successor lineages;
* distinct runtime or execution identities.

Expected result:

```text
state_lineage = BRANCHED
transition_status = BRANCHED
runtime_continuity = TERMINATED
execution_continuity = TERMINATED
operational_status = PASS
```

The higher-level service may remain continuous or conflicted depending on authority.

---

## 36. Merge Classification

Required conditions:

* two or more parent states;
* one new state identity;
* explicit merge event;
* preserved parent references.

Expected result:

```text
state_lineage = MERGED
state_continuity = CONDITIONALLY_CONTINUOUS
runtime_continuity = TERMINATED
execution_continuity = TERMINATED
transition_status = MERGED
operational_status = PASS
```

---

## 37. Unknown Event Classification

Unsupported event type:

```text
transition_status = UNKNOWN
operational_status = HOLD
confidence = UNKNOWN
```

Reason:

```text
Event type is not supported by prototype version 0.1.
```

---

## 38. Binding Classifier Boundary

The binding classifier must answer:

```text
Does this reference currently identify the declared target?
```

It must not answer:

```text
Is this target historically continuous with a prior target?
```

That second question belongs to the continuity classifier.

---

## 39. Continuity Classifier Boundary

The continuity classifier must answer:

```text
How are the prior and current identity layers connected?
```

It must not alter binding records or resolve authority conflicts.

---

## 40. Lineage Graph Validator

The lineage graph validator must support:

```text
one-to-one succession
one-to-many branching
many-to-one merging
termination
new roots
restoration
```

The derivation graph must remain directed and acyclic.

Non-derivation relationships must be excluded.

---

## 41. Non-Derivation Relationships

The following relationships must not be stored as lineage edges:

```text
communicates_with
mirrors
monitors
references
synchronized_with
depends_on
```

They may be represented later in a separate relationship graph.

---

## 42. Explainability Requirements

Every classification must include:

```text
applied_rules
reasons
missing_evidence
conflicts
confidence
operational_status
```

Example:

```text
Applied rule: RS-001 Restart
Reason: Runtime and execution identifiers changed.
Reason: Service identifier remained stable.
Missing evidence: None.
Operational status: PASS.
```

---

## 43. Initial Required Tests

### Test T-001 — Address Change

Expected:

```text
runtime continuity = CONTINUOUS
execution continuity = CONTINUOUS
binding = REBOUND
PASS
```

### Test T-002 — Warm Restart

Expected:

```text
service continuity = CONTINUOUS
runtime continuity = TERMINATED
execution continuity = TERMINATED
state lineage = RESTORED
PASS
```

### Test T-003 — Cold Restart

Expected:

```text
state continuity = INTERRUPTED
state lineage = NEW_ROOT
PASS
```

### Test T-004 — Valid Migration

Expected:

```text
runtime continuity = CONDITIONALLY_CONTINUOUS
execution continuity = CONDITIONALLY_CONTINUOUS
PASS
```

### Test T-005 — Unverified Migration

Expected:

```text
runtime continuity = UNVERIFIED
execution continuity = UNKNOWN
HOLD
```

### Test T-006 — Restore

Expected:

```text
new runtime
new execution
restored state lineage
PASS
```

### Test T-007 — Clone

Expected:

```text
distinct runtimes
shared parent lineage
PASS
```

### Test T-008 — Branch

Expected:

```text
branched lineage
distinct successors
PASS
```

### Test T-009 — Merge

Expected:

```text
multiple parents
new merged state
PASS
```

---

## 44. Required Negative Tests

### Test N-001 — Duplicate Event ID

Expected:

```text
FAIL
```

### Test N-002 — Missing Parent

Expected:

```text
HOLD
```

### Test N-003 — Lineage Cycle

Expected:

```text
FAIL
```

### Test N-004 — Merge With One Parent

Expected:

```text
FAIL
```

### Test N-005 — Clone With Reused Runtime ID

Expected:

```text
FAIL
```

### Test N-006 — Exclusive Authority Collision

Expected:

```text
binding = COLLIDING
conflict = COLLIDING
HOLD
```

### Test N-007 — Child Sequence Before Parent

Expected:

```text
FAIL
```

---

## 45. Classifier Rule Precedence

Rules must execute in this order:

```text
1. Structural validation
2. Parent validation
3. Temporal and sequence validation
4. Lineage-cycle validation
5. Authority-collision detection
6. Branch detection
7. Merge detection
8. Transition classification
9. Binding classification
10. Continuity classification
11. Operational status assignment
12. Explanation generation
```

---

## 46. Operational Status Assignment

### PASS

Assign only where:

* required evidence is complete;
* no collision exists;
* no invalid structure exists;
* continuity classification is supported.

### HOLD

Assign where:

* evidence is missing;
* migration is unverified;
* authority is conflicted;
* lineage is incomplete;
* classification is unsupported.

### FAIL

Assign where:

* duplicate identity exists where prohibited;
* lineage cycle exists;
* temporal order is invalid;
* merge structure is invalid;
* self-ancestry exists;
* immutable invariants are violated.

---

## 47. Error Handling

The classifier must use explicit domain errors.

Recommended exceptions:

```text
InvalidEventError
DuplicateEventError
MissingParentError
LineageCycleError
InvalidMergeError
AuthorityCollisionError
UnsupportedEventError
```

Services must not swallow validation errors.

---

## 48. Reproducibility Requirement

The same valid input set must always produce the same classification result.

```text
Same Inputs
        +
Same Rules
        =
Same Output
```

No random behavior is permitted.

---

## 49. Versioning

Prototype version:

```text
0.1.0
```

The version should be recorded in every classification result.

Recommended field:

```text
classifier_version
```

---

## 50. First Implementation Sequence

Implementation must proceed in this order:

```text
1. Freeze vocabulary
2. Define enums
3. Define immutable models
4. Write model tests
5. Implement structural validator
6. Write validator tests
7. Implement lineage graph validator
8. Write graph tests
9. Implement address-change classifier
10. Implement restart classifier
11. Implement migration classifier
12. Implement restore classifier
13. Implement clone classifier
14. Implement branch classifier
15. Implement merge classifier
16. Implement explanation service
17. Run full suite
18. Commit and freeze
```

---

## 51. Initial Checkpoint Boundary

Checkpoint 001 should include only:

```text
Enums
Immutable Models
Structural Validation
Lineage Graph Validation
Address Change
Restart
Migration
Restore
Clone
Branch
Merge
Explanation
Tests
```

Deferred capabilities must not be included in Checkpoint 001.

---

## 52. Freeze Conditions

The prototype may be frozen when:

1. all enums are defined;
2. all core models are immutable;
3. required fields are validated;
4. lineage cycles are rejected;
5. unknown migration returns HOLD;
6. branch and merge tests pass;
7. classifications contain reasons;
8. PASS, HOLD, and FAIL are explicit;
9. the full test suite passes;
10. checkpoint documentation is complete;
11. GitHub is synchronized;
12. the working tree is clean.

---

## 53. Acceptance Criteria

Version 0.1 is accepted when the classifier correctly distinguishes:

```text
Address Change
Restart
Migration
Restore
Clone
Branch
Merge
```

and refuses unsupported continuity where evidence is insufficient.

The minimum invariant is:

```text
No proof
    ↓
No continuity admission
    ↓
HOLD
```

---

## 54. Research Value

The prototype will test whether the four-threshold model can be represented computationally through:

* explicit identity layers;
* immutable events;
* binding assessments;
* lineage graphs;
* deterministic rules;
* explainable outputs;
* unknown preservation.

The prototype will not prove the universal sufficiency of the model.

---

## 55. Prototype Status

```text
SPECIFICATION: COMPLETE
IMPLEMENTATION: NOT STARTED
VOCABULARY: FROZEN FOR VERSION 0.1
MODEL BOUNDARIES: DEFINED
TEST BOUNDARIES: DEFINED
SIDE EFFECTS: PROHIBITED
UNKNOWN → HOLD: REQUIRED
```

---

## 56. Next Required Step

The next step is to create the prototype package structure and begin with enums and immutable models.

Recommended first command sequence:

```bat
mkdir research\RP-000001\artifacts\process_lineage_classifier\enums
mkdir research\RP-000001\artifacts\process_lineage_classifier\models
mkdir research\RP-000001\artifacts\process_lineage_classifier\services
mkdir research\RP-000001\artifacts\process_lineage_classifier\tests
mkdir research\RP-000001\artifacts\process_lineage_classifier\docs
```

No classifier service should be implemented before the vocabulary and model tests exist.

---

## 57. Specification Conclusion

RA-000001 defines the first executable research boundary for process lineage and continuity classification.

The prototype must preserve:

```text
Identity Layer
Transition Type
Binding Status
Continuity Status
Lineage Status
Authority
Evidence
Conflict
Operational Status
Explanation
```

The implementation posture is:

```text
DEFINE
TEST
IMPLEMENT MINIMALLY
VALIDATE
FREEZE
UNKNOWN → HOLD
```

---

End of RA-000001 Version 0.1
