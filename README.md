# IrrigationScheduler

**Morteza Khoshsimaie Chenar** · GreenSmart-DSS

A lightweight Python framework for daily root-zone water balance and depletion-based irrigation scheduling.

---

## Overview

IrrigationScheduler provides a simple and transparent framework for simulating daily soil-water dynamics in the crop root zone and generating irrigation decisions based on allowable soil-water depletion.

The core model consists of three interconnected components:

- **Weather + Crop + Soil** → Reference evapotranspiration (ETo) → ETc
- **Daily water balance** → Soil storage dynamics
- **Depletion assessment** → MAD threshold → Irrigation decision

---

## Core Equations

### 1. Crop Evapotranspiration (ETc)

$$\text{ETc}_d = \text{ETo}_d \times K_{c,d}$$

where:
- $\text{ETc}_d$ = crop evapotranspiration on day $d$ [mm/day]
- $\text{ETo}_d$ = reference evapotranspiration on day $d$ [mm/day]
- $K_{c,d}$ = crop coefficient on day $d$ (varies by growth stage)

The crop coefficient $K_{c,d}$ follows a four-stage linear development:

$$K_{c,d} = 
\begin{cases}
K_{c,\text{initial}} & \text{if } d \leq D_{\text{initial}} \\[6pt]
K_{c,\text{initial}} + \frac{d - D_{\text{initial}}}{D_{\text{dev}}} (K_{c,\text{mid}} - K_{c,\text{initial}}) & \text{if } D_{\text{initial}} < d \leq D_{\text{initial}} + D_{\text{dev}} \\[6pt]
K_{c,\text{mid}} & \text{if } D_{\text{initial}} + D_{\text{dev}} < d \leq D_{\text{initial}} + D_{\text{dev}} + D_{\text{mid}} \\[6pt]
K_{c,\text{mid}} + \frac{d - (D_{\text{initial}} + D_{\text{dev}} + D_{\text{mid}})}{D_{\text{late}}} (K_{c,\text{end}} - K_{c,\text{mid}}) & \text{if } d > D_{\text{initial}} + D_{\text{dev}} + D_{\text{mid}}
\end{cases}$$

where $D_{\text{initial}}, D_{\text{dev}}, D_{\text{mid}}, D_{\text{late}}$ are the initial, development, mid-, and late-stage durations.

### 2. Daily Root-Zone Water Balance

$$S_{d} = S_{d-1} + P_d + I_d - \text{ETc}_d - D_d$$

where:
- $S_d$ = final storage on day $d$ [mm]
- $S_{d-1}$ = initial storage at start of day $d$ [mm]
- $P_d$ = precipitation on day $d$ [mm]
- $I_d$ = irrigation applied on day $d$ [mm]
- $\text{ETc}_d$ = crop evapotranspiration on day $d$ [mm]
- $D_d$ = drainage on day $d$ [mm]

Drainage when storage exceeds field capacity:

$$D_d = \max(0, S^*_d - \theta_{fc})$$

where $S^*_d = S_{d-1} + P_d + I_d$ and $\theta_{fc}$ = field capacity.

Available water above wilting point:

$$AW_d = S_d - \theta_{wp}$$

Actual evapotranspiration limited by available water:

$$\text{AET}_d = \min(\text{ETc}_d, AW_d)$$

Water deficit (unmet crop water demand):

$$\text{WD}_d = \text{ETc}_d - \text{AET}_d$$

Soil depletion (water used from available storage):

$$\Delta S_d = \theta_{fc} - S_d$$

### 3. Irrigation Scheduling (MAD-based)

Readily available water:

$$\text{RAW} = \text{MAD} \times \text{TAW}$$

where:
- $\text{MAD}$ = maximum allowable depletion (fraction, 0–1)
- $\text{TAW} = \theta_{fc} - \theta_{wp}$ = total available water [mm]

Irrigation trigger condition:

$$\text{Trigger} = \begin{cases} \text{TRUE} & \text{if } \Delta S_d \geq \text{RAW} \\ \text{FALSE} & \text{if } \Delta S_d < \text{RAW} \end{cases}$$

Net irrigation requirement (when triggered):

$$I_{\text{net}} = \Delta S_d$$

Gross irrigation requirement (accounting for system efficiency $\epsilon$):

$$I_{\text{gross}} = \frac{I_{\text{net}}}{\epsilon}$$

where $\epsilon$ = irrigation system efficiency (0 < $\epsilon$ ≤ 1).

---

## Conceptual Workflow

```
Weather + Crop + Soil
    ↓
    ETo → ETc (via Kc)
    ↓
Daily Water Balance:
    S ← S + P + I − AET − D
    ↓
Depletion: ΔS = θfc − S
    ↓
MAD Threshold: ΔS ≥ MAD × TAW ?
    ↓
Irrigation Decision: Net/Irrigation computed
```

---

## Installation

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/GreenSmart-DSS/IrrigationScheduler.git
cd IrrigationScheduler
pip install -e .
```

---

## Status

This project is under active development.

Version 0.1 focuses on a minimal and transparent depletion-based irrigation scheduling model.

---

## References

- **FAO Irrigation and Drainage Paper 56**: Crop evapotranspiration guidelines
- **Plant Soil Water Relations**: Field capacity, wilting point, and available water concepts