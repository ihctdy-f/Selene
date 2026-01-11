# Airbus Consortium Historical Case Study
## Out-of-Sample Validation Research Template

**Document Type:** Historical Research Template (DRAFT)  
**Status:** Initial Research Phase  
**Purpose:** De-risk Phase 5.2 by beginning historical documentation now  
**Target Completion:** Data sufficient for validation test design

---

## 1. Research Objective

Document the Airbus consortium formation (1967-1979) as an out-of-sample validation case for the Project Selene ABM. The model was calibrated on ECSC (1951); Airbus provides an independent test of whether ECSC-derived parameters predict outcomes in a different sector (aviation vs. coal/steel) but similar cooperation dynamics.

### Why Airbus?

| Criterion | ECSC (Calibration) | Airbus (Validation) | Match |
|-----------|-------------------|---------------------|-------|
| Multilateral European consortium | ✓ | ✓ | ✓ |
| High sunk costs | ✓ | ✓ | ✓ |
| Defection events | Minimal | UK withdrawal 1969 | Different |
| Sector | Coal/Steel | Aviation | Different |
| Era | 1950s | 1960s-70s | Different |
| Outcome | Durable success | Durable success (with turbulence) | Similar |

The key test: Can parameters calibrated to ECSC predict the Airbus trajectory (including UK withdrawal and return) without re-tuning?

---

## 2. Key Events Timeline

### Phase 1: Consortium Formation (1965-1970)

| Date | Event | Relevance to Model |
|------|-------|-------------------|
| 1965 | European governments begin coordinating on civil aviation | Initial trust formation |
| July 1967 | UK, France, Germany MoU on A300 development | Formal commitment |
| 1968 | Disagreement on aircraft specification | Trust test |
| April 1969 | **UK withdraws from consortium** | Defection event |
| Dec 1970 | France-Germany proceed as Airbus Industrie | Partial success |

### Phase 2: Early Operations (1970-1978)

| Date | Event | Relevance to Model |
|------|-------|-------------------|
| 1970 | Airbus Industrie GIE formed (France 50%, Germany 50%) | Restructured consortium |
| 1971 | Spain joins (4.2% share) | New member |
| 1972 | First A300 flight | Sunk cost milestone |
| 1974 | First delivery (Air France) | Revenue generation |
| 1978 | Eastern Airlines order (breakthrough in US market) | External validation |

### Phase 3: UK Reintegration (1978-1979)

| Date | Event | Relevance to Model |
|------|-------|-------------------|
| 1978 | UK begins renegotiation | Return after defection |
| Jan 1979 | **UK rejoins through BAe (20% share)** | Reentry event |
| Post-1979 | Stable 4-member structure | Structural success |

---

## 3. Research Questions

### 3.1 Trust Dynamics

**Question:** What was the initial trust level between UK, France, and Germany circa 1967?

**Sources to consult:**
- [ ] Diplomatic archives (UK National Archives, French Foreign Ministry)
- [ ] Contemporary news coverage (The Times, Le Monde, FAZ)
- [ ] Academic histories (Hayward 1994, McGuire 1997)

**Proxies for trust:**
- Prior bilateral aviation cooperation (e.g., Concorde)
- Trade relationships
- Political alignment scores (UNGA voting, etc.)

**Current assessment:** [TBD]

---

### 3.2 UK Withdrawal Event

**Question:** Why did the UK withdraw in 1969? Does this match model defection mechanisms?

**Hypothesized factors:**
- [ ] Economic pressure (balance of payments crisis)
- [ ] Domestic politics (Wilson government priorities)
- [ ] Technical disagreement (specification disputes)
- [ ] Insufficient sunk costs (low lock-in pre-Phase 3)

**Sources to consult:**
- [ ] Cabinet papers (30-year rule, now declassified)
- [ ] Parliamentary debates (Hansard)
- [ ] Industry accounts (Rolls-Royce archives)

**Current assessment:** [TBD]

---

### 3.3 Sunk Cost Accumulation

**Question:** What was the investment trajectory, and at what point did sunk costs become significant?

**Data needed:**
- [ ] Annual investment by country (€ or equivalent, inflation-adjusted)
- [ ] Cumulative investment at time of UK withdrawal
- [ ] Investment threshold before irreversibility

**Sources to consult:**
- [ ] Airbus corporate histories
- [ ] Government budget documents
- [ ] Industry analysis (Jane's, Flight International)

**Current assessment:** [TBD]

---

### 3.4 Cascade Risk

**Question:** Did UK withdrawal trigger cascade concern? Why did France/Germany continue?

**Evidence to gather:**
- [ ] Statements by French/German officials on UK withdrawal
- [ ] Alternative partnership options considered
- [ ] Risk assessments from the period

**Model prediction:** Strong sunk cost lock-in by 1969 should predict France/Germany continuation. Test whether this matches historical record.

**Current assessment:** [TBD]

---

### 3.5 UK Return Mechanism

**Question:** What drove UK reentry in 1979? Does the model account for member return?

**Hypothesized factors:**
- [ ] Commercial success of A300 demonstrated viability
- [ ] UK aerospace industry pressure (BAe, Rolls-Royce)
- [ ] Political change (Thatcher government)
- [ ] Changed cost-benefit calculation

**Model implication:** Current model does not have explicit "return" mechanism. If UK return was driven by factors outside the model, this is a limitation to document.

**Current assessment:** [TBD]

---

## 4. Model Parameter Mapping

### Agent Type Mapping

| Airbus Member | Selene Agent Type | Rationale |
|---------------|-------------------|-----------|
| France | Track A Core | Founding member, high commitment |
| Germany | Track A Core | Founding member, high commitment |
| UK (1967-1969) | Track B Core? | Major partner, higher defection risk |
| UK (1979+) | Track B Core | Returning member |
| Spain | Associate | Minor partner, lower commitment |
| Netherlands (later) | Associate | Minor partner |

### Trust Initialization

| Pair | Initial Trust (Estimate) | Basis |
|------|-------------------------|-------|
| France-Germany | 0.6-0.7 | Recent reconciliation, but historical tensions |
| France-UK | 0.5-0.6 | Concorde cooperation, but political tensions |
| Germany-UK | 0.5-0.6 | NATO allies, but limited prior cooperation |

### Sunk Cost Timeline (Preliminary)

| Year | Cumulative Investment (Est.) | Phase Equivalent |
|------|------------------------------|------------------|
| 1967 | ~€0.5B (adjusted) | Phase 0-1 |
| 1969 | ~€2B (adjusted) | Phase 2 |
| 1972 | ~€5B (adjusted) | Phase 3 |
| 1979 | ~€15B (adjusted) | Phase 5+ |

*These figures need verification from primary sources.*

---

## 5. Validation Test Design

### Test Structure

1. **Initialize model with Airbus parameters:**
   - 3 agents (France, Germany, UK)
   - Trust levels per Section 4
   - ECSC-calibrated behavioral parameters (unchanged)

2. **Run simulation:**
   - N = 1000 runs
   - Collect outcome distributions

3. **Compare to historical trajectory:**
   - Did model produce "defection followed by continuation" pattern?
   - Was UK the most likely defector?
   - Did remaining consortium achieve structural success?

### Success Criteria

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| UK as primary defector | >50% of defection runs | UK should be most likely to exit |
| France/Germany continuation | >70% of post-UK-defection runs | Historical outcome was continuation |
| Eventual structural success | >60% | Airbus succeeded long-term |
| Model produces "turbulent success" | Qualitative match | Not smooth path |

### Failure Modes

| If Model Shows... | Interpretation |
|-------------------|----------------|
| No defections | Parameters may be too stable; review ECSC calibration |
| Wrong defector | Agent typing may be incorrect |
| Total collapse after UK exit | Cascade mechanism too strong |
| Smooth success (no turbulence) | Trust dynamics too stable |

---

## 6. Data Sources

### Primary Sources

| Source | Location | Status |
|--------|----------|--------|
| UK Cabinet Papers (1967-1970) | National Archives, Kew | [ ] Not accessed |
| French Foreign Ministry Archives | La Courneuve | [ ] Not accessed |
| German Federal Archives | Koblenz | [ ] Not accessed |
| Airbus Corporate Archives | Toulouse | [ ] Not accessed |

### Secondary Sources

| Source | Citation | Status |
|--------|----------|--------|
| Hayward, K. (1994). *The World Aerospace Industry* | Standard reference | [ ] To obtain |
| McGuire, S. (1997). *Airbus Industrie: Conflict and Cooperation in US-EC Trade Relations* | Political economy | [ ] To obtain |
| Thornton, D.W. (1995). *Airbus Industrie: The Politics of an International Industrial Collaboration* | Most detailed | [ ] To obtain |
| Lynn, M. (1997). *Birds of Prey: Boeing vs. Airbus* | Popular account | [ ] Available |

### Data Quality Assessment

| Data Type | Availability | Quality | Notes |
|-----------|--------------|---------|-------|
| Timeline of events | High | Good | Well-documented |
| Investment figures | Medium | Moderate | Requires reconstruction |
| Trust proxies | Low | Poor | Must infer from behavior |
| Decision-maker intentions | Medium | Moderate | Cabinet papers help |

---

## 7. Alternative Validation Cases

If Airbus data proves insufficient, these alternatives are available:

### Alternative 1: ISS Partnership (1984-1998)

| Criterion | Assessment |
|-----------|------------|
| Multilateral consortium | ✓ (US, Russia, ESA, Japan, Canada) |
| Defection events | Russia partial withdrawal 2024 |
| Data availability | High (public program) |
| Sector match | Different (space, not industrial) |

### Alternative 2: ITER Fusion Consortium (2006-present)

| Criterion | Assessment |
|-----------|------------|
| Multilateral consortium | ✓ (EU, US, Russia, China, Japan, Korea, India) |
| Defection events | US withdrawal 1998, return 2003 |
| Data availability | High (public program) |
| Sector match | Different (science megaproject) |

### Alternative 3: Eurofighter Consortium (1983-present)

| Criterion | Assessment |
|-----------|------------|
| Multilateral consortium | ✓ (UK, Germany, Italy, Spain) |
| Defection events | France withdrew 1985 |
| Data availability | Medium (defense sector) |
| Sector match | Similar (aerospace) |

---

## 8. Research Tasks

### Immediate (Can Begin Now)

| Task | Owner | Hours | Status |
|------|-------|-------|--------|
| Obtain secondary sources (Thornton, McGuire, Hayward) | SME | 4 | [ ] |
| Extract timeline from secondary sources | SME | 6 | [ ] |
| Preliminary investment estimates | SME | 4 | [ ] |
| Trust proxy research (alliance data) | SME | 4 | [ ] |
| **Total** | | **18** | |

### Phase 5.2 (Upon Authorization)

| Task | Owner | Hours | Status |
|------|-------|-------|--------|
| Primary source access (archives) | SME | 20 | [ ] |
| Detailed parameter extraction | SME | 15 | [ ] |
| Validation test implementation | Lead Modeler | 20 | [ ] |
| Analysis and reporting | Both | 15 | [ ] |
| **Total** | | **70** | |

---

## 9. Current Research Notes

*[To be populated as research progresses]*

### Source Notes

**Source:** ____________________  
**Date accessed:** ____________________  
**Key findings:**
- 
- 
- 

**Relevance to model:**
- 

---

### Open Questions

1. What was the precise financial structure of the 1967 MoU?
2. Did France/Germany consider abandoning after UK withdrawal?
3. What triggered UK's decision to return in 1978?
4. Were there other potential members who declined?

---

## 10. Next Steps

### Before Authorization

1. [ ] Obtain secondary source books
2. [ ] Complete preliminary timeline
3. [ ] Estimate initial parameter values
4. [ ] Identify archive access requirements

### Upon Authorization

1. [ ] Request archive access
2. [ ] Complete detailed case documentation
3. [ ] Design validation test protocol
4. [ ] Execute validation runs
5. [ ] Document results

---

*Document Version 1.0 — DRAFT*  
*Research in progress*
