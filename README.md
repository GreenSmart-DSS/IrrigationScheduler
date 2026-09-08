# IrrigationScheduler

A lightweight Python framework for daily root-zone water balance and
depletion-based irrigation scheduling.

## Overview

IrrigationScheduler provides a simple and transparent framework for
simulating daily soil-water dynamics in the crop root zone and generating
irrigation decisions based on allowable soil-water depletion.

The first version focuses on:

- Daily root-zone water balance
- Crop evapotranspiration (ETc)
- Rainfall accounting
- Soil-water depletion
- Allowable depletion (MAD)
- Irrigation requirement
- Irrigation efficiency
- Drainage

## Concept

The basic workflow is:

Weather + Crop + Soil
        ↓
       ETc
        ↓
Soil Water Balance
        ↓
     Depletion
        ↓
  MAD Threshold
        ↓
Irrigation Decision

## Status

This project is under active development.

Version 0.1 focuses on a minimal and transparent depletion-based
irrigation scheduling model.

## Installation

Clone the repository and install it in editable mode:

```bash
pip install -e .