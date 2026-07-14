# ROB-000011

# Executable Process Lineage and Continuity Classification

**Research Program:** RP-000001 — Organized Understanding
**Research Question:** RQ-000001 — Irreducible Structures of Organized Understanding
**Related Model:** RM-000001 — Minimum Distinguishability, Identity, Binding Integrity, and Continuity Model, Version 0.4
**Related Review:** RR-000010 — Research Review of Process Identity Across Migration and Restart
**Artifact Type:** Research Observation
**Version:** 0.1
**Status:** OBSERVED
**Date:** 2026-07-14

---

## 1. Observation Purpose

This observation defines a minimal executable classification structure for process identity and continuity events.

It tests whether explicit structured records can distinguish:

* restart;
* migration;
* restoration;
* cloning;
* branching;
* merging;
* failover;
* split-brain;
* termination;
* revival;
* identifier reuse.

This is the first observation in RP-000001 designed to support direct implementation as a small research simulator.

---

## 2. Research Prompt

> Can a minimal process-lineage simulator classify continuity outcomes using explicit identity layers, event lineage, binding status, and transition evidence?

The central structure is:

```text
Prior Process State
        +
Transition Event
        +
Current Process State
        +
Evidence
        =
Continuity Classification
```

---

## 3. Classification Objective

The simulator should not answer only:

```text
same process = true
```

or:

```text
same process = false
```

It should classify continuity separately across:

* service identity;
* runtime-instance identity;
* execution identity;
* state identity;
* state lineage;
* availability;
* authority;
* event lineage.

---

## 4. Minimal Research Object

A process-lineage record should contain:

```text
event_id
event_type
timestamp
service_id
runtime_id
execution_id
state_id
host_id
address
authority_role
parent_event_ids
parent_state_ids
binding_status
continuity_evidence
```

The record may also include:

```text
migration_id
snapshot_id
branch_id
merge_id
confidence
notes
```

---

## 5. Identity Layers

The simulator should represent the following identity layers independently.

### 5.1 Service Identity

The logical capability or institutionally recognized service.

### 5.2 Runtime-Instance Identity

A specific instantiated deployment.

### 5.3 Execution Identity

One uninterrupted or formally bridged execution.

### 5.4 State Identity

A specific state version or snapshot.

### 5.5 State-Lineage Identity

The derivation path connecting states.

### 5.6 Authority Identity

The runtime currently authorized to occupy a role.

### 5.7 Availability Identity

The logical service presented as reachable or operational.

These layers may receive different classifications for the same transition.

---

## 6. Event Types

The first executable vocabulary should include:

```text
START
ADDRESS_CHANGE
MIGRATE
RESTART
CHECKPOINT
RESTORE
CLONE
PROMOTE
DEMOTE
FAILOVER
BRANCH
MERGE
TERMINATE
REVIVE
REBIND
```

Unknown or unsupported transitions should use:

```text
UNKNOWN_EVENT
```

---

## 7. Continuity Status Vocabulary

The classifier should produce one or more of:

```text
CONTINUOUS
CONDITIONALLY_CONTINUOUS
MIGRATED
RESTARTED
RESTORED
SUCCEEDED
REPLACED
CLONED
BRANCHED
MERGED
REVIVED
TERMINATED
INTERRUPTED
CONFLICTED
UNVERIFIED
UNKNOWN
```

The status must identify its layer.

Example:

```text
service_continuity: CONTINUOUS
runtime_continuity: REPLACED
execution_continuity: TERMINATED
state_lineage: RESTORED
authority_continuity: CONTINUOUS
```

---

## 8. Binding Status Vocabulary

The classifier should separately assess binding integrity.

Candidate statuses include:

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

Continuity and binding must not be merged.

```text
Correct Binding
        ≠
Established Continuity
```

---

## 9. Classification Inputs

A transition should be classified from two or more process records.

Example prior record:

```json
{
  "event_id": "EV-001",
  "event_type": "START",
  "service_id": "SERVICE-A",
  "runtime_id": "INSTANCE-001",
  "execution_id": "EXEC-001",
  "state_id": "S-100",
  "host_id": "HOST-01",
  "address": "10.0.0.12",
  "authority_role": "PRIMARY"
}
```

Example current record:

```json
{
  "event_id": "EV-002",
  "event_type": "ADDRESS_CHANGE",
  "service_id": "SERVICE-A",
  "runtime_id": "INSTANCE-001",
  "execution_id": "EXEC-001",
  "state_id": "S-101",
  "host_id": "HOST-01",
  "address": "10.0.0.33",
  "authority_role": "PRIMARY",
  "parent_event_ids": ["EV-001"]
}
```

---

## 10. Address-Change Classification

Where:

* service ID remains unchanged;
* runtime ID remains unchanged;
* execution ID remains unchanged;
* event lineage is preserved;
* only the address changes;

the expected classification is:

```text
service_continuity: CONTINUOUS
runtime_continuity: CONTINUOUS
execution_continuity: CONTINUOUS
state_lineage: CONTINUOUS
address_binding: REBOUND
```

This tests:

```text
Address Change
        ≠
Identity Loss
```

---

## 11. Restart Classification

Where:

* service ID remains;
* runtime ID changes;
* execution ID changes;
* the prior process terminates;
* a new process starts;

the expected classification is:

```text
service_continuity: CONTINUOUS
runtime_continuity: REPLACED
execution_continuity: TERMINATED
transition_status: RESTARTED
```

State lineage depends on restoration evidence.

---

## 12. Warm Restart Classification

Where the new runtime restores the latest verified state:

```text
state_lineage: RESTORED
service_continuity: CONTINUOUS
runtime_continuity: REPLACED
execution_continuity: TERMINATED
```

This preserves:

```text
State Succession
```

but not:

```text
Uninterrupted Execution
```

---

## 13. Cold Restart Classification

Where the service restarts without restoring prior state:

```text
service_continuity: CONTINUOUS
runtime_continuity: REPLACED
execution_continuity: TERMINATED
state_continuity: INTERRUPTED
state_lineage: SUCCEEDED
```

The service remains the authorized logical successor while prior state continuity is lost.

---

## 14. Validated Migration Classification

A migration should be classified as continuity-preserving only when evidence includes:

* migration transaction;
* source runtime;
* destination runtime;
* state-transfer validation;
* source deactivation;
* absence of duplicate active execution;
* parent event linkage.

Expected classification:

```text
service_continuity: CONTINUOUS
runtime_continuity: MIGRATED
execution_continuity: CONDITIONALLY_CONTINUOUS
state_lineage: CONTINUOUS
host_binding: REBOUND
```

---

## 15. Unverified Migration Classification

Where host and runtime identifiers change but no migration bridge exists:

```text
service_continuity: CONDITIONALLY_CONTINUOUS
runtime_continuity: UNVERIFIED
execution_continuity: UNKNOWN
state_lineage: UNVERIFIED
```

The simulator should not infer migration from similarity alone.

---

## 16. Stop-and-Restore Classification

Where:

* prior execution terminates;
* state is checkpointed;
* a new runtime restores that state;

the expected classification is:

```text
service_continuity: CONTINUOUS
runtime_continuity: REPLACED
execution_continuity: TERMINATED
state_lineage: RESTORED
transition_status: SUCCEEDED
```

The new runtime is a successor execution.

---

## 17. Snapshot Classification

A checkpoint event should create a state artifact.

```text
snapshot_identity: CREATED
runtime_continuity: CONTINUOUS
execution_continuity: CONTINUOUS
state_lineage: CHECKPOINTED
```

The snapshot is not the process.

```text
Snapshot Identity
        ≠
Runtime Identity
```

---

## 18. Clone Classification

Where two new runtimes derive from the same snapshot:

```text
runtime_A.state_parent = SNAPSHOT-001
runtime_B.state_parent = SNAPSHOT-001
```

the expected classification is:

```text
runtime_identity: DISTINCT
execution_identity: DISTINCT
state_lineage: SHARED_PARENT
branching_status: BRANCHED
```

This rejects:

```text
Identical Initial State
        =
Same Runtime
```

---

## 19. Branch Classification

A branch occurs when one prior execution or state produces multiple active successors.

Expected result:

```text
lineage_status: BRANCHED
unique_runtime_continuity: NOT_PRESERVED
service_continuity: CONDITIONALLY_CONTINUOUS
```

The service identity may remain valid at a higher level.

Unique execution continuity does not.

---

## 20. Split-Brain Classification

Where two runtimes simultaneously claim one exclusive authority role:

```text
INSTANCE-A.authority_role = PRIMARY
INSTANCE-B.authority_role = PRIMARY
```

the expected classification is:

```text
service_identity: CONFLICTED
authority_binding: COLLIDING
state_lineage: BRANCHED
runtime_identity: DISTINCT
operational_status: HOLD
```

Split-brain is both:

* a continuity conflict;
* a binding-integrity conflict;
* an authority conflict.

---

## 21. Failover Classification

Where one runtime terminates and an authorized replica becomes primary:

```text
service_continuity: CONTINUOUS
availability_continuity: CONTINUOUS
runtime_continuity: REPLACED
execution_continuity: TERMINATED
authority_continuity: SUCCEEDED
state_lineage: CONDITIONALLY_CONTINUOUS
```

State continuity depends on synchronization evidence.

---

## 22. Stale Failover Classification

Where the promoted replica has older state:

```text
service_continuity: CONTINUOUS
availability_continuity: CONTINUOUS
state_continuity: DEGRADED
state_lineage: SUCCEEDED
runtime_continuity: REPLACED
```

The classifier should preserve:

```text
Availability Continuity
        ≠
Complete State Continuity
```

---

## 23. Merge Classification

Where divergent branches are reconciled into one state:

```text
parent_state_ids = ["S-300A", "S-300B"]
event_type = "MERGE"
```

the expected classification is:

```text
state_lineage: MERGED
runtime_identity: NEW_OR_SUCCEEDED
execution_identity: NEW
service_continuity: CONDITIONALLY_CONTINUOUS
```

The merged state has multiple lineages.

It is not identical to either parent state.

---

## 24. Termination Classification

Where a runtime or execution ends without a successor:

```text
runtime_continuity: TERMINATED
execution_continuity: TERMINATED
availability_continuity: TERMINATED_OR_UNKNOWN
service_continuity: UNKNOWN_OR_TERMINATED
```

The service result depends on whether another authorized runtime remains.

---

## 25. Revival Classification

Where a service returns after termination using historical state or lineage:

```text
service_continuity: REVIVED
runtime_continuity: NEW
execution_continuity: NEW
state_lineage: RESTORED_OR_SUCCEEDED
availability_continuity: INTERRUPTED
```

Revival should not be classified as uninterrupted continuity.

---

## 26. Identifier-Reuse Classification

Suppose:

```text
HOST-01 / PID 4102
```

identified `EXEC-001`, terminated, and later identified `EXEC-009`.

Expected classification:

```text
pid_binding: REBOUND
execution_identity: DISTINCT
false_continuity_risk: DETECTED
```

The same scoped identifier does not establish the same process.

---

## 27. Service-Name Reuse Classification

Where a new system adopts an old service name without:

* preserved state;
* event lineage;
* authorized succession;
* continuity evidence;

the expected classification is:

```text
service_identity: UNVERIFIED
name_binding: REUSED
service_continuity: UNKNOWN
```

Name equality is insufficient.

---

## 28. Authority Transfer Classification

Where authority transfers from one runtime to another:

```text
INSTANCE-A: PRIMARY → DEMOTED
INSTANCE-B: SECONDARY → PRIMARY
```

the expected classification is:

```text
authority_continuity: SUCCEEDED
runtime_identity: DISTINCT
service_continuity: CONTINUOUS
authority_binding: REBOUND
```

Role continuity does not imply occupant continuity.

---

## 29. Unknown Classification

The simulator should return `UNKNOWN` when evidence is insufficient.

Examples include:

* missing parent events;
* missing state lineage;
* ambiguous timestamps;
* duplicate exclusive roles;
* unverified migration;
* inconsistent identifiers;
* unsupported event types.

The system must not infer continuity merely because fields look similar.

---

## 30. Minimal Classification Rules

A first implementation may use explicit deterministic rules.

### Rule A — Restart

```text
event_type = RESTART
runtime_id changes
execution_id changes
```

Result:

```text
runtime: REPLACED
execution: TERMINATED
service: CONTINUOUS if service_id and authority succession are valid
```

### Rule B — Migration

```text
event_type = MIGRATE
migration evidence valid
no duplicate active execution
```

Result:

```text
runtime: MIGRATED
execution: CONDITIONALLY_CONTINUOUS
```

### Rule C — Restore

```text
event_type = RESTORE
snapshot parent exists
state hash verified
```

Result:

```text
state_lineage: RESTORED
execution: NEW
```

### Rule D — Clone

```text
multiple active children share one state parent
```

Result:

```text
lineage: BRANCHED
runtime identities: DISTINCT
```

### Rule E — Split-Brain

```text
multiple active runtimes hold one exclusive role
```

Result:

```text
authority_binding: COLLIDING
service_identity: CONFLICTED
```

### Rule F — Merge

```text
one state has multiple parent state identifiers
```

Result:

```text
state_lineage: MERGED
state_identity: NEW
```

---

## 31. Rule Precedence

The classifier should avoid hidden precedence.

Recommended order:

```text
1. Validate records
2. Validate identity layers
3. Validate parent links
4. Detect collisions
5. Detect branching
6. Detect merging
7. Classify transition type
8. Assess binding integrity
9. Assess continuity by layer
10. Preserve UNKNOWN where evidence is insufficient
```

Conflict detection should occur before optimistic continuity admission.

---

## 32. Validation Requirements

Each record should be checked for:

* required identifiers;
* valid event type;
* temporal order;
* parent existence;
* duplicate event IDs;
* duplicate runtime IDs within incompatible lifetimes;
* impossible state lineage;
* conflicting authority roles;
* missing transition evidence.

Structural validity does not prove semantic truth.

```text
Valid Record
        ≠
Valid Continuity Claim
```

---

## 33. Classification Output

A classification result should include:

```json
{
  "transition_id": "TR-001",
  "service_continuity": "CONTINUOUS",
  "runtime_continuity": "REPLACED",
  "execution_continuity": "TERMINATED",
  "state_lineage": "RESTORED",
  "availability_continuity": "UNKNOWN",
  "authority_continuity": "CONTINUOUS",
  "binding_status": "BOUND",
  "confidence": "HIGH",
  "reasons": [
    "service identifier preserved",
    "runtime identifier changed",
    "prior execution terminated",
    "verified snapshot restored"
  ]
}
```

The reasons are necessary for inspectability.

---

## 34. Explainability Requirement

Every classification should preserve:

* applied rules;
* supporting records;
* missing evidence;
* assumptions;
* conflicting signals;
* confidence.

A label without explanation is insufficient for research use.

---

## 35. Confidence

A simple first vocabulary may use:

```text
HIGH
MODERATE
LOW
UNKNOWN
```

Confidence should derive from evidence completeness.

It should not be invented numerically without an explicit method.

---

## 36. Expected Scenario Table

| Scenario         | Service                  | Runtime          | Execution                | State Lineage         | Binding            |
| ---------------- | ------------------------ | ---------------- | ------------------------ | --------------------- | ------------------ |
| Address change   | Continuous               | Continuous       | Continuous               | Continuous            | Rebound            |
| Restart          | Continuous               | Replaced         | Terminated               | Succeeded or restored | Bound              |
| Live migration   | Continuous               | Migrated         | Conditionally continuous | Continuous            | Bound              |
| Stop-and-restore | Continuous               | Replaced         | Terminated               | Restored              | Bound              |
| Clone            | Continuous or conflicted | Distinct         | Distinct                 | Branched              | Possibly colliding |
| Failover         | Continuous               | Replaced         | Terminated               | Succeeded             | Rebound            |
| Split-brain      | Conflicted               | Distinct         | Distinct                 | Branched              | Colliding          |
| Merge            | Conditionally continuous | New or succeeded | New                      | Merged                | Reconciled         |
| Revival          | Revived                  | New              | New                      | Restored or succeeded | Rebound            |
| Identifier reuse | Unknown                  | Distinct         | Distinct                 | None                  | Rebound            |

The table is provisional.

---

## 37. Four-Threshold Integration

Each scenario may also be evaluated using RM-000001 Version 0.4.

### Distinguishability

Can the relevant layers and events be separated?

### Identity

Can service, runtime, execution, state, and authority be identified?

### Binding Integrity

Are references correctly attached to targets?

### Continuity

Are transitions adequately connected?

A classification should not be admitted where any required threshold is unmet.

---

## 38. Example Threshold Assessment

For validated migration:

```text
D: PASS
I: PASS
B: PASS
C: PASS
```

For unverified host replacement:

```text
D: PASS
I: PARTIAL
B: UNKNOWN
C: UNKNOWN
```

Result:

```text
UNKNOWN → HOLD
```

---

## 39. Research Simulator Structure

A minimal implementation may contain:

```text
models/
    process_event.py
    process_state.py
    continuity_result.py

services/
    lineage_classifier.py
    transition_validator.py

tests/
    test_restart_classification.py
    test_migration_classification.py
    test_restore_classification.py
    test_clone_classification.py
    test_split_brain_classification.py
    test_merge_classification.py
```

This is a proposed future implementation structure, not yet implemented.

---

## 40. Immutable Models

The simulator should prefer immutable research records.

A process event should not be rewritten after classification.

Corrections should be appended as new records.

This preserves:

* event identity;
* review history;
* correction traceability;
* reproducibility.

---

## 41. Test-First Requirement

Implementation should follow:

```text
Vocabulary
    ↓
Immutable Models
    ↓
Tests
    ↓
Minimal Classifier
    ↓
Full Validation
    ↓
Commit and Freeze
```

The first implementation should support only the smallest explicit rule set necessary to satisfy the tests.

---

## 42. Initial Test Cases

### Test 1 — Address Change

Expected:

```text
runtime continuous
execution continuous
address rebound
```

### Test 2 — Restart With Restore

Expected:

```text
service continuous
runtime replaced
execution terminated
state restored
```

### Test 3 — Valid Migration

Expected:

```text
runtime migrated
execution conditionally continuous
```

### Test 4 — Clone

Expected:

```text
distinct runtimes
branched lineage
```

### Test 5 — Split-Brain

Expected:

```text
authority collision
service conflicted
```

### Test 6 — Merge

Expected:

```text
new state
multiple parent lineages
```

### Test 7 — PID Reuse

Expected:

```text
distinct executions
false continuity detected
```

---

## 43. Negative Test Cases

The simulator should reject or hold:

* migration without evidence;
* restoration without a snapshot parent;
* merge without multiple parent states;
* clone with reused runtime identity;
* two exclusive primaries without conflict status;
* child event preceding parent event;
* reused event identifier;
* state lineage cycle;
* missing identity layer.

---

## 44. Lineage Graph

The simulator may represent state and execution lineage as a directed graph.

```text
Node
    =
event, execution, runtime, or state

Edge
    =
started_from, migrated_from, restored_from,
branched_from, merged_from, succeeded
```

The graph should permit:

* one-to-one transitions;
* one-to-many branches;
* many-to-one merges;
* terminated nodes;
* active nodes.

---

## 45. Graph Integrity Conditions

Candidate graph constraints include:

1. Event IDs must be unique.
2. Parent events must exist.
3. Time must not move backward along an edge.
4. A runtime cannot be its own ancestor.
5. A merge must contain at least two parent lineages.
6. A branch must produce at least two child lineages.
7. Exclusive authority roles must not overlap without conflict status.
8. Terminated execution cannot later emit events without revival or restoration.

---

## 46. Cycle Detection

A lineage cycle such as:

```text
EXEC-001 → EXEC-002 → EXEC-001
```

is invalid unless the relationship represents reference rather than derivation.

Derivation graphs should remain acyclic.

### Candidate Determination

**LINEAGE DERIVATION: DIRECTED ACYCLIC STRUCTURE**

This remains provisional.

---

## 47. State-Lineage Graph

State lineage may be represented as:

```text
S-100 → S-101 → S-102
                  ├── S-103A
                  └── S-103B
```

Merge:

```text
S-103A ──\
          → S-104M
S-103B ──/
```

This explicitly preserves branching and merging.

---

## 48. Service-Lineage Graph

Service succession may differ from runtime lineage.

```text
SERVICE-A
├── INSTANCE-001
├── INSTANCE-002
└── INSTANCE-003
```

The service node persists as a higher-level identity while runtime nodes are replaced.

---

## 49. Authority Graph

Authority transitions may be represented separately:

```text
INSTANCE-001
    PRIMARY
        ↓ demote

INSTANCE-002
    SECONDARY
        ↓ promote
    PRIMARY
```

This distinguishes:

* service continuity;
* runtime replacement;
* authority succession.

---

## 50. Classification Boundary

The simulator should classify only what the supplied evidence supports.

It should not decide:

* metaphysical numerical identity;
* legal ownership;
* moral responsibility;
* human identity;
* universal continuity criteria.

Its function is operational classification.

---

## 51. Candidate Finding

The following candidate finding is admitted for review:

> A minimal process-lineage simulator can classify restart, migration, restoration, cloning, branching, merging, failover, and split-brain outcomes only when identity layers, transition events, parent lineage, authority, binding status, and continuity evidence are represented separately. Binary “same process” classification is insufficient.

This remains provisional until implementation.

---

## 52. Effect on RM-000001

ROB-000011 operationalizes RM-000001 Version 0.4.

It directly applies:

```text
D = distinguishability
I = identity
B = binding integrity
C = continuity
```

It also converts model vocabulary into:

* structured fields;
* deterministic rules;
* expected classifications;
* test cases;
* graph constraints;
* explicit unknown handling.

No model revision is currently required.

---

## 53. Research Status

**Candidate Structure:** Executable Layered Continuity Classification
**Current Assessment:** PLAUSIBLE
**Structured Classification:** DEFINED
**Executable Implementation:** NOT YET IMPLEMENTED
**Layered Identity Requirement:** SUPPORTED
**Event Lineage Requirement:** SUPPORTED
**Binding Separation:** SUPPORTED
**Branch and Merge Representation:** SUPPORTED
**Split-Brain Classification:** DEFINED
**Unknown Preservation:** REQUIRED
**Irreducibility Status:** UNKNOWN
**Review Status:** NOT REVIEWED

---

## 54. Evidence Supporting the Observation

The observation defines:

* explicit input records;
* event vocabulary;
* continuity vocabulary;
* binding vocabulary;
* rule precedence;
* scenario classifications;
* negative tests;
* graph constraints;
* expected outputs.

This is stronger than a purely conceptual example but remains pre-implementation.

---

## 55. Evidence Limitations

This observation does not establish that:

* the rules are complete;
* the classifications are universally correct;
* live migration semantics are platform-independent;
* continuity confidence can be measured reliably;
* a DAG captures every valid process history;
* authority conflicts can always be resolved;
* state equivalence can always be verified;
* the four-threshold model is computationally sufficient.

Implementation and testing remain required.

---

## 56. Next Required Review

The formal review should examine:

* whether the event vocabulary is sufficient;
* whether restart and succession are correctly separated;
* whether validated migration should preserve execution identity;
* whether branching and merging classifications are internally consistent;
* whether service identity belongs in the same graph as runtime identity;
* whether lineage graphs must be acyclic;
* whether confidence and unknown handling are adequate;
* whether the proposed tests are sufficient for the first implementation.

---

## 57. Next Required Artifact

If retained by review, the next artifact should be an implementation charter or prototype specification.

Suggested artifact:

```text
RA-000001
Process Lineage Classifier Prototype Specification
```

or:

```text
research/RP-000001/artifacts/process_lineage_classifier/
```

The first executable checkpoint should implement:

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

with test-first validation.

---

## 58. Operational Conclusion

ROB-000011 converts the continuity model into a candidate executable classification structure.

The key operational finding is:

```text
One Transition
        ↓
Multiple Identity Layers
        ↓
Multiple Continuity Outcomes
```

A restart may preserve service identity while terminating execution identity.

A migration may preserve execution continuity only when a valid migration bridge exists.

A restoration preserves state lineage while creating a new execution.

A clone creates distinct runtimes with shared ancestry.

A split-brain event creates a binding and authority conflict.

The correct status remains:

```text
OBSERVED
CLASSIFICATION STRUCTURE DEFINED
EXECUTABLE IMPLEMENTATION NOT YET PRESENT
TEST-FIRST IMPLEMENTATION REQUIRED
LAYERED IDENTITY REQUIRED
EVENT LINEAGE REQUIRED
UNKNOWN → HOLD
```

---

End of ROB-000011
