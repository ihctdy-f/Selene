# Structural Assumptions Documentation

**Document Type:** Technical Reference  
**Version:** 1.0  
**Date:** January 2026

---

## Purpose

This document identifies the structural assumptions underlying the Project Selene ABM—the design choices about *how* agents behave, *how* mechanisms work, and *how* interactions unfold. These assumptions are distinct from parameter values and represent a source of uncertainty not captured by parametric confidence intervals.

---

## Why Structural Uncertainty Matters

**Parametric uncertainty:** "Given this model structure, how do results vary across parameter ranges?"  
→ Captured by bootstrap CIs and sensitivity analysis

**Structural uncertainty:** "How would results change if the model worked differently?"  
→ NOT captured in current analysis

For novel systems like Selene, structural uncertainty likely dominates. Different experts would build different models, making different structural choices. The current analysis explores one plausible structure, not the space of plausible structures.

---

## Load-Bearing Structural Assumptions

### 1. Agent Decision Rule

**Current Assumption:**  
Agents defect probabilistically based on a weighted combination of factors:
```
P(defect) = base × (1-trust)^0.5 × pressure × mechanism_adjustments + shock
```

**Why It Matters:**  
This assumes agents are boundedly rational, responding to environmental signals with noise. Results could differ substantially under:

| Alternative | Expected Impact |
|-------------|-----------------|
| Expected utility maximization | More strategic behavior; potentially more defection early, less late |
| Pure threshold rule | Sharper transitions; less gradual evolution |
| Adaptive learning | Early experiences shape later behavior |
| Satisficing | Different sensitivity to mechanism design |

**Robustness Assessment:** Not tested. Results may be sensitive to decision rule specification.

---

### 2. Phase Structure

**Current Assumption:**  
Consortium proceeds through 5 discrete phases (0-4), each adding sunk costs and building trust.

**Why It Matters:**  
Discrete phases create "commitment points" that don't exist in continuous processes. Real Selene may have more gradual commitment accumulation.

| Alternative | Expected Impact |
|-------------|-----------------|
| Continuous time | Smoother dynamics; different threshold effects |
| Irregular phases | More realistic but harder to calibrate |
| Reversible phases | Qualitatively different lock-in dynamics |

**Robustness Assessment:** Not tested. Phase discretization likely affects threshold findings.

---

### 3. Sunk Cost Mechanism

**Current Assumption:**  
Sunk costs monotonically reduce defection probability through a multiplicative factor.

**Why It Matters:**  
This assumes rational responsiveness to investment. Real actors may:
- Ignore sunk costs (economically rational but psychologically unrealistic)
- Over-weight sunk costs (loss aversion)
- Hit thresholds where sunk costs suddenly matter

| Alternative | Expected Impact |
|-------------|-----------------|
| No sunk cost effect | Major reduction in cooperation rates |
| Threshold effect | Sharper transitions at specific investment levels |
| Hyperbolic discounting | Different temporal dynamics |

**Robustness Assessment:** Sensitivity analysis shows sunk cost is load-bearing (+16.6pp). Alternative specifications would significantly affect conclusions.

---

### 4. Trust Evolution

**Current Assumption:**  
Trust increases incrementally with successful phase completion and decays slowly without positive signals.

**Why It Matters:**  
This assumes trust is learnable and that past cooperation predicts future cooperation. Real trust dynamics may be:
- Path-dependent (historical grievances persist)
- Non-monotonic (trust can collapse suddenly)
- Heterogeneous (different actors have different trust trajectories)

| Alternative | Expected Impact |
|-------------|-----------------|
| Bayesian updating | More rational learning; different calibration |
| Prospect theory | Loss-aversion in trust changes |
| Sudden collapse | More fragile cooperation |
| Agent-specific trust | Heterogeneous dynamics |

**Robustness Assessment:** Not tested. Trust specification likely affects late-phase dynamics.

---

### 5. Shock Process

**Current Assumption:**  
Shocks are IID draws from a fixed distribution each phase.

**Why It Matters:**  
Real geopolitical shocks are often:
- Correlated over time (crises cluster)
- Regime-dependent (different eras have different shock patterns)
- Endogenous (model behavior affects shock likelihood)

| Alternative | Expected Impact |
|-------------|-----------------|
| Correlated shocks | Clustered crises; higher failure rates |
| Regime-switching | Different baseline fragility in different periods |
| Endogenous shocks | Strategic behavior could trigger crises |

**Robustness Assessment:** Not tested. IID assumption is a simplification of convenience.

---

### 6. Poison Pill Implementation

**Current Assumption:**  
≥2 late defections trigger collapse with 70% probability.

**Why It Matters:**  
This is a specific mechanism design choice. Real Selene may implement poison pills differently:
- Different thresholds
- Graduated responses
- Conditional triggers

| Alternative | Expected Impact |
|-------------|-----------------|
| Higher threshold (≥3) | More robust to defection |
| Lower threshold (≥1) | More fragile |
| Graduated response | Different cascade dynamics |

**Robustness Assessment:** Sensitivity analysis explored poison pill strength. Threshold choice affects cascade frequency.

---

### 7. Agent Heterogeneity

**Current Assumption:**  
Agents are classified into 5 types with fixed behavioral profiles.

**Why It Matters:**  
Real Selene participants may be:
- More heterogeneous within types
- Evolving over time
- Responsive to model dynamics (reflexivity)

| Alternative | Expected Impact |
|-------------|-----------------|
| Continuous heterogeneity | Smoother outcome distributions |
| Evolving types | Time-varying dynamics |
| Reflexive agents | Fundamentally unpredictable |

**Robustness Assessment:** Not tested. Type system is a simplification.

---

### 8. Bilateral-Consortium Linkage

**Current Assumption:**  
Bilateral friction degrades consortium outcomes through additive shock transmission.

**Why It Matters:**  
Real linkages may be:
- More complex (feedback loops)
- Contingent (only matter under specific conditions)
- Asymmetric (some bilateral relationships matter more)

| Alternative | Expected Impact |
|-------------|-----------------|
| Feedback loops | Potential instability |
| Conditional activation | Different scenario sensitivity |
| Weighted linkages | Different member importance |

**Robustness Assessment:** Integration test shows 10pp degradation. Alternative specifications not tested.

---

## Structural Assumptions NOT Expected to Matter

### Low-Impact Assumptions

| Assumption | Why Less Important |
|------------|-------------------|
| Specific random seed | Results averaged over many runs |
| Exact phase duration | Relative dynamics matter, not absolutes |
| UI/display choices | No effect on simulation dynamics |

---

## Implications for Interpretation

### What Current CIs Mean

The bootstrap CI [+39.6pp, +44.7pp] means:
> "Given this model structure, across Monte Carlo runs, the mechanism effect falls in this range."

### What Current CIs Do NOT Mean

The CI does NOT mean:
> "The real-world mechanism effect will fall in this range."

### Structural Uncertainty Envelope (Estimated)

Based on the load-bearing assumptions identified above, reasonable alternative specifications could plausibly produce:

| Finding | Current Estimate | Plausible Range Under Alternative Structures |
|---------|------------------|----------------------------------------------|
| Mechanism effect | +42pp | +15pp to +60pp |
| Sunk cost contribution | +16.6pp | +5pp to +25pp |
| Trust threshold shift | 36pp | 15pp to 50pp |

These ranges are expert judgments, not computed from an ensemble. They indicate substantial structural uncertainty.

---

## Path to Structural Uncertainty Quantification

### Proposed Multi-Model Ensemble

1. **Build alternative specifications:**
   - Expected utility decision rule
   - Threshold-based sunk cost
   - Correlated shock process
   - Bayesian trust evolution

2. **Run ensemble analysis:**
   - Same scenarios, different models
   - Characterize outcome distributions
   - Identify robust vs. fragile findings

3. **Report structural uncertainty:**
   - Findings consistent across models: "Robust"
   - Findings vary across models: "Sensitive to structural assumptions"

### Resource Requirement

Estimated 120-200 hours of development and analysis time. See FUTURE_WORK_ROADMAP.md for timeline.

---

## Summary

| Category | Assessed? | Impact |
|----------|-----------|--------|
| Parametric uncertainty | ✅ Yes | Moderate (CIs available) |
| Structural uncertainty | ❌ No | Likely large (not quantified) |
| Real-world uncertainty | ❌ No | Unknown (model vs reality gap) |

**Bottom Line:** Current confidence intervals understate total uncertainty. Structural assumptions are load-bearing and untested. Results should be interpreted as "what one plausible model produces," not "what will happen."

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | January 2026 | Initial documentation |
