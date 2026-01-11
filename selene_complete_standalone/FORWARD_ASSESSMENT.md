# Forward Assessment — Project Selene ABM v2.1

**Date:** January 2026  
**From:** Team A (Author Team)  
**Purpose:** Capacity self-assessment and recommendations for next iteration

---

## What This Team Can Improve

### Capabilities Demonstrated

**Technical Execution:**
- Model architecture is sound; mechanisms produce intended behaviors
- Statistical analysis (bootstrap CIs, sensitivity) implemented correctly
- Historical calibration achieved target patterns (ECSC 86.9%, bilateral pattern matching)
- Integration between bilateral and consortium models functional

**Responsiveness:**
- Accepted core critique without defensive posturing
- Implemented comprehensive terminology corrections
- Created substantial new documentation (4 new files, ~6,000 words)
- Maintained clear traceability between findings and responses

**Methodological Self-Awareness:**
- Correctly distinguished calibration from validation once prompted
- Acknowledged structural uncertainty as dominant concern
- Proposed concrete path to decision-grade status

### What We Can Build Next

Given demonstrated capabilities, the team is positioned to deliver:

| Capability | Confidence | Timeline |
|------------|------------|----------|
| Expert elicitation protocol | High | 4 weeks |
| Expert elicitation execution | High | 8 weeks (60-day target) |
| Out-of-sample test (Airbus) | Medium | 12 weeks (data-dependent) |
| Structural uncertainty documentation | High | 6 weeks |
| Multi-model ensemble | Medium | 20 weeks |
| Full decision-grade package | Medium | 6 months |

---

## Technical Debt Identified

### Documentation Debt (Now Addressed)

- Parameter provenance was inconsistent → Now documented in PARAMETER_PROVENANCE.md
- Structural assumptions were implicit → Now explicit in STRUCTURAL_ASSUMPTIONS.md
- Use conditions were undefined → Now specified in CONDITIONS_OF_USE.md

### Remaining Technical Debt

| Issue | Severity | Remediation |
|-------|----------|-------------|
| No formal test suite | Medium | Create pytest/unittest framework |
| ODD protocol incomplete | Low | Complete ODD documentation |
| KS distribution tests not implemented | Low | Add to statistical_rigor.py |
| Latin Hypercube sampling not done | Medium | Implement for Phase 5 |
| No CI/CD pipeline | Low | Add automated testing |

### Architectural Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| IID shock assumption | Medium | Document as structural assumption; test alternatives in ensemble |
| No adaptive learning | Medium | Note in limitations; defer to v3 |
| Fixed agent types | Low | Sensitivity analysis on type parameters |
| Linear mechanisms | Low | Document; test threshold variants in ensemble |

---

## Opportunities Identified But Deferred

### Near-Term (Could Do in 90 Days)

1. **Airbus Consortium Out-of-Sample Test**
   - Data likely available from public sources
   - Would directly address Principal Scientist's hold condition
   - Estimate: 90 hours

2. **Alternative Behavioral Specification**
   - Expected utility decision rule (vs. probabilistic threshold)
   - Would begin structural uncertainty exploration
   - Estimate: 60 hours

3. **Negative Validation Documentation**
   - Characterize what the model *cannot* produce
   - Strengthens empirical content claims
   - Estimate: 30 hours

### Medium-Term (90-180 Days)

4. **Full Multi-Model Ensemble**
   - 3-4 alternative specifications
   - Robustness classification of findings
   - Estimate: 150 hours

5. **Formal Test Suite**
   - pytest framework for all verification tests
   - Automated regression testing
   - Estimate: 40 hours

### Long-Term (Deferred to v3)

6. **Adaptive Learning Agents**
   - Agents update strategies based on experience
   - Major architectural change
   - Estimate: 200+ hours

7. **Correlated Shock Process**
   - Regime-switching or autoregressive shocks
   - Requires new calibration approach
   - Estimate: 80 hours

---

## Resource and Expertise Gaps

### Current Team Constraints

| Gap | Impact | Mitigation |
|-----|--------|------------|
| No dedicated V&V specialist | Medium | Lead Modeler covering; could use external review |
| Limited access to domain experts | High | Expert elicitation requires recruitment |
| No HPC allocation for ensemble | Medium | Can use local compute for initial ensemble |
| Historical data access uncertain | Medium | Airbus public sources may suffice; ITER/ISS as backup |

### Expertise Gaps

| Domain | Current Level | Needed Level | Path |
|--------|---------------|--------------|------|
| Formal V&V methodology | Competent | Expert | Training or consultant |
| Geopolitical domain expertise | Good | Expert | Expert elicitation compensates |
| Bayesian calibration | Limited | Competent | Would strengthen parameter estimation |
| Multi-model ensemble methods | Limited | Competent | Literature review; trial implementation |

---

## Recommended Priorities for Next Iteration

### Priority 1: Expert Elicitation (60 Days)

**Rationale:** Directly addresses Professor's core concern. Validates mechanism assumptions. Most feasible near-term improvement.

**Approach:**
1. Recruit 5-8 domain experts (international cooperation, space policy, game theory)
2. Present mechanism hypotheses without model outputs
3. Structured elicitation: plausibility, failure conditions, missing dynamics
4. Revise model if warranted; document expert-endorsed assumptions

**Resources:** 80 hours + expert compensation (~$15,000)

### Priority 2: Out-of-Sample Test (90 Days)

**Rationale:** Directly addresses Principal Scientist's hold condition. Tests predictive validity beyond calibration data.

**Approach:**
1. Document Airbus consortium formation (1967-1970) as test case
2. Apply ECSC-calibrated parameters without modification
3. Generate outcome distribution; compare to historical trajectory
4. Report honestly: pass, fail, or inconclusive

**Resources:** 90 hours; no external cost if public data sufficient

### Priority 3: Structural Uncertainty Exploration (180 Days)

**Rationale:** Addresses Professor's epistemological concern. Required for decision-grade status.

**Approach:**
1. Implement 2-3 alternative behavioral specifications
2. Run ensemble with same scenarios
3. Characterize which findings are robust vs. sensitive
4. Report structural uncertainty envelope

**Resources:** 150 hours

---

## Conclusion

The revision cycle demonstrated that Team A can:
- Accept critique constructively
- Implement comprehensive documentation improvements
- Maintain methodological discipline

The path to decision-grade status is clear: expert elicitation, out-of-sample testing, and structural uncertainty exploration. These are achievable within 6 months given adequate resources.

The primary constraint is not capability but time and access: expert recruitment takes time, and historical data access may require effort. The team recommends prioritizing expert elicitation as the highest-value near-term investment.

---

**Submitted by:**

Lead Computational Modeler: _______________  

Domain Expert (SME): _______________  

Program Lead: _______________  

**Date:** January 2026
