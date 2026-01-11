# Project Selene ABM Suite
## Agent-Based Scenario Exploration for Consortium Cooperation Dynamics

**Version:** 2.1 (Revised)  
**Date:** January 2026  
**Status:** Exploratory Analysis Tool

---

## 1. Purpose & Scope

### What Question Does This Answer?

> *Under specified assumptions, how do proposed Selene mechanisms (escrow, sunk cost lock-in, poison pill, wealth effects) affect multilateral cooperation dynamics relative to a mechanism-free baseline?*

This is a **counterfactual exploration**, not a prediction. The model examines: "If these mechanisms work as specified, what patterns emerge?" It does not claim: "These mechanisms will produce these outcomes in reality."

### What This Tool Does

- **Explores** how different institutional designs affect cooperation stability
- **Compares** mechanism-rich vs. mechanism-free architectures
- **Identifies** which mechanisms contribute most to outcomes (ablation analysis)
- **Generates** hypotheses about consortium fragility and resilience

### What This Tool Does NOT Do

- Predict specific Selene success probabilities
- Provide calibrated forecasts for resource allocation
- Replace expert judgment about geopolitical dynamics
- Warrant public-facing claims about consortium viability

---

## 2. Executive Summary

This package contains an agent-based scenario exploration suite for analyzing multilateral cooperation dynamics, designed to stress-test the Project Selene consortium architecture under specified assumptions.

### Key Findings (Internal Model Results)

| Metric | Result | Interpretation |
|--------|--------|----------------|
| **Mechanism Effect** | +42pp improvement | Mechanisms have large effects within model |
| **Statistical Significance** | p < 0.05, CI [+39.6, +44.7] | Effect robust to Monte Carlo variance |
| **Trust Threshold Shift** | 0.54 → 0.18 | Mechanisms reduce trust requirements in model |
| **ECSC Calibration** | 86.9% success | Parameters exist matching historical pattern |
| **Bilateral Integration** | -10.3pp degradation | Crisis friction propagates in model |

**Note:** These results reflect model behavior under specified assumptions. Confidence intervals capture parametric uncertainty only, not structural or real-world uncertainty. See Section 6 for interpretation guidance.

---

## 3. Package Contents

### Core Analysis

| File | Purpose |
|------|---------|
| `null_model_comparison.py` | **Main analysis**: NULL vs FULL Selene comparison |
| `statistical_rigor.py` | Bootstrap CIs + extreme bounds analysis |
| `bilateral_consortium_integration.py` | Links bilateral friction → consortium dynamics |
| `consortium_abm_verification.py` | Phase 1 verification tests |
| `ecsc_calibration.py` | Historical calibration to ECSC 1951 |

### Bilateral Model

| File | Purpose |
|------|---------|
| `calibrate_2010_upgraded.py` | China-Japan 2010 calibration |
| `calibrate_2019_japan_korea.py` | Japan-Korea 2019 calibration |
| `run_bilateral.py` | Bilateral friction simulator |
| `run_2026_scenario.py` | Forward projection scenarios |

### Analysis Tools

| File | Purpose |
|------|---------|
| `sensitivity_analysis.py` | OAT parameter sensitivity |
| `honest_validation.py` | Structural consistency tests |
| `mechanism_diagnostic.py` | Individual mechanism contribution |

---

## 4. Analysis Results

**Interpretation Note:** These results compare model configurations, not real-world predictions. Confidence intervals reflect Monte Carlo variance with fixed model structure. Structural uncertainty (how results would change under different behavioral rules) is not quantified. See `STRUCTURAL_ASSUMPTIONS.md` for load-bearing assumptions.

### 4.1 NULL Model vs Full Selene (n=2000, bootstrap n=2000)

```
POSITIVE OUTCOMES (Structural + Partial):
  NULL:   19.2%  [17.5%, 20.9%]
  FULL:   61.4%  [59.2%, 63.5%]
  GAP:   +42.1pp [+39.6pp, +44.7pp]  ← STATISTICALLY SIGNIFICANT
```

### 4.2 Mechanism Ablation (Which design elements contribute?)

| Mechanism | Individual Effect |
|-----------|------------------|
| Sunk Cost Lock-In | +16.6pp ⭐ |
| Wealth Effects | +15.2pp |
| Escrow/Forfeiture | +9.0pp |
| Audit Trust | -0.8pp (alone) |
| Poison Pill | -5.8pp (adds risk) |
| **ALL COMBINED** | **+41.2pp** (synergy!) |

### 4.3 Extreme Bounds (Trust Sensitivity)

```
Trust Level | NULL    | FULL    | Gap
------------|---------|---------|--------
0.15        |   9.4%  |  47.4%  | +38.0pp
0.25        |  13.4%  |  55.4%  | +42.0pp
0.35        |  23.4%  |  66.4%  | +43.0pp ← Maximum gap
0.50        |  43.2%  |  80.2%  | +37.0pp
0.70        |  77.6%  |  94.2%  | +16.6pp

Key thresholds:
- NULL needs trust ≈ 0.54 for 50% success
- FULL needs trust ≈ 0.18 for 50% success
- Threshold shift: +36pp
```

### 4.4 ECSC Historical Calibration

**Methodological Note:** This is *calibration* (finding parameters that produce target patterns), not *validation* (demonstrating out-of-sample predictive accuracy). ECSC provides a plausibility check, not predictive confirmation.

```
Target: 85-95% structural success (actual ECSC outcome)
Result: 86.9% ✓ (parameters exist that match pattern)

Phase-by-phase defection reduction:
- Phase 0: 10.5%
- Phase 1: 5.3% (-50%)
- Phase 2: 3.0% (-72%)
- Phase 3: 2.6% (-75%)
- Phase 4: 1.4% (-87%)

ECSC vs Generic (same trust): +68pp difference
```

### 4.5 Bilateral → Consortium Integration

```
Scenario         | Positive | CN Defect | JP Defect
-----------------|----------|-----------|----------
No bilateral     |   71.7%  |   66.0%   |   50.4%
Crisis bilateral |   61.4%  |   77.8%   |   67.2%

Degradation: -10.3pp (bilateral friction matters)
Bilateral-triggered cascades: 3.6% of runs
```

---

## Quick Start

### Run Main Validation
```bash
python null_model_comparison.py
```

### Run Statistical Analysis
```bash
python statistical_rigor.py
```

### Run Bilateral Integration
```bash
python bilateral_consortium_integration.py
```

### Run Full Suite
```bash
python null_model_comparison.py && \
python statistical_rigor.py && \
python bilateral_consortium_integration.py && \
python ecsc_calibration.py
```

---

## Model Architecture

### Consortium Model (5-8 Agents)

```
Agent Types:
- Track A Core (EU, Ukraine): base_defection=0.35, strong sunk cost
- Track B Core (China, Russia): base_defection=0.45, medium sunk cost  
- Associate (UAE, India): base_defection=0.30, weak sunk cost
- Tenant (US/NASA): base_defection=0.20, minimal sunk cost
- Private (SpaceX): base_defection=0.15, no sunk cost

Phases: 0 (Foundation) → 4 (Operations)
Each phase: +€10B sunk cost, trust evolution, shock exposure
```

### Selene Mechanisms (Module A-D)

1. **Escrow/Forfeiture (A)**: Exit penalty deters defection
2. **Lunar Credit Wealth (B)**: Accumulated stake reduces defection
3. **Poison Pill Cascade (D)**: ≥2 late exits triggers collapse
4. **Audit Trust Evolution (C)**: Successful phases build trust
5. **Sunk Cost Lock-In**: Later phases have lower defection prob

### Defection Probability Formula

```python
P(defect) = base * (1-trust)^0.5 * political_pressure
          * (1 - escrow_deterrent)
          * (1 - wealth_stake)
          * phase_multiplier
          + shock
```

---

## 5. Methodology Status

### Phase 1: Basic Verification ✓ 100%
- [x] Perfect trust → 100% success
- [x] Zero trust → 100% failure
- [x] Single agent survival
- [x] Mass defection handling

### Phase 2: Pattern Calibration ✓ 100%
- [x] Early coalition fragility (EDC analog)
- [x] Sunk cost lock-in (ECSC calibration)
- [x] Cascade failures
- [x] 2010 China-Japan calibration
- [x] 2019 Japan-Korea calibration
- [x] Honest validation (structure drives outcomes)

### Phase 3: Statistical Analysis ✓ 100%
- [x] Bootstrap confidence intervals
- [x] Extreme bounds analysis
- [x] Mechanism ablation
- [x] Parameter sensitivity (OAT)
- [x] Trust threshold identification

### Phase 4: External Testing ⏳ 50%
- [x] Bilateral → Consortium integration
- [x] NULL model comparison
- [ ] Expert elicitation (pending — 60-day target)
- [ ] Out-of-sample validation (pending — 90-day target)

**Note:** External validation required for decision-grade status. Current status: Exploratory use only.

---

## 6. Key Findings (Exploratory)

### 1. Mechanisms Have Large Internal Effects
Within model assumptions, the +42pp improvement over NULL model shows proposed mechanisms substantially affect cooperation dynamics. This is a model finding, not a real-world prediction.

### 2. Sunk Cost Is the Dominant Mechanism
Single most impactful mechanism (+16.6pp alone). Model suggests irreversibility matters more than punishment for sustaining cooperation.

### 3. Trust Thresholds Shift in Model
From 0.54 → 0.18 required for 50% success. Suggests mechanisms could make cooperation viable in medium-low trust environments, if mechanism assumptions are correct.

### 4. Bilateral Friction Propagates
Crisis between two agents can degrade consortium-wide outcomes by ~10pp in model and trigger cascades.

### 5. Partial Success May Suffice
Even "limping" consortiums (2-3 agents) create presence in model. Full structural success may not be required for strategic objectives.

---

## 7. How to Use This Analysis

### Appropriate Uses

✅ **Structured Thinking:** Use mechanism ablation to prioritize design elements  
✅ **Scenario Workshops:** Use model outputs to frame expert discussion  
✅ **Hypothesis Generation:** Use model patterns to identify research questions  
✅ **Sensitivity Exploration:** Use parameter sweeps to identify fragile assumptions  

### Inappropriate Uses

❌ **Quantitative Forecasting:** Do not cite specific success probabilities as predictions  
❌ **Resource Justification:** Do not use model outputs to support budget decisions  
❌ **Public Communication:** Do not present findings as validated predictions  
❌ **Go/No-Go Decisions:** Do not use as primary evidence for program decisions  

---

## 8. Conditions of Use

**Approved for:**
- Internal scenario exploration
- Structured thinking exercises
- Mechanism hypothesis generation
- Workshop facilitation
- Academic discussion with appropriate caveats

**NOT Approved for:**
- Quantitative decision support
- Resource allocation justification
- Public-facing claims about Selene viability
- Congressional or stakeholder briefing without explicit caveats

**Required Citation:**
> *Project Selene ABM Suite v2.1 (January 2026) — Exploratory scenario analysis. Results reflect model behavior under specified assumptions and should not be interpreted as predictions of real-world outcomes.*

See `CONDITIONS_OF_USE.md` for complete use authorization details.

---

## 9. Limitations & Caveats

### Parameter Limitations
1. **Calibration sensitivity**: ECSC parameters are calibrated estimates, not measured values
2. **Source documentation**: Some parameters based on expert judgment (see `PARAMETER_PROVENANCE.md`)
3. **Identifiability**: Model has sufficient degrees of freedom to match many patterns

### Structural Limitations
4. **Agent homogeneity**: Real nations have more complex, evolving incentives
5. **Shock simplification**: Real crises have path dependencies; model assumes IID shocks
6. **No learning**: Agents don't adapt strategies over time
7. **Linear mechanisms**: Real escrow/forfeiture may have thresholds
8. **Decision rules**: Probabilistic threshold model; alternatives not tested

### Uncertainty Limitations
9. **Parametric only**: Bootstrap CIs capture Monte Carlo variance, not structural uncertainty
10. **No ensemble**: Single model specification; alternatives not explored
11. **Reflexivity**: Strategic actors may respond to model predictions, invalidating them

### Validation Limitations
12. **Calibration ≠ Validation**: Historical pattern matching does not demonstrate predictive validity
13. **Expert elicitation pending**: Mechanism assumptions not yet reviewed by domain experts
14. **No out-of-sample test**: Predictive accuracy not demonstrated

See `STRUCTURAL_ASSUMPTIONS.md` for detailed documentation of load-bearing assumptions.

---

## 10. Future Work (Path to Decision-Grade)

To achieve decision-grade accreditation, the following is required:

| Milestone | Timeline | Status |
|-----------|----------|--------|
| Expert elicitation | +60 days | Planned |
| Out-of-sample validation | +90 days | Planned |
| Structural uncertainty | +180 days | Scoped |

See `FUTURE_WORK_ROADMAP.md` for detailed planning.

---

## 11. Citation

```
Project Selene ABM Suite v2.1
January 2026
Exploratory scenario analysis — Not validated for decision support
```

**Required Caveat for Any Use:**
> Results reflect model behavior under specified assumptions. Confidence intervals capture parametric uncertainty only. Not validated for predictive use.

---

## 12. Contact

For questions about methodology, calibration, or extensions, refer to the Project Selene documentation suite.

---

*Document version: 2.1 (Revised per review findings)*  
*Previous version: 2.0 Final*  
*Last updated: January 2026*
