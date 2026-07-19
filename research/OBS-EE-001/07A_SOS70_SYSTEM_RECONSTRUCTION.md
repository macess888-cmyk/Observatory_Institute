# OBS-EE-001 — SOS70 SYSTEM RECONSTRUCTION 001

**Card ID:** OBS-EE-001  
**System ID:** SOS70-TOMSK-001  
**Title:** Space Observing System — Tomsk Multi-Domain Monitoring Reconstruction  
**Project:** Observatory OS  
**Date:** 2026-07-19  
**Status:** SYSTEM RECONSTRUCTION OPEN  
**Operating Posture:** SOURCE-RECONSTRUCTED / INSTRUMENT-SEPARATED / MODEL-SEPARATED / COPYRIGHT-BOUND / NON-CERTIFYING / UNKNOWN → HOLD

---

# 1. PURPOSE

This document reconstructs the publicly observable architecture, measurement methods, processing pipelines, data products, forecast products, interpretive layers, limitations, and governance boundaries of the SOS70 Space Observing System based in Tomsk, Russia.

The reconstruction preserves distinctions among:

    direct local measurement
    derived local observable
    externally sourced observation
    processed visualization
    empirical model
    forecast
    weekly bulletin
    interpretation
    public commentary

The purpose is not to certify SOS70.

The purpose is to establish what the system appears to measure, derive, model, forecast, and communicate before its products are used within OBS-EE-001.

---

# 2. SYSTEM IDENTITY

    System name:
    Space Observing System

    Public abbreviation:
    SOS70

    Public domain:
    sos70.ru

    Geographic reference:
    Tomsk, Russia
    Region 70

    Principal time basis:
    Tomsk decree time

    Declared offset:
    UTC+7

    General system class:
    MULTI-DOMAIN ENVIRONMENTAL AND SPACE-WEATHER OBSERVATION INTERFACE

    Principal domains:
    extremely low-frequency electromagnetic monitoring
    Schumann resonance analysis
    medium- and high-frequency electromagnetic background
    ionospheric observation
    solar X-ray activity
    solar activity
    geomagnetic activity
    weekly heliogeophysical bulletins
    empirical forecasting

    Observatory OS disposition:
    SYSTEM IDENTIFIED / ARCHITECTURE PARTIALLY RECONSTRUCTED

---

# 3. PUBLIC SYSTEM SECTIONS

The public interface includes or references the following sections:

    brief history of research
    ELF-noise measurement methodology
    ELF-noise sonogram
    principal Schumann resonance parameters
    seasonal and diurnal variation
    Schumann resonance forecast

    electromagnetic background
    radio broadcasting
    MF and HF electromagnetic background

    ionospheric data
    ionogram
    critical frequencies
    virtual heights
    vertical ionospheric plasma-transfer velocity

    solar X-rays and flares
    solar and geomagnetic activity
    weekly bulletins
    latest week
    weekly bulletin archive
    forecast

    important events
    contact and organizational information
    example graphical and tabular data formats
    subscription-linked current products

The system must therefore be treated as a product family rather than one sensor or one visualization.

---

# 4. SYSTEM LAYER MODEL

SOS70 can be reconstructed into the following layers:

    Layer 1 — Local sensing
    Layer 2 — Signal conditioning
    Layer 3 — Digitization
    Layer 4 — Numerical processing
    Layer 5 — Derived observables
    Layer 6 — Long-term empirical modelling
    Layer 7 — Forecast generation
    Layer 8 — External space-weather data integration
    Layer 9 — Public visualization
    Layer 10 — Weekly interpretation and commentary

These layers must not be collapsed.

Boundary:

    Local Sensor
    ≠
    Derived Parameter

    Derived Parameter
    ≠
    Forecast

    Forecast
    ≠
    Observation

    Observation
    ≠
    Interpretation

---

# 5. LOCAL ELF MEASUREMENT SYSTEM

## 5.1 Measurement target

    Domain:
    EXTREMELY LOW FREQUENCY ELECTROMAGNETIC FIELD

    Candidate measured component:
    vertical electric-field component

    Operational frequency region:
    approximately below 40 Hz

    Primary analytical band:
    6–32 Hz

    Principal research target:
    first four Schumann resonance modes

---

## 5.2 Antenna

    Instrument:
    vertical whip antenna

    Declared height:
    5 metres

    Function:
    receiving local ELF electric-field variation

    Exact antenna transfer function:
    UNKNOWN

    Antenna calibration:
    NOT ACQUIRED

    Grounding configuration:
    UNKNOWN

    Site-noise map:
    NOT ACQUIRED

---

## 5.3 Input filtering

The measurement system includes a narrow-band rejection filter centred on the electrical mains frequency.

    Filter type:
    notch filter

    Centre frequency:
    50 Hz

    Declared attenuation:
    approximately 40 dB per octave in the rejection region

    Purpose:
    suppress mains-frequency interference
    preserve receiver dynamic range

Boundary:

    50 Hz Suppression
    ≠
    Removal of All Technogenic Interference

---

## 5.4 Low-pass filtering

Two low-pass stages are described.

### Stage one

    Cutoff frequency:
    approximately 35 Hz

    Out-of-band attenuation:
    approximately 20 dB per octave

    In-band attenuation:
    not more than approximately 0.5 dB per octave

### Stage two

    Cutoff frequency:
    approximately 31.5 Hz

    Out-of-band attenuation:
    at least approximately 24 dB per octave

    Maximum reported attenuation:
    approximately 60 dB per octave

    In-band attenuation:
    not more than approximately 0.5 dB per octave

Combined function:

    constrain received signals to the ELF analytical band
    reduce higher-frequency interference
    support reliable digitization

---

# 6. ANALOG-TO-DIGITAL CONVERSION

The documented ADC characteristics include:

    differential channels:
    16

    ADC resolution:
    12 bits

    conversion time:
    2 microseconds

    differential nonlinearity:
    approximately 0.02%

    full-scale nonlinearity:
    approximately 0.02%

    input resistance:
    approximately 1 megaohm

    programmable sampling capability:
    approximately 150 kHz

The operational monitoring method separately states:

    actual ELF sampling rate:
    80 Hz

These values must remain distinct.

Boundary:

    ADC Maximum Capability
    ≠
    Operational Sampling Rate

---

# 7. ELF PROCESSING PIPELINE

The reconstructed processing chain is:

    vertical ELF electric-field signal
    →
    analog amplification
    →
    50 Hz rejection
    →
    cascaded low-pass filtering
    →
    12-bit digitization at 80 Hz
    →
    50-second analysis window
    →
    discrete Fourier transform
    →
    five-second time shift
    →
    amplitude spectrum
    →
    modal peak detection
    →
    instantaneous frequency, amplitude and Q extraction
    →
    statistical aggregation
    →
    three-minute record

---

## 7.1 Spectral window

    Window duration:
    50 seconds

    Window shift:
    5 seconds

    Declared frequency resolution:
    0.02 Hz

    Analysis range:
    6–32 Hz

---

## 7.2 Three-minute aggregation

The source describes twenty spectral estimates contributing to one three-minute record.

    Record interval:
    3 minutes

    Approximate daily record count:
    480

    Derived values:
    mean
    standard deviation

    Modes:
    first four Schumann resonance modes

---

# 8. DERIVED SCHUMANN PARAMETERS

## 8.1 Resonance frequency

For each expected mode:

    search near known average frequency
    identify maximum spectral power density
    assign frequency of that maximum
    record as instantaneous modal frequency

Boundary:

    Derived Peak Frequency
    ≠
    Direct Sensor Sample

---

## 8.2 Resonance amplitude

The modal amplitude is described as:

    square root
    of
    maximum spectral power density

Exact physical calibration and final amplitude unit remain unresolved.

---

## 8.3 Quality factor

The quality factor is described as:

    resonance frequency
    divided by
    half-power bandwidth

The half-power level corresponds to:

    0.5 of maximum power

or approximately:

    0.707 of maximum amplitude

Boundary:

    Q Estimate
    ≠
    Independent Direct Measurement

---

# 9. SONOGRAM PRODUCT

## 9.1 Product identity

    Product:
    ELF-noise sonogram

    Product class:
    PROCESSED LOCAL OBSERVATION

    Display:
    time × frequency × displayed amplitude or intensity

    Typical visible interval:
    latest three experimental days

    Frequency range:
    approximately 0–40 Hz in public display
    principal analytical range 6–32 Hz

---

## 9.2 Source-declared interpretation

    Black vertical bands:
    missing data or missing registration

    White high-level vertical bands:
    impulsive interference
    especially interpreted as local lightning discharges

    Horizontal narrow-band signals:
    technogenic electromagnetic sources

    Horizontal resonance structures:
    Schumann resonance modes

---

## 9.3 Interpretation boundary

A white interval may be consistent with:

    local lightning
    impulsive electromagnetic interference
    display clipping
    receiver saturation
    other high-amplitude local events

The exact classification still requires:

    raw waveform
    instrument state
    gain record
    clipping flags
    local lightning data
    local weather data

Boundary:

    White Vertical Band
    ≠
    Global Energy Event

---

# 10. NATURAL AND TECHNOGENIC SOURCE SEPARATION

## 10.1 Natural sources

The source identifies:

    local lightning
    distant lightning
    atmospheric impulses
    globally propagating atmospherics
    Earth–ionosphere cavity resonance

## 10.2 Technogenic sources

The source identifies:

    electrical transmission lines
    transformer substations
    industrial equipment
    narrow-band electromagnetic emitters
    local infrastructure

## 10.3 Required analytical posture

Every visible feature must be classified among:

    resonance structure
    local lightning
    distant atmospheric activity
    technogenic interference
    missing data
    clipping or saturation
    unresolved feature

No unexplained feature may automatically become evidence of a global anomaly.

---

# 11. SCHUMANN PARAMETER PRODUCTS

The system displays three-day time series for:

    F1–F4:
    resonance frequencies

    A1–A4:
    resonance amplitudes

    Q1–Q4:
    quality factors

Product class:

    ALGORITHM-DERIVED LOCAL OBSERVABLES

Required metadata still missing:

    final physical amplitude calibration
    uncertainty per three-minute record
    mode-tracking failure flags
    modal overlap handling
    interference-rejection algorithm
    data-quality masks

---

# 12. LONG-TERM DATASET

    Monitoring start:
    March 1997

    Reconstructed model-data end:
    March 2025

    Approximate series length:
    28 years

    Declared purpose:
    long-term monitoring
    statistical analysis
    seasonal and diurnal modelling
    resonance forecasting

Potential continuity risks:

    hardware replacement
    antenna replacement
    receiver gain changes
    filter replacement
    ADC replacement
    software changes
    algorithm changes
    site-environment changes
    urban electromagnetic-noise changes
    missing-data intervals

Long-term homogeneity is not established merely by record duration.

---

# 13. SEASONAL–DIURNAL MODEL

## 13.1 Model inputs

For each mode, the model reportedly uses:

    hourly values
    monthly mean resonance frequencies
    observations from March 1997 to March 2025

## 13.2 Dominant daily harmonics

    24 hours
    12 hours
    8 hours

## 13.3 Dominant seasonal harmonics

    12 months
    6 months
    4 months

## 13.4 Model structure

The model includes:

    monthly and local-time mean
    daily harmonic components
    seasonal variation of harmonic coefficients
    low-frequency long-period trend
    residual component

Exact coefficients have not been acquired.

---

# 14. REPORTED MODEL FIT

Reported coefficients of determination:

    Mode 1:
    R² = 0.96

    Mode 2:
    R² = 0.98

    Mode 3:
    R² = 0.93

    Mode 4:
    R² = 0.85

These values describe fit to the modelled historical data.

Boundary:

    High Historical R²
    ≠
    Independent Forecast Skill

Required forecast validation:

    untouched time interval
    prediction timestamp
    observed value
    error metric
    uncertainty interval
    benchmark comparison

---

# 15. LONG-PERIOD TREND FINDING

The source reports that earlier shorter records were approximated using seventh-degree polynomials.

The longer record reportedly shows that this description is inadequate.

The source further reports:

    dominant spectral component:
    approximately 27-year harmonic

    11-year harmonic:
    not observed in the analysed long-term trend

    proposed interpretation:
    possible long-period climatic influence
    rather than direct 11-year solar-cycle control

This finding must be preserved as a source claim, not elevated to final causal proof.

Boundary:

    11-Year Harmonic Not Found
    ≠
    Solar Influence Universally Impossible

    27-Year Component Reported
    ≠
    Climatic Cause Demonstrated

Current status:

    LONG-PERIOD COMPONENT REPORTED
    CAUSE UNRESOLVED

---

# 16. SEASONAL–DIURNAL MAP ASSETS

The uploaded model and distribution maps represent:

    local month
    ×
    local hour
    ×
    resonance frequency

Approximate displayed ranges:

    Mode 1:
    7.71–7.93 Hz

    Mode 2:
    13.72–14.22 Hz

    Mode 3:
    19.56–20.35 Hz

    Mode 4:
    25.14–25.75 Hz

The maps may be digitized as:

    colour-quantized approximate frequency matrices

Reconstruction status:

    DISPLAY-DERIVED
    GRID-INTERPOLATED
    APPROXIMATE
    NON-SUBSTITUTIVE FOR ORIGINAL MODEL OUTPUT

---

# 17. SCHUMANN FORECAST

## 17.1 Forecast class

    Product class:
    EMPIRICAL FORECAST

    Principal basis:
    regular seasonal variation
    regular diurnal variation
    long-term historical model

## 17.2 Known limitation

The public description indicates that:

    latest-day behaviour
    full physical-mathematical model outputs
    broader real-time forcing

are not necessarily integrated into the displayed forecast.

Boundary:

    Empirical Seasonal Forecast
    ≠
    Full Physical Earth-System Forecast

    Schumann Forecast
    ≠
    Earthquake Forecast

---

# 18. MF AND HF ELECTROMAGNETIC BACKGROUND

## 18.1 Product domain

    medium-frequency radio background
    high-frequency radio background

## 18.2 Main influences

    broadcast transmitters
    ionospheric propagation
    transmitter schedules
    propagation distance
    ionospheric reflection
    receiver configuration
    local noise

## 18.3 Distinction

    MF/HF background
    ≠
    ELF Schumann resonance

## 18.4 Confirmed configuration risk

The SOS70 commentary records that changes in displayed MF/HF levels may result from:

    equipment retuning
    expanded dynamic range
    reduced threshold level

This is direct evidence that instrument configuration may alter visual appearance.

Boundary:

    Display-Level Change
    ≠
    Environmental-Level Change

Required metadata:

    gain
    threshold
    tuning
    dynamic range
    receiver bandwidth
    configuration-change timestamp

---

# 19. IONOSPHERIC SYSTEM

## 19.1 Ionosonde identity

    System:
    TOMION digital ionosonde

    Product:
    ionogram

    General cadence:
    approximately every 15 minutes

    Time basis:
    local Tomsk time unless otherwise declared

## 19.2 Ionogram interpretation

An ionogram represents:

    transmitted radio frequency
    versus
    virtual reflection height

Candidate traces include:

    ordinary component
    extraordinary component

Derived ionospheric parameters may include:

    foE
    foEs
    foF1
    foF2
    virtual heights
    layer structure
    minimum observable frequency

---

# 20. CRITICAL FREQUENCY PRODUCTS

Product class:

    DERIVED IONOSPHERIC OBSERVABLE

Candidate parameters:

    foE
    foEs
    foF1
    foF2

Critical frequency is not a direct altitude measurement.

It is associated with plasma frequency and electron concentration under the relevant ionospheric-layer interpretation.

Required lineage:

    ionogram
    →
    trace classification
    →
    parameter extraction
    →
    critical-frequency record

---

# 21. VIRTUAL HEIGHT PRODUCTS

Product class:

    DERIVED IONOSPHERIC OBSERVABLE

Virtual height represents an equivalent radio-reflection path under an assumed propagation model.

Boundary:

    Virtual Height
    ≠
    Direct Geometric Layer Height

Required caution:

    group delay
    propagation path
    ionospheric gradients
    inversion assumptions
    automatic scaling errors

---

# 22. VERTICAL PLASMA-TRANSFER VELOCITY

## 22.1 Product identity

    Product:
    average vertical ionospheric plasma-transfer velocity

    Regions:
    E
    F2

    Display interval:
    latest three days

    Unit:
    metres per second

    Traces:
    VE
    VF2

## 22.2 Product class

    DERIVED IONOSPHERIC OBSERVABLE

It is not direct tracking of individual plasma particles.

## 22.3 Required reconstruction

The derivation method must identify:

    source ionogram parameters
    time derivative
    height model
    plasma-motion assumptions
    smoothing
    missing-data handling
    uncertainty

Current status:

    PRODUCT IDENTIFIED
    ALGORITHM NOT FULLY RECONSTRUCTED

---

# 23. MACHINE-READABLE FORMATS

The public documentation references example formats including:

    .afq
    .dbt
    .hfi

Candidate roles:

    AFQ:
    Schumann resonance amplitudes, frequencies and quality factors

    DBT:
    radio-background data bands

    HFI:
    ionospheric frequencies, heights and plasma-transfer variables

These formats provide a potential path from display inspection to numerical ingestion.

Required before ingestion:

    schema version
    field definitions
    timestamp format
    missing-value code
    units
    sample cadence
    licence
    integrity hash
    provenance

---

# 24. EXTERNAL SOLAR X-RAY PRODUCT FAMILY

## 24.1 Product identity

SOS70 displays seven-day solar X-ray activity charts containing:

    A
    B
    C
    M
    X
    X10

class bands.

The charts include:

    continuous background envelope
    event peaks
    labelled M- and X-class events
    seven-day local-time axis

## 24.2 Object class

    PROCESSED EXTERNAL SOLAR X-RAY OBSERVATION

SOS70 is not presently established as the original orbital X-ray instrument operator.

The upstream source must be reconstructed.

## 24.3 Time basis

    Tomsk local time
    UTC+7

## 24.4 Mathematical reconstruction

The chart family may support approximate extraction of:

    background class level
    event timing
    unlabelled peak timing
    event-density regimes
    continuity gaps

Exact event records should preferentially use bulletin tables where available.

Boundary:

    Display Height
    ≠
    Exact Original Flux Sample

---

# 25. SOLAR X-RAY CLASSIFICATION

The source describes logarithmic X-ray classes:

    A:
    approximately 10–100 nW/m²

    B:
    approximately 100 nW/m²–1 μW/m²

    C:
    approximately 1–10 μW/m²

    M:
    approximately 10–100 μW/m²

    X:
    approximately 100 μW/m²–1 mW/m²

    X10:
    approximately 1 mW/m² and above

The class scale is logarithmic.

Boundary:

    Equal Vertical Distance Between Classes
    ≠
    Equal Linear Flux Difference

---

# 26. SOLAR X-RAY ARCHIVE

The acquired chart sequence spans approximately:

    5 January 2026
    through
    19 July 2026

Known weekly windows include:

    January 2026
    February 2026
    March 2026
    April 2026
    May 2026
    June 2026
    July 2026

Product family identifier:

    SOS70_SOLAR_XRAY_WEEKLY_2026

Object identity rule:

    each image receives a unique asset identifier
    duplicate date ranges receive duplicate-candidate status
    byte and pixel identity must be tested

---

# 27. FLARE COUNT PRODUCT

The system also displays flare counts over a multi-week interval.

Candidate event classes:

    C
    M
    X
    X10

Product class:

    DERIVED EVENT-COUNT SUMMARY

Required reconstruction:

    upstream event catalogue
    count interval
    event inclusion rule
    duplicate-event handling
    time-zone conversion
    revision handling

---

# 28. SOLAR ACTIVITY INDEX PRODUCT

The system presents:

    F10.7 solar radio-flux index
    Wolf sunspot number

Candidate history interval:

    approximately 135 days

Candidate forecast interval:

    approximately 45 days

Displayed colour distinction:

    historical or compiled values
    forecast continuation

Boundary:

    Historical Segment
    ≠
    Forecast Segment

---

# 29. GEOMAGNETIC INDEX PRODUCTS

## 29.1 Ap

    history interval:
    approximately 125 days

    forecast interval:
    approximately 45 days

## 29.2 Kp

    history interval:
    approximately 20 days

    forecast interval:
    approximately 3 days

Red forecast sections must not be interpreted as completed observations.

Boundary:

    Forecast Kp or Ap
    ≠
    Observed Kp or Ap

---

# 30. WEEKLY BULLETINS

The weekly bulletin family integrates:

    solar flare events
    active-region descriptions
    radio bursts
    filament eruptions
    CME analysis
    Earth-directed or non-Earth-directed assessment
    proton flux
    electron flux
    solar-wind conditions
    geomagnetic activity
    forecast statements

Object class:

    EXTERNAL DATA SYNTHESIS
    INTERPRETIVE BULLETIN

The bulletin is not one instrument output.

---

# 31. FEBRUARY 2026 SOLAR-ACTIVITY COUNTEREXAMPLE

The source reports that from approximately 1–6 February 2026:

    total flares:
    119

    C class:
    62

    M class:
    51

    X class:
    6

The source states that this intense flare interval produced no major Earth manifestation because the associated CMEs were not directed toward Earth.

Preserved reduction:

    High Flare Count
    ≠
    Earth Impact

Required causal chain:

    flare
    →
    eruption or CME
    →
    direction
    →
    propagation
    →
    Earth encounter
    →
    observed response

---

# 32. JANUARY 20, 2026 SPACE-WEATHER EVENT

The source describes a strong event chain including:

    X1.9 flare
    halo CME
    severe proton event
    interplanetary shock
    strong magnetic field
    strongly southward Bz
    high solar-wind speed
    G4 geomagnetic storm
    magnetopause compression
    reduction of F2-region electron concentration at Tomsk

The source separately states that no significant changes were observed in the local environmental electromagnetic background across the monitored radio bands.

Preserved reduction:

    Strong Geomagnetic Event
    ≠
    Necessary Local ELF/MF/HF Background Anomaly

This event is a candidate for quantitative comparative reconstruction.

---

# 33. IMPORTANT-EVENT COMMENTARY BOUNDARY

The SOS70 commentary contains interpretive language concerning possible future developments.

Such language must be classified separately from measured data.

Object classes:

    measured condition
    official or upstream forecast
    SOS70 analysis
    informal interpretation
    speculative commentary

Boundary:

    Commentary
    ≠
    Forecast Product

    Impression
    ≠
    Evidence

---

# 34. FORECAST PRODUCTS

The system contains forecast statements regarding:

    solar activity
    M-class flare possibility
    proton-event probability
    high-energy electron flux
    geomagnetic activity
    CME influence
    coronal-hole high-speed streams

Each forecast must preserve:

    issue time
    valid interval
    upstream source
    model
    confidence
    outcome
    expiry

Forecasts must not silently become observations after the fact.

---

# 35. SOURCE AND UPSTREAM DEPENDENCY MAP

## Local SOS70 sources

    ELF antenna system
    Schumann resonance processing
    TOMION ionosonde
    local MF/HF monitoring
    local ionospheric derived products

## External or integrated sources

    orbital solar X-ray measurements
    solar active-region information
    coronagraph imagery
    CME analysis
    solar-wind L1 measurements
    proton flux
    electron flux
    Kp
    Ap
    F10.7
    Wolf number
    space-weather forecasts

The exact upstream source of each imported product remains to be recorded.

---

# 36. TIME NORMALIZATION

SOS70 uses:

    Tomsk decree time
    UTC+7

Required conversion:

    UTC = Tomsk local time − 7 hours

Every record must preserve:

    source local time
    source time-zone declaration
    normalized UTC time
    conversion method

Boundary:

    Same Calendar Date
    ≠
    Same UTC Interval

---

# 37. COPYRIGHT AND REUSE STATE

The SOS70 pages state that site materials are protected by copyright and that copying, distribution, or other use requires prior permission from the rights holder.

Current governance state:

    private inspection:
    permitted within bounded research review

    public repository upload of source images:
    HOLD

    redistribution:
    HOLD

    mathematical reconstruction:
    DERIVED-WORK REVIEW REQUIRED

    citation and source linking:
    PERMITTED SUBJECT TO NORMAL ATTRIBUTION

No source image should be committed publicly until permission or a defensible reuse basis is established.

---

# 38. ASSET INVENTORY STATE

Known candidate asset inventory now includes approximately:

    original OBS-EE transfer:
    12 assets

    SOS70 scientific and ionospheric expansion:
    multiple assets

    SOS70 weekly solar X-ray archive:
    multiple weekly images

    seasonal–diurnal model maps:
    multiple images

    long-period trend figure:
    1 image

Current candidate total:

    approximately 63 assets

This is not yet a final count.

Required operations:

    enumerate exact filenames
    compute hashes
    detect duplicate images
    identify duplicate date windows
    assign unique asset identifiers
    classify copyright state
    preserve repository policy

---

# 39. MATHEMATICAL IMAGE RECONSTRUCTION

## 39.1 Reconstructable product classes

    Schumann sonogram
    F1–F4 frequency traces
    A1–A4 amplitude traces
    Q1–Q4 quality-factor traces
    MF/HF spectrogram
    ionogram
    critical-frequency traces
    virtual-height traces
    vertical plasma-transfer traces
    X-ray class charts
    F10.7 and Wolf-number graphs
    Ap graphs
    Kp graphs
    seasonal–diurnal frequency maps
    long-period trend curves

## 39.2 Reconstruction chain

    source image
    →
    image integrity hash
    →
    plot-region detection
    →
    axis calibration
    →
    colour or trace segmentation
    →
    pixel-to-unit conversion
    →
    uncertainty estimate
    →
    machine-readable output
    →
    validation report

## 39.3 Required labels

Every reconstructed dataset must state:

    DISPLAY-DERIVED
    APPROXIMATE
    UNCERTAINTY-BOUND
    NON-SUBSTITUTIVE FOR RAW DATA

---

# 40. RECONSTRUCTION UNCERTAINTY

Uncertainty sources include:

    pixel resolution
    axis-label resolution
    line thickness
    anti-aliasing
    JPEG compression
    colour quantization
    gridline overlap
    label overlap
    hidden values
    interpolation
    chart scaling
    unknown source smoothing
    unknown original precision

No reconstructed value may imply precision finer than the display supports.

---

# 41. DUPLICATE DETECTION

Duplicate analysis must compare:

    filename
    byte length
    SHA-256 hash
    perceptual hash
    dimensions
    date range
    visible labels
    pixel similarity

Possible dispositions:

    BYTE IDENTICAL
    PIXEL IDENTICAL
    VISUALLY EQUIVALENT
    SAME DATE RANGE / DIFFERENT RENDER
    UNIQUE
    UNKNOWN

Boundary:

    Same Date Range
    ≠
    Independent Observation

---

# 42. DATA-QUALITY FLAGS

Required SOS70 quality flags:

    DATA COMPLETE
    MISSING DATA
    LOCAL LIGHTNING
    TECHNOGENIC INTERFERENCE
    POSSIBLE CLIPPING
    POSSIBLE SATURATION
    CONFIGURATION CHANGE
    FORECAST
    OBSERVATION
    DERIVED VALUE
    EXTERNAL SOURCE
    TIMESTAMP UNRESOLVED
    COPYRIGHT HOLD
    DUPLICATE CANDIDATE
    RECONSTRUCTION APPROXIMATE

---

# 43. SCIENTIFIC STRENGTHS

The reconstructed SOS70 system has several methodological strengths:

    long-term continuous monitoring objective
    documented ELF instrument chain
    explicit sampling rate
    explicit spectral processing
    explicit modal-parameter definitions
    missing-data interpretation
    local-lightning interpretation
    technogenic-source acknowledgement
    multiple Schumann parameters
    ionospheric observation capability
    historical archive
    seasonal–diurnal empirical modelling
    distinction between Earth-directed and non-Earth-directed CMEs
    documented counterexamples

---

# 44. SCIENTIFIC LIMITATIONS

Material limitations include:

    single ELF station
    incomplete raw-data access
    incomplete calibration records
    incomplete instrument-change history
    incomplete algorithm versioning
    incomplete uncertainty publication
    imported upstream products
    interpretation mixed with observations
    copyright restrictions
    public-image dependence
    forecast verification not yet reconstructed
    external independent replication not yet completed

---

# 45. ADVERSARIAL FINDINGS PRESERVED

    White bands can reflect local lightning or impulsive interference.

    Black bands represent missing data.

    Horizontal narrow-band lines can be technogenic.

    MF/HF changes can result from receiver configuration changes.

    High solar-flare counts may have no Earth effect when CMEs are not Earth-directed.

    A strong geomagnetic event may alter the ionosphere without producing a significant local electromagnetic-background anomaly.

    The long-period Schumann-frequency analysis did not identify an 11-year solar harmonic.

These findings materially constrain broad unified-energy interpretations.

---

# 46. CURRENT CAUSAL DISPOSITION

## Established

    lightning → ELF impulsive signals
    global lightning → Schumann resonances
    solar event → solar X-ray record
    Earth-directed solar-wind disturbance → geomagnetic response
    geomagnetic event → ionospheric response

## Investigable

    solar or geomagnetic disturbance → Schumann parameter change
    long-period climate variation → Schumann trend
    local weather → ELF measurement variation

## Not established

    solar flare count → local ELF anomaly
    Schumann anomaly → earthquake
    local ELF anomaly → global Earth-system event
    11-year solar cycle → long-term Tomsk Schumann trend
    all SOS70 panels → one unified physical process

---

# 47. REQUIRED INDEPENDENT COMPARISONS

    compare SOS70 ELF products with independent ELF stations

    compare lightning signatures with independent lightning networks

    compare SOS70 ionograms with independent ionosonde networks

    compare flare tables with official upstream solar event catalogues

    compare CMEs with official coronagraph and modelling products

    compare Kp and Ap with authoritative geomagnetic sources

    compare F10.7 and Wolf number with authoritative archives

    verify weekly forecasts against later observations

    test reconstructed image data against machine-readable SOS70 formats

---

# 48. REQUIRED REPOSITORY STRUCTURE

Recommended private research structure:

    research\OBS-EE-001\sources\sos70\
    research\OBS-EE-001\observations\sos70\
    research\OBS-EE-001\reviews\sos70\
    research\OBS-EE-001\reconstructed_data\sos70\
    research\OBS-EE-001\reconstruction_reports\sos70\
    research\OBS-EE-001\private_assets\sos70\

Public repository policy:

    source images:
    EXCLUDE UNTIL PERMISSION RESOLVED

    source metadata:
    INCLUDE

    source URLs:
    INCLUDE

    derived summaries:
    INCLUDE WITH ATTRIBUTION

    reconstructed numerical outputs:
    HOLD FOR COPYRIGHT AND METHODOLOGY REVIEW

---

# 49. REQUIRED MACHINE-READABLE RECORDS

Future machine-readable artifacts:

    SOS70_SOURCE_REGISTRY.json
    SOS70_ASSET_METADATA.json
    SOS70_PRODUCT_REGISTRY.json
    SOS70_RECONSTRUCTION_JOBS.json
    SOS70_RECONSTRUCTION_RESULTS.json
    SOS70_FORECAST_VERIFICATION.json
    SOS70_DUPLICATE_REPORT.json

---

# 50. NEXT AUTHORIZED ACTIONS

    freeze this system reconstruction
    update the source registry with SOS70 product records
    revise the asset manifest from twelve assets to expanded inventory
    retain SOS70 source images outside the public Git history
    create private hash inventory
    identify duplicates
    define image-reconstruction tests
    reconstruct one pilot chart before bulk extraction
    verify one reconstructed product against tabular source data

---

# 51. NEXT AUTHORIZED ARTIFACT

    07B_SOS70_RECONSTRUCTION_TEST_CONTRACT.md

That document will define:

    image classes
    coordinate calibration
    colour extraction
    trace extraction
    uncertainty rules
    duplicate detection
    validation thresholds
    refusal conditions
    output schemas
    pilot test selection

The recommended first pilot is:

    one weekly solar X-ray chart

because:

    axes are regular
    dates are explicit
    class bands are explicit
    event labels are visible
    bulletin records provide independent verification

---

# 52. PRESERVED BOUNDARIES

    Public Visualization
    ≠
    Raw Measurement

    Local ELF Signal
    ≠
    Global ELF State

    White Band
    ≠
    Global Energy Spike

    Missing Data
    ≠
    Low Signal

    Derived Resonance Parameter
    ≠
    Direct Instrument Reading

    High Historical R²
    ≠
    Forecast Validation

    Long-Term Harmonic
    ≠
    Cause Established

    Solar Flare
    ≠
    Earth-Directed CME

    Earth-Directed CME
    ≠
    Identical Local Response Everywhere

    Strong Geomagnetic Storm
    ≠
    Necessary Local ELF Anomaly

    Display Reconstruction
    ≠
    Raw-Data Recovery

    Copyrighted Source
    ≠
    Public Redistribution Permission

---

# 53. FINAL STATUS

    SOS70 system identity: ESTABLISHED
    Public architecture: SUBSTANTIALLY RECONSTRUCTED
    ELF antenna chain: ESTABLISHED FROM SOURCE DESCRIPTION
    Analog filtering: ESTABLISHED FROM SOURCE DESCRIPTION
    ADC characteristics: RECORDED
    Operational sampling rate: ESTABLISHED
    Spectral processing: ESTABLISHED
    Modal extraction method: ESTABLISHED
    Sonogram interpretation: ESTABLISHED
    Schumann parameter products: REGISTERED
    Long-term dataset: REGISTERED
    Seasonal–diurnal model: PARTIALLY RECONSTRUCTED
    Reported model fit: RECORDED
    Long-period trend result: RECORDED
    Ionosonde system: IDENTIFIED
    Ionospheric products: REGISTERED
    Plasma-transfer product: REGISTERED / ALGORITHM PARTIAL
    MF/HF system: IDENTIFIED
    External solar products: REGISTERED
    Geomagnetic products: REGISTERED
    Weekly bulletins: REGISTERED
    Forecast products: REGISTERED
    Natural counterexamples: REGISTERED
    Asset candidate count: APPROXIMATELY 63
    Duplicate inspection: REQUIRED
    Mathematical reconstruction: AUTHORIZED AS APPROXIMATION
    Raw-data equivalence: REFUSED
    Independent replication: NOT STARTED
    Copyright permission: UNRESOLVED
    Public image publication: HOLD
    Cross-domain causal inference: HOLD
    Prediction or escalation: NOT AUTHORIZED
    UNKNOWN → HOLD