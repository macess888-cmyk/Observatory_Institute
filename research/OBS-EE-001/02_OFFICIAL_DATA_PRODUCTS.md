# OBS-EE-001 — OFFICIAL DATA PRODUCTS 001

**Card ID:** OBS-EE-001  
**Title:** Earth–Sun Multi-Domain Observation Probe  
**Project:** Observatory OS  
**Date:** 2026-07-19  
**Status:** OFFICIAL PRODUCT RECONSTRUCTION OPEN  
**Operating Posture:** PRIMARY-SOURCE-FIRST / PRODUCT-TYPED / TIME-BOUND / NON-CERTIFYING / UNKNOWN → HOLD

---

# 1. PURPOSE

This document reconstructs the official upstream scientific products represented within the OBS-EE-001 transfer package.

The reconstruction separates:

    direct observation
    processed observation
    model output
    forecast
    event catalogue
    derived index
    public visualization
    interpretation

The purpose is to determine what each asset actually represents before any cross-domain comparison begins.

A product being official does not make every interpretation of that product official.

Boundary:

    Official Source
    ≠
    Official Interpretation of Surrounding Claims

---

# 2. PRODUCT RECONSTRUCTION RULE

Every transferred asset must be reconstructed through:

    source institution
    →
    instrument or model
    →
    measured or modelled variable
    →
    source product
    →
    observation or forecast time
    →
    processing
    →
    web visualization
    →
    local transferred file
    →
    viewer interpretation

A break anywhere in this chain forces:

    UNKNOWN → HOLD

---

# 3. REQUIRED PRODUCT FIELDS

Each official product record must include:

    product_id
    source institution
    mission or programme
    instrument or model
    product title
    product type
    measured or modelled variable
    physical unit
    wavelength or energy range
    spatial coverage
    native resolution
    source cadence
    displayed cadence
    observation time
    processing time
    forecast issue time
    forecast validity window
    retrieval time
    source time zone
    normalized UTC time
    product version
    model version
    processing level
    known quality flags
    missing-data behaviour
    saturation behaviour
    uncertainty
    archive availability
    source URL
    local asset
    integrity hash
    interpretation boundary
    Observatory OS status

Unknown fields must be recorded explicitly.

---

# 4. PRODUCT TYPE VOCABULARY

Permitted product classes:

    DIRECT OBSERVATION
    CALIBRATED OBSERVATION
    PROCESSED IMAGERY
    DERIVED OBSERVABLE
    NOWCAST
    FORECAST
    ENSEMBLE FORECAST
    EVENT CATALOGUE
    DERIVED INDEX
    PUBLIC SUMMARY
    UNKNOWN

These classes must not be collapsed.

---

# 5. NASA SOLAR DYNAMICS OBSERVATORY

## 5.1 Mission

    Source institution:
    National Aeronautics and Space Administration

    Mission:
    Solar Dynamics Observatory

    Abbreviation:
    SDO

    Primary relevance:
    Full-disk solar observations across multiple wavelengths
    and photospheric magnetic and intensity measurements

Official source family:

    https://sdo.gsfc.nasa.gov/
    https://sdo.gsfc.nasa.gov/data/

Initial product status:

    OFFICIAL SOURCE IDENTIFIED
    LOCAL ASSET MATCHING REQUIRED

---

# 6. ATMOSPHERIC IMAGING ASSEMBLY

## 6.1 Instrument identity

    Instrument:
    Atmospheric Imaging Assembly

    Abbreviation:
    AIA

    Product class:
    CALIBRATED OBSERVATION / PROCESSED IMAGERY

    General subject:
    Wavelength-specific solar-atmosphere emission

AIA imagery does not measure one generalized quantity called:

    solar energy

Each channel responds to different plasma conditions and emission lines.

Boundary:

    Shared Solar Disk
    ≠
    Same Physical Observable

---

## 6.2 AIA 171 Å

    Product ID:
    OFF-AIA-171-001

    Local asset:
    latest_1024_0171(1).mp4

    Channel:
    171 Å

    Product type:
    PROCESSED SOLAR OBSERVATION

    Primary scientific use:
    observation of coronal loops and quiet-coronal structure

    Spatial coverage:
    full visible solar disk

    Current local observation time:
    UNKNOWN

    Source cadence:
    REQUIRES VERIFICATION

    Displayed cadence:
    REQUIRES FILE INSPECTION

    Processing history:
    official source imagery
    web animation creation
    local download
    possible filename duplication suffix

    Primary limitations:
    image brightness alone does not determine flare class
    image brightness alone does not establish CME direction
    image brightness alone does not establish Earth impact
    colour is representational rather than natural visual colour

    Observatory OS status:
    IDENTIFIED / PROCESSED OBSERVATION / METADATA INCOMPLETE

---

## 6.3 AIA 193 Å

    Product ID:
    OFF-AIA-193-001

    Local asset:
    latest_1024_0193(1).mp4

    Channel:
    193 Å

    Product type:
    PROCESSED SOLAR OBSERVATION

    Primary scientific use:
    coronal structure
    coronal holes
    hot flare-related plasma under appropriate conditions

    Spatial coverage:
    full visible solar disk

    Current local observation time:
    UNKNOWN

    Primary limitations:
    dark regions may represent coronal holes but require contextual analysis
    bright regions require event and flux context
    imagery alone does not establish geoeffectiveness

    Observatory OS status:
    IDENTIFIED / PROCESSED OBSERVATION / METADATA INCOMPLETE

---

## 6.4 AIA 304 Å

    Product ID:
    OFF-AIA-304-001

    Local asset:
    latest_1024_0304(1).mp4

    Channel:
    304 Å

    Product type:
    PROCESSED SOLAR OBSERVATION

    Primary scientific use:
    chromosphere and transition-region structures
    prominences and filament-related features

    Spatial coverage:
    full visible solar disk

    Current local observation time:
    UNKNOWN

    Primary limitations:
    visible feature prominence does not establish Earth-directed propagation
    image scale and colour mapping affect visual interpretation

    Observatory OS status:
    IDENTIFIED / PROCESSED OBSERVATION / METADATA INCOMPLETE

---

## 6.5 AIA 131 Å

    Product ID:
    OFF-AIA-131-001

    Local asset:
    latest_1024_0131(1).mp4

    Channel:
    131 Å

    Product type:
    PROCESSED SOLAR OBSERVATION

    Primary scientific use:
    hot flare-region plasma and selected cooler structures

    Spatial coverage:
    full visible solar disk

    Current local observation time:
    UNKNOWN

    Primary limitations:
    apparent visual intensity must not be treated as flare classification
    frame normalization may alter perceived changes
    associated X-ray and event records are required

    Observatory OS status:
    IDENTIFIED / PROCESSED OBSERVATION / METADATA INCOMPLETE

---

# 7. HELIOSEISMIC AND MAGNETIC IMAGER

## 7.1 Instrument identity

    Instrument:
    Helioseismic and Magnetic Imager

    Abbreviation:
    HMI

    Primary observations:
    photospheric intensity
    line-of-sight magnetic-field observables
    vector magnetic-field products
    velocity and related photospheric observables

HMI products are produced through calibrated instrument measurements and processing pipelines.

Boundary:

    Displayed JPEG
    ≠
    Raw Instrument Measurement

---

## 7.2 HMI continuum intensitygram

    Product ID:
    OFF-HMI-INT-001

    Local assets:
    latest_1024_HMIIF(1).jpg
    Ic_flat_2d(1).mp4

    Product type:
    DERIVED OBSERVABLE / PROCESSED IMAGERY

    Subject:
    photospheric continuum intensity

    Visible features:
    solar disk
    sunspots
    photospheric brightness structure

    Source timestamp visible in uploaded still:
    2026-07-19 03:15:00
    exact time standard requires confirmation

    Primary limitations:
    sunspot visibility does not establish eruptive potential by itself
    processed contrast may change feature prominence
    exact source series must be identified
    animation time interval must be reconstructed

    Observatory OS status:
    IDENTIFIED / TIMESTAMP PARTIAL / SERIES ID REQUIRED

---

## 7.3 HMI line-of-sight magnetogram

    Product ID:
    OFF-HMI-MAG-001

    Local assets:
    latest_1024_HMIBC(1).jpg
    M_color_2d(1).mp4

    Product type:
    DERIVED MAGNETIC-FIELD OBSERVABLE / PROCESSED IMAGERY

    Subject:
    line-of-sight photospheric magnetic flux density

    Instrument principle:
    magnetic-field inference from polarized spectral-line measurements

    Official cadence families:
    45-second line-of-sight product
    720-second derived product

    Spatial coverage:
    full visible solar disk

    Source timestamp visible in uploaded still:
    2026-07-19 03:15:00
    exact time standard requires confirmation

    Native physical quantity:
    magnetic flux density

    Candidate unit:
    Mx/cm² or equivalent Gauss representation
    exact displayed unit requires product-series verification

    Primary limitations:
    displayed colour indicates polarity representation
    line-of-sight geometry affects interpretation
    magnetic complexity does not by itself establish flare or CME outcome
    instrument and inversion artifacts must remain visible

    Observatory OS status:
    IDENTIFIED / DERIVED OBSERVABLE / SERIES ID REQUIRED

---

# 8. NOAA SPACE WEATHER PREDICTION CENTER

## 8.1 Product family

    Source institution:
    National Oceanic and Atmospheric Administration

    Operational centre:
    Space Weather Prediction Center

    Abbreviation:
    NOAA SWPC

Relevant official product families include:

    GOES X-ray flux
    solar-wind observations
    GOES proton flux
    GOES electron flux
    planetary K index
    auroral forecast products
    coronagraph imagery
    solar-region summaries
    solar and geophysical event reports
    alerts, watches and warnings
    forecast discussions

Official product interface:

    https://www.swpc.noaa.gov/products-and-data

Observatory OS status:

    OFFICIAL COMPLEMENTARY SOURCE FAMILY IDENTIFIED

---

## 8.2 GOES X-ray flux

    Product ID:
    OFF-NOAA-XRS-001

    Instrument family:
    GOES X-Ray Sensor

    Product type:
    DIRECT / CALIBRATED OBSERVATION

    Observed variable:
    full-disk solar X-ray flux

    Passbands:
    1–8 Å
    0.5–4 Å

    Common unit:
    W/m²

    Operational use:
    tracking solar flares
    radio-blackout assessment
    event classification context

    Known limitations:
    calibration intervals
    satellite eclipses
    data dropouts
    possible contamination under some energetic-particle conditions

    Required role in OBS-EE-001:
    compare visual active-region evolution with measured X-ray activity

    Boundary:
    Bright EUV Image
    ≠
    X-Ray Flare Classification

    Observatory OS status:
    OFFICIAL COMPLEMENTARY OBSERVATION

---

## 8.3 Real-time solar wind

    Product ID:
    OFF-NOAA-SW-001

    Product type:
    DIRECT / CALIBRATED IN-SITU OBSERVATION

    Candidate upstream spacecraft:
    DSCOVR
    ACE
    other operational sources as declared by NOAA

    Candidate variables:
    solar-wind speed
    proton density
    temperature
    interplanetary magnetic-field components

    Spatial context:
    upstream solar-wind monitoring near the Sun–Earth L1 region

    Required role:
    distinguish solar-disk imagery from measured near-Earth solar-wind conditions

    Primary limitation:
    upstream measurement is not identical to global magnetospheric response

    Observatory OS status:
    OFFICIAL COMPLEMENTARY OBSERVATION / EXACT PRODUCT SNAPSHOT REQUIRED

---

## 8.4 Planetary K index

    Product ID:
    OFF-NOAA-KP-001

    Product type:
    DERIVED GEOMAGNETIC INDEX / NOWCAST / FORECAST FAMILY

    Subject:
    planetary geomagnetic disturbance level

    Required distinctions:
    observed Kp
    estimated Kp
    forecast Kp
    local station K
    global planetary summary

    Boundary:
    Kp Forecast
    ≠
    Kp Observation

    Observatory OS status:
    OFFICIAL INDEX FAMILY / EXACT OBJECT REQUIRED

---

## 8.5 Coronagraph and CME context

    Product ID:
    OFF-NOAA-CME-001

    Product type:
    PROCESSED OBSERVATION / EVENT ANALYSIS / FORECAST INPUT

    Candidate product sources:
    LASCO coronagraph
    NOAA coronagraph products
    operational CME analysis
    WSA–Enlil modelling

    Required role:
    determine whether a solar eruption exists
    estimate direction
    estimate speed
    assess possible Earth encounter

    Boundary:
    Solar Active Region
    ≠
    Earth-Directed CME

    Observatory OS status:
    COMPLEMENTARY SOURCE FAMILY / EVENT MATCHING REQUIRED

---

# 9. GFZ DATA-ASSIMILATIVE RADIATION-BELT FORECAST

## 9.1 Product identity

    Product ID:
    OFF-GFZ-RB-001

    Source institution:
    GFZ German Research Centre for Geosciences

    Product:
    Data-assimilative Radiation Belt Forecast

    Local asset:
    Forecast_UTC_E_1_MeV_PA_50_latest_mean_ensemble(1).mp4

    Product type:
    ENSEMBLE FORECAST / DATA-ASSIMILATIVE MODEL OUTPUT

    Forecast subject:
    1 MeV electron flux

    Pitch-angle reference in filename:
    PA 50
    exact definition requires source-product confirmation

    Forecast horizon:
    two days

    Update cadence:
    automatically generated hourly

    Model:
    VERB

    Declared input families:
    radiation-belt observations
    ACE data
    GOES data
    previous and recent Kp
    forecast Kp

    Declared version:
    Version 2.0 identified in current official documentation

    Magnetic-field model:
    T89 identified in current official documentation

    Primary boundary:
    Forecast Mean
    ≠
    Direct Measurement

    Required metadata:
    forecast issue time
    validity start and end
    model version
    ensemble definition
    input data cutoff
    data-assimilation window
    observed verification data
    forecast skill

    Observatory OS status:
    OFFICIAL FORECAST / METADATA EXTRACTION REQUIRED

---

# 10. GFZ AURORAL ACTIVITY FORECAST

## 10.1 Product identity

    Product ID:
    OFF-GFZ-AUR-001

    Source institution:
    GFZ German Research Centre for Geosciences

    Product:
    Aurora Activity Forecast

    Local asset:
    aurora_forecast_browser(1).webm

    Product type:
    FORECAST / MODEL OUTPUT

    Candidate driving input:
    Kp forecast or Kp-related geomagnetic input

    Forecast subject:
    predicted auroral activity or boundary

    Required metadata:
    issue time
    valid time
    hemisphere
    model version
    Kp input source
    forecast horizon
    spatial grid
    verification method
    uncertainty

    Primary boundary:
    Predicted Aurora
    ≠
    Observed Aurora

    Additional observation requirements:
    ground cameras
    satellite observations
    cloud cover
    local darkness
    geographic visibility

    Observatory OS status:
    OFFICIAL FORECAST / MODEL DOCUMENTATION REQUIRED

---

# 11. USGS ANSS COMCAT

## 11.1 Catalogue identity

    Product ID:
    OFF-USGS-COMCAT-001

    Source institution:
    United States Geological Survey

    Catalogue:
    ANSS Comprehensive Earthquake Catalog

    Abbreviation:
    ComCat

    Product type:
    EVENT CATALOGUE

    Recorded event information may include:
    hypocentre
    origin time
    magnitude
    magnitude type
    source network
    phase picks
    amplitudes
    moment tensors
    focal mechanisms
    macroseismic products
    tectonic summaries

    Time standard:
    UTC

    Important revision fields:
    event identifier
    product identifier
    source
    update time
    preferred product
    event updated time

    Important limitations:
    events may be revised
    preferred identifiers may change
    magnitude estimates may change
    network completeness differs by region and time
    depth uncertainty may be substantial
    catalogue products may have multiple contributing sources

    Observatory OS status:
    OFFICIAL SEISMIC RECONSTRUCTION SOURCE

---

## 11.2 Magnitude boundary

Earthquake magnitude is logarithmic.

A one-unit increase commonly corresponds approximately to:

    ten times greater recorded wave amplitude
    approximately thirty-two times greater released energy

Therefore:

    magnitude values must not be added
    as though they were linear energy quantities

Boundary:

    Sum of Magnitudes
    ≠
    Sum of Physical Energy

Required alternative comparisons:

    event count
    maximum magnitude
    summed seismic moment
    estimated radiated energy
    magnitude-threshold counts
    declustered event count
    aftershock-inclusive count
    regional completeness-adjusted count

---

# 12. VOLCANO DISCOVERY GLOBAL SEISMIC ACTIVITY LEVEL

## 12.1 Display identity

    Product ID:
    DER-VD-SEISMIC-001

    Source publisher:
    Volcano Discovery

    Local asset:
    seismic-activity-level(1).png

    Display date:
    19 July 2026

    Displayed status:
    MODERATE

    Product type:
    PUBLIC DERIVED INDEX

    Displayed right-axis term:
    Combined magnitude

    Current interpretation:
    compact public activity summary

    Not yet established:
    aggregation formula
    magnitude threshold
    regional weighting
    catalogue source
    update latency
    revision treatment
    aftershock treatment
    completeness model

    Primary boundary:
    Public Activity Level
    ≠
    Standard Global Seismic Observable

    Required reconstruction:
    identify source catalogue
    reproduce daily event selection
    derive exact calculation
    compare against linear-energy and moment-based alternatives
    test sensitivity to one large event
    test UTC-day versus rolling-window result

    Observatory OS status:
    DERIVED INDEX / METHOD RECONSTRUCTION REQUIRED / HOLD

---

# 13. TOMSK SCHUMANN-RESONANCE SPECTROGRAM

## 13.1 Product identity

    Product ID:
    OBS-TOMSK-ELF-001

    Local asset:
    provider(1).jpg

    Product type:
    PROCESSED SINGLE-STATION OBSERVATION

    Candidate measured domain:
    extremely low-frequency electric-field activity

    Displayed frequency range:
    approximately 0–40 Hz

    Displayed interval:
    17–19 July 2026

    Candidate resonance bands visible:
    approximately 8 Hz
    approximately 14 Hz
    approximately 20 Hz
    approximately 26 Hz

    Spatial coverage:
    single station

    White intervals:
    visually saturated or clipped regions
    exact status not independently established

    Known possible contamination:
    local weather
    atmospheric electricity
    wind-induced vibration
    microphonic behaviour
    lightning
    electrical interference
    automatic gain changes
    clipping
    packet loss
    missing data
    instrument restart

    Required official documentation:
    station operator
    instrument model
    antenna design
    channel identity
    sampling rate
    gain
    calibration
    local time zone
    colour scale
    clipping threshold
    missing-data representation
    archive access
    raw time series

    Primary boundary:
    White Spectrogram Region
    ≠
    Extraordinary Global Energy Event

    Current classification:
    SATURATION OR INTERFERENCE POSSIBLE
    CAUSE UNRESOLVED

    Observatory OS status:
    OBSERVATION / SINGLE STATION / QUALITY HOLD

---

# 14. TIME NORMALIZATION ISSUE

Several transferred assets are labelled or appear to contain:

    19 July 2026

The collection and review process began on:

    18 July 2026
    local user time

This discrepancy may result from:

    UTC date rollover
    source-station local time
    forecast validity date
    source server clock
    file-generation clock
    retrieval clock
    future-dated metadata
    display-window extension

Required temporal fields:

    observation_time
    product_generation_time
    forecast_issue_time
    forecast_valid_time
    source_update_time
    retrieval_time
    local_file_creation_time
    local_file_modification_time

No unified chronology may be claimed until all fields are normalized to UTC.

Current chronology status:

    UNRESOLVED
    UNKNOWN → HOLD

---

# 15. TRANSFERRED ASSET MAP

## Solar observations

    latest_1024_0171(1).mp4
    latest_1024_0193(1).mp4
    latest_1024_0304(1).mp4
    latest_1024_0131(1).mp4
    latest_1024_HMIIF(1).jpg
    latest_1024_HMIBC(1).jpg
    Ic_flat_2d(1).mp4
    M_color_2d(1).mp4

## Space-weather forecasts

    Forecast_UTC_E_1_MeV_PA_50_latest_mean_ensemble(1).mp4
    aurora_forecast_browser(1).webm

## Atmospheric-electromagnetic observation

    provider(1).jpg

## Seismic derived index

    seismic-activity-level(1).png

All asset hashes, byte lengths, media durations, frame dimensions and embedded timestamps remain to be recorded.

---

# 16. OFFICIAL PRODUCT COMPARISON MATRIX

## Solar imagery

    Source:
    NASA SDO

    Type:
    processed observation

    Directly supports:
    wavelength-specific solar structure

    Does not directly support:
    Earth-directed CME
    geomagnetic severity
    earthquake effect

## HMI magnetogram

    Source:
    NASA SDO / JSOC

    Type:
    derived magnetic observable

    Directly supports:
    photospheric line-of-sight magnetic structure

    Does not directly support:
    eruption probability without analysis
    terrestrial consequence

## GOES X-ray flux

    Source:
    NOAA

    Type:
    calibrated observation

    Directly supports:
    solar X-ray flare measurement

    Does not directly support:
    CME direction
    seismic consequence

## Solar-wind data

    Source:
    NOAA operational spacecraft products

    Type:
    in-situ observation

    Directly supports:
    upstream plasma and magnetic conditions

    Does not directly support:
    global seismic triggering

## Radiation-belt product

    Source:
    GFZ

    Type:
    ensemble forecast

    Directly supports:
    predicted energetic-electron conditions

    Does not directly support:
    observed radiation-belt outcome without later verification

## Aurora product

    Source:
    GFZ

    Type:
    forecast

    Directly supports:
    predicted auroral activity

    Does not directly support:
    current visible aurora at a specific location

## ComCat

    Source:
    USGS and contributing networks

    Type:
    event catalogue

    Directly supports:
    recorded earthquake-event parameters

    Does not directly support:
    one unified global activity variable

## Volcano Discovery chart

    Source:
    public derived interface

    Type:
    derived index

    Directly supports:
    publisher’s summarized activity presentation

    Does not directly support:
    conserved physical global seismic state

## Tomsk spectrogram

    Source:
    single station

    Type:
    processed observation

    Directly supports:
    displayed local station spectral response

    Does not directly support:
    global anomaly without distributed confirmation

---

# 17. REQUIRED COMPLEMENTARY PRODUCTS

Before interpreting Earth-directed solar effects, obtain:

    GOES X-ray flux
    official flare event record
    active-region summary
    coronagraph observation
    CME event analysis
    solar-wind speed
    solar-wind density
    IMF magnitude
    IMF Bz
    observed Kp
    Dst or comparable storm index
    GOES particle flux
    auroral observation where relevant

Before interpreting seismic change, obtain:

    USGS ComCat event list
    magnitude types
    event revisions
    catalogue completeness threshold
    declustered catalogue
    seismic moment where available
    aftershock-family identity
    UTC event windows

Before interpreting Schumann anomalies, obtain:

    raw station data
    local weather
    lightning records
    gain and saturation information
    missing-data flags
    distributed station comparison
    calibration documentation

---

# 18. PRODUCT ADMISSION CONDITIONS

An official product may be admitted for bounded comparison only when:

    source identity is established
    product identity is established
    object type is established
    observed or modelled variable is established
    physical unit is established
    observation or forecast time is established
    forecast horizon is established where applicable
    processing history is sufficiently known
    source limitations are recorded
    local asset identity is preserved
    integrity hash is recorded

Official origin alone is insufficient.

---

# 19. PRODUCT HOLD CONDITIONS

A product remains HOLD when:

    local asset cannot be matched to source product
    timestamp is unresolved
    source series is unknown
    unit is unknown
    object type is ambiguous
    forecast is presented as observation
    processing history is missing
    source asset may be stale
    file appears future-dated without explanation
    saturation state is unresolved
    media chronology cannot be reconstructed
    model version is unknown
    transformation history is unknown

---

# 20. CURRENT FINDINGS

    NASA SDO source family:
    IDENTIFIED

    AIA channels:
    IDENTIFIED

    HMI intensity product:
    IDENTIFIED / EXACT SERIES REQUIRED

    HMI magnetogram:
    IDENTIFIED / EXACT SERIES REQUIRED

    NOAA X-ray product:
    IDENTIFIED

    NOAA solar-wind family:
    IDENTIFIED

    NOAA geomagnetic family:
    IDENTIFIED

    GFZ radiation-belt forecast:
    IDENTIFIED / VERSION PARTIAL

    GFZ auroral forecast:
    IDENTIFIED / MODEL DETAILS PARTIAL

    USGS ComCat:
    IDENTIFIED

    Volcano Discovery method:
    UNRESOLVED

    Tomsk station method:
    INCOMPLETE

    Asset-to-source matching:
    PARTIAL

    UTC normalization:
    NOT COMPLETE

    Integrity hashes:
    NOT RECORDED

    Comparative inference:
    HOLD

    Causal inference:
    HOLD

    Warning or prediction:
    NOT AUTHORIZED

---

# 21. NEXT AUTHORIZED ARTIFACT

    03_SUPPORTING_HYPOTHESES.md

That document will register the strongest published claims supporting:

    solar–seismic association
    electromagnetic earthquake precursors
    lithosphere–atmosphere–ionosphere coupling
    Schumann-resonance anomaly interpretation
    planetary and tidal hypotheses
    unified Earth-system interpretations

Every supporting claim will be paired with its required evidence burden and future adversarial comparison.

---

# 22. FINAL STATUS

    Official source reconstruction: ESTABLISHED
    Product-type vocabulary: ESTABLISHED
    Solar products: REGISTERED
    Space-weather products: REGISTERED
    Seismic catalogue: REGISTERED
    Derived seismic index: REGISTERED / METHOD UNKNOWN
    Schumann product: REGISTERED / QUALITY UNKNOWN
    Time discrepancy: RECORDED
    Product limitations: RECORDED
    Local asset matching: PARTIAL
    Provenance completion: REQUIRED
    Cross-domain comparison: HOLD
    Causal inference: HOLD
    Prediction or escalation: NOT AUTHORIZED
    UNKNOWN → HOLD