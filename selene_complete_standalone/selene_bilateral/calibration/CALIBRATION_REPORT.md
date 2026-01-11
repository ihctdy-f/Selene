# Project Selene Bilateral Friction Model - Calibration Report
## 2010 Japan-China Rare Earth Crisis

**Date:** January 2026 (Updated v2.1)  
**Overall Calibration Score:** 0.76 (PASSED)

**Terminology Note:** "Calibration" means finding parameters that produce target patterns.
This does NOT demonstrate predictive validity. See Response Matrix P-1, S-2.

---

## Summary

The bilateral friction model was calibrated against the 2010 Japan-China rare earth crisis. The model successfully reproduces **friction dynamics** (peak friction, escalation rates) but does **not** reproduce the historical **de-escalation pattern**.

### Key Results

| Metric | Score | Notes |
|--------|-------|-------|
| Peak Friction | 0.97 | Excellent - 0.474 avg within 0.40-0.55 target |
| Non-Spiral Rate | 0.99 | Excellent - only 1.3% escalation spirals |
| Non-Decouple Rate | 1.00 | Perfect - no gradual decoupling |
| Outcome Distribution | 0.33 | Poor - doesn't match historical pattern |
| **Overall** | **0.76** | **PASSED** |

### Outcome Distribution Mismatch

| Outcome | Model | Historical Target | 
|---------|-------|-------------------|
| Normalization | 0% | 30% |
| Stable Interdependence | 0% | 50% |
| Managed Competition | 99% | 12% |
| Escalation Spiral | 1% | 5% |

---

## Root Cause Analysis

The model produces "managed competition" outcomes (friction stabilizes at 0.2-0.5) rather than "normalization" (friction returns to <0.1) because:

### 1. Model Architecture
The bilateral friction model is designed for **mutual escalation dynamics** - both parties deciding to escalate or de-escalate based on pain/benefit calculations. The 2010 case was **unilateral coercion** followed by **international pressure-induced de-escalation**.

### 2. Decision Logic
The model's `decide_action()` function compares escalation vs de-escalation as competing options. Escalation on new sectors often has higher net benefit than de-escalation on existing sectors, even when total pain exceeds thresholds.

### 3. Missing Mechanisms
The model lacks:
- International reputation cost accumulation
- Time-decay pressure on maintaining restrictions
- Third-party mediation forcing de-escalation
- Asymmetric crisis management dynamics

---

## Model Capabilities (Within Scope)

The model produces plausible results for:
- Simulating bilateral friction escalation dynamics
- Testing poison pill / dependency chain mechanisms
- Exploring tit-for-tat retaliation scenarios
- Modeling gradual decoupling over multi-year horizons

The model is NOT designed for:
- Unilateral coercion followed by de-escalation
- Short-term crisis management dynamics
- International pressure-induced outcomes

**Note:** "Plausible results" means internally consistent behavior, not validated predictions.

---

## Parameters Used (Final)

### Japan (State A)
- nationalism: 0.55
- escalation_threshold: 0.60 (high - very cautious)
- de_escalation_threshold: 0.10 (low - quick to back down)
- retaliation_propensity: 0.10 (low)
- action_cooldown: 5 steps

### China (State B)
- nationalism: 0.85
- escalation_threshold: 0.10 (low - quick to escalate)
- de_escalation_threshold: 0.20
- retaliation_propensity: 0.90 (high)
- action_cooldown: 1 step

### Rare Earth Sector
- b_exports_to_a: 0.8 (China → Japan)
- b_restriction_self_harm: 0.80 (high - captures lost revenue)
- a_criticality_score: 0.95 (critical for Japan)
- a_substitution_time: 36 months

---

## Recommendations for Future Development

1. **Add international pressure module**: Third parties should be able to impose costs for maintaining restrictions over time

2. **Add time-decay mechanism**: Cost of maintaining restrictions should increase with duration

3. **Separate escalation from de-escalation logic**: Don't compare them as competing options

4. **Calibrate on bilateral cases**: Try 2012 Senkaku dispute, 2019 Japan-Korea semiconductor dispute

---

## Conclusion

The model passes calibration for friction dynamics but requires architectural modifications to reproduce de-escalation patterns seen in unilateral coercion scenarios. For Project Selene's primary use case (testing consortium stability under defection scenarios), the current model is **appropriate** since those are bilateral dynamics.
