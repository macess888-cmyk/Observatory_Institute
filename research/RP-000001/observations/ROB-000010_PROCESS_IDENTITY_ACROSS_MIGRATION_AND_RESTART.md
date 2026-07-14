# ROB-000010

# Process Identity Across Migration and Restart

**Research Program:** RP-000001 — Organized Understanding
**Research Question:** RQ-000001 — Irreducible Structures of Organized Understanding
**Related Model:** RM-000001 — Minimum Distinguishability, Identity, and Binding Integrity Model, Version 0.3
**Related Review:** RR-000009 — Research Review of Identity Through Continuous Transformation
**Artifact Type:** Research Observation
**Version:** 0.1
**Status:** OBSERVED
**Date:** 2026-07-14

---

## 1. Observation Purpose

This observation investigates whether a software process retains identity across:

* migration;
* restart;
* address change;
* runtime replacement;
* state restoration;
* component replacement;
* cloning;
* branching;
* termination and recreation.

It provides the first concrete operational pressure test of continuity-based identity within RP-000001.

The observation distinguishes among:

* service identity;
* runtime-instance identity;
* process identity;
* execution identity;
* state identity;
* lineage;
* binding continuity.

This observation does not assume that a software process is equivalent to a physical object, institution, or living system.

---

## 2. Research Prompt

> Can a software process retain identity across controlled migration, restart, state restoration, address change, and runtime replacement?

The central comparison is:

```text
Logical service preserved
        +
Runtime implementation changed
        +
State continuity varied
        =
Which identities remain?
```

---

## 3. Operational Scenario

Consider a software service named:

```text
SERVICE-A
```

At time `t₁`, it runs as:

```text
Service Identity: SERVICE-A
Runtime Instance: INSTANCE-001
Process ID: 4102
Host: HOST-01
Address: 10.0.0.12
State Version: S-100
```

The system later performs controlled migration and restart operations.

The observation examines whether each post-transition state represents:

* the same service;
* the same runtime instance;
* the same process;
* the same execution;
* the same state lineage;
* a successor;
* a clone;
* a new entity.

---

## 4. Initial Identity Layers

The initial operational object contains several separable identities.

### 4.1 Service Identity

```text
SERVICE-A
```

The logical capability presented to users or dependent systems.

### 4.2 Runtime-Instance Identity

```text
INSTANCE-001
```

A particular instantiated deployment of the service.

### 4.3 Operating-System Process Identity

```text
PID 4102
```

A process identity assigned within a host and operating-system scope.

### 4.4 Host Identity

```text
HOST-01
```

The machine or runtime environment executing the process.

### 4.5 Network Identity

```text
10.0.0.12
```

The current address through which the process may be reached.

### 4.6 State Identity

```text
S-100
```

The preserved logical state at a defined moment.

### 4.7 Execution Identity

The particular uninterrupted execution beginning when the process starts and ending when it terminates.

These identities may change independently.

---

## 5. Initial Observation

A software system can preserve service identity while replacing its runtime process.

Therefore:

```text
Service Identity
        ≠
Runtime Process Identity
```

and:

```text
Logical Continuity
        ≠
Execution Continuity
```

A statement that “the service remained available” does not establish that the same process continued to execute.

---

## 6. Address-Change Test

At time `t₂`, the process remains running but its address changes:

```text
Service Identity: SERVICE-A
Runtime Instance: INSTANCE-001
Process ID: 4102
Host: HOST-01
Address: 10.0.0.33
State Version: S-105
```

Preserved:

* service identity;
* runtime-instance identity;
* process identity;
* host identity;
* execution continuity;
* state lineage.

Changed:

* network address.

Therefore:

```text
Address Change
        ≠
Process Replacement
```

and:

```text
Network Identity
        ≠
Service Identity
```

A stable network address is not required for process continuity.

---

## 7. Process-ID Scope

A process identifier such as `4102` is meaningful only within a defined host and time interval.

After termination, the same PID may be reused.

Example:

```text
t₁:
HOST-01 / PID 4102 → SERVICE-A

t₄:
HOST-01 / PID 4102 → UNRELATED-PROCESS
```

Therefore:

```text
Same PID
        ≠
Same Process
```

without temporal and host scope.

This is an operational example of identifier reuse and false continuity.

---

## 8. In-Place Restart Test

At time `t₃`, the process terminates and restarts on the same host:

```text
Before Restart:
Service Identity: SERVICE-A
Runtime Instance: INSTANCE-001
Process ID: 4102
Host: HOST-01
State Version: S-110

After Restart:
Service Identity: SERVICE-A
Runtime Instance: INSTANCE-002
Process ID: 4821
Host: HOST-01
State Version: S-110
```

Preserved:

* service identity;
* host identity;
* restored state;
* deployment lineage.

Terminated:

* original operating-system process;
* uninterrupted execution;
* runtime-instance identity, if instance identifiers are restart-specific.

Therefore:

```text
Service Restart
        =
Execution Discontinuity
```

while:

```text
Service Restart
        ≠
Necessary Service Identity Loss
```

---

## 9. Restart Without State Restoration

Suppose the process restarts with default state:

```text
Before:
State Version: S-110

After:
State Version: S-000
```

The service may retain:

* name;
* endpoint;
* function;
* ownership;
* deployment role.

It may lose:

* prior operational state;
* session continuity;
* execution history;
* user-specific continuity.

This produces:

```text
Service Continuity
        +
State Discontinuity
```

The resulting system may be the same service but not the continuation of the prior stateful process.

---

## 10. Warm Restart

A warm restart restores the immediately preceding state:

```text
S-110
    ↓ terminate
S-110
    ↓ resume
S-111
```

This supports state lineage.

However, execution continuity is still broken.

Therefore:

```text
State Continuity
        ≠
Execution Continuity
```

A restarted process may continue the same state lineage through a new execution instance.

---

## 11. Cold Restart

A cold restart begins without prior runtime state.

```text
S-110
    ↓ terminate
S-000
```

The logical service may remain the same under administrative and functional criteria.

The process lineage may be:

```text
SERVICE-A
├── EXECUTION-001
└── EXECUTION-002
```

The second execution is a successor execution, not the uninterrupted continuation of the first.

---

## 12. Migration Without Restart

Suppose a runtime environment supports live migration from `HOST-01` to `HOST-02`.

```text
Before:
Runtime Instance: INSTANCE-001
Process ID: 4102
Host: HOST-01
State: S-120

After:
Runtime Instance: INSTANCE-001
Process ID: 7308
Host: HOST-02
State: S-121
```

If execution state is transferred continuously and no logical interruption occurs, the system may preserve:

* runtime-instance identity;
* execution identity;
* state lineage;
* service identity.

It changes:

* host identity;
* process identifier;
* network bindings.

This suggests:

```text
Process Identity
        ≠
Host-Bound Identifier
```

provided that a validated migration bridge exists.

---

## 13. Migration Bridge

A valid live-migration identity claim requires evidence connecting:

```text
Pre-Migration Runtime
        ↓
Migration Event
        ↓
Post-Migration Runtime
```

Candidate evidence includes:

* migration transaction ID;
* state-transfer checksum;
* source and destination acknowledgement;
* monotonic state sequence;
* paused-and-resumed execution record;
* absence of simultaneous duplicate execution;
* preserved runtime identifier.

Without this bridge, migration may be indistinguishable from termination and recreation.

---

## 14. Stop-and-Restore Migration

Suppose the process stops on `HOST-01`, its state is copied, and a new process starts on `HOST-02`.

```text
HOST-01 / EXECUTION-001
        ↓ snapshot S-130
        ↓ termination
HOST-02 / EXECUTION-002
        ↓ restore S-130
```

Preserved:

* service identity;
* state lineage, if the snapshot is valid;
* deployment lineage;
* logical process role.

Not preserved:

* uninterrupted execution;
* original runtime-instance identity, under a strict execution criterion.

This is better represented as:

```text
Execution Successor
        +
Restored State Lineage
```

rather than uninterrupted runtime continuity.

---

## 15. Migration Versus Restart

Migration and restart may produce similar external outcomes.

Both can preserve:

* service name;
* function;
* state;
* interface.

They differ in:

* execution continuity;
* runtime-instance continuity;
* transition path;
* overlap;
* migration evidence;
* process termination.

Therefore:

```text
Equivalent External Behaviour
        ≠
Equivalent Process History
```

---

## 16. Snapshot Creation

At time `t₄`, the service creates snapshot:

```text
SNAPSHOT-001
State: S-140
Source Execution: EXECUTION-003
Created At: t₄
```

The snapshot has its own identity.

It is not the running process.

```text
Snapshot Identity
        ≠
Runtime Identity
```

The snapshot preserves a representation of state at a moment.

It does not preserve active execution.

---

## 17. Restoration From Snapshot

At time `t₅`, the process terminates.

At time `t₆`, a new runtime restores `SNAPSHOT-001`.

```text
EXECUTION-003
        ↓ snapshot
SNAPSHOT-001
        ↓ restore
EXECUTION-004
```

The new execution inherits state lineage from the earlier execution.

It is not the same uninterrupted execution.

Possible claims include:

```text
Same Service: PLAUSIBLE
Same State Lineage: SUPPORTED
Same Runtime Execution: NO
Same Process Instance: NO
Successor Process: SUPPORTED
```

---

## 18. Restoration After Continued Execution

Suppose the original process continues after snapshot creation:

```text
SNAPSHOT-001 = S-140
Original Process continues to S-160
```

Later, a new process restores `S-140`.

There are now two lineages:

```text
S-140
├── Original continuation → S-160
└── Restored continuation → S-141R
```

This is branching.

The restored process is not the unique continuation of the original current process.

It is a branch from an earlier state.

---

## 19. Branching Through Snapshot

Snapshot restoration demonstrates:

```text
Shared Prior State
        ≠
Shared Current Identity
```

Both branches may claim lineage from `S-140`.

They cannot both be the same unique execution.

Therefore:

```text
State Lineage Preserved
        +
Execution Identity Branched
```

---

## 20. Clone Test

Suppose `SNAPSHOT-001` is restored twice:

```text
SNAPSHOT-001
├── INSTANCE-A
└── INSTANCE-B
```

Both instances begin with identical state.

They remain distinct because:

* they execute independently;
* they can diverge;
* they occupy different runtime positions;
* they produce separate events.

Therefore:

```text
Identical Initial State
        ≠
Same Runtime Identity
```

and:

```text
Common Lineage
        ≠
Common Numerical Identity
```

---

## 21. Simultaneous Clone Conflict

If both clones claim:

```text
I am SERVICE-A primary instance.
```

the system may experience:

* duplicate authority;
* conflicting writes;
* split-brain state;
* duplicated external actions;
* identity collision.

This creates a binding-integrity failure if one unique primary identity is required.

---

## 22. Primary Role Identity

The label:

```text
PRIMARY
```

is a role identity.

It may transfer from one runtime to another.

```text
t₁:
INSTANCE-A = PRIMARY

t₂:
INSTANCE-B = PRIMARY
```

Therefore:

```text
Primary Role Continuity
        ≠
Runtime-Instance Continuity
```

A service may preserve role continuity while replacing the actor occupying the role.

---

## 23. Failover Test

Suppose `INSTANCE-A` fails and `INSTANCE-B` becomes primary.

Preserved:

* service identity;
* logical capability;
* primary role;
* replicated state, if synchronized.

Changed:

* active runtime instance;
* process identity;
* host;
* possibly state freshness.

The event is:

```text
Service Continuity Through Role Transfer
```

not:

```text
Same Runtime Process Continued
```

---

## 24. Failover With State Lag

Suppose the replica is behind:

```text
Primary before failure: S-200
Replica at promotion: S-197
```

The service remains available.

State continuity is degraded.

Therefore:

```text
Availability Continuity
        ≠
State Continuity
```

A user may observe the same service identity while losing recent state history.

---

## 25. Service Identity

Service identity may be preserved through:

* stable purpose;
* stable interface;
* administrative designation;
* continuous authority;
* accepted succession;
* preserved state lineage;
* role continuity.

It is not equivalent to a specific runtime process.

A provisional structure is:

```text
SERVICE-A
├── Runtime Instance 001
├── Runtime Instance 002
├── Runtime Instance 003
└── Runtime Instance 004
```

---

## 26. Runtime-Instance Identity

Runtime-instance identity identifies one instantiated execution environment.

It may be bounded by:

* creation;
* start;
* migration;
* pause;
* resume;
* termination.

Whether migration preserves runtime-instance identity depends on the migration semantics and evidence.

A restart usually creates a new runtime instance under strict criteria.

---

## 27. Execution Identity

Execution identity concerns one continuous or formally bridged run.

It may persist through:

* address change;
* host migration;
* pause and resume;
* resource replacement;

if the execution transition remains singular and traceable.

It ends through:

* termination;
* unbridged recreation;
* parallel cloning;
* branch creation.

---

## 28. Process Identity

“Process identity” is ambiguous unless its criterion is declared.

It may mean:

* operating-system process;
* logical process;
* workflow;
* service execution;
* state lineage;
* institutional capability.

Therefore:

```text
Process Identity Claim
        Requires
Declared Process Level
```

---

## 29. State Identity

State identity concerns a defined state version or snapshot.

Two runtimes can possess equivalent copies of the same state.

They remain separate runtime identities.

State equivalence does not imply process identity.

```text
Same State
        ≠
Same Execution
```

---

## 30. State Lineage

State lineage records derivation:

```text
S-100
    ↓
S-101
    ↓
S-102
```

A branch produces:

```text
S-102
├── S-103A
└── S-103B
```

Lineage may remain inspectable after process identity branches.

---

## 31. Event-Lineage Requirement

A strong process-continuity claim should preserve event lineage:

```text
Start
Migration
Checkpoint
Restart
Restore
Promotion
Termination
```

Without event lineage, a stable service name may conceal multiple unrelated executions.

---

## 32. Restart Counterexample

Suppose a new implementation is deployed under the same service name:

```text
Before:
SERVICE-A / Code Version 1

After:
SERVICE-A / Code Version 2
```

The service identity may remain.

The implementation identity changes.

If state is reset, both runtime and state continuity may fail.

Thus:

```text
Same Service Name
        ≠
Same Implementation
        ≠
Same Runtime
        ≠
Same State
```

---

## 33. Complete Component Replacement

A long-lived service may replace:

* hosts;
* processes;
* containers;
* addresses;
* code versions;
* operators;
* storage devices.

The service may remain institutionally and functionally continuous.

This is an operational example of complete component replacement with preserved higher-level identity.

The continuity criterion is not material sameness.

It is a combination of:

* accepted succession;
* function;
* authority;
* interface;
* state lineage;
* history.

---

## 34. Service of Theseus Boundary

The system may eventually preserve only:

* service name;
* institutional recognition;
* purpose;
* historical lineage.

Every technical component may have changed.

The service may still be treated as continuing.

This does not prove that a metaphysically identical entity persists.

It demonstrates operational and institutional identity continuity.

---

## 35. Termination and Recreation

Suppose `SERVICE-A` is fully removed.

Months later, a new system is created with:

* the same name;
* the same interface;
* the same purpose;
* no preserved state;
* no deployment lineage;
* no continuity record.

The claim that it is the same service is weak.

It may be:

* a recreation;
* a successor;
* a replacement;
* a revival by convention.

Therefore:

```text
Name Reuse
        ≠
Service Continuity
```

---

## 36. Restoration After Long Gap

Suppose a valid historical snapshot is restored after a long gap.

The new process has lineage from the old state.

The gap breaks continuous operation.

Possible statuses include:

```text
SERVICE REVIVED
STATE LINEAGE RESTORED
EXECUTION CONTINUITY BROKEN
```

This is more precise than calling it simply the same process.

---

## 37. Continuous Availability Without Process Continuity

A cluster may provide uninterrupted service while every runtime process is replaced.

```text
INSTANCE-A → INSTANCE-B → INSTANCE-C
```

Users observe no outage.

This supports:

```text
Availability Continuity
        ≠
Runtime Continuity
```

Service identity can persist through coordinated succession.

---

## 38. Process Continuity Without Availability

A process may continue running while temporarily unreachable.

```text
Execution persists
Network path fails
```

This supports:

```text
Runtime Continuity
        ≠
Availability Continuity
```

Operational identity claims must specify the continuity dimension.

---

## 39. State Continuity Without Service Continuity

A state archive may be imported into a different service.

```text
SERVICE-A state
        ↓ imported
SERVICE-B
```

State lineage is preserved.

Service identity is not.

Therefore:

```text
State Lineage
        ≠
Service Identity
```

---

## 40. Service Continuity Without State Continuity

A stateless service may restart repeatedly while preserving:

* interface;
* function;
* authority;
* role.

State continuity may be irrelevant.

This demonstrates operation-dependent identity requirements.

---

## 41. Migration Failure

Suppose migration partially succeeds and both source and destination run.

```text
SOURCE INSTANCE ACTIVE
DESTINATION INSTANCE ACTIVE
```

If only one active instance is permitted, execution identity has branched unexpectedly.

This is a split-brain condition.

Binding integrity becomes degraded because:

```text
ACTIVE-SERVICE-INSTANCE
```

may refer to two targets.

---

## 42. Split-Brain Identity

In split-brain operation:

* both runtimes may possess valid lineage;
* both may present the same service identity;
* both may accept actions;
* states may diverge.

The service identity is no longer uniquely bound to one active execution.

This creates:

```text
Service Identity Collision
```

---

## 43. Reconciliation After Split-Brain

Reconciliation may:

* select one branch;
* merge state;
* discard one branch;
* preserve both as historical lineages;
* create a new authoritative state.

The surviving service identity is established operationally.

The discarded branch remains historically real.

---

## 44. Merge Test

Suppose divergent branches produce states:

```text
S-300A
S-300B
```

A reconciliation process merges them into:

```text
S-301M
```

The merged state has lineage from both.

It is not identical to either prior branch state.

Therefore:

```text
Merged State
        =
New State With Multiple Lineages
```

The service may remain continuous through institutional reconciliation.

---

## 45. Runtime Identity and Authority

A runtime may technically execute the service code without being authorized to represent the service.

Therefore:

```text
Executable Capability
        ≠
Authorized Service Identity
```

Authority binding is part of service identity.

An unauthorized clone may be behaviourally identical while remaining institutionally distinct.

---

## 46. Runtime Identity and Provenance

A valid runtime identity may require:

* deployment record;
* source version;
* environment provenance;
* start event;
* host binding;
* authority;
* state source;
* execution lineage.

Without provenance, the runtime may be operationally visible but institutionally untrusted.

---

## 47. Identity Claim Matrix

| Claim                   | Minimum Evidence                               |
| ----------------------- | ---------------------------------------------- |
| Same service name       | Stable label or route                          |
| Same logical service    | Function, authority, succession                |
| Same runtime instance   | Instance continuity or validated migration     |
| Same OS process         | Host-scoped PID and uninterrupted process life |
| Same execution          | Continuous or formally bridged execution trace |
| Same state              | Verified state equivalence                     |
| Same state lineage      | Valid derivation or restoration history        |
| Same authorized primary | Authority assignment and unique active binding |
| Same process history    | Complete event lineage                         |
| Same numerical entity   | Not established by software continuity alone   |

---

## 48. Continuity Dimensions

The operational test identifies at least seven continuity dimensions:

```text
Service Continuity
Runtime-Instance Continuity
Execution Continuity
State Continuity
State-Lineage Continuity
Availability Continuity
Authority Continuity
```

These dimensions can diverge.

A binary field such as:

```text
same_process = true
```

would conceal important distinctions.

---

## 49. Continuity Status Vocabulary

Candidate statuses include:

```text
CONTINUOUS
MIGRATED
RESTARTED
RESTORED
SUCCEEDED
CLONED
BRANCHED
MERGED
REPLACED
REVIVED
TERMINATED
UNVERIFIED
UNKNOWN
```

Each status should specify the identity layer.

Example:

```text
service_identity: CONTINUOUS
runtime_identity: REPLACED
execution_identity: TERMINATED
state_lineage: RESTORED
```

---

## 50. Binding Integrity Test

A process identity claim requires binding between:

* logical service;
* runtime instance;
* execution;
* state;
* host;
* address;
* authority;
* event history.

The binding must be temporally scoped.

For example:

```text
SERVICE-A
    ↓ active_runtime
INSTANCE-004
    ↓ executes_on
HOST-02
    ↓ carries_state
S-210
    ↓ authorized_as
PRIMARY
```

---

## 51. False Continuity Risks

False continuity may arise from:

* PID reuse;
* address reuse;
* service-name reuse;
* instance-label reuse;
* stale registry records;
* hidden process replacement;
* snapshot restoration presented as uninterrupted execution;
* clone presented as original;
* primary-role collision;
* missing migration events.

---

## 52. False Discontinuity Risks

The opposite error is also possible.

A system may treat a migrated runtime as a new unrelated process even when:

* execution was formally transferred;
* state remained continuous;
* no branch occurred;
* authority remained preserved.

Therefore:

```text
Changed Host or PID
        ≠
Necessary Identity Loss
```

---

## 53. Candidate Finding

The following candidate finding is admitted for review:

> Software continuity is layered. Service identity can persist across runtime replacement, restart, migration, address change, and complete component turnover, while runtime-instance, execution, state, availability, and authority continuity may independently persist, terminate, branch, or transfer. A valid identity claim must declare its layer and preserve the corresponding transition evidence.

This remains provisional.

---

## 54. Effect on RM-000001

ROB-000010 operationally supports several elements of RM-000001 Version 0.3:

* distinguishability among identity layers;
* temporal binding;
* identifier reuse;
* false continuity;
* lineage;
* branching;
* merging;
* authority binding;
* consequence-specific thresholds.

It provides concrete pressure for adding:

* continuity as a separate threshold;
* layered continuity statuses;
* process identity;
* service identity;
* state lineage;
* event lineage;
* succession;
* restoration;
* cloning;
* split-brain conflict.

The model should remain unchanged until formal review.

---

## 55. Research Status

**Candidate Structure:** Layered Process Continuity
**Current Assessment:** PLAUSIBLE
**Service Identity Across Restart:** SUPPORTED
**Runtime Identity Across Restart:** NOT PRESERVED UNDER STRICT CRITERION
**Runtime Identity Across Validated Live Migration:** CONDITIONALLY SUPPORTED
**Execution Continuity Across Restart:** NOT PRESERVED
**State Lineage Across Restore:** SUPPORTED WHEN VERIFIED
**Clone Identity:** DISTINCT
**Branching:** SUPPORTED
**Merging:** MULTIPLE LINEAGES
**Identifier Reuse Risk:** SUPPORTED
**Continuity Threshold:** OPERATIONALLY SUPPORTED
**Irreducibility Status:** UNKNOWN
**Review Status:** NOT REVIEWED

---

## 56. Evidence Supporting the Observation

The observation uses concrete operational cases involving:

* address change;
* PID scope and reuse;
* in-place restart;
* warm restart;
* cold restart;
* live migration;
* stop-and-restore migration;
* snapshots;
* restoration;
* cloning;
* failover;
* split-brain operation;
* state merge;
* complete component replacement;
* service revival.

The cases are operationally grounded but not yet executed as an experimental software harness.

---

## 57. Evidence Limitations

This observation does not establish that:

* all software platforms use the same identity semantics;
* live migration always preserves execution identity;
* restored state is always correct;
* service identity is independent of implementation;
* authority continuity is always necessary;
* snapshot lineage is sufficient for accountability;
* process identity is irreducible;
* numerical identity has a single technical meaning.

Executable testing and cross-platform comparison remain required.

---

## 58. Next Required Review

Review should examine:

* whether live migration genuinely preserves runtime identity;
* whether restart always terminates execution identity;
* whether service identity is institutional rather than technical;
* whether state restoration creates succession or continuation;
* whether process identity is reducible to event lineage;
* whether availability continuity affects service identity;
* whether split-brain creates two service identities or one conflicted service identity;
* whether a fourth continuity threshold should be added to RM-000001.

---

## 59. Operational Conclusion

The concrete software test demonstrates that “same process” is too ambiguous for reliable analysis.

A software system may preserve one identity layer while replacing another.

The correct structure is:

```text
Logical Service
        ↓ instantiated as
Runtime Instance
        ↓ performs
Execution
        ↓ carries
State
        ↓ produces
Event Lineage
```

Each layer possesses separate continuity conditions.

The correct status remains:

```text
OBSERVED
SERVICE IDENTITY LAYERED
RESTART BREAKS EXECUTION CONTINUITY
VALIDATED MIGRATION MAY PRESERVE RUNTIME CONTINUITY
STATE RESTORATION PRESERVES LINEAGE, NOT UNINTERRUPTED EXECUTION
CLONING CREATES DISTINCT RUNTIMES
BRANCHING AND SPLIT-BRAIN REQUIRE CONFLICT HANDLING
UNKNOWN → HOLD
```

---

End of ROB-000010
