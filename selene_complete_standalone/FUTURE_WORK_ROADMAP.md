# Future Work Roadmap — Path to Decision-Grade Status

**Document Type:** Technical Planning  
**Version:** 1.0  
**Date:** January 2026  
**Status:** Planned Work (Post-Review)

---

## Overview

This document outlines the work required to advance Project Selene ABM from exploratory analysis to decision-grade accreditation, as specified by the Review Authority.

---

## Current State Assessment

### Completed Work

| Phase | Status | Evidence |
|-------|--------|----------|
| **Phase 1:** Basic Verification | ✅ Complete | Boundary tests, edge cases |
| **Phase 2:** Pattern Calibration | ✅ Complete | ECSC, 2010, 2019 calibrations |
| **Phase 3:** Sensitivity Analysis | ✅ Complete | OAT analysis, bootstrap CIs |
| **Phase 4:** Internal Validation | ✅ Complete | Honest validation, null comparison |

### Gap Analysis (Per Review Findings)

| Requirement | Current State | Gap |
|-------------|---------------|-----|
| Expert elicitation | Planned, not executed | Mechanism assumptions unreviewed |
| Out-of-sample validation | Not attempted | No independent predictive test |
| Structural uncertainty | Not quantified | CIs misleading re: total uncertainty |
| Decision context | Now specified | Previously ambiguous |
| Parameter provenance | Partially documented | Now fully documented |

---

## Phase 5: External Validation (Proposed)

### 5.1 Expert Elicitation

**Objective:** Domain experts review mechanism assumptions independent of model outputs.

**Methodology:**
1. Document mechanism hypotheses in prose (no model reference)
2. Recruit 5-8 experts in:
   - International cooperation theory
   - Space policy
   - Game theory / institutional design
   - Geopolitical risk analysis
3. Structured elicitation:
   - "Is this behavioral rule plausible?"
   - "What would make this assumption fail?"
   - "Are there important dynamics not captured?"
4. Aggregate findings and revise as warranted

**Timeline:** 60 days from authorization

**Deliverables:**
- Expert elicitation protocol
- Expert feedback summary
- Assumption revision log
- Updated STRUCTURAL_ASSUMPTIONS.md

**Resource Requirements:**
- 40 hours expert time (compensated)
- 20 hours facilitation/synthesis
- Protocol development: 2 weeks

---

### 5.2 Out-of-Sample Historical Test

**Objective:** Calibrate to one historical case, test prediction against another without re-tuning.

**Proposed Approach:**

| Role | Historical Case | Rationale |
|------|-----------------|-----------|
| **Calibration** | ECSC (1951) | Already done; well-documented |
| **Validation** | Airbus Consortium (1967-1970) | Different sector, same cooperation dynamics |

**Airbus Test Design:**
1. Characterize Airbus formation as consortium problem:
   - Initial members: France, Germany, UK (later withdrew, then returned)
   - Sunk cost dynamics (aircraft development investment)
   - Defection risk (UK withdrew 1969, rejoined 1979)
   - External shocks (oil crisis, currency fluctuations)
   
2. Using ECSC-calibrated parameters (without modification):
   - Generate outcome distribution
   - Compare to actual Airbus trajectory
   
3. Success criteria:
   - Model produces "durable cooperation with turbulence" not "collapse"
   - UK withdrawal event falls within plausible model trajectories
   - Long-term integration outcome emerges

**Alternative Candidates (if Airbus data unavailable):**
- ISS partnership formation (1984-1998)
- ITER fusion consortium (2006-present)
- CERN expansion phases

**Timeline:** 90 days from authorization (contingent on data access)

**Deliverables:**
- Airbus case characterization document
- Validation test protocol
- Results report with statistical comparison
- Honest assessment: did model pass or fail?

**Resource Requirements:**
- Historical research: 40 hours
- Model adaptation: 20 hours
- Analysis and reporting: 30 hours

---

### 5.3 Structural Uncertainty Exploration

**Objective:** Quantify how conclusions change under alternative model specifications.

**Proposed Approach:**

**Alternative Specifications to Test:**

| Element | Baseline | Alternative 1 | Alternative 2 |
|---------|----------|---------------|---------------|
| Defection decision | Probability threshold | Expected utility calculation | Heuristic rule |
| Trust evolution | Linear update | Bayesian learning | Prospect theory |
| Sunk cost effect | Continuous reduction | Threshold trigger | Hyperbolic discount |
| Shock process | IID draws | Correlated over time | Regime-switching |
| Agent heterogeneity | Fixed types | Evolving types | Emergent types |

**Multi-Model Ensemble:**
1. Implement 3-4 alternative behavioral specifications
2. Run each with same scenario parameters
3. Characterize conclusion robustness:
   - Which findings hold across specifications?
   - Which are sensitive to behavioral assumptions?
   - What is the envelope of plausible outcomes?

**Timeline:** 180 days from authorization

**Deliverables:**
- Alternative model implementations (documented)
- Ensemble analysis report
- Robustness classification of findings
- Revised uncertainty characterization

**Resource Requirements:**
- Model development: 120 hours
- Sensitivity analysis: 60 hours
- Documentation: 40 hours

---

### 5.4 Negative Validation

**Objective:** Specify what patterns the model *cannot* produce, establishing empirical content.

**Approach:**
1. Run parameter sweeps across full plausible ranges
2. Characterize outcome space: what distributions emerge?
3. Identify "impossible" regions:
   - Are there outcome patterns the model never produces?
   - If not, model has too many degrees of freedom
4. Document constraints on model predictions

**Deliverables:**
- Outcome space characterization
- "What the model can't do" documentation
- Falsifiability statement

**Timeline:** Concurrent with 5.3 (180 days)

---

## Phase 6: Decision-Grade Submission (Future)

### Prerequisites

All Phase 5 items must be complete and satisfactory:

| Requirement | Source | Status |
|-------------|--------|--------|
| Expert elicitation complete | Distinguished Professor | ⏳ |
| Out-of-sample test passed | Principal Scientist | ⏳ |
| Structural uncertainty characterized | Principal Scientist | ⏳ |
| Decision context specified | Director | ✅ |
| Conditions of Use documented | Director | ✅ |

### Submission Package

1. Revised technical documentation
2. Expert elicitation report
3. Out-of-sample validation report
4. Structural uncertainty analysis
5. Updated README with validation claims
6. Formal accreditation request

### Review Process

1. Principal Scientist technical review
2. Distinguished Professor epistemological review
3. Director strategic assessment
4. Joint sign-off meeting

---

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Out-of-sample test fails | Medium | High | Have backup historical cases; treat failure as learning |
| Experts reject key assumptions | Medium | Medium | Revise model; document contested assumptions |
| Structural uncertainty too large | Medium | High | May constrain allowable claims; acceptable outcome |
| Data unavailable for Airbus | Low | Medium | Use ISS or ITER as alternative |

### Schedule Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Expert recruitment delays | Medium | Medium | Begin recruitment immediately; have backup list |
| Resource competition | Medium | Medium | Secure commitment from Program Lead |
| Scope creep in Phase 5 | Medium | Low | Fixed deliverables, time-boxed phases |

---

## Resource Summary

### Phase 5 Total Estimate

| Activity | Hours | Cost (Est.) |
|----------|-------|-------------|
| Expert elicitation | 80 | $15,000 (expert fees) |
| Out-of-sample validation | 90 | — (internal) |
| Structural uncertainty | 220 | — (internal) |
| Project management | 40 | — (internal) |
| **Total** | **430** | **$15,000 + labor** |

### Timeline Summary

```
Month 1-2:  Expert elicitation (5.1)
Month 2-3:  Out-of-sample validation (5.2)
Month 3-6:  Structural uncertainty (5.3, 5.4)
Month 6+:   Decision-grade submission (Phase 6)
```

---

## Approval

**Proposed by:** Lead Computational Modeler  
**Reviewed by:** Domain Expert (SME)  
**Approved by:** Program Lead  

**Authorization to proceed pending resource confirmation.**

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | January 2026 | Initial roadmap (post-review) |
