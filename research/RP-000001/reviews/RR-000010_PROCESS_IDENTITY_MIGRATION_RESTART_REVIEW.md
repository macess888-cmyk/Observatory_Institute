# RR-000010

# Research Review of Process Identity Across Migration and Restart

**Research Program:** RP-000001 — Organized Understanding
**Research Question:** RQ-000001 — Irreducible Structures of Organized Understanding
**Reviewed Observation:** ROB-000010 — Process Identity Across Migration and Restart
**Related Model:** RM-000001 — Minimum Distinguishability, Identity, and Binding Integrity Model, Version 0.3
**Artifact Type:** Research Review
**Version:** 0.1
**Status:** REVIEWED
**Date:** 2026-07-14

---

## 1. Review Purpose

This review evaluates whether ROB-000010 successfully demonstrates that software identity is layered and that separate continuity conditions apply to:

* logical service;
* runtime instance;
* operating-system process;
* execution;
* state;
* state lineage;
* availability;
* authority;
* event history.

The review also determines whether continuity now warrants formal inclusion as a fourth threshold in RM-000001.

---

## 2. Review Scope

The review examines:

* address change;
* process-identifier reuse;
* restart;
* live migration;
* stop-and-restore migration;
* snapshots;
* state restoration;
* cloning;
* failover;
* split-brain operation;
* branching;
* merging;
* service succession;
* authority transfer;
* continuity evidence;
* identity-layer separation.

---

## 3. Summary of the Observation

ROB-000010 begins with a running service represented through multiple identity layers:

```text
Service Identity: SERVICE-A
Runtime Instance: INSTANCE-001
Process ID: 4102
Host: HOST-01
Address: 10.0.0.12
State Version: S-100
```

The observation tests what remains continuous when these elements change independently.

Its central finding is:

> Software continuity is layered. Service identity can persist while runtime-instance identity, execution identity, state continuity, availability, authority, and host bindings independently persist, terminate, transfer, branch, or merge.

---

## 4. Observation Quality

ROB-000010 provides a concrete operational test rather than a purely abstract identity example.

It applies the prior model to:

* scoped identifiers;
* runtime events;
* state transitions;
* process replacement;
* failover;
* restoration;
* branching;
* conflict.

The examples are sufficiently structured to pressure-test RM-000001.

### Determination

**OBSERVATION QUALITY: SUPPORTED**

---

## 5. Is Software Identity Layered?

Yes.

The observation correctly separates:

```text
Service Identity
Runtime-Instance Identity
Operating-System Process Identity
Execution Identity
State Identity
State-Lineage Identity
Availability Continuity
Authority Continuity
```

These structures can change independently.

For example, a service may remain continuously available while every runtime instance is replaced.

### Determination

**LAYERED SOFTWARE IDENTITY: SUPPORTED**

---

## 6. Service Identity

Service identity concerns the logical capability recognized as the continuing service.

It may depend on:

* function;
* interface;
* institutional designation;
* authority;
* accepted succession;
* deployment history;
* state lineage;
* user-facing continuity.

Service identity is not reducible to one operating-system process.

### Determination

**SERVICE IDENTITY: DISTINCT AND SUPPORTED**

---

## 7. Runtime-Instance Identity

Runtime-instance identity concerns one instantiated deployment.

A strict runtime-instance criterion may begin at creation and end at termination.

It may survive:

* address changes;
* resource changes;
* host migration;

where a formally validated migration bridge preserves the same instantiated runtime.

It usually does not survive ordinary termination and recreation.

### Determination

**RUNTIME-INSTANCE IDENTITY: DISTINCT**

---

## 8. Operating-System Process Identity

An operating-system process identifier is scoped by:

* host;
* operating-system environment;
* process lifetime;
* time.

The same PID can later identify a different process.

Therefore:

```text
Same PID
        ≠
Same Process
```

### Determination

**PID ALONE: INSUFFICIENT FOR PROCESS CONTINUITY**

---

## 9. Execution Identity

Execution identity concerns one continuous or formally bridged run.

It can persist through:

* network-address change;
* resource reallocation;
* pause and resume;
* validated migration.

It terminates through:

* ordinary process termination;
* unbridged recreation;
* restart;
* branching into parallel executions.

### Determination

**EXECUTION IDENTITY: DISTINCT AND TEMPORALLY BOUNDED**

---

## 10. Address-Change Test

ROB-000010 correctly concludes that a network-address change does not necessarily alter:

* service identity;
* runtime identity;
* execution identity;
* state lineage.

The address is a reachability binding, not the full identity of the service or process.

### Determination

**ADDRESS CHANGE DOES NOT NECESSARILY BREAK PROCESS CONTINUITY**

---

## 11. Restart Test

An ordinary restart terminates the current execution and creates a new execution.

It may preserve:

* service identity;
* administrative role;
* state lineage;
* functional continuity;
* host identity.

It does not preserve uninterrupted execution.

Therefore:

```text
Restart
        =
Execution Discontinuity
```

### Determination

**EXECUTION CONTINUITY ACROSS RESTART: NOT PRESERVED**

---

## 12. Does Restart Preserve Runtime Identity?

Under a strict instance criterion, no.

A terminated runtime and newly created runtime are separate instances even when they share:

* service name;
* host;
* configuration;
* state;
* interface.

A platform may conventionally reuse an instance label, but label reuse does not prove instance continuity.

### Determination

**RUNTIME IDENTITY ACROSS RESTART: NOT PRESERVED UNDER STRICT CRITERION**

---

## 13. Service Identity Across Restart

The service may remain the same logical service after restart where:

* succession is authorized;
* role and function remain stable;
* the restart belongs to the same deployment lineage;
* no competing service identity exists.

### Determination

**SERVICE IDENTITY ACROSS RESTART: SUPPORTED**

---

## 14. Warm Restart

A warm restart can preserve state lineage through restoration of the latest state.

It does not preserve uninterrupted execution.

```text
State Lineage Preserved
        ≠
Execution Continuity Preserved
```

### Determination

**WARM RESTART: STATE SUCCESSION, NOT EXECUTION CONTINUITY**

---

## 15. Cold Restart

A cold restart may preserve service identity while losing prior operational state.

This confirms that:

```text
Service Continuity
        ≠
State Continuity
```

### Determination

**SUPPORTED**

---

## 16. Live Migration

A validated live migration may preserve runtime and execution identity when:

* one execution is transferred rather than duplicated;
* source and destination are linked by a migration event;
* state sequence remains continuous;
* simultaneous active copies are excluded;
* authority remains bound;
* the migration record is complete.

### Determination

**RUNTIME CONTINUITY ACROSS VALIDATED LIVE MIGRATION: CONDITIONALLY SUPPORTED**

---

## 17. Migration Evidence

A migration claim should preserve:

* source runtime;
* destination runtime;
* migration transaction;
* state-transfer evidence;
* pause and resume sequence;
* source termination or deactivation;
* authority continuity;
* absence of unrecorded branching.

Without this evidence, apparent migration may be termination and recreation.

### Determination

**MIGRATION BRIDGE: REQUIRED**

---

## 18. Stop-and-Restore Migration

Stopping one runtime and restoring its state into another creates:

* a new execution;
* a new runtime instance;
* preserved or inherited state lineage;
* continued service identity, where succession is recognized.

It does not preserve uninterrupted execution.

### Determination

**STOP-AND-RESTORE: SUCCESSION, NOT LIVE EXECUTION CONTINUITY**

---

## 19. Snapshot Identity

A snapshot has its own artifact identity.

It preserves a representation of state.

It is not:

* the running runtime;
* active execution;
* the service itself.

### Determination

**SNAPSHOT IDENTITY ≠ RUNTIME IDENTITY**

---

## 20. Restoration From Snapshot

Restoration creates a new execution derived from the saved state.

This supports:

* state lineage;
* service succession;
* historical derivation.

It does not support:

* uninterrupted execution;
* original runtime-instance continuity.

### Determination

**STATE LINEAGE ACROSS VERIFIED RESTORATION: SUPPORTED**

---

## 21. Branching Through Restoration

If the original execution continues after a snapshot while another runtime restores the same snapshot, two lineages emerge.

```text
Shared State Ancestor
        ↓
Two Distinct Executions
```

The branches share lineage but not numerical runtime identity.

### Determination

**BRANCHING: SUPPORTED**

---

## 22. Clone Identity

Two clones restored from the same snapshot may begin in equivalent states.

They remain distinct because:

* they execute independently;
* they occupy separate runtime positions;
* they produce separate events;
* their state histories can diverge.

### Determination

**CLONE IDENTITIES: DISTINCT**

---

## 23. State Equivalence

Equivalent state does not establish equivalent process identity.

```text
Same State
        ≠
Same Execution
```

State equality is one dimension of continuity, not a complete identity proof.

### Determination

**SUPPORTED**

---

## 24. Failover

Failover can preserve:

* service identity;
* availability;
* active role;
* authority;
* state lineage, where replication is current.

It replaces:

* active runtime;
* operating-system process;
* host binding.

### Determination

**SERVICE CONTINUITY THROUGH FAILOVER: SUPPORTED**

---

## 25. Availability Continuity

A service may remain continuously available while its runtime processes change.

Therefore:

```text
Availability Continuity
        ≠
Runtime Continuity
```

### Determination

**SUPPORTED**

---

## 26. Process Continuity Without Availability

A process may remain alive while network reachability fails.

Therefore:

```text
Runtime Continuity
        ≠
Availability Continuity
```

### Determination

**SUPPORTED**

---

## 27. Failover With State Lag

Failover to a stale replica can preserve service availability while degrading state continuity.

The same service identity may therefore contain a discontinuity in recent state history.

### Determination

**AVAILABILITY DOES NOT PROVE COMPLETE STATE CONTINUITY**

---

## 28. Primary Role Identity

`PRIMARY` is a role identity.

It may transfer between runtimes.

```text
Role Continuity
        ≠
Runtime-Instance Continuity
```

The role remains institutionally continuous while the occupant changes.

### Determination

**SUPPORTED**

---

## 29. Authority Continuity

A runtime may execute technically valid code without authority to represent the service.

Therefore:

```text
Execution Capability
        ≠
Authorized Service Identity
```

Authority is a separate binding dimension.

### Determination

**AUTHORITY CONTINUITY: DISTINCT AND REQUIRED FOR GOVERNED SERVICE IDENTITY**

---

## 30. Split-Brain Operation

Split-brain occurs when more than one runtime claims the same exclusive active role.

Possible consequences include:

* duplicate authority;
* conflicting writes;
* state divergence;
* identity collision;
* ambiguous controlling runtime.

### Determination

**SPLIT-BRAIN: SERVICE-BINDING CONFLICT SUPPORTED**

---

## 31. Does Split-Brain Create Two Service Identities?

Not necessarily.

It may create:

* one service identity bound inconsistently to two active runtimes;
* two competing service continuations;
* two branches sharing one prior service lineage.

The correct classification depends on the service’s identity and authority rules.

### Determination

**SPLIT-BRAIN IDENTITY: CONFLICTED AND BRANCHED**

---

## 32. Merging Divergent States

A merged state derived from two branches possesses multiple lineages.

It is not identical to either prior branch state.

The logical service may continue through an institutionally accepted reconciliation.

### Determination

**MERGING PRESERVES MULTIPLE LINEAGES AND CREATES A NEW STATE**

---

## 33. Complete Component Replacement

A service can preserve higher-level identity while replacing:

* hosts;
* processes;
* containers;
* addresses;
* code versions;
* storage;
* operators.

This supports the earlier finding that component identity is not universally required for higher-level identity.

### Determination

**HIGHER-LEVEL IDENTITY ACROSS COMPLETE COMPONENT REPLACEMENT: CONDITIONALLY SUPPORTED**

---

## 34. Service Identity as Institutional Identity

Service identity depends partly on institutional structures:

* naming;
* authority;
* ownership;
* succession rules;
* accepted deployment lineage;
* interface commitments.

It is therefore not purely technical.

### Determination

**SERVICE IDENTITY: PARTLY INSTITUTIONAL**

---

## 35. Service Identity as Process Identity

A service may also be viewed as a continuing process composed of successive runtime instances.

This process persists through authorized succession rather than one uninterrupted execution.

### Determination

**SERVICE IDENTITY: PROCESS-LIKE AT THE LOGICAL LEVEL**

---

## 36. Process Identity Versus Event Lineage

Event lineage records:

* start;
* migration;
* restart;
* restore;
* promotion;
* termination;
* branch;
* merge.

Process identity may be reconstructed from this lineage.

However, lineage alone does not decide which identity criterion should govern every claim.

### Determination

**PROCESS IDENTITY DEPENDS STRONGLY ON EVENT LINEAGE BUT IS NOT REDUCED TO IT YET**

---

## 37. Identifier Reuse

ROB-000010 provides concrete support for earlier concerns about:

* PID reuse;
* address reuse;
* service-name reuse;
* instance-label reuse.

Temporal scope and binding history are required.

### Determination

**IDENTIFIER REUSE RISK: SUPPORTED**

---

## 38. False Continuity

False continuity can occur when a stable label conceals:

* restart;
* replacement;
* restoration;
* branch creation;
* authority transfer;
* process termination.

### Determination

**FALSE CONTINUITY RISK: OPERATIONALLY SUPPORTED**

---

## 39. False Discontinuity

False discontinuity can occur when a changed host, PID, or address is treated as proof of new identity despite a validated migration bridge.

### Determination

**FALSE DISCONTINUITY RISK: SUPPORTED**

---

## 40. Continuity as a Separate Structure

ROB-000009 conceptually distinguished continuity from binding integrity.

ROB-000010 operationally confirms the distinction.

### Continuity asks:

> How are target states connected across time?

### Binding integrity asks:

> Does the reference or claim remain correctly associated with the intended target?

A binding may be valid while continuity is broken.

A target may remain continuous while its binding is incorrect.

### Determination

**CONTINUITY AND BINDING INTEGRITY: DISTINCT**

---

## 41. Is Continuity Reducible to Identity?

Not fully established.

Identity claims require continuity in many temporal operations.

However, continuity is independently inspectable through:

* event lineage;
* transition evidence;
* state succession;
* migration bridges;
* branch records;
* merge records.

### Determination

**CONTINUITY: NOT YET REDUCED TO IDENTITY**

---

## 42. Is Continuity Reducible to Binding Integrity?

No.

Binding integrity can preserve the correct current reference while the target’s prior execution has terminated.

Example:

```text
SERVICE-A correctly bound to INSTANCE-002
```

does not imply that `INSTANCE-002` is continuous with `INSTANCE-001`.

### Determination

**CONTINUITY ≠ BINDING INTEGRITY**

---

## 43. Fourth Threshold Proposal

RM-000001 currently uses:

```text
D = distinguishability
I = identity
B = binding integrity
```

The accumulated evidence supports adding:

```text
C = continuity evidence
```

with threshold:

```text
T꜀(operation, level, scale, context, time, consequence)
```

An operation requiring temporal persistence is admissible only when:

```text
C ≥ T꜀
```

### Determination

**FOURTH CONTINUITY THRESHOLD: WARRANTED**

---

## 44. Continuity Threshold Meaning

The continuity threshold concerns whether sufficient evidence connects the relevant target across states.

It may require:

* valid event lineage;
* transition trace;
* migration bridge;
* state derivation;
* branch visibility;
* merge history;
* observer-gap evidence;
* succession rules.

---

## 45. Operations With Low Continuity Requirements

Some operations require little or no continuity evidence.

Examples:

* count current instances;
* inspect current health;
* route to any healthy replica;
* verify present availability;
* recognize current pattern.

### Determination

**CONTINUITY REQUIREMENT: OPERATION-DEPENDENT**

---

## 46. Operations With High Continuity Requirements

High continuity may be required for:

* historical attribution;
* recurrence detection;
* accountability;
* stateful correction;
* rollback;
* audit;
* ownership;
* provenance;
* irreversible action.

### Determination

**SUPPORTED**

---

## 47. Layer-Specific Continuity

Continuity must be declared by layer.

Examples:

```text
service_continuity
runtime_continuity
execution_continuity
state_continuity
authority_continuity
availability_continuity
```

A general field such as:

```text
continuous = true
```

is insufficient.

### Determination

**LAYER-SPECIFIC CONTINUITY: REQUIRED**

---

## 48. Continuity Status Vocabulary

The observation supports statuses such as:

```text
CONTINUOUS
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
UNVERIFIED
UNKNOWN
```

Status should be attached to a declared identity layer.

### Determination

**EXPLICIT CONTINUITY STATUS: SUPPORTED**

---

## 49. Model Impact

ROB-000010 supplies the concrete operational evidence requested by RR-000009.

The evidence base now supports model revision.

The revised model should include:

* continuity as a fourth threshold;
* layered continuity;
* service identity;
* runtime identity;
* execution identity;
* state identity;
* state lineage;
* authority continuity;
* availability continuity;
* event lineage;
* migration;
* restart;
* restoration;
* succession;
* branching;
* merging.

### Determination

**MODEL REVISION: WARRANTED**

---

## 50. Proposed Model Version

Recommended revision:

```text
RM-000001 Version 0.4
Minimum Distinguishability, Identity, Binding Integrity, and Continuity Model
```

The model should preserve all prior version history.

---

## 51. Evidentiary Sufficiency

ROB-000010 is operationally concrete and internally coherent.

It does not yet include an executable test harness, but it moves beyond abstract analogy by using actual software lifecycle semantics.

### Determination

**ASSESSMENT: PARTIALLY SUPPORTED**

---

## 52. Evidence Limitations

The review does not establish that:

* all platforms define migration identically;
* live migration always preserves execution identity;
* service identity has one universal definition;
* state restoration always preserves valid lineage;
* event logs are complete;
* process identity is irreducible;
* continuity can be measured numerically without domain-specific rules.

---

## 53. Counterexamples and Future Tests

Future evidence should include:

### Executable Migration Harness

Record state before and after controlled migration.

### Restart Trace

Verify that state lineage survives while execution identity changes.

### PID-Reuse Test

Demonstrate false continuity from host-scoped identifier reuse.

### Clone Test

Create two runtimes from one snapshot and observe divergence.

### Split-Brain Test

Allow two primaries and inspect identity collision.

### Merge Test

Reconcile divergent states and preserve multiple lineage.

---

## 54. Review Outcome

The review outcome is:

```text
OBSERVATION QUALITY: SUPPORTED
LAYERED SOFTWARE IDENTITY: SUPPORTED
SERVICE IDENTITY: DISTINCT
RUNTIME-INSTANCE IDENTITY: DISTINCT
EXECUTION IDENTITY: DISTINCT
STATE IDENTITY: DISTINCT
STATE LINEAGE: DISTINCT
AVAILABILITY CONTINUITY: DISTINCT
AUTHORITY CONTINUITY: DISTINCT
RESTART BREAKS EXECUTION CONTINUITY
SERVICE IDENTITY MAY SURVIVE RESTART
VALIDATED MIGRATION MAY PRESERVE RUNTIME CONTINUITY
RESTORATION PRESERVES LINEAGE, NOT UNINTERRUPTED EXECUTION
CLONES ARE DISTINCT
BRANCHING: SUPPORTED
MERGING: MULTIPLE LINEAGES
SPLIT-BRAIN: IDENTITY AND AUTHORITY CONFLICT
CONTINUITY ≠ IDENTITY
CONTINUITY ≠ BINDING INTEGRITY
FOURTH CONTINUITY THRESHOLD: WARRANTED
MODEL REVISION: WARRANTED
IRREDUCIBILITY: NOT ESTABLISHED
```

---

## 55. Formal Status Determination

**Review Status:** COMPLETED
**Observation Status:** RETAINED
**Assessment:** PARTIALLY SUPPORTED
**Layered Process Identity:** SUPPORTED
**Service Identity Across Restart:** SUPPORTED
**Runtime Identity Across Restart:** NOT PRESERVED UNDER STRICT CRITERION
**Execution Continuity Across Restart:** NOT PRESERVED
**Runtime Continuity Across Validated Migration:** CONDITIONALLY SUPPORTED
**State Lineage Across Restore:** SUPPORTED WHEN VERIFIED
**Clone Identity:** DISTINCT
**Branching:** SUPPORTED
**Merging:** MULTIPLE LINEAGES SUPPORTED
**Split-Brain:** IDENTITY COLLISION AND AUTHORITY CONFLICT
**Continuity Threshold:** WARRANTED
**Model Impact:** REVISION WARRANTED
**Irreducibility Status:** UNKNOWN

---

## 56. Required Model Revision

RM-000001 Version 0.4 should add:

```text
D = distinguishability
I = identity
B = binding integrity
C = continuity
```

with operation-specific thresholds:

```text
D ≥ Tᴅ
I ≥ Tᵢ
B ≥ Tᵦ
C ≥ T꜀
```

The model should specify that continuity thresholds apply only where an operation depends on persistence across time or transformation.

---

## 57. Next Required Artifact

The next artifact should revise the model:

```text
RM-000001 Version 0.4
Minimum Distinguishability, Identity, Binding Integrity, and Continuity Model
```

The revision basis should include:

```text
ROB-000008
ROB-000009
ROB-000010
RR-000008
RR-000009
RR-000010
```

---

## 58. Review Conclusion

ROB-000010 demonstrates that software identity cannot be represented reliably through one identifier or one continuity claim.

A service may remain the same logical service while:

* runtime instances are replaced;
* executions terminate;
* state is restored;
* hosts change;
* authority transfers;
* branches emerge;
* lineages merge.

Continuity is therefore a distinct research structure.

It connects target states across time and transformation, while binding integrity connects references and claims to targets.

The evidence now warrants adding continuity as a fourth threshold within RM-000001.

The correct posture remains:

```text
RETAIN
PARTIALLY SUPPORT
SEPARATE IDENTITY LAYERS
SEPARATE SERVICE FROM RUNTIME
SEPARATE STATE LINEAGE FROM EXECUTION
PRESERVE BRANCHING AND MERGING
ADD CONTINUITY THRESHOLD
REVISE THE MODEL
UNKNOWN → HOLD
```

---

End of RR-000010
