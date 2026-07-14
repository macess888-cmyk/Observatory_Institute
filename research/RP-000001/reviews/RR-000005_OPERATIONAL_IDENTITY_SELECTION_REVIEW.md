# RR-000005

# Research Review of Operational Identity Created Through Selection

**Research Program:** RP-000001 — Organized Understanding
**Research Question:** RQ-000001 — Irreducible Structures of Organized Understanding
**Reviewed Observation:** ROB-000005 — Operational Identity Created Through Selection
**Related Model:** RM-000001 — Minimum Distinguishability and Identity Threshold Model, Version 0.2
**Artifact Type:** Research Review
**Version:** 0.1
**Status:** REVIEWED
**Date:** 2026-07-14

---

## 1. Review Purpose

This review evaluates whether selection creates sufficient operational identity for correction, continuity, audit, and verification.

It examines whether selection:

* creates identity or only reference;
* produces a valid target;
* preserves target binding;
* supports immediate correction;
* supports persistent continuity;
* supports accountability;
* supports member-specific verification;
* requires explicit expiration;
* changes RM-000001 Version 0.2.

---

## 2. Review Scope

The review examines:

* symmetry breaking through selection;
* temporary operational identity;
* target binding;
* position-bound and occupant-bound selection;
* label and reference continuity;
* target exchange and replacement;
* audit requirements;
* post-action verification;
* authority and accountability boundaries;
* operation-specific identity thresholds.

---

## 3. Summary of the Observation

ROB-000005 begins with structurally equivalent members:

```text
? ↔ ?
```

Selection creates:

```text
[selected] ↔ [unselected]
```

The observation concludes that selection creates temporary operational asymmetry and immediate targetability.

It also concludes that selection alone does not establish:

* persistent identity;
* historical continuity;
* auditability;
* accountability;
* post-action reidentification;
* proof that the intended member received the verified result.

Its central candidate finding is:

> Selection can create sufficient temporary operational identity for some immediate actions, but correction continuity, auditability, accountability, and member-specific verification require preserved target binding beyond the selection event.

---

## 4. Does Selection Break Symmetry?

Yes.

Before selection, equivalent members share the same operational status.

After selection:

```text
selected member
        ≠
unselected member
```

The selection event introduces a difference relevant to the current operation.

This difference may support:

* targeting;
* intervention;
* isolation;
* measurement;
* comparison;
* immediate verification.

### Determination

**OPERATIONAL SYMMETRY BREAKING: SUPPORTED**

---

## 5. Does Selection Create Identity or Reference?

The observation supports two compatible interpretations.

### Identity-Creation Interpretation

Selection creates a new operational identity:

```text
the selected target
```

This identity did not exist as a unique operational category before selection.

### Reference-Creation Interpretation

Selection creates a reference to one already existing member.

The target existed before selection, but selection made it operationally addressable.

The evidence does not determine which interpretation is ontologically primary.

For operational purposes, both interpretations produce a distinguishable target.

### Determination

**OPERATIONAL TARGET IDENTITY: CREATED OR ACTIVATED**

**ONTOLOGICAL IDENTITY CREATION: UNKNOWN**

---

## 6. Identity Versus Reference

A reference may point to a target without preserving the target’s identity.

Examples include:

* a memory address;
* a process handle;
* a role name;
* a screen coordinate;
* a temporary label;
* a network endpoint.

These references may remain stable while the underlying occupant changes.

Therefore:

```text
Reference Stability
        ≠
Target Stability
```

A valid operational identity requires more than a reference token.

It requires evidence that the reference remains correctly bound.

### Determination

**SUPPORTED**

---

## 7. Target Binding

Target binding is the maintained association between:

* the selection record;
* the reference;
* the intended target;
* the action;
* the resulting state.

A provisional chain is:

```text
Selection
    ↓
Reference
    ↓
Target Binding
    ↓
Action
    ↓
Result
    ↓
Reidentification
```

If the binding breaks at any point, a later claim about the target becomes uncertain.

### Determination

**TARGET BINDING IS REQUIRED FOR MEMBER-SPECIFIC CLAIMS**

---

## 8. What Preserves Binding?

Candidate binding mechanisms include:

* persistent identifiers;
* immutable selection records;
* physical continuity;
* cryptographic references;
* stable object handles;
* chain of custody;
* controlled locks;
* versioned state transitions;
* trusted observation;
* verified event linkage.

No mechanism is universally sufficient.

Each mechanism has possible failure modes.

For example:

```text
Persistent Identifier Exists
        ≠
Identifier Still Refers to Same Target
```

### Determination

**BINDING REQUIRES BOTH REFERENCE AND CONTINUITY EVIDENCE**

---

## 9. Position-Bound Selection

Position-bound selection targets a location or role.

Example:

```text
correct the object occupying position P
```

This may be valid when the operation concerns the position rather than the occupant.

It becomes unsafe when:

* occupants can exchange;
* replacement can occur;
* responsibility belongs to a person or object;
* prior history matters;
* the intended target moves.

### Determination

**POSITION-BOUND TARGETING: VALID FOR POSITION-SPECIFIC OPERATIONS**

**OCCUPANT-SPECIFIC CLAIMS: NOT SUPPORTED WITHOUT ADDITIONAL EVIDENCE**

---

## 10. Occupant-Bound Selection

Occupant-bound selection follows the selected member across movement or role change.

This requires continuity evidence that survives:

* position exchange;
* migration;
* replacement;
* relabeling;
* process restart;
* address change.

Occupant-bound selection supports stronger claims but requires stronger identity.

### Determination

**OCCUPANT-BOUND TARGETING: REQUIRES PERSISTENT OR CONTINUOUS IDENTITY**

---

## 11. Target Exchange Review

ROB-000005 correctly identifies target exchange as a central pressure test.

If selection attaches to a position while occupants exchange, intervention may reach the wrong occupant.

Therefore:

```text
Selected Position Preserved
        ≠
Selected Occupant Preserved
```

A selection record must state whether its target semantics are:

* positional;
* occupant-based;
* role-based;
* state-based;
* event-based;
* record-based.

### Determination

**TARGET SEMANTICS MUST BE EXPLICIT**

---

## 12. Replacement Review

A target may be replaced while preserving:

* role;
* address;
* name;
* location;
* process identifier;
* interface;
* pattern position.

This can create false continuity.

Therefore:

```text
Interface Continuity
        ≠
Entity Continuity
```

and:

```text
Role Continuity
        ≠
Occupant Continuity
```

### Determination

**SUPPORTED**

---

## 13. Label Persistence Review

A temporary label may support targeting while correctly bound.

It fails when:

* duplicated;
* transferred;
* reused;
* detached;
* corrupted;
* expired;
* assigned to a replacement.

The existence of a label proves only that a reference exists.

It does not prove binding validity.

### Determination

**LABELS ARE SUPPORTING MECHANISMS, NOT SELF-VALIDATING IDENTITY**

---

## 14. Immediate Correction

Temporary operational identity may be sufficient for immediate correction when:

* the target remains stable;
* the intervention window is short;
* the target semantics are explicit;
* exchange is prevented or detectable;
* the result can be checked before binding expires;
* persistent attribution is unnecessary.

Examples include:

* restarting any failed replica;
* removing a selected defective item;
* measuring a selected sample;
* adjusting a currently isolated process.

### Determination

**IMMEDIATE TARGETED CORRECTION: SUPPORTED UNDER CONTROLLED CONDITIONS**

---

## 15. Correction Continuity

Correction continuity requires the system to preserve the same target through:

```text
Selection
    ↓
Intervention
    ↓
Post-Action Observation
```

Without continuity, the system may prove only that:

* an action occurred;
* a result appeared;
* the system improved.

It may not prove that the selected member changed.

### Determination

**CORRECTION CONTINUITY REQUIRES PRESERVED TARGET BINDING**

---

## 16. System-Level Versus Member-Level Outcomes

The observation correctly distinguishes three outcomes.

### System-Level Outcome

The overall system improved.

### Class-Level Outcome

A valid member of the target class now satisfies the requirement.

### Member-Level Outcome

The exact selected member was changed and verified.

These claims require increasing identity strength.

```text
System-Level Claim
        <
Class-Level Claim
        <
Member-Level Claim
```

in identity requirements.

### Determination

**SUPPORTED**

---

## 17. Class-Level Verification

Class-level verification may be sufficient when:

* members are genuinely interchangeable;
* history does not matter;
* responsibility is irrelevant;
* the success condition concerns system capacity;
* replacement is acceptable.

Example:

```text
At least one healthy service instance is available.
```

This does not support:

```text
The selected instance was repaired.
```

### Determination

**CLASS-LEVEL VERIFICATION: VALID FOR CLASS-LEVEL CLAIMS**

---

## 18. Member-Specific Verification

Member-specific verification requires proof that:

* the post-action target is the selected target;
* no exchange or replacement occurred;
* the result belongs to that target;
* the observation occurred within the binding period;
* the verification method addressed the correct identity level.

### Determination

**REIDENTIFICATION REQUIRED**

---

## 19. Auditability

Auditability requires more than operational success.

A sufficient audit record should preserve:

* selection event;
* selector identity or process;
* selection time;
* target reference;
* binding method;
* target semantics;
* action;
* authority;
* resulting state;
* verification;
* binding expiration;
* exceptions or uncertainty.

### Determination

**SELECTION ALONE DOES NOT PROVIDE AUDITABILITY**

---

## 20. Immutable Record Boundary

An immutable record can preserve what was claimed.

It does not guarantee that the original claim was correct.

Therefore:

```text
Immutable Record
        ≠
Correct Target Binding
```

An immutable false binding remains false.

Immutability supports preservation, not truth.

### Determination

**SUPPORTED**

---

## 21. Can Temporary Identity Support Accountability?

Usually not by itself.

Accountability requires continuity between:

* actor;
* action;
* authority;
* consequence;
* evidence;
* review.

Temporary operational identity may support accountability only when the temporary binding is preserved into an attributable record.

Thus:

```text
Temporary Identity
        +
Preserved Attributable Binding
        =
Possible Accountability
```

Temporary identity without preserved attribution is insufficient.

### Determination

**ACCOUNTABILITY: CONDITIONALLY POSSIBLE, NOT PROVIDED BY SELECTION ALONE**

---

## 22. Authority Boundary

Selection does not establish authority.

```text
Target Identified
        ≠
Action Authorized
```

A complete intervention requires separate evidence of:

* target identity;
* actor authority;
* action admissibility;
* scope;
* timing;
* result verification.

### Determination

**SUPPORTED**

---

## 23. Consent Boundary

In human contexts:

```text
Selected
        ≠
Consented
```

Selection provides neither permission nor legitimacy.

The identity structure must remain separate from authority, consent, and governance.

### Determination

**SUPPORTED**

---

## 24. Expiration

Operational identity should be treated as time-bounded unless continuity is actively preserved.

Expiration may occur through:

* timeout;
* movement;
* replacement;
* role change;
* process restart;
* label loss;
* rebinding;
* evidence degradation;
* completion of the operation.

A valid selection record should include an expiration condition.

### Determination

**EXPLICIT EXPIRATION: WARRANTED**

---

## 25. Rebinding Review

Reference rebinding is a major continuity risk.

```text
TARGET-1 at t₁ = A
TARGET-1 at t₂ = B
```

If rebinding is not recorded, the reference may create a false appearance of identity continuity.

### Determination

**REFERENCE REUSE REQUIRES VERSIONED OR TEMPORALLY BOUNDED BINDING**

---

## 26. Observer Dependence

Selection may be created by:

* a human observer;
* a software controller;
* a measurement system;
* an institutional process;
* an automated policy.

The resulting operational identity depends on:

* selection rule;
* visibility;
* authority;
* accuracy;
* representation;
* timing.

Different observers may select different members from the same class.

This does not invalidate operational identity but makes its provenance important.

### Determination

**SELECTION IDENTITY IS OBSERVER- OR PROCESS-DEPENDENT**

---

## 27. Does Selection Reveal or Produce Asymmetry?

It can do either.

### Reveal

Selection identifies a difference that already existed but was not represented.

### Produce

Selection imposes a new difference by assigning target status.

The evidence does not always allow these cases to be separated.

A valid record should state whether selection was:

* discovery;
* classification;
* arbitrary choice;
* intervention preparation;
* policy assignment.

### Determination

**ASYMMETRY ORIGIN MUST REMAIN EXPLICIT WHERE POSSIBLE**

---

## 28. Identity Threshold Implications

ROB-000005 supports distinct thresholds.

### Immediate Action Threshold

May require:

* current target distinction;
* stable short-term binding;
* action scope;
* immediate verification.

### Audit Threshold

Additionally requires:

* preserved record;
* source identity;
* authority evidence;
* target semantics;
* continuity evidence.

### Accountability Threshold

Additionally requires:

* attributable actor;
* persistent identity;
* consequence linkage;
* reviewability.

### Determination

**OPERATION-SPECIFIC IDENTITY THRESHOLDS: FURTHER SUPPORTED**

---

## 29. Effect on RM-000001 Version 0.2

ROB-000005 supports the existing model’s distinctions among:

* class identity;
* operational identity;
* unique identity;
* persistent identity;
* source identity;
* temporal identity.

It adds pressure for explicit inclusion of:

* target binding;
* binding scope;
* attachment semantics;
* expiration;
* rebinding;
* verification identity;
* claim-level identity requirements.

The current model remains valid.

Immediate revision is not yet required.

### Determination

**MODEL RETAINED — FUTURE REFINEMENT WARRANTED**

---

## 30. Evidentiary Sufficiency

ROB-000005 provides a coherent conceptual test with operational examples.

Its strongest contribution is the separation of:

* selection;
* binding;
* action;
* verification;
* audit.

However, the evidence remains conceptual.

It has not yet been tested using:

* software execution traces;
* physical object tracking;
* institutional assignment records;
* controlled target-exchange experiments;
* adversarial rebinding cases.

### Determination

**ASSESSMENT: PARTIALLY SUPPORTED**

---

## 31. Counterexamples and Pressure Tests

Future research should test:

### Stable Lock

Does an exclusive lock provide sufficient target binding?

### Migrating Target

Can occupant identity survive position or address change?

### Duplicate Identifier

What happens when two targets share the same identifier?

### Immutable False Binding

Can a perfectly preserved record support a false target claim?

### Class-Level Success

When is system improvement sufficient without member verification?

### Delayed Verification

How long can operational identity remain valid after action?

### Authority Transfer

Can the target remain stable while authority changes?

### Observer Disagreement

What happens when two selectors identify different targets?

### Determination

**OPEN**

---

## 32. Review Outcome

The review outcome is:

```text
OBSERVATION QUALITY: SUPPORTED
SELECTION AS SYMMETRY BREAKING: SUPPORTED
IMMEDIATE TARGETABILITY: SUPPORTED
IDENTITY OR REFERENCE CREATION: OPERATIONALLY EQUIVALENT, ONTOLOGICALLY UNKNOWN
TARGET BINDING: REQUIRED
POSITION-BOUND TARGETING: CONDITIONALLY VALID
OCCUPANT-BOUND TARGETING: REQUIRES CONTINUITY
PERSISTENT IDENTITY: NOT CREATED BY SELECTION ALONE
AUDITABILITY: REQUIRES PRESERVED EVIDENCE
ACCOUNTABILITY: REQUIRES ATTRIBUTABLE CONTINUITY
MEMBER-SPECIFIC VERIFICATION: REQUIRES REIDENTIFICATION
EXPIRATION: WARRANTED
MODEL REVISION: NOT YET REQUIRED
IRREDUCIBILITY: NOT ESTABLISHED
```

---

## 33. Formal Status Determination

**Review Status:** COMPLETED
**Observation Status:** RETAINED
**Assessment:** PARTIALLY SUPPORTED
**Immediate Targetability:** SUPPORTED
**Operational Identity:** SUPPORTED
**Persistent Identity:** NOT ESTABLISHED
**Target Binding:** REQUIRED
**Auditability:** CONDITIONALLY SUPPORTED THROUGH PRESERVED EVIDENCE
**Accountability:** REQUIRES STRONGER IDENTITY
**Member-Specific Verification:** REQUIRES REIDENTIFICATION
**Expiration Requirement:** SUPPORTED
**Model Impact:** RETAIN AND CONTINUE TESTING
**Irreducibility Status:** UNKNOWN

---

## 34. Next Required Research

The next observation should pressure-test target binding directly.

Recommended question:

> Can an immutable selection record preserve valid identity when the original target binding was incorrect, incomplete, or later rebound?

Suggested artifact:

```text
ROB-000006
Immutable Records and False Target Continuity
```

This should test:

* immutable false claims;
* stale references;
* identifier reuse;
* target replacement;
* binding verification;
* evidence preservation versus truth.

A later observation should examine anchor regress and identity foundations.

---

## 35. Review Conclusion

ROB-000005 successfully demonstrates that selection can create or activate temporary operational identity sufficient for some immediate actions.

Selection does not alone provide persistent identity, auditability, accountability, or proof of member-specific correction.

The decisive structure is not selection alone but preserved target binding across:

```text
Selection
    ↓
Action
    ↓
Verification
    ↓
Review
```

Operational identity should be treated as scoped, time-bounded, and evidence-dependent.

The correct posture remains:

```text
RETAIN
PARTIALLY SUPPORT
PRESERVE TARGET BINDING
DECLARE ATTACHMENT SEMANTICS
REQUIRE EXPIRATION
SEPARATE ACTION SUCCESS FROM TARGET PROOF
UNKNOWN → HOLD
```

---

End of RR-000005
