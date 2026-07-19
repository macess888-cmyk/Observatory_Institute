# OBS-EE-001 — SOS70 RECONSTRUCTION TEST CONTRACT 001

**Card ID:** OBS-EE-001  
**System ID:** SOS70-TOMSK-001  
**Contract ID:** OBS-EE-001-RTC-001  
**Title:** SOS70 Display-Derived Reconstruction Test Contract  
**Project:** Observatory OS  
**Date:** 2026-07-19  
**Status:** TEST CONTRACT OPEN  
**Operating Posture:** TEST-FIRST / DETERMINISTIC / UNCERTAINTY-BOUND / COPYRIGHT-SAFE / REFUSAL-CAPABLE / UNKNOWN → HOLD

---

# 1. PURPOSE

This contract defines the first executable boundary for mathematically reconstructing SOS70 scientific visualizations.

The first authorized pilot is one weekly solar X-ray chart.

The contract freezes:

    input requirements
    asset identity requirements
    plot geometry
    temporal calibration
    logarithmic vertical calibration
    trace extraction
    event-label extraction
    bulletin validation
    uncertainty accounting
    deterministic outputs
    positive controls
    negative controls
    corruption tests
    acceptance thresholds
    refusal conditions
    reconstruction receipts

Implementation must not begin until this contract is frozen.

---

# 2. CONTRACT SCOPE

This contract authorizes only:

    one SOS70 weekly solar X-ray chart
    one corresponding bulletin event table
    one deterministic reconstruction execution
    one validation report
    controlled corruption variants
    one reconstruction receipt

This contract does not authorize:

    bulk archive extraction
    Schumann sonogram reconstruction
    ionogram reconstruction
    seasonal–diurnal heat-map reconstruction
    cross-domain correlation
    causal inference
    prediction
    public hazard communication
    redistribution of copyrighted source media

---

# 3. PILOT OBJECT CLASS

    Product family:
    SOS70_SOLAR_XRAY_WEEKLY_2026

    Object class:
    PROCESSED EXTERNAL SOLAR X-RAY OBSERVATION

    Display type:
    seven-day line chart

    Horizontal variable:
    local date and time

    Vertical variable:
    logarithmic solar X-ray flux class

    Source time zone:
    Tomsk decree time
    UTC+7

    Display classes:
    A
    B
    C
    M
    X
    X10

    Validation source:
    corresponding SOS70 weekly bulletin event table

    Copyright state:
    PERMISSION REQUIRED

    Repository state:
    SOURCE IMAGE EXCLUDED
    METADATA AND DERIVED TEST OUTPUT ONLY

---

# 4. RECOMMENDED PILOT WINDOW

Recommended pilot interval:

    6–12 July 2026

Reason:

    bulletin table is available
    multiple C- and M-class events are present
    event start, maximum and end times are documented
    chart geometry is representative
    no X-class scale extreme is required for the first test
    event density is sufficient to test overlap and matching
    the interval includes both labelled and unlabelled activity

Alternative pilot interval:

    31 January–6 February 2026

The alternative should be reserved for later testing because it contains dense M- and X-class activity and may introduce substantial event-label overlap.

---

# 5. PILOT ASSET IDENTITY

Before execution, record:

    pilot_asset_id
    visible filename
    displayed start date
    displayed end date
    source page URL
    retrieval time
    private byte length, where lawfully available
    private SHA-256, where lawfully available
    dimensions
    duplicate-candidate state
    copyright state
    repository exclusion state

Minimum accepted identity:

    source system established
    product family established
    displayed date window established
    image dimensions established
    duplicate state recorded
    source URL recorded

Failure to establish the date window forces:

    REFUSE

---

# 6. INPUT CONTRACT

The reconstruction engine accepts:

    source image reference
    asset metadata
    displayed start date
    displayed end date
    source time zone
    chart-class definitions
    optional bulletin event records
    optional manually verified plot boundary
    reconstruction configuration

The engine must not require the source image to be committed to Git.

Permitted private input:

    local private path
    ephemeral runtime image
    authorized source snapshot

Public output must not include:

    copied source image
    recoverable full-resolution source rendering
    protected source archive substitute

---

# 7. INPUT IMMUTABILITY

The execution must bind to:

    input identity
    configuration identity
    algorithm version
    execution version

If the input bytes are available privately:

    compute SHA-256

If input bytes are unavailable:

    record SOURCE-BY-REFERENCE

Boundary:

    Source-by-Reference
    ≠
    Byte-Level Replayable

The receipt must state the replayability level.

---

# 8. REPLAYABILITY LEVELS

Permitted states:

    BYTE-REPLAYABLE
    PIXEL-REPLAYABLE
    DISPLAY-REPLAYABLE
    METADATA-REPLAYABLE
    NON-REPLAYABLE
    UNKNOWN → HOLD

Definitions:

    BYTE-REPLAYABLE
    exact input bytes are preserved privately and hash-bound

    PIXEL-REPLAYABLE
    decoded pixel matrix can be reproduced

    DISPLAY-REPLAYABLE
    equivalent source display can be retrieved but bytes may vary

    METADATA-REPLAYABLE
    product identity and parameters are known but source display is unavailable

    NON-REPLAYABLE
    reconstruction cannot be independently rerun

Pilot acceptance requires at least:

    PIXEL-REPLAYABLE

or:

    explicit test-only exception approved before execution

---

# 9. IMAGE PRECONDITIONS

Required image conditions:

    complete chart frame visible
    x-axis visible
    y-axis class labels visible
    plot boundaries visible or inferable
    no major crop through data region
    sufficient resolution
    source date interval visible or externally verified
    trace distinguishable from background
    no unknown rotation
    no severe perspective distortion

Refuse when:

    more than 10% of plot area is missing
    vertical class labels are unavailable
    date range cannot be established
    chart is materially skewed
    trace cannot be distinguished
    source image appears corrupted

---

# 10. IMAGE NORMALIZATION

Permitted normalization:

    decode image
    preserve original pixel matrix
    create working copy
    convert to lossless internal representation
    inspect colour channels
    record dimensions
    record orientation
    detect plot rectangle

Prohibited silent transformations:

    contrast enhancement
    sharpening
    denoising
    colour substitution
    resizing
    cropping
    perspective correction
    interpolation

Any transformation must produce:

    new derived object identity
    operation record
    information-loss statement

---

# 11. PLOT-REGION MODEL

The chart is divided into:

    title region
    y-axis label region
    x-axis label region
    legend region
    plot region
    event-label overlay region
    source annotation region

The reconstruction engine must identify:

    plot_left_px
    plot_right_px
    plot_top_px
    plot_bottom_px

The boundary source must be recorded as:

    AUTOMATIC
    MANUAL
    HYBRID

---

# 12. PLOT-BOUNDARY ACCEPTANCE

Automatic plot-boundary detection passes when:

    all four boundaries are identified
    boundary error is estimated
    repeated execution returns the same result
    known tick or grid positions fall within tolerance

Tolerance:

    maximum boundary deviation:
    3 pixels

or:

    0.5% of plot dimension

whichever is larger.

Failure triggers:

    MANUAL CALIBRATION REQUIRED

Manual calibration must remain separately receipted.

---

# 13. HORIZONTAL TIME MODEL

The horizontal axis represents seven consecutive local days.

Required values:

    local_start_datetime
    local_end_datetime
    UTC_start_datetime
    UTC_end_datetime
    plot_left_px
    plot_right_px

Generic transform:

    local_time(x) =
    local_start
    +
    ((x - plot_left) / plot_width)
    ×
    displayed_duration

UTC conversion:

    UTC = Tomsk local time − 7 hours

Both local and UTC values must be retained.

---

# 14. TIME-AXIS UNCERTAINTY

Time uncertainty includes:

    boundary uncertainty
    pixel rounding
    axis-label placement
    chart rendering
    trace width
    event-label overlap
    unknown internal source cadence

Required output:

    estimated_local_time
    estimated_UTC_time
    lower_time_bound
    upper_time_bound
    time_uncertainty_seconds

No event match may imply precision beyond the chart resolution.

---

# 15. TIME-CALIBRATION TEST

Create known x-coordinate controls:

    left boundary
    one-day tick positions
    middle of chart
    right boundary

Expected results:

    left boundary maps to displayed start
    daily ticks map to local midnight or declared tick time
    right boundary maps to displayed end

Acceptance threshold:

    daily tick error ≤ 15 minutes

Pilot target:

    daily tick error ≤ 5 minutes

---

# 16. VERTICAL LOGARITHMIC MODEL

The chart uses logarithmic solar X-ray flux classes.

Reference lower bounds:

    A1 = 10^-8 W/m²
    B1 = 10^-7 W/m²
    C1 = 10^-6 W/m²
    M1 = 10^-5 W/m²
    X1 = 10^-4 W/m²
    X10 = 10^-3 W/m²

The exact visible chart bounds must be calibrated from the image.

Generic transform:

    log10_flux(y) =
    log10_flux_top
    +
    ((y - plot_top) / plot_height)
    ×
    (log10_flux_bottom - log10_flux_top)

Then:

    flux_W_m2 = 10 ^ log10_flux

---

# 17. CLASSIFICATION MODEL

Reconstructed flux is assigned to:

    A
    B
    C
    M
    X
    X10+

Class value examples:

    M1.0 = 1.0 × 10^-5 W/m²
    M5.3 = 5.3 × 10^-5 W/m²
    X1.0 = 1.0 × 10^-4 W/m²

Required output fields:

    estimated_flux_W_m2
    estimated_class
    estimated_multiplier
    lower_class_bound
    upper_class_bound
    class_uncertainty

---

# 18. VERTICAL-CALIBRATION TEST

Control points:

    A1 boundary
    B1 boundary
    C1 boundary
    M1 boundary
    X1 boundary
    X10 boundary where visible

Acceptance:

    each detected class boundary within 3 pixels

or:

    estimated logarithmic error ≤ 0.05 log10 units

Pilot target:

    ≤ 0.03 log10 units

---

# 19. TRACE MODEL

The visible X-ray trace is reconstructed as:

    one estimated y-coordinate
    for each accepted x-coordinate

Permitted trace states:

    TRACE OBSERVED
    TRACE PARTIALLY OBSERVED
    TRACE OCCLUDED
    TRACE BELOW DISPLAY FLOOR
    TRACE ABOVE DISPLAY CEILING
    TRACE UNRESOLVED
    MISSING DATA

The engine must not silently interpolate across:

    event labels
    missing chart region
    clipped peaks
    undecodable trace
    display ceiling

---

# 20. TRACE EXTRACTION METHOD

Minimum deterministic method:

    identify candidate trace colours
    calculate colour-distance mask
    remove background and grid candidates
    exclude text-label regions where possible
    identify connected trace candidates
    select continuity-consistent path
    estimate centreline
    assign uncertainty from trace thickness and ambiguity

The first implementation may use:

    rule-based colour segmentation
    deterministic morphology
    dynamic-programming path continuity

Machine learning is not authorized for the first pilot.

---

# 21. TRACE EXTRACTION OUTPUT

Required per-sample fields:

    sample_index
    pixel_x
    pixel_y_estimate
    pixel_y_lower
    pixel_y_upper
    local_time
    UTC_time
    estimated_flux_W_m2
    estimated_class
    recoverability_state
    occlusion_state
    quality_flags

Sampling interval must be declared.

Recommended initial interval:

    one horizontal pixel

Downsampled products may be created later as derived outputs.

---

# 22. GRIDLINE SEPARATION

The engine must distinguish:

    horizontal class gridlines
    vertical daily gridlines
    chart border
    X-ray trace
    event annotation lines
    text

Gridline removal must be deterministic.

Failure condition:

    extracted trace follows a gridline for more than 2% of plot width

Disposition:

    FAIL

---

# 23. LABEL OCCLUSION

Event labels may cover the trace.

Required response:

    mark occluded region
    preserve surrounding trace
    avoid invented values
    report occlusion duration
    optionally estimate bounded continuity
    never classify estimated continuity as observed trace

Permitted output:

    CONTINUITY ESTIMATE

but it must remain distinct from:

    TRACE OBSERVED

---

# 24. PEAK DETECTION

Candidate flare peaks are detected from the reconstructed trace using:

    local maximum
    prominence threshold
    minimum temporal separation
    minimum class threshold

Initial pilot threshold:

    C1.0 or above

Labelled validation subset:

    M1.0 or above

Peak detection parameters must be frozen before execution.

---

# 25. PEAK OUTPUT

Required fields:

    peak_id
    estimated_peak_local_time
    estimated_peak_UTC_time
    estimated_peak_flux
    estimated_peak_class
    prominence
    lower_time_bound
    upper_time_bound
    lower_flux_bound
    upper_flux_bound
    label_match_state
    bulletin_match_state

---

# 26. BULLETIN VALIDATION INPUT

The bulletin validation table should preserve:

    source event identifier
    class
    event date
    start time
    maximum time
    end time
    active region
    blackout level
    source time zone
    normalized UTC fields
    source-value validity state

Bulletin data must be transcribed separately from image reconstruction.

---

# 27. EVENT MATCHING

A reconstructed peak may match a bulletin event when:

    peak time falls within event interval plus uncertainty

or:

    peak maximum differs from bulletin maximum within tolerance

Initial timing tolerance:

    ±15 minutes

Pilot target:

    ±7 minutes

Class tolerance:

    within 0.20 logarithmic units

or:

    same class letter with multiplier error ≤ 30%

---

# 28. MATCH STATES

Permitted states:

    EXACT MATCH
    TIME MATCH / CLASS MISMATCH
    CLASS MATCH / TIME MISMATCH
    PARTIAL MATCH
    MULTIPLE CANDIDATE MATCH
    NO MATCH
    BULLETIN EVENT NOT VISIBLE
    VISIBLE PEAK NOT IN BULLETIN
    UNRESOLVED

---

# 29. PILOT VALIDATION METRICS

Required metrics:

    bulletin_event_count
    reconstructed_peak_count
    matched_event_count
    unmatched_bulletin_count
    unmatched_reconstruction_count
    median_peak_time_error
    maximum_peak_time_error
    median_log_flux_error
    class-letter accuracy
    M-class-or-higher recall
    M-class-or-higher precision
    occluded-duration fraction
    unresolved-duration fraction

---

# 30. PILOT ACCEPTANCE THRESHOLDS

Minimum PASS conditions:

    plot calibration PASS
    time calibration PASS
    vertical calibration PASS
    deterministic rerun PASS
    no silent interpolation
    receipt generated
    all M-class-or-higher bulletin events assessed
    M-class-or-higher recall ≥ 0.80
    M-class-or-higher precision ≥ 0.80
    median peak-time error ≤ 10 minutes
    maximum accepted peak-time error ≤ 20 minutes
    class-letter accuracy ≥ 0.85
    unresolved plot fraction ≤ 0.20

A result below these thresholds is:

    HOLD

not automatic FAIL, unless a contract violation occurred.

---

# 31. CONTRACT VIOLATION FAILURES

Immediate FAIL conditions:

    source image modified without receipt
    linear flux model used on logarithmic axis
    local time treated as UTC
    forecast treated as observation
    source event table silently corrected
    occluded values represented as observed
    copyrighted source image committed publicly
    reconstruction output claims raw-data equivalence
    nondeterministic output without declaration
    test thresholds changed after seeing results

---

# 32. POSITIVE CONTROLS

## Positive Control PC-001

    known M-class labelled peak
    expected reconstruction:
    visible peak near bulletin maximum time

## Positive Control PC-002

    known day boundary
    expected reconstruction:
    correct local-to-UTC conversion

## Positive Control PC-003

    known class boundary
    expected reconstruction:
    correct logarithmic flux mapping

## Positive Control PC-004

    known event interval
    expected reconstruction:
    detected peak within start–end window

All positive controls must pass before novel peaks are interpreted.

---

# 33. NEGATIVE CONTROLS

## Negative Control NC-001

    blank background interval
    expected:
    no M-class peak

## Negative Control NC-002

    vertical gridline
    expected:
    not classified as flare trace

## Negative Control NC-003

    event label text
    expected:
    not classified as X-ray signal

## Negative Control NC-004

    shifted bulletin times
    expected:
    lower match rate than correct alignment

## Negative Control NC-005

    randomized event list
    expected:
    materially lower matching performance

---

# 34. CORRUPTION TESTS

Required controlled variants:

    CT-001:
    shift image time window by +7 hours

    CT-002:
    classify vertical axis as linear

    CT-003:
    crop one class label

    CT-004:
    remove one date label

    CT-005:
    inject a false vertical coloured line

    CT-006:
    duplicate one chart under another filename

    CT-007:
    recompress image at reduced quality

    CT-008:
    obscure one labelled M-class peak

    CT-009:
    reverse horizontal image orientation

    CT-010:
    replace source URL metadata

Expected result:

    detection
    degraded state
    or refusal

Silent PASS is failure.

---

# 35. DETERMINISM TEST

Run the reconstruction at least three times with:

    same input
    same configuration
    same software version
    same environment declaration

Required outcome:

    identical structured output
    identical output hash
    identical receipt classification

Any nondeterminism must be explained and bounded.

First pilot requirement:

    deterministic execution mandatory

---

# 36. ENVIRONMENT RECORD

The execution receipt must record:

    operating system
    Python version
    package versions
    script version
    configuration version
    locale
    time-zone setting
    image-decoder version
    numerical-library version

Locale-dependent date parsing is prohibited.

Dates must be parsed explicitly.

---

# 37. OUTPUT ARTIFACTS

The pilot must produce:

    reconstructed_trace.csv
    reconstructed_events.json
    calibration.json
    validation_report.md
    reconstruction_receipt.json
    quality_flags.json
    refusal_report.md if applicable

Optional private-only output:

    annotated_validation_overlay.png

The private overlay must not be committed publicly when it reproduces protected source content.

---

# 38. CSV SCHEMA

Required columns:

    sample_index
    pixel_x
    pixel_y_estimate
    local_datetime
    utc_datetime
    estimated_flux_w_m2
    estimated_class
    estimated_multiplier
    lower_flux_w_m2
    upper_flux_w_m2
    recoverability_state
    quality_flags

---

# 39. EVENT JSON SCHEMA

Each event record must contain:

    event_id
    source_asset_id
    estimated_peak_local_datetime
    estimated_peak_utc_datetime
    estimated_flux_w_m2
    estimated_class
    estimated_multiplier
    timing_uncertainty_seconds
    log_flux_uncertainty
    bulletin_match_state
    bulletin_event_id
    quality_flags

---

# 40. CALIBRATION SCHEMA

Required fields:

    plot_left_px
    plot_right_px
    plot_top_px
    plot_bottom_px
    local_start_datetime
    local_end_datetime
    utc_start_datetime
    utc_end_datetime
    vertical_scale_type
    flux_top_w_m2
    flux_bottom_w_m2
    class_boundary_pixels
    boundary_uncertainty_px
    calibration_method
    calibration_status

---

# 41. RECONSTRUCTION RECEIPT SCHEMA

Required fields:

    reconstruction_id
    contract_id
    asset_id
    product_family_id
    source_reference
    replayability_level
    input_hash_state
    input_hash
    algorithm_name
    algorithm_version
    configuration_id
    execution_started_at
    execution_completed_at
    environment
    output_files
    output_hashes
    validation_status
    warnings
    refusals
    copyright_state
    public_repository_state
    final_disposition

---

# 42. VALIDATION DISPOSITIONS

Permitted states:

    PASS
    PASS WITH LIMITATIONS
    HOLD
    FAIL
    REFUSED
    UNKNOWN → HOLD

Definitions:

    PASS
    all critical thresholds satisfied

    PASS WITH LIMITATIONS
    critical thresholds satisfied but non-critical limitations remain

    HOLD
    evidence incomplete or metrics below threshold without contract violation

    FAIL
    contract violation or required control failure

    REFUSED
    execution stopped by predefined refusal condition

---

# 43. REFUSAL CONDITIONS

The pilot must refuse when:

    source date range cannot be established
    source time zone cannot be established
    plot rectangle cannot be calibrated
    logarithmic class scale cannot be calibrated
    chart is too degraded
    trace is not separable
    protected source use conflicts with intended output
    bulletin validation source is unavailable and validation is required
    duplicate identity undermines pilot identity
    requested output would substitute for raw or protected source data
    requested precision exceeds display capability

Refusal is a valid result.

---

# 44. COPYRIGHT-SAFE OUTPUT RULE

Public outputs may include:

    numeric approximations
    uncertainty
    validation metrics
    method
    source attribution
    source URL
    reconstruction receipt
    bounded event summaries

Public outputs must not include:

    the complete protected chart
    a high-fidelity reconstructed visual substitute
    copied source labels beyond what is necessary
    bulk archive recreation
    protected full bulletin text
    source media bundles

The pilot must remain a scientific validation exercise, not an archive replacement.

---

# 45. MANUAL INTERVENTION RULE

Permitted manual interventions:

    plot-boundary confirmation
    class-boundary confirmation
    date-window confirmation
    source metadata confirmation

Manual intervention must record:

    field changed
    original automatic value
    new value
    reason
    operator
    time
    effect on output

Manual trace drawing is prohibited for the first pilot.

---

# 46. BLIND REVIEW

After reconstruction, provide a reviewer with:

    reconstructed event list
    uncertainty
    no source image
    no surrounding narrative
    no cross-domain context

The reviewer assesses:

    whether matches are supported
    whether uncertainty is adequate
    whether unmatched peaks are overstated
    whether the output exceeds the contract

Blind review does not certify the source science.

---

# 47. BIDIRECTIONAL VALIDATION

Forward direction:

    bulletin event
    →
    expected chart peak
    →
    reconstructed event

Reverse direction:

    reconstructed event
    →
    candidate chart peak
    →
    bulletin event or unmatched status

Both directions must be reported.

A one-way match is insufficient for full validation.

---

# 48. MULTIDIRECTIONAL FAILURE ANALYSIS

For every unmatched reconstructed peak, test:

    small event omitted from bulletin
    trace extraction artifact
    label interference
    chart rendering artifact
    time calibration error
    class calibration error
    overlapping events
    source revision
    local maximum in background
    duplicate annotation

For every unmatched bulletin event, test:

    event below visible resolution
    peak outside plot bounds
    label occlusion
    chart sampling limitation
    event overlap
    transcription error
    source time conversion error

---

# 49. PILOT COMPLETION RULE

The pilot is complete only when:

    source metadata frozen
    test fixtures frozen
    implementation completed
    unit tests pass
    positive controls pass
    negative controls pass
    corruption tests evaluated
    deterministic reruns pass
    validation report completed
    reconstruction receipt completed
    independent review recorded
    final disposition assigned

Creating output files alone does not complete the pilot.

---

# 50. BULK-EXPANSION GATE

Bulk weekly X-ray reconstruction remains HOLD until:

    first pilot PASS or PASS WITH LIMITATIONS
    copyright review remains satisfied
    automatic asset enumeration exists
    duplicate handling exists
    error thresholds remain stable
    independent reviewer accepts the pilot method
    no source-owner objection is known
    bulk output does not become a protected archive substitute

---

# 51. NEXT AUTHORIZED IMPLEMENTATION STRUCTURE

After this contract is frozen, create:

    research\OBS-EE-001\reconstruction\
    research\OBS-EE-001\reconstruction\fixtures\
    research\OBS-EE-001\reconstruction\expected\
    research\OBS-EE-001\reconstruction\reports\
    tools\sos70_reconstruction\
    tests\sos70_reconstruction\

Recommended initial files:

    tools\sos70_reconstruction\models.py
    tools\sos70_reconstruction\calibration.py
    tools\sos70_reconstruction\trace_extractor.py
    tools\sos70_reconstruction\event_matcher.py
    tools\sos70_reconstruction\receipt.py
    tests\sos70_reconstruction\test_calibration.py
    tests\sos70_reconstruction\test_log_scale.py
    tests\sos70_reconstruction\test_event_matching.py
    tests\sos70_reconstruction\test_refusal.py
    tests\sos70_reconstruction\test_determinism.py

No implementation is authorized before contract freeze.

---

# 52. PRESERVED BOUNDARIES

    Test Contract
    ≠
    Implementation

    Implementation
    ≠
    Validation

    Validation
    ≠
    Raw-Data Recovery

    Chart Peak
    ≠
    Official Event Until Matched

    Bulletin Event
    ≠
    Perfect Chart Representation

    Approximate Flux
    ≠
    Instrument Sample

    Deterministic Output
    ≠
    Scientifically Correct Output

    High Match Rate
    ≠
    Cross-Domain Causation

    Reconstruction Capability
    ≠
    Redistribution Permission

---

# 53. FINAL STATUS

    Pilot object class: DEFINED
    Pilot window: RECOMMENDED
    Input contract: DEFINED
    Replayability states: DEFINED
    Image preconditions: DEFINED
    Plot geometry: DEFINED
    Time calibration: DEFINED
    UTC conversion: DEFINED
    Logarithmic calibration: DEFINED
    Trace extraction: DEFINED
    Peak detection: DEFINED
    Bulletin validation: DEFINED
    Match states: DEFINED
    Metrics: DEFINED
    Acceptance thresholds: DEFINED
    Positive controls: DEFINED
    Negative controls: DEFINED
    Corruption tests: DEFINED
    Determinism test: DEFINED
    Output schemas: DEFINED
    Receipt schema: DEFINED
    Refusal conditions: DEFINED
    Copyright-safe output rule: DEFINED
    Manual intervention boundary: DEFINED
    Bidirectional validation: DEFINED
    Multidirectional failure analysis: DEFINED
    Bulk expansion gate: DEFINED
    Implementation: NOT STARTED
    Pilot execution: NOT STARTED
    Independent review: NOT STARTED
    Cross-domain inference: HOLD
    Prediction or escalation: NOT AUTHORIZED
    UNKNOWN → HOLD