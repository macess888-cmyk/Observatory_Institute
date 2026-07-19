# OBS-EE-001 — METADATA-ONLY ASSET MANIFEST 002

**Card ID:** OBS-EE-001  
**Title:** Earth–Sun Multi-Domain Observation Probe  
**Project:** Observatory OS  
**Date:** 2026-07-19  
**Status:** METADATA-ONLY ASSET MANIFEST OPEN  
**Supersedes:** ASSET MANIFEST 001  
**Operating Posture:** METADATA-FIRST / COPYRIGHT-BOUND / SOURCE-LINKED / NON-REDISTRIBUTING / NON-CERTIFYING / UNKNOWN → HOLD

---

# 1. PURPOSE

This document registers the source objects, visual products, forecasts, screenshots, animations, charts, and other media inspected under OBS-EE-001 without requiring copyrighted or externally sourced media files to be stored in the public repository.

The manifest preserves:

    source identity
    product identity
    visible filename
    source URL
    product family
    domain
    object class
    observation or forecast status
    visible temporal coverage
    source time zone
    copyright state
    repository inclusion state
    reconstruction eligibility
    duplicate-candidate state
    interpretation boundary
    Observatory OS disposition

This manifest does not claim possession of the original raw measurements.

Boundary:

    Source Object Registered
    ≠
    Source File Redistributed

    Publicly Visible
    ≠
    Public-Domain Material

    Metadata Preserved
    ≠
    Reuse Permission Granted

---

# 2. MANIFEST POLICY

The repository may contain:

    source names
    source URLs
    product names
    visible filenames
    scientific classifications
    observation notes
    source descriptions
    copyright status
    reconstruction methodology
    derived summaries
    bounded findings

The repository must not contain without permission:

    copyrighted SOS70 source images
    copyrighted SOS70 source videos
    copied site archives
    paywalled or subscriber-only data
    unlicensed raw data
    source objects whose reuse rights remain unresolved

External scientific products may be registered without being copied into Git.

---

# 3. ASSET REGISTRATION MODEL

Each registered object receives:

    asset_id
    product_family_id
    source_system
    source_institution
    visible_filename
    source_page
    direct_source_url
    domain
    object_class
    observed_or_modelled_variable
    displayed_unit
    wavelength_or_energy_range
    spatial_coverage
    temporal_coverage
    source_time_zone
    forecast_issue_state
    forecast_validity_state
    provenance_state
    copyright_state
    repository_state
    reconstruction_state
    duplicate_state
    quality_state
    interpretation_boundary
    Observatory_OS_status

Unknown values remain:

    UNKNOWN

---

# 4. OBJECT CLASS VOCABULARY

Permitted classes:

    DIRECT OBSERVATION
    CALIBRATED OBSERVATION
    PROCESSED OBSERVATION
    DERIVED OBSERVABLE
    MODEL OUTPUT
    NOWCAST
    FORECAST
    ENSEMBLE FORECAST
    DERIVED INDEX
    EVENT SUMMARY
    WEEKLY BULLETIN
    SOURCE SNAPSHOT
    PUBLIC VISUALIZATION
    INTERPRETIVE COMMENTARY
    UNKNOWN

---

# 5. COPYRIGHT STATE VOCABULARY

Permitted copyright states:

    PUBLIC DOMAIN
    OPEN LICENCE
    SOURCE TERMS PERMIT REUSE
    ATTRIBUTION REQUIRED
    PERMISSION REQUIRED
    REUSE UNRESOLVED
    PRIVATE RESEARCH ONLY
    UNKNOWN → HOLD

---

# 6. REPOSITORY STATE VOCABULARY

Permitted repository states:

    METADATA ONLY
    LINK ONLY
    SOURCE FILE EXCLUDED
    DERIVED SUMMARY INCLUDED
    RECONSTRUCTED DATA HOLD
    PERMISSION PENDING
    ELIGIBLE FOR PUBLIC INCLUSION
    UNKNOWN → HOLD

---

# 7. RECONSTRUCTION STATE VOCABULARY

Permitted reconstruction states:

    NOT REQUIRED
    RECONSTRUCTABLE
    PILOT AUTHORIZED
    DISPLAY-DERIVED APPROXIMATION
    VALIDATION REQUIRED
    RAW-DATA COMPARISON REQUIRED
    NON-RECONSTRUCTABLE
    HOLD
    UNKNOWN → HOLD

---

# 8. DUPLICATE STATE VOCABULARY

Permitted duplicate states:

    UNIQUE
    DUPLICATE CANDIDATE
    SAME DATE RANGE
    BYTE IDENTITY UNKNOWN
    PIXEL IDENTITY UNKNOWN
    VISUALLY EQUIVALENT
    DUPLICATE CONFIRMED
    UNKNOWN

---

# 9. PRODUCT FAMILY PF-001 — NASA SDO AIA SOLAR ANIMATIONS

    Product family ID:
    PF-001

    Source institution:
    NASA Solar Dynamics Observatory

    Instrument:
    Atmospheric Imaging Assembly

    Domain:
    SOLAR

    Object class:
    PROCESSED OBSERVATION

    Source family:
    official SDO imagery products

    Copyright state:
    SOURCE TERMS REQUIRE VERIFICATION

    Repository state:
    METADATA ONLY

    Reconstruction state:
    NOT REQUIRED FOR CURRENT PHASE

## OBS-EE-A-001

    Visible filename:
    latest_1024_0171.mp4

    Channel:
    171 Å

    Observed variable:
    wavelength-specific EUV intensity

    Spatial coverage:
    full solar disk

    Temporal coverage:
    UNKNOWN

    Interpretation boundary:
    Coronal structure
    ≠
    Earth-directed consequence

    Status:
    REGISTERED / METADATA ONLY

## OBS-EE-A-002

    Visible filename:
    latest_1024_0193.mp4

    Channel:
    193 Å

    Observed variable:
    wavelength-specific EUV intensity

    Interpretation boundary:
    Coronal structure or coronal-hole visibility
    ≠
    Geomagnetic consequence established

    Status:
    REGISTERED / METADATA ONLY

## OBS-EE-A-003

    Visible filename:
    latest_1024_0304.mp4

    Channel:
    304 Å

    Observed variable:
    wavelength-specific EUV intensity

    Interpretation boundary:
    Filament or chromospheric structure
    ≠
    Earth-directed propagation

    Status:
    REGISTERED / METADATA ONLY

## OBS-EE-A-004

    Visible filename:
    latest_1024_0131.mp4

    Channel:
    131 Å

    Observed variable:
    wavelength-specific EUV intensity

    Interpretation boundary:
    Hot active-region structure
    ≠
    Flare classification

    Status:
    REGISTERED / METADATA ONLY

---

# 10. PRODUCT FAMILY PF-002 — NASA SDO HMI PRODUCTS

    Product family ID:
    PF-002

    Source institution:
    NASA Solar Dynamics Observatory / JSOC

    Instrument:
    Helioseismic and Magnetic Imager

    Domain:
    SOLAR

    Object class:
    DERIVED OBSERVABLE / PROCESSED OBSERVATION

    Repository state:
    METADATA ONLY

## OBS-EE-A-005

    Visible filename:
    Ic_flat_2d.mp4

    Product:
    continuum intensity animation

    Observed variable:
    photospheric continuum intensity

    Exact source series:
    UNKNOWN

    Interpretation boundary:
    Photospheric structure
    ≠
    Eruption prediction

    Status:
    REGISTERED / SOURCE SERIES REQUIRED

## OBS-EE-A-006

    Visible filename:
    M_color_2d.mp4

    Product:
    colour magnetogram animation

    Observed variable:
    photospheric magnetic-field representation

    Exact source series:
    UNKNOWN

    Interpretation boundary:
    Magnetic configuration
    ≠
    Terrestrial consequence

    Status:
    REGISTERED / SOURCE SERIES REQUIRED

## OBS-EE-A-007

    Visible filename:
    latest_1024_HMIIF.jpg

    Product:
    continuum intensity still

    Visible timestamp:
    approximately 2026-07-19 03:15:00

    Time standard:
    UNCONFIRMED

    Duplicate state:
    UNIQUE CANDIDATE

    Status:
    REGISTERED / UTC NORMALIZATION REQUIRED

## OBS-EE-A-008

    Visible filename:
    latest_1024_HMIBC.jpg

    Product:
    line-of-sight magnetic-field still

    Visible timestamp:
    approximately 2026-07-19 03:15:00

    Time standard:
    UNCONFIRMED

    Status:
    REGISTERED / UTC NORMALIZATION REQUIRED

---

# 11. PRODUCT FAMILY PF-003 — GFZ RADIATION-BELT FORECAST

    Product family ID:
    PF-003

    Source institution:
    GFZ German Research Centre for Geosciences

    Domain:
    RADIATION-BELT

    Object class:
    ENSEMBLE FORECAST / MODEL OUTPUT

    Repository state:
    METADATA ONLY

## OBS-EE-A-009

    Visible filename:
    Forecast_UTC_E_1_MeV_PA_50_latest_mean_ensemble.mp4

    Model:
    VERB family

    Modelled variable:
    1 MeV electron conditions

    Pitch-angle indicator:
    PA 50

    Forecast horizon:
    approximately two days

    Forecast issue time:
    UNKNOWN

    Forecast validity:
    UNKNOWN

    Interpretation boundary:
    Forecast mean
    ≠
    Direct particle observation

    Status:
    REGISTERED / FORECAST VERIFICATION REQUIRED

---

# 12. PRODUCT FAMILY PF-004 — GFZ AURORA FORECAST

    Product family ID:
    PF-004

    Source institution:
    GFZ German Research Centre for Geosciences

    Domain:
    AURORAL / IONOSPHERIC

    Object class:
    FORECAST / MODEL OUTPUT

    Repository state:
    METADATA ONLY

## OBS-EE-A-010

    Visible filename:
    aurora_forecast_browser.webm

    Modelled variable:
    predicted auroral activity or boundary

    Forecast issue time:
    UNKNOWN

    Forecast validity:
    UNKNOWN

    Interpretation boundary:
    Predicted aurora
    ≠
    Observed visible aurora

    Status:
    REGISTERED / FORECAST VERIFICATION REQUIRED

---

# 13. PRODUCT FAMILY PF-005 — THIRD-PARTY SEISMIC INDEX

    Product family ID:
    PF-005

    Source institution:
    Volcano Discovery

    Domain:
    SEISMIC

    Object class:
    DERIVED INDEX / PUBLIC VISUALIZATION

    Repository state:
    METADATA ONLY

## OBS-EE-A-011

    Visible filename:
    seismic-activity-level.png

    Displayed metric:
    combined magnitude

    Displayed activity state:
    MODERATE

    Displayed date:
    19 July 2026

    Method:
    UNKNOWN

    Reconstruction state:
    METHOD RECONSTRUCTION REQUIRED

    Interpretation boundary:
    Publisher-defined summary
    ≠
    Conserved global seismic variable

    Status:
    REGISTERED / NON-ADMISSIBLE FOR CAUSAL USE

---

# 14. PRODUCT FAMILY PF-006 — SOS70 ELF SONOGRAM

    Product family ID:
    PF-006

    Source system:
    SOS70-TOMSK-001

    Source institution:
    Space Observing System, Tomsk

    Domain:
    SCHUMANN-RESONANCE / ATMOSPHERIC-ELECTROMAGNETIC

    Object class:
    PROCESSED LOCAL OBSERVATION

    Copyright state:
    PERMISSION REQUIRED

    Repository state:
    SOURCE FILE EXCLUDED / METADATA ONLY

## OBS-EE-A-012

    Visible filename:
    provider.jpg
    or equivalent SOS70 sonogram image

    Displayed variable:
    ELF spectral amplitude versus frequency and time

    Frequency range:
    approximately 0–40 Hz

    Principal analytical range:
    6–32 Hz

    Spatial coverage:
    single Tomsk station

    Source time:
    Tomsk local time / UTC+7

    Source-declared symbols:
    black vertical bands = missing data
    white impulsive bands = local lightning or impulsive interference
    horizontal narrow bands = technogenic sources
    horizontal modal structures = Schumann resonances

    Reconstruction state:
    RECONSTRUCTABLE

    Interpretation boundary:
    Local processed ELF display
    ≠
    Global electromagnetic state

    Status:
    REGISTERED / COPYRIGHT HOLD

---

# 15. PRODUCT FAMILY PF-007 — SOS70 SCHUMANN PARAMETER CHARTS

    Product family ID:
    PF-007

    Source system:
    SOS70-TOMSK-001

    Object class:
    DERIVED LOCAL OBSERVABLE

    Copyright state:
    PERMISSION REQUIRED

    Repository state:
    SOURCE FILE EXCLUDED / METADATA ONLY

## OBS-EE-A-013

    Product:
    F1–F4 resonance-frequency chart

    Displayed variables:
    first four resonance frequencies

    Source cadence:
    three-minute derived records

    Reconstruction state:
    RECONSTRUCTABLE

    Interpretation boundary:
    Algorithm-derived modal frequencies
    ≠
    Direct sensor samples

## OBS-EE-A-014

    Product:
    A1–A4 resonance-amplitude chart

    Displayed variables:
    first four modal amplitudes

    Physical calibration:
    INCOMPLETE

    Reconstruction state:
    RECONSTRUCTABLE

## OBS-EE-A-015

    Product:
    Q1–Q4 quality-factor chart

    Displayed variables:
    first four modal quality factors

    Reconstruction state:
    RECONSTRUCTABLE

---

# 16. PRODUCT FAMILY PF-008 — SOS70 SEASONAL–DIURNAL MODEL MAPS

    Product family ID:
    PF-008

    Source system:
    SOS70-TOMSK-001

    Object class:
    EMPIRICAL MODEL VISUALIZATION

    Copyright state:
    PERMISSION REQUIRED

    Repository state:
    SOURCE FILE EXCLUDED / METADATA ONLY

    Reconstruction state:
    DISPLAY-DERIVED APPROXIMATION

## OBS-EE-A-016

    Visible filename:
    mf1.jpg

    Mode:
    first Schumann resonance

    Approximate display range:
    7.71–7.93 Hz

## OBS-EE-A-017

    Visible filename:
    mf2.jpg

    Mode:
    second Schumann resonance

    Approximate display range:
    13.72–14.22 Hz

## OBS-EE-A-018

    Visible filename:
    mf3.jpg

    Mode:
    third Schumann resonance

    Approximate display range:
    19.56–20.35 Hz

## OBS-EE-A-019

    Visible filename:
    mf4.jpg

    Mode:
    fourth Schumann resonance

    Approximate display range:
    25.14–25.75 Hz

## OBS-EE-A-020

    Visible filename:
    ef4.jpg

    Exact role:
    seasonal–diurnal distribution or companion figure

    Exact mode:
    PAGE-ORDER VERIFICATION REQUIRED

    Duplicate state:
    UNIQUE CANDIDATE

## OBS-EE-A-021

    Visible filename:
    Trend.jpg

    Product:
    long-period trends for the first four resonance frequencies

    Reported finding:
    long-period component present
    11-year harmonic not identified by source analysis

    Interpretation boundary:
    Trend reported
    ≠
    Cause demonstrated

---

# 17. PRODUCT FAMILY PF-009 — SOS70 MF/HF ELECTROMAGNETIC BACKGROUND

    Product family ID:
    PF-009

    Source system:
    SOS70-TOMSK-001

    Domain:
    MF/HF ELECTROMAGNETIC BACKGROUND

    Object class:
    PROCESSED LOCAL OBSERVATION

    Copyright state:
    PERMISSION REQUIRED

    Repository state:
    SOURCE FILE EXCLUDED / METADATA ONLY

## OBS-EE-A-022

    Product:
    MF/HF background spectrogram

    Frequency coverage:
    up to approximately 30 MHz

    Dominant influences:
    broadcast transmitters
    ionospheric propagation
    receiver configuration
    local interference

    Reconstruction state:
    RECONSTRUCTABLE

    Interpretation boundary:
    MF/HF radio background
    ≠
    ELF Schumann-resonance field

## OBS-EE-A-023

    Product:
    radio-propagation path map

    Object class:
    MODEL OR EXPLANATORY VISUALIZATION

    Reconstruction state:
    NOT REQUIRED

---

# 18. PRODUCT FAMILY PF-010 — SOS70 IONOSPHERIC PRODUCTS

    Product family ID:
    PF-010

    Source system:
    SOS70-TOMSK-001

    Instrument:
    TOMION digital ionosonde

    Copyright state:
    PERMISSION REQUIRED

    Repository state:
    SOURCE FILE EXCLUDED / METADATA ONLY

## OBS-EE-A-024

    Product:
    ionogram

    Object class:
    PROCESSED IONOSPHERIC OBSERVATION

    Displayed axes:
    radio frequency
    virtual reflection height

    Typical cadence:
    approximately fifteen minutes

    Reconstruction state:
    RECONSTRUCTABLE

## OBS-EE-A-025

    Product:
    critical-frequency chart

    Candidate variables:
    foE
    foEs
    foF1
    foF2

    Object class:
    DERIVED IONOSPHERIC OBSERVABLE

    Reconstruction state:
    RECONSTRUCTABLE

## OBS-EE-A-026

    Product:
    virtual-height chart

    Object class:
    DERIVED IONOSPHERIC OBSERVABLE

    Interpretation boundary:
    Virtual height
    ≠
    Direct geometric altitude

    Reconstruction state:
    RECONSTRUCTABLE

## OBS-EE-A-027

    Product:
    vertical plasma-transfer velocity

    Candidate variables:
    VE
    VF2

    Unit:
    m/s

    Display interval:
    latest three days

    Object class:
    DERIVED IONOSPHERIC OBSERVABLE

    Derivation method:
    PARTIAL

    Reconstruction state:
    RECONSTRUCTABLE

## OBS-EE-A-028

    Visible filename:
    model.bmp

    Product:
    ionospheric model or profile visualization

    Exact role:
    SOURCE PAGE VERIFICATION REQUIRED

## OBS-EE-A-029

    Visible filename:
    source.bmp

    Product:
    ionospheric source or comparison visualization

    Exact role:
    SOURCE PAGE VERIFICATION REQUIRED

---

# 19. PRODUCT FAMILY PF-011 — SOS70 SOLAR X-RAY WEEKLY ARCHIVE

    Product family ID:
    PF-011

    Family identifier:
    SOS70_SOLAR_XRAY_WEEKLY_2026

    Source system:
    SOS70-TOMSK-001

    Upstream source:
    EXTERNAL ORBITAL SOLAR X-RAY DATA
    exact upstream lineage requires confirmation

    Object class:
    PROCESSED EXTERNAL SOLAR OBSERVATION

    Source time:
    Tomsk local time / UTC+7

    Copyright state:
    PERMISSION REQUIRED

    Repository state:
    SOURCE FILE EXCLUDED / METADATA ONLY

    Reconstruction state:
    PILOT AUTHORIZED

    Approximate archive coverage:
    5 January 2026 through 19 July 2026

    Displayed classes:
    A
    B
    C
    M
    X
    X10

    Preferred event source:
    bulletin tables where available

    Image use:
    visual continuity
    background envelope
    quality control
    approximate unlabelled peak extraction

---

# 20. WEEKLY X-RAY ASSET RANGE

The known weekly X-ray chart family contains approximately thirty-one candidate images.

Assign the range:

    OBS-EE-A-030
    through
    OBS-EE-A-060

Each weekly asset must preserve:

    visible filename
    displayed start date
    displayed end date
    duplicate-candidate state
    source page
    source local time
    bulletin availability
    reconstruction status

Known later windows include:

    4–10 May 2026
    11–17 May 2026
    18–24 May 2026
    25–31 May 2026
    1–7 June 2026
    8–14 June 2026
    15–21 June 2026
    22–28 June 2026
    29 June–5 July 2026
    6–12 July 2026
    13–19 July 2026

Earlier windows extend backward into January 2026.

Exact enumeration remains required.

---

# 21. DUPLICATE-CANDIDATE X-RAY ASSETS

At least one uploaded chart appears to cover a date interval already represented by another image.

Candidate example:

    31 January–6 February 2026

Required duplicate tests:

    date-range comparison
    image dimensions
    filename
    byte identity if privately available
    perceptual hash if privately available
    pixel comparison if privately available
    label comparison
    chart-render variation

Current state:

    DUPLICATE CANDIDATE
    IDENTITY UNRESOLVED

---

# 22. PRODUCT FAMILY PF-012 — SOS70 FLARE-COUNT SUMMARY

    Product family ID:
    PF-012

    Source system:
    SOS70-TOMSK-001

    Object class:
    DERIVED EVENT SUMMARY

## OBS-EE-A-061

    Product:
    multi-week C/M/X/X10 flare-count graph

    Time interval:
    approximately ten weeks

    Source event catalogue:
    UPSTREAM SOURCE REQUIRES CONFIRMATION

    Reconstruction state:
    RECONSTRUCTABLE

    Interpretation boundary:
    Flare count
    ≠
    Earth impact

---

# 23. PRODUCT FAMILY PF-013 — SOS70 SOLAR AND GEOMAGNETIC INDICES

    Product family ID:
    PF-013

    Source system:
    SOS70-TOMSK-001

    Copyright state:
    PERMISSION REQUIRED

    Repository state:
    SOURCE FILE EXCLUDED / METADATA ONLY

## OBS-EE-A-062

    Product:
    F10.7 and Wolf-number chart

    Object class:
    HISTORICAL DATA PLUS FORECAST

    Historical interval:
    approximately 135 days

    Forecast interval:
    approximately 45 days

    Interpretation boundary:
    Historical segment
    ≠
    Forecast segment

## OBS-EE-A-063

    Product:
    Ap history and forecast

    Historical interval:
    approximately 125 days

    Forecast interval:
    approximately 45 days

    Object class:
    DERIVED INDEX PLUS FORECAST

## OBS-EE-A-064

    Product:
    Kp history and forecast

    Historical interval:
    approximately 20 days

    Forecast interval:
    approximately three days

    Object class:
    DERIVED INDEX PLUS FORECAST

---

# 24. PRODUCT FAMILY PF-014 — SOS70 WEEKLY BULLETINS

    Product family ID:
    PF-014

    Source system:
    SOS70-TOMSK-001

    Object class:
    WEEKLY BULLETIN / EXTERNAL DATA SYNTHESIS

    Repository state:
    METADATA AND DERIVED SUMMARY ONLY

    Copyright state:
    PERMISSION REQUIRED FOR FULL REPUBLICATION

Bulletin content may include:

    flare class
    flare start
    flare maximum
    flare end
    active region
    blackout level
    radio burst
    filament eruption
    CME detection
    CME direction
    CME model result
    proton flux
    electron flux
    solar-wind speed
    Bt
    Bz
    Kp
    Ap
    geomagnetic storm level
    forecast

The bulletin is stronger than chart digitization for exact labelled event times.

---

# 25. BULLETIN DATA-QUALITY RULE

Every extracted bulletin value must preserve:

    source text
    normalized value
    normalization status
    correction status
    correction rationale
    reviewer identity

No silent correction is permitted.

Known anomaly type:

    invalid or unusual clock values
    possible transcription errors
    translation errors
    source formatting errors
    extraction errors

Status:

    REVIEW REQUIRED

---

# 26. PRODUCT FAMILY PF-015 — SOS70 FORECASTS

    Product family ID:
    PF-015

    Source system:
    SOS70-TOMSK-001

    Object class:
    FORECAST / INTERPRETIVE BULLETIN

Forecast subjects include:

    solar activity
    M-class flare probability
    proton-event expectation
    greater-than-2 MeV electron levels
    CME influence
    coronal-hole high-speed streams
    geomagnetic activity

Every forecast requires:

    issue time
    valid interval
    source
    confidence
    expiry
    later outcome

Forecast statements must not be reclassified as observations after the event.

---

# 27. PRODUCT FAMILY PF-016 — SOS70 IMPORTANT-EVENT COMMENTARY

    Product family ID:
    PF-016

    Source system:
    SOS70-TOMSK-001

    Object class:
    INTERPRETIVE COMMENTARY

    Repository state:
    DERIVED SUMMARY ONLY

Examples may include:

    impressions
    comparative narrative
    statements about possible future developments
    statements about apparent quiet or escalation

Boundary:

    Commentary
    ≠
    Forecast Product

    Impression
    ≠
    Measurement

---

# 28. NATURAL COUNTEREXAMPLE RECORDS

## Counterexample CE-001

    Event:
    1–6 February 2026 solar flare episode

    Reported flare count:
    119

    Reported classes:
    62 C
    51 M
    6 X

    Source interpretation:
    limited terrestrial manifestation because CMEs were not Earth-directed

    Preserved reduction:
    High flare count
    ≠
    Earth impact

## Counterexample CE-002

    Event:
    20 January 2026 geomagnetic storm

    Reported chain:
    flare and halo CME
    interplanetary shock
    severe proton event
    high solar-wind speed
    strong Bt
    strongly southward Bz
    G4 geomagnetic response
    F2-region electron-density reduction

    Reported local EM result:
    no substantial ELF/MF/HF background change detected

    Preserved reduction:
    Strong space-weather response
    ≠
    Necessary local electromagnetic-background anomaly

---

# 29. METADATA-ONLY ASSET COUNT

Current candidate asset count:

    approximately 64

This number includes:

    original solar and space-weather assets
    seismic index
    SOS70 Schumann products
    SOS70 ionospheric products
    SOS70 MF/HF products
    seasonal–diurnal model figures
    long-term trend figure
    weekly X-ray archive
    solar and geomagnetic index charts
    forecast and bulletin products

The count remains provisional because:

    some visible files may be duplicates
    some screenshots may represent the same product instance
    exact weekly chart enumeration is incomplete
    some source-page images have unresolved roles

---

# 30. EXCLUDED SOURCE FILE POLICY

The following are intentionally excluded from Git:

    SOS70 images
    SOS70 videos
    SOS70 copied webpages
    subscription-linked source media
    source objects with unresolved reuse permission

This exclusion is methodological, not evidentiary deletion.

The manifest preserves their existence and role without redistributing them.

---

# 31. PRIVATE VERIFICATION POLICY

Private inspection may preserve where lawful:

    source screenshot
    source filename
    retrieval time
    private hash
    byte length
    dimensions
    perceptual hash
    reconstruction workspace

Private verification records must not automatically enter public Git history.

Public artifacts should contain:

    metadata
    methods
    classifications
    findings
    uncertainty
    source links
    permission state

---

# 32. MATHEMATICAL RECONSTRUCTION POLICY

Authorized reconstruction classes:

    weekly solar X-ray chart
    Schumann sonogram
    F1–F4 chart
    A1–A4 chart
    Q1–Q4 chart
    seasonal–diurnal maps
    MF/HF spectrogram
    ionogram
    critical-frequency chart
    virtual-height chart
    plasma-transfer chart
    F10.7 and Wolf-number chart
    Ap chart
    Kp chart
    long-period trend chart

All outputs must be labelled:

    DISPLAY-DERIVED
    APPROXIMATE
    UNCERTAINTY-BOUND
    NON-SUBSTITUTIVE FOR RAW DATA

---

# 33. FIRST PILOT RECONSTRUCTION

Recommended pilot:

    one SOS70 weekly solar X-ray chart

Reason:

    regular axes
    explicit logarithmic class bands
    explicit dates
    visible event labels
    bulletin event table available for validation
    contained product family
    low ambiguity relative to spectrogram reconstruction

Pilot output:

    approximate X-ray background trace
    labelled flare-event table
    axis-calibration record
    uncertainty report
    validation comparison
    reconstruction refusal notes

---

# 34. ASSET ADMISSION CONDITIONS

An external asset may be admitted into this metadata-only manifest when:

    source system is identified
    product family is identified
    object class is assigned
    visible filename or product label is preserved
    source URL is preserved or pending
    copyright state is declared
    repository state is declared
    interpretation boundary is recorded

The source file itself need not be committed.

---

# 35. EMPIRICAL COMPARISON CONDITIONS

An asset may support empirical comparison only when:

    time is sufficiently normalized
    object class is correct
    product lineage is sufficiently known
    forecast and observation are separated
    missing-data state is known
    instrument or model limitations are recorded
    reconstruction uncertainty is recorded when applicable
    comparison does not exceed the source’s spatial coverage

---

# 36. HOLD CONDITIONS

An asset remains HOLD when:

    source identity is unresolved
    source URL is unresolved
    product type is ambiguous
    copyright state is unresolved
    time zone is unresolved
    observation time is unresolved
    forecast validity is unresolved
    duplicate state affects counting
    visual reconstruction lacks uncertainty
    source image is treated as raw data
    copied source media would violate repository policy

---

# 37. NEXT AUTHORIZED ARTIFACT

    07B_SOS70_RECONSTRUCTION_TEST_CONTRACT.md

That artifact will define:

    pilot asset identity
    plot-region detection
    axis calibration
    logarithmic class conversion
    trace extraction
    label extraction
    uncertainty calculation
    bulletin validation
    acceptance thresholds
    refusal conditions
    output schema
    reproducibility requirements

---

# 38. PRESERVED BOUNDARIES

    Metadata Registered
    ≠
    Media Republished

    Copyright Hold
    ≠
    Research Prohibited

    Image Available
    ≠
    Raw Data Available

    Image Digitized
    ≠
    Original Samples Recovered

    Same Date Range
    ≠
    Independent Evidence

    Forecast Displayed
    ≠
    Event Observed

    Bulletin Interpretation
    ≠
    Instrument Measurement

    Local Measurement
    ≠
    Global State

    Approximate Asset Count
    ≠
    Final Inventory

---

# 39. FINAL STATUS

    Metadata-only policy: ESTABLISHED
    Source-media redistribution: REFUSED WITHOUT PERMISSION
    Original OBS-EE assets: REGISTERED
    NASA SDO products: REGISTERED
    GFZ forecasts: REGISTERED
    Seismic derived index: REGISTERED
    SOS70 ELF products: REGISTERED
    SOS70 Schumann parameters: REGISTERED
    SOS70 long-term model figures: REGISTERED
    SOS70 MF/HF products: REGISTERED
    SOS70 ionospheric products: REGISTERED
    SOS70 X-ray archive family: REGISTERED
    SOS70 solar and geomagnetic indexes: REGISTERED
    SOS70 bulletins: REGISTERED
    SOS70 forecasts: REGISTERED
    SOS70 commentary: CLASSIFIED SEPARATELY
    Candidate asset count: APPROXIMATELY 64
    Duplicate review: REQUIRED
    Exact weekly enumeration: REQUIRED
    Source URLs: PARTIAL
    Copyright permission: UNRESOLVED
    Public source files: EXCLUDED
    Mathematical reconstruction: AUTHORIZED AS APPROXIMATION
    Raw-data equivalence: REFUSED
    Reconstruction test contract: NEXT
    Cross-domain empirical testing: HOLD
    Prediction or escalation: NOT AUTHORIZED
    UNKNOWN → HOLD