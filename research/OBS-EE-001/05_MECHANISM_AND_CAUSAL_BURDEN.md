# OBS-EE-001 — MECHANISM AND CAUSAL BURDEN 001

**Card ID:** OBS-EE-001  
**Title:** Earth–Sun Multi-Domain Observation Probe  
**Project:** Observatory OS  
**Date:** 2026-07-19  
**Status:** MECHANISM AND CAUSAL BURDEN OPEN  
**Operating Posture:** MECHANISM-FIRST / QUANTITATIVE-BURDEN-FIRST / DIRECTION-SEPARATED / NON-CERTIFYING / UNKNOWN → HOLD

---

# 1. PURPOSE

This document reduces every proposed relationship in OBS-EE-001 into an explicit causal burden.

Each proposed causal pathway must identify:

    source condition
    transmitted physical quantity
    transmission medium
    physical transformation
    spatial reach
    temporal lag
    coupling target
    expected response
    quantitative magnitude
    uncertainty
    alternative explanations
    falsification condition
    replication requirement

A causal arrow may not be retained merely because:

    two panels appear together
    two variables move near the same time
    a statistical association is reported
    a physical mechanism is imaginable
    an anomaly remains unexplained
    an official scientific product is displayed nearby

---

# 2. GOVERNING CAUSAL RULE

Every candidate relationship must be reconstructed in both directions.

Forward reconstruction:

    source condition
    →
    transmitted quantity
    →
    propagation
    →
    target interaction
    →
    measurable response
    →
    observed record
    →
    interpretation

Reverse burden:

    proposed claim
    →
    required observable
    →
    required instrument
    →
    required mechanism
    →
    required quantitative sufficiency
    →
    required controls
    →
    required replication

Any unreconstructed link forces:

    UNKNOWN → HOLD

---

# 3. CAUSAL STATUS VOCABULARY

Permitted statuses:

    PHYSICALLY ESTABLISHED
    MECHANISM ESTABLISHED
    MECHANISM PLAUSIBLE
    MECHANISM PROPOSED
    ASSOCIATION REPORTED
    PARTIALLY MODELLED
    QUANTITATIVE SUFFICIENCY UNESTABLISHED
    DIRECTIONALITY UNRESOLVED
    CONFOUNDED
    REPLICATION REQUIRED
    NOT ESTABLISHED
    UNSUPPORTED
    UNKNOWN → HOLD

Only the following conditions permit:

    CAUSAL PATH ESTABLISHED

Required conditions:

    source identified
    transmitted quantity identified
    transformation identified
    directionality demonstrated
    temporal order preserved
    spatial reach established
    magnitude sufficient
    competing mechanisms controlled
    relationship replicated independently
    falsification test survived

---

# 4. REQUIRED MECHANISM FIELDS

Every candidate pathway must record:

    mechanism_id
    source domain
    target domain
    source object
    target object
    source condition
    transmitted quantity
    physical unit
    transmission medium
    transformation
    attenuation
    spatial scale
    temporal scale
    expected lag
    target sensitivity
    expected measurable response
    required instruments
    quantitative estimate
    uncertainty
    confounders
    alternative direction
    common-cause candidates
    falsification condition
    replication state
    current disposition

Blank fields are prohibited in a completed mechanism record.

Unknown fields must remain:

    UNKNOWN

---

# 5. MECHANISM M-001 — SUN TO SOLAR WIND

    Mechanism ID:
    M-001

    Source domain:
    SOLAR

    Target domain:
    SOLAR-WIND

    Status:
    PHYSICALLY ESTABLISHED

## 5.1 Source condition

    coronal heating
    magnetic-field evolution
    coronal holes
    active-region eruption
    coronal mass ejection

## 5.2 Transmitted quantities

    plasma
    protons
    electrons
    magnetic field
    momentum
    kinetic energy
    electromagnetic radiation

## 5.3 Transmission medium

    heliosphere

## 5.4 Expected measurements

    solar-wind speed
    proton density
    proton temperature
    interplanetary magnetic-field magnitude
    IMF components
    energetic-particle flux

## 5.5 Required instruments

    coronagraphs
    heliospheric imagers
    ACE
    DSCOVR
    GOES
    other in-situ spacecraft

## 5.6 Current burden

This pathway is physically established.

Specific Earth-directed impact still requires:

    event identity
    direction
    speed
    propagation model
    arrival observation

## 5.7 Observatory OS disposition

    GENERAL PATHWAY:
    ESTABLISHED

    SPECIFIC EVENT CONNECTION:
    REQUIRES EVENT MATCHING

---

# 6. MECHANISM M-002 — SOLAR WIND TO MAGNETOSPHERE

    Mechanism ID:
    M-002

    Source domain:
    SOLAR-WIND

    Target domain:
    MAGNETOSPHERIC

    Status:
    PHYSICALLY ESTABLISHED

## 6.1 Transmitted quantities

    plasma momentum
    dynamic pressure
    magnetic field
    electric field
    energetic particles

## 6.2 Physical interaction

    magnetopause compression
    magnetic reconnection
    plasma entry
    current-system modification
    energy transfer into magnetosphere

## 6.3 Important variables

    solar-wind speed
    proton density
    dynamic pressure
    IMF magnitude
    IMF Bz
    electric-field proxies

## 6.4 Expected responses

    magnetopause movement
    geomagnetic disturbance
    ring-current development
    auroral activity
    radiation-belt change
    geomagnetic-index change

## 6.5 Required measurements

    upstream solar wind
    magnetometers
    Kp
    Dst
    satellite plasma measurements
    auroral observations

## 6.6 Observatory OS disposition

    GENERAL PATHWAY:
    ESTABLISHED

    EVENT-SPECIFIC EFFECT:
    REQUIRES SYNCHRONIZED OBSERVATION

---

# 7. MECHANISM M-003 — MAGNETOSPHERE TO RADIATION BELTS

    Mechanism ID:
    M-003

    Source domain:
    MAGNETOSPHERIC

    Target domain:
    RADIATION-BELT

    Status:
    PHYSICALLY ESTABLISHED

## 7.1 Candidate processes

    radial diffusion
    wave-particle interaction
    particle acceleration
    particle loss
    magnetopause shadowing
    pitch-angle scattering

## 7.2 Transmitted quantities

    electromagnetic-wave energy
    electric and magnetic fluctuations
    energetic-particle phase-space redistribution

## 7.3 Expected measurements

    electron flux
    proton flux
    phase-space density
    pitch-angle distribution
    L-shell distribution

## 7.4 Current transferred object

    GFZ data-assimilative radiation-belt forecast

## 7.5 Boundary

    Physical pathway established
    ≠
    Forecast verified

## 7.6 Observatory OS disposition

    PATHWAY:
    ESTABLISHED

    TRANSFERRED FORECAST:
    REQUIRES LATER OBSERVATIONAL VERIFICATION

---

# 8. MECHANISM M-004 — MAGNETOSPHERE TO AURORA

    Mechanism ID:
    M-004

    Source domain:
    MAGNETOSPHERIC

    Target domains:
    IONOSPHERIC
    AURORAL

    Status:
    PHYSICALLY ESTABLISHED

## 8.1 Candidate processes

    particle precipitation
    field-aligned currents
    magnetotail reconnection
    ionospheric excitation

## 8.2 Transmitted quantities

    energetic electrons
    energetic ions
    electric currents
    electromagnetic energy

## 8.3 Expected response

    optical aurora
    ionospheric conductivity change
    current-system change
    radio-propagation effects

## 8.4 Transferred object

    GFZ auroral forecast

## 8.5 Boundary

    Auroral forecast
    ≠
    Auroral observation

## 8.6 Observatory OS disposition

    GENERAL PATHWAY:
    ESTABLISHED

    SPECIFIC FORECAST ACCURACY:
    UNVERIFIED

---

# 9. MECHANISM M-005 — LIGHTNING TO SCHUMANN RESONANCES

    Mechanism ID:
    M-005

    Source domain:
    LIGHTNING

    Target domain:
    SCHUMANN-RESONANCE

    Status:
    PHYSICALLY ESTABLISHED

## 9.1 Source condition

    global lightning discharges

## 9.2 Transmitted quantity

    extremely low-frequency electromagnetic radiation

## 9.3 Transmission medium

    Earth–ionosphere cavity

## 9.4 Physical transformation

Lightning impulses excite resonant electromagnetic modes within the cavity.

## 9.5 Expected response

    spectral bands near characteristic resonance frequencies
    amplitude variation
    frequency variation
    bandwidth variation

## 9.6 Required measurements

    calibrated ELF stations
    lightning networks
    ionospheric context
    synchronized UTC records

## 9.7 Important confounders

    local electrical noise
    local weather
    station gain
    clipping
    missing data
    instrument vibration

## 9.8 Observatory OS disposition

    GENERAL MECHANISM:
    ESTABLISHED

    TOMSK WHITE INTERVAL CAUSE:
    UNRESOLVED

---

# 10. MECHANISM M-006 — LOCAL WEATHER TO ELF SENSOR

    Mechanism ID:
    M-006

    Source domain:
    ATMOSPHERIC

    Target domain:
    SCHUMANN-RESONANCE INSTRUMENT

    Status:
    MECHANISM PLAUSIBLE
    INSTRUMENT-SPECIFIC

## 10.1 Candidate source conditions

    wind
    local atmospheric electricity
    precipitation
    lightning
    temperature variation
    humidity variation

## 10.2 Candidate interactions

    mast vibration
    cable movement
    microphonic response
    grounding change
    local electric-field change
    amplifier response

## 10.3 Expected instrument effects

    broadband noise
    vertical streaking
    apparent amplitude increase
    clipping
    saturation
    spectral contamination

## 10.4 Required evidence

    station weather record
    station maintenance record
    gain history
    calibration record
    local lightning record
    raw waveform
    reference channel

## 10.5 Observatory OS disposition

    ALTERNATIVE EXPLANATION:
    ACTIVE

    GLOBAL INTERPRETATION:
    HOLD

---

# 11. MECHANISM M-007 — SOLAR OR GEOMAGNETIC CHANGE TO SCHUMANN OBSERVATION

    Mechanism ID:
    M-007

    Source domains:
    SOLAR
    SOLAR-WIND
    MAGNETOSPHERIC

    Target domain:
    SCHUMANN-RESONANCE

    Status:
    MECHANISM PLAUSIBLE IN GENERAL
    EVENT-SPECIFIC CONNECTION UNESTABLISHED

## 11.1 Candidate pathway

    solar or geomagnetic disturbance
    →
    ionospheric conductivity or cavity-boundary change
    →
    Earth–ionosphere cavity response
    →
    altered resonance frequency, amplitude, or quality factor
    →
    station observation

## 11.2 Required quantities

    ionospheric conductivity
    effective cavity height
    geomagnetic indices
    solar-wind conditions
    lightning-source distribution
    ELF amplitude and frequency

## 11.3 Required controls

    local weather
    global lightning
    instrument gain
    multiple ELF stations
    day–night variation
    seasonal variation

## 11.4 Refusal condition

A visual coincidence between solar imagery and one spectrogram is insufficient.

## 11.5 Observatory OS disposition

    GENERAL COUPLING:
    INVESTIGABLE

    CURRENT ASSET CONNECTION:
    NOT ESTABLISHED

---

# 12. MECHANISM M-008 — TECTONIC STRESS TO EARTHQUAKE

    Mechanism ID:
    M-008

    Source domain:
    LITHOSPHERIC / SEISMIC

    Target domain:
    SEISMIC

    Status:
    PHYSICALLY ESTABLISHED GENERAL PROCESS

## 12.1 Source condition

    tectonic loading
    fault stress accumulation
    fluid pressure
    frictional instability

## 12.2 Physical transformation

    stored elastic strain
    →
    rupture initiation
    →
    fault slip
    →
    seismic-wave radiation

## 12.3 Transmitted quantities

    stress
    strain
    seismic moment
    radiated seismic energy

## 12.4 Expected measurements

    hypocentre
    origin time
    magnitude
    seismic moment
    waveform
    focal mechanism
    displacement

## 12.5 Observatory OS disposition

    GENERAL EARTHQUAKE PROCESS:
    ESTABLISHED

    PRECISE EVENT PREDICTION:
    NOT ESTABLISHED

---

# 13. MECHANISM M-009 — EARTHQUAKE TO LOCAL ELECTROMAGNETIC EFFECT

    Mechanism ID:
    M-009

    Source domain:
    SEISMIC / LITHOSPHERIC

    Target domain:
    ATMOSPHERIC-ELECTROMAGNETIC

    Status:
    MECHANISM PROPOSED
    SOME OBSERVATIONS REPORTED
    ORIGIN DIFFICULT TO ESTABLISH

## 13.1 Candidate pathways

    rock fracture
    fluid movement
    electrokinetic effects
    piezoelectric effects
    charge-carrier activation
    triboelectric effects
    cable or instrument motion
    infrastructure disruption

## 13.2 Expected observations

    electric-field variation
    magnetic variation
    ULF signals
    atmospheric ionization
    local conductivity changes

## 13.3 Directionality issue

Some electromagnetic effects may occur:

    before rupture
    during rupture
    after rupture

These states must not be collapsed.

## 13.4 Required controls

    instrument vibration
    seismic-wave arrival
    power-grid effects
    lightning
    geomagnetic activity
    nearby reference stations

## 13.5 Observatory OS disposition

    LOCAL SECONDARY EFFECT:
    INVESTIGABLE

    RELIABLE PRECURSOR:
    NOT ESTABLISHED

---

# 14. MECHANISM M-010 — STRESSED ROCK TO ATMOSPHERIC OR IONOSPHERIC ANOMALY

    Mechanism ID:
    M-010

    Source domain:
    LITHOSPHERIC

    Target domains:
    ATMOSPHERIC-ELECTROMAGNETIC
    IONOSPHERIC

    Status:
    MECHANISM PROPOSED
    PARTIALLY MODELLED
    FIELD-SCALE SUFFICIENCY UNESTABLISHED

## 14.1 Candidate pathway

    stressed rock
    →
    charge activation
    →
    current or surface potential
    →
    air ionization or conductivity change
    →
    atmospheric electric-field change
    →
    ionospheric response

## 14.2 Required quantitative burden

    charge production rate
    current density
    crustal attenuation
    surface potential
    atmospheric transport
    spatial extent
    ionospheric field strength
    measurable TEC response

## 14.3 Scaling problem

Laboratory observations must be scaled to:

    fault dimensions
    crustal heterogeneity
    groundwater
    conductivity
    atmospheric conditions
    regional ionosphere

## 14.4 Observatory OS disposition

    CONCEPTUAL PATHWAY:
    REGISTERED

    FIELD-SCALE CAUSATION:
    NOT ESTABLISHED

---

# 15. MECHANISM M-011 — EARTHQUAKE PREPARATION TO TEC ANOMALY

    Mechanism ID:
    M-011

    Source domain:
    LITHOSPHERIC

    Target domain:
    IONOSPHERIC

    Status:
    ASSOCIATION REPORTED
    DIRECTIONALITY AND SPECIFICITY UNRESOLVED

## 15.1 Proposed pathway

    earthquake preparation
    →
    ground or atmospheric electrical process
    →
    vertical coupling
    →
    ionospheric plasma redistribution
    →
    TEC anomaly

## 15.2 Competing causes

    solar flare
    geomagnetic storm
    solar-wind variation
    atmospheric wave
    weather
    seasonal ionosphere
    GNSS geometry
    map processing

## 15.3 Required burden

    anomaly before event
    stable threshold
    spatial localization
    solar and geomagnetic exclusion
    matched non-event controls
    prospective prediction
    false-alarm measurement

## 15.4 Observatory OS disposition

    TEC ANOMALY:
    OBSERVABLE

    EARTHQUAKE CAUSATION:
    NOT ESTABLISHED

---

# 16. MECHANISM M-012 — SOLAR WIND TO EARTHQUAKE TRIGGERING

    Mechanism ID:
    M-012

    Source domain:
    SOLAR-WIND

    Target domain:
    SEISMIC

    Status:
    ASSOCIATION REPORTED
    MECHANISM PROPOSED
    QUANTITATIVE SUFFICIENCY UNESTABLISHED

## 16.1 Supporting claim

Changes in solar-wind proton density may alter the global ionosphere–Earth electrical environment.

A resulting electrical effect may perturb a fault already near failure.

## 16.2 Proposed chain

    solar-wind proton-density change
    →
    magnetospheric or ionospheric electrical change
    →
    changed Earth–ionosphere potential
    →
    current or voltage within conductive fault structures
    →
    reverse piezoelectric perturbation
    →
    rupture timing shift

## 16.3 Missing links

    event-specific ionospheric potential measurement
    current pathway into crust
    fault-specific conductivity
    voltage at fault
    induced stress magnitude
    sign of induced stress
    attenuation
    geographic localization
    reproducible one-day lag

## 16.4 Quantitative questions

    What field reaches the ground?
    What current enters the crust?
    What voltage reaches the fault?
    What stress change is produced?
    How does it compare with tidal stress?
    How does it compare with ordinary stress fluctuations?
    Why are selected faults affected and others not?
    Why is the lag stable?

## 16.5 Required replication

    independent solar-wind data
    independent earthquake catalogue
    preregistered thresholds
    declustered catalogue
    post-2016 validation
    prospective predictions
    mechanism measurement

## 16.6 Observatory OS disposition

    HYPOTHESIS:
    RETAINED FOR TESTING

    CAUSAL PATH:
    NOT ESTABLISHED

    WARNING USE:
    NOT AUTHORIZED

---

# 17. MECHANISM M-013 — LUNI-SOLAR TIDAL STRESS TO FAULT TRIGGERING

    Mechanism ID:
    M-013

    Source domains:
    LUNAR-GRAVITATIONAL
    SOLAR-GRAVITATIONAL

    Target domain:
    SEISMIC

    Status:
    PHYSICAL STRESS PERTURBATION ESTABLISHED
    EVENT-LEVEL TRIGGERING VALUE UNRESOLVED

## 17.1 Transmitted quantity

    gravitational tidal stress

## 17.2 Target

    fault plane
    surrounding crust
    fluids within fault system

## 17.3 Required calculation

    fault location
    fault orientation
    focal mechanism
    normal stress change
    shear stress change
    ocean loading
    Earth tide
    event time

## 17.4 Important boundary

    Tidal Stress Exists
    ≠
    Earthquake Prediction Established

## 17.5 Observatory OS disposition

    PHYSICAL FORCING:
    ESTABLISHED

    GENERAL PREDICTIVE VALUE:
    NOT ESTABLISHED

---

# 18. MECHANISM M-014 — PLANETARY GEOMETRY TO EARTHQUAKE

    Mechanism ID:
    M-014

    Source domain:
    PLANETARY-GEOMETRY

    Target domain:
    SEISMIC

    Status:
    MECHANISM UNSPECIFIED OR QUANTITATIVELY INSUFFICIENT

## 18.1 Required source definition

    planet or planets involved
    position
    distance
    mass
    alignment geometry
    time

## 18.2 Required transmitted quantity

One of the following must be explicitly identified:

    gravitational force
    tidal gradient
    electromagnetic field
    radiation
    particle flux
    other defined physical quantity

## 18.3 Required comparison

    lunar tide
    solar tide
    ocean loading
    atmospheric loading
    hydrological loading
    ordinary tectonic stress

## 18.4 Current failure

Most broad alignment claims do not provide:

    fault-specific forcing
    adequate magnitude
    stable lag
    prospective prediction
    multiple-testing correction
    independent replication

## 18.5 Observatory OS disposition

    POSITIONAL GEOMETRY:
    CALCULABLE

    SEISMIC CAUSATION:
    NOT ESTABLISHED

---

# 19. MECHANISM M-015 — SOLAR ACTIVITY TO HUMAN BIOLOGICAL OR PSYCHOLOGICAL EFFECT

    Mechanism ID:
    M-015

    Source domain:
    SOLAR / SPACE-WEATHER

    Target domain:
    HUMAN BIOLOGICAL OR PSYCHOLOGICAL

    Status:
    OUTSIDE CURRENT EMPIRICAL PACKAGE
    CLAIM BURDEN UNMET

## 19.1 Required pathway

Any claim must identify:

    solar variable
    terrestrial mediator
    exposure pathway
    biological target
    dose
    response
    timing
    effect size
    controls

## 19.2 Candidate mediators

    geomagnetic variation
    radiation exposure
    radio-frequency disruption
    light
    behavioural expectation

## 19.3 Major confounders

    sleep
    season
    weather
    media exposure
    expectation
    stress
    selection bias
    health conditions

## 19.4 Observatory OS disposition

    CURRENT ASSET PACKAGE:
    INSUFFICIENT

    HEALTH CLAIM:
    NOT AUTHORIZED

---

# 20. MECHANISM M-016 — MULTIPLE PANELS TO UNIFIED EARTH-ENERGY CLAIM

    Mechanism ID:
    M-016

    Source domain:
    INTERFACE / INTERPRETATION

    Target domain:
    CROSS-DOMAIN PUBLIC CLAIM

    Status:
    NO PHYSICAL UNIFICATION ESTABLISHED

## 20.1 Displayed quantities

    EUV intensity
    magnetic flux density
    electron flux forecast
    auroral forecast
    local ELF amplitude
    earthquake magnitude-derived index
    planetary geometry

## 20.2 Missing common variable

No single common measurement has been defined with:

    shared unit
    shared scale
    shared transformation
    shared spatial coverage
    shared causal direction

## 20.3 Human-factors pathway

    scientific panels displayed together
    →
    perceived simultaneity
    →
    perceived coherence
    →
    inferred unified energy
    →
    inferred consequence

## 20.4 Observatory OS disposition

    INTERFACE-INDUCED SYNTHESIS:
    PLAUSIBLE

    PHYSICAL UNIFICATION:
    NOT ESTABLISHED

---

# 21. CAUSAL-CANDIDATE DIRECTION MATRIX

## Sun to magnetosphere

    Direction:
    Sun → magnetosphere

    Standing:
    ESTABLISHED

## Magnetosphere to radiation belts

    Direction:
    Magnetosphere → radiation belts

    Standing:
    ESTABLISHED

## Magnetosphere to aurora

    Direction:
    Magnetosphere → aurora

    Standing:
    ESTABLISHED

## Lightning to Schumann resonances

    Direction:
    Lightning → Schumann resonances

    Standing:
    ESTABLISHED

## Local weather to ELF sensor

    Direction:
    Local weather → sensor response

    Standing:
    PLAUSIBLE / INSTRUMENT-SPECIFIC

## Earthquake to local electromagnetic response

    Direction:
    Earthquake → local EM response

    Standing:
    INVESTIGABLE / EVENT-SPECIFIC

## Electromagnetic anomaly to earthquake

    Direction:
    EM anomaly → earthquake

    Standing:
    NOT ESTABLISHED

## Solar wind to earthquake

    Direction:
    Solar wind → earthquake

    Standing:
    CONTESTED / NOT ESTABLISHED

## Planetary geometry to earthquake

    Direction:
    Planetary geometry → earthquake

    Standing:
    NOT ESTABLISHED

## Multiple panels to unified physical system

    Direction:
    Display proximity → inferred connection

    Standing:
    HUMAN-FACTORS PATHWAY PLAUSIBLE
    PHYSICAL CONNECTION NOT ESTABLISHED

---

# 22. REVERSE-DIRECTION TESTS

Every candidate must test the reverse direction.

Examples:

    earthquake
    →
    electromagnetic disturbance

versus:

    electromagnetic disturbance
    →
    earthquake

Examples:

    geomagnetic event
    →
    Schumann variation

versus:

    global lightning or weather
    →
    Schumann variation

Examples:

    solar event
    →
    earthquake count

versus:

    selected earthquake interval
    →
    post-hoc solar-variable selection

Reverse direction must not be treated as equivalent causation.

---

# 23. COMMON-CAUSE REGISTER

Potential common causes include:

    season
    time of day
    solar cycle
    weather
    lightning
    catalogue update timing
    source refresh timing
    event-selection bias
    visual normalization
    reporting latency
    observer expectation

Candidate pattern:

    common cause C
    →
    A

and:

    common cause C
    →
    B

may create apparent:

    A ↔ B

without a direct causal path.

---

# 24. QUANTITATIVE SUFFICIENCY RULE

A mechanism must quantify:

    input magnitude
    attenuation
    transmitted magnitude
    target threshold
    expected response magnitude
    uncertainty range

Minimum comparison:

    proposed external perturbation

against:

    ordinary environmental variation
    ordinary instrument noise
    ordinary tectonic stress variation
    known established forcing
    measurement uncertainty

A mechanism remains incomplete when the only argument is:

    the fault was already near failure

Near-criticality does not eliminate the need to show that the perturbation:

    reached the target
    had the correct sign
    had sufficient magnitude
    occurred at the correct time

---

# 25. TEMPORAL BURDEN

Every causal claim must preserve:

    source event time
    transmission start
    propagation duration
    target-arrival time
    target-response time
    observation time
    processing time
    retrieval time
    interpretation time

Boundary:

    Recorded Near the Same Date
    ≠
    Correct Temporal Order Established

---

# 26. SPATIAL BURDEN

Every causal claim must preserve:

    source location
    transmission path
    target location
    spatial coverage
    expected geographic footprint
    observed footprint
    control regions

Global claims require global or geographically distributed evidence.

Boundary:

    Single Station
    ≠
    Global Spatial Coverage

---

# 27. DOSE–RESPONSE BURDEN

A causal mechanism should predict a relationship between:

    source magnitude
    and
    target response

Questions:

    Do stronger solar-wind changes produce stronger effects?
    Do larger tidal stresses produce larger response probabilities?
    Do larger electromagnetic anomalies precede larger earthquakes?
    Does the relationship remain monotonic?
    Is a threshold declared?
    Is the threshold stable?

A mechanism without dose–response structure remains weakly specified.

---

# 28. SPECIFICITY BURDEN

A causal indicator should distinguish target events from non-target events.

Required comparison:

    anomaly before earthquake

against:

    anomaly without earthquake
    earthquake without anomaly
    ordinary background period
    unrelated region
    randomized time

Required metrics:

    true positives
    false positives
    true negatives
    false negatives
    precision
    recall
    specificity
    lead time

---

# 29. FALSIFICATION REGISTER

## Solar-wind earthquake hypothesis

Falsified or weakened if:

    effect fails on later data
    effect disappears after declustering
    randomized shifts produce similar results
    lag is unstable
    mechanism magnitude is insufficient

## Schumann global-anomaly hypothesis

Falsified or weakened if:

    other stations do not reproduce the signal
    white regions are saturation or missing data
    local weather explains the signal
    lightning distribution explains the signal

## TEC precursor hypothesis

Falsified or weakened if:

    matched non-event controls show similar anomalies
    solar or geomagnetic conditions explain the result
    prospective false-alarm rate is high

## Planetary-geometry hypothesis

Falsified or weakened if:

    random alignments perform similarly
    calculated force is negligible
    prospective forecasts fail
    effect disappears after multiple-testing correction

## Unified energy hypothesis

Falsified or weakened if:

    no common variable exists
    domain changes remain independent
    apparent coherence disappears when panels are randomized
    causal transformations cannot be defined

---

# 30. REQUIRED MECHANISM TESTS

    TEST-M-001
    Event-specific Sun-to-Earth chain reconstruction

    TEST-M-002
    Solar-wind to geomagnetic response timing

    TEST-M-003
    Forecast-versus-observation verification

    TEST-M-004
    Multi-station Schumann comparison

    TEST-M-005
    Local weather and lightning control

    TEST-M-006
    Earthquake catalogue declustering

    TEST-M-007
    Solar-wind earthquake replication

    TEST-M-008
    Fault-specific quantitative stress estimate

    TEST-M-009
    TEC anomaly matched-control analysis

    TEST-M-010
    Tidal-stress projection by focal mechanism

    TEST-M-011
    Planetary-force magnitude comparison

    TEST-M-012
    Panel-order human-factors test

    TEST-M-013
    Common-variable search

    TEST-M-014
    Dose–response analysis

    TEST-M-015
    Prospective prediction trial

---

# 31. CAUSAL ADMISSION CONDITIONS

A causal pathway may be retained as established only when:

    source is observed
    target is observed
    temporal order is correct
    transmitted quantity is defined
    mechanism is defined
    spatial reach is demonstrated
    quantitative sufficiency is demonstrated
    confounders are controlled
    reverse causation is addressed
    common causes are addressed
    effect is independently replicated
    falsification tests are survived

Failure of one critical condition prevents causal admission.

---

# 32. CAUSAL HOLD CONDITIONS

A causal pathway remains HOLD when:

    one or more links are hypothetical
    transmitted quantity is undefined
    units are incompatible
    magnitude is unknown
    chronology is unresolved
    spatial reach is unresolved
    mechanism is only qualitative
    confounders remain active
    result is retrospective
    replication is absent
    prediction performance is absent

---

# 33. CURRENT MECHANISM STATE

    Sun → solar wind:
    ESTABLISHED

    Solar wind → magnetosphere:
    ESTABLISHED

    Magnetosphere → radiation belts:
    ESTABLISHED

    Magnetosphere → aurora:
    ESTABLISHED

    Lightning → Schumann resonances:
    ESTABLISHED

    Local weather → ELF sensor:
    PLAUSIBLE / INSTRUMENT-SPECIFIC

    Solar or geomagnetic activity → Schumann change:
    INVESTIGABLE / EVENT CONNECTION UNESTABLISHED

    Tectonic stress → earthquake:
    ESTABLISHED GENERAL PROCESS

    Earthquake → local electromagnetic effect:
    INVESTIGABLE

    Stressed rock → ionospheric anomaly:
    PROPOSED / FIELD SUFFICIENCY UNESTABLISHED

    TEC anomaly → earthquake precursor:
    NOT ESTABLISHED

    Solar wind → earthquake:
    CONTESTED / NOT ESTABLISHED

    Luni-solar tide → fault stress:
    PHYSICAL FORCING ESTABLISHED

    Luni-solar tide → useful prediction:
    NOT ESTABLISHED

    Planetary geometry → earthquake:
    NOT ESTABLISHED

    Multiple panels → unified physical system:
    NOT ESTABLISHED

    Independent mechanism tests:
    NOT STARTED

    Causal synthesis:
    HOLD

    Warning or prediction:
    NOT AUTHORIZED

    UNKNOWN → HOLD

---

# 34. NEXT AUTHORIZED ARTIFACT

    06_COMPARATIVE_EVIDENCE_MATRIX.md

That document will compare each candidate claim across:

    supporting evidence
    adversarial evidence
    official sources
    mechanism status
    statistical status
    replication status
    provenance status
    prediction status
    current Observatory OS disposition

No final cross-domain conclusion may be issued before that matrix is complete.

---

# 35. PRESERVED BOUNDARIES

    Association Reported
    ≠
    Mechanism Established

    Mechanism Plausible
    ≠
    Quantitative Sufficiency

    Quantitative Sufficiency
    ≠
    Independent Replication

    Independent Replication
    ≠
    Prediction

    Prediction
    ≠
    Warning Authority

    Temporal Proximity
    ≠
    Correct Causal Order

    Spatial Proximity
    ≠
    Transmission Path

    Near-Critical Target
    ≠
    Any Perturbation Sufficient

    Common Word Energy
    ≠
    Common Physical Variable

---

# 36. FINAL STATUS

    Mechanism vocabulary: ESTABLISHED
    Established physical pathways: REGISTERED
    Proposed pathways: REGISTERED
    Directionality burdens: DEFINED
    Quantitative burdens: DEFINED
    Temporal burdens: DEFINED
    Spatial burdens: DEFINED
    Dose–response burdens: DEFINED
    Specificity burdens: DEFINED
    Falsification conditions: DEFINED
    Required mechanism tests: DEFINED
    Independent execution: NOT STARTED
    Comparative matrix: NEXT
    Causal inference: HOLD
    Prediction or escalation: NOT AUTHORIZED
    UNKNOWN → HOLD