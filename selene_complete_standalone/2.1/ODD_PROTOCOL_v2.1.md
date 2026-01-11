# ODD Protocol: Project Selene Consortium Simulator v2.1
## Overview, Design concepts, and Details

**Status:** REVISED — Aligned with v2.1 Implementation  
**Date:** January 2026  
**Standard:** Grimm et al. (2020) ODD+D Protocol  
**Review Status:** Exploratory Use Approved

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | Dec 2025 | Initial draft |
| 2.1 | Jan 2026 | Aligned with v2.1; terminology corrections; validation status updated |

---

## 1. PURPOSE AND PATTERNS

### 1.1 Purpose

**Primary Question:**
> Under specified assumptions, how do proposed Selene mechanisms (escrow, sunk cost lock-in, poison pill, wealth effects) affect multilateral cooperation dynamics relative to a mechanism-free baseline?

**Framing (Per Review):**
This is an **exploratory scenario analysis** answering "how-possibly" questions, not "how-actually" predictions. The model examines: "If these mechanisms work as specified, what patterns emerge?" It does not claim predictive validity for real-world outcomes.

**Decision Context:**
- Structured thinking about consortium design
- Mechanism comparison and prioritization  
- Hypothesis generation for empirical research
- Workshop facilitation

### 1.2 Patterns

**Patterns the model should reproduce (calibration targets):**

| Pattern | Historical Reference | Model Target | Status |
|---------|---------------------|--------------|--------|
| Early coalition fragility | EDC failure (1954) | High early defection rates | ✓ Achieved |
| Sunk cost lock-in | ECSC → EU path dependency | Declining defection with investment | ✓ Achieved |
| Cascade failures | Financial contagion | Defection spreading through chains | ✓ Achieved |
| Asymmetric recovery | Consortium buyouts | Remainers strengthening post-exit | ✓ Achieved |

**Note:** Reproducing these patterns demonstrates *calibration*, not *validation*. See VALIDATION_CHECKLIST_STATUS.md for distinction.

---

## 2. ENTITIES, STATE VARIABLES, AND SCALES

### 2.1 Agents

| Agent Type | Count | Base Defection | Sunk Cost Sensitivity | Description |
|------------|-------|----------------|----------------------|-------------|
| Track A Core | 2-3 | 0.35 | 0.2 (strong effect) | Protected founders (EU, Ukraine) |
| Track B Core | 2-3 | 0.45 | 0.4 (medium effect) | Major partners (China, Russia) |
| Associate | 1-3 | 0.25-0.30 | 0.6 (weak effect) | Can switch tracks (UAE, India) |
| Tenant | 0-2 | 0.15-0.20 | 0.8 (minimal effect) | Service users (US/NASA) |
| Private | 0-2 | 0.10-0.15 | 0.9 (negligible effect) | Commercial (SpaceX) |

*Parameter sources documented in PARAMETER_PROVENANCE.md*

### 2.2 State Variables per Agent

```python
@dataclass
class ConsortiumAgent:
    # Identity
    agent_id: str
    agent_type: AgentType
    
    # Core attributes
    trust_level: float          # [0.0, 1.0] - current trust
    committed_capital: float    # €B escrowed
    sunk_cost: float           # €B accumulated investment
    domestic_stability: float   # [0.0, 1.0] - political stability
    
    # Decision parameters
    base_defection_prob: float  # Type-specific baseline
    sunk_cost_sensitivity: float # Type-specific multiplier
    shock_sensitivity: float    # Response to external shocks
    
    # Selene mechanisms
    lc_balance: float          # Lunar Credit holdings
    escrow_amount: float       # Forfeitable escrow
    
    # State tracking
    active: bool = True
    defected: bool = False
    defection_phase: Optional[int] = None
    defection_reason: str = ""
```

### 2.3 Environment Variables

```python
@dataclass
class GlobalState:
    current_phase: int          # [0, 12+]
    total_investment: float     # €B consortium-wide
    system_functionality: float # [0.0, 1.0] post-cascade
    political_volatility: float # [0.0, 1.0] shock intensity
    isru_operational: bool      # Revenue generation enabled
    revenue_generated: float    # €B total
```

### 2.4 Scales

| Dimension | Value | Rationale |
|-----------|-------|-----------|
| Temporal | 1 tick = 6 months | Aligns with project phases |
| Run length | 24-30 ticks (12-15 years) | Full project lifecycle |
| Spatial | Non-spatial | Agents interact via dependency graph |
| Ensemble size | N ≥ 200 | Statistical stability |

---

## 3. PROCESS OVERVIEW AND SCHEDULING

### 3.1 Process Sequence (per tick)

```
┌─────────────────────────────────────────────────────────┐
│                    TICK BEGINS                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 1. EXTERNAL_SHOCK_PHASE                                 │
│    - Generate election shocks (p = 0.25 × cycle_factor) │
│    - Generate economic shocks (p = 0.15 × stress)       │
│    - Generate technical shocks (p = 0.10 × risk)        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 2. DOMESTIC_POLITICS_PHASE                              │
│    - Update public_approval based on progress           │
│    - Check leadership_stability thresholds              │
│    - Trigger domestic_veto if conditions met            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 3. DEFECTION_DECISION_PHASE                             │
│    - Each agent calculates P(defect)                    │
│    - Compare to uniform random draw                     │
│    - Record defection if triggered                      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 4. FORFEITURE_PHASE (if defection post-threshold)       │
│    - Execute escrow forfeiture (Module A)               │
│    - Trigger poison pill cascade (Module D)             │
│    - Redistribute equity to remainers                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 5. CASCADE_PHASE                                        │
│    - Propagate dependency chain effects                 │
│    - Calculate system_functionality                     │
│    - Check termination conditions                       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 6. INVESTMENT_PHASE                                     │
│    - Remaining agents contribute to sunk_cost           │
│    - Update total_investment                            │
│    - Check phase transition milestones                  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 7. REVENUE_PHASE (if phase ≥ 9)                         │
│    - Generate ISRU/operational revenue                  │
│    - Convert to Lunar Credits (Module B)                │
│    - Distribute to remaining agents                     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 8. AUDIT_PHASE (quarterly)                              │
│    - Run compliance checks (Module C)                   │
│    - Update trust based on audit results                │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                     TICK ENDS                           │
└─────────────────────────────────────────────────────────┘
```

---

## 4. DESIGN CONCEPTS

### 4.1 Basic Principles

The model operationalizes the design thesis:

> "Cooperation can be made more robust through architectural design (mechanisms), not solely through diplomatic trust."

**Selene Mechanisms (from Module A-D):**

| Mechanism | Module | Effect | Implementation |
|-----------|--------|--------|----------------|
| Escrow/Forfeiture | A | Financial penalty deters exit | Multiplicative reduction in P(defect) |
| Lunar Credit Wealth | B | Accumulated stake reduces exit | Wealth effect on P(defect) |
| Poison Pill Cascade | D | Mutual deterrence via interdependence | Conditional collapse if ≥N exit |
| Audit Trust | C | Transparency builds confidence | Trust evolution per successful audit |
| Sunk Cost Lock-In | (implicit) | Investment reduces exit | Phase-dependent P(defect) multiplier |

### 4.2 Emergence

System-level outcomes emerge from individual decisions:
- Coalition survival/failure patterns
- Cascade propagation paths
- Path dependency in trust evolution
- Threshold effects in mechanism activation

### 4.3 Adaptation

Agents adapt defection probability based on:
- Accumulated sunk costs → reduces P(defect)
- External shocks → increases P(defect)
- Trust levels → modulates base rate
- Domestic political pressure → conditional increase

**Note:** No inter-run learning. Each simulation is independent.

### 4.4 Objectives

Agents implicitly maximize utility:

```
U = α(future_revenue) - β(sunk_cost_loss) - γ(reputation_cost) + δ(domestic_approval)
```

Weights (α, β, γ, δ) vary by agent type. Not explicitly modeled; embedded in base defection probabilities.

### 4.5 Prediction

Agents have **imperfect information**:
- Observe: Other agents' public commitments, investment levels, presence/absence
- Cannot observe: Other agents' internal P(defect), future shocks

### 4.6 Stochasticity

| Process | Distribution | Parameters |
|---------|-------------|------------|
| Defection decision | Bernoulli(p) | p = calculated probability |
| External shocks | Poisson-like | λ varies by phase, scenario |
| Trust initialization | Uniform | [trust_low, trust_high] per scenario |
| Technical failures | Bernoulli | p = TRL-based risk |
| Shock intensity | Triangular | [0.1, mode, 0.4] |

### 4.7 Observation

**Per-tick output:**
- Agent states (trust, sunk_cost, active)
- Defection events (who, when, why)
- Shock events (type, intensity)

**Per-run output:**
- Final outcome category
- Phase reached
- Remaining agent count
- Defection timing

**Aggregate output:**
- Success rates by scenario
- Mechanism effect sizes
- Trust threshold identification

---

## 5. INITIALIZATION

### 5.1 Scenario Configurations

| Scenario | Trust Baseline | Variance | Poison Pill | Shocks |
|----------|---------------|----------|-------------|--------|
| High Trust + Strong Pill | 0.7-0.9 | 0.05 | ≥3 triggers cascade | Enabled |
| High Trust + Weak Pill | 0.7-0.9 | 0.05 | ≥2 triggers cascade | Enabled |
| Medium Trust + Strong Pill | 0.4-0.6 | 0.10 | ≥3 triggers cascade | Enabled |
| Low Trust + Weak Pill | 0.1-0.3 | 0.05 | ≥2 triggers cascade | Enabled |
| NULL Model | 0.5 | 0.10 | Disabled | Enabled |
| FULL Model | 0.5 | 0.10 | ≥3 triggers cascade | Enabled |

### 5.2 Agent Initialization

```python
def initialize_agents(scenario_config):
    agents = []
    
    # Standard consortium composition
    composition = [
        (AgentType.TRACK_A_CORE, 2),   # EU, Ukraine
        (AgentType.TRACK_B_CORE, 2),   # China, Russia
        (AgentType.ASSOCIATE, 1),       # India
    ]
    
    for agent_type, count in composition:
        for i in range(count):
            trust = sample_trust(
                scenario_config.trust_baseline,
                scenario_config.trust_variance
            )
            
            agent = ConsortiumAgent(
                agent_id=f"{agent_type.value}_{i}",
                agent_type=agent_type,
                trust_level=trust,
                domestic_stability=random.uniform(0.5, 0.9),
                # Type-specific parameters set in __post_init__
            )
            agents.append(agent)
    
    return agents
```

---

## 6. INPUT DATA

**No external time-series required.**

### Calibration Targets (from historical analogs)

| Case | Target Pattern | Model Result | Status |
|------|---------------|--------------|--------|
| ECSC (1951) | ~85-95% founding success | 86.9% | ✓ Calibrated |
| China-Japan 2010 | Initial shock → partial recovery | Pattern matched | ✓ Calibrated |
| Japan-Korea 2019 | Prolonged friction | Pattern matched | ✓ Calibrated |
| EDC (1954) | Domestic veto → collapse | Pattern available | ✓ Calibrated |

**Note:** These are *calibration* results, not *validation*. Out-of-sample validation (Airbus case) pending.

---

## 7. SUBMODELS

### 7.1 Defection Probability Calculator

```python
def calculate_defection_probability(
    agent: ConsortiumAgent,
    phase: int,
    global_state: GlobalState,
    mechanisms_enabled: bool = True
) -> float:
    """
    Core defection calculation.
    
    Formula:
    P(defect) = base × trust_modifier × phase_modifier × mechanism_modifiers + shock
    
    Where:
    - trust_modifier = (1 - trust)^0.5
    - phase_modifier = declining with phase (sunk cost effect)
    - mechanism_modifiers = escrow, LC wealth, poison pill awareness
    """
    
    # Base rate (type-specific)
    base = agent.base_defection_prob
    
    # Trust effect: low trust → high defection
    trust_modifier = (1.0 - agent.trust_level) ** 0.5
    
    # Phase/sunk cost effect: later phases → lower defection
    phase_multipliers = {
        0: 1.5, 1: 1.2, 2: 0.8, 3: 0.5, 4: 0.3
    }
    phase_modifier = phase_multipliers.get(min(phase, 4), 0.3)
    
    # Sunk cost explicit effect
    sunk_ratio = min(1.0, agent.sunk_cost / 50.0)  # €50B max reference
    sunk_effect = 1.0 - (agent.sunk_cost_sensitivity * sunk_ratio)
    
    # Mechanism effects (if enabled)
    if mechanisms_enabled:
        # Escrow deterrent (Module A)
        escrow_deterrent = 0.1 * min(1.0, agent.escrow_amount / 5.0)
        
        # LC wealth effect (Module B)
        lc_effect = 0.1 * min(1.0, agent.lc_balance / 500.0)
        
        mechanism_modifier = (1.0 - escrow_deterrent) * (1.0 - lc_effect)
    else:
        mechanism_modifier = 1.0
    
    # External shock effect
    shock_effect = global_state.political_volatility * agent.shock_sensitivity
    
    # Combined probability
    prob = (
        base * 
        trust_modifier * 
        sunk_effect * 
        phase_modifier * 
        mechanism_modifier +
        shock_effect
    )
    
    # Clamp to valid range
    return max(0.05, min(0.95, prob))
```

### 7.2 Cascade Propagation

```python
def propagate_cascade(
    dependency_graph: Dict,
    withdrawn_agents: Set[str],
    coupling: float = 0.6,
    threshold: float = 0.4
) -> float:
    """
    Calculate system functionality after withdrawals.
    Uses criticality-weighted graph propagation.
    
    Returns: functionality score [0.0, 1.0]
    """
    stress = {node: 1.0 if node in withdrawn_agents else 0.0 
              for node in dependency_graph}
    
    # Propagate stress through dependencies
    for iteration in range(10):
        converged = True
        for node, data in dependency_graph.items():
            if node not in withdrawn_agents:
                incoming = sum(
                    stress[dep] * coupling
                    for dep in data['requires']
                    if dep in stress
                )
                new_stress = min(1.0, incoming)
                if abs(new_stress - stress[node]) > 0.01:
                    converged = False
                stress[node] = new_stress
        
        if converged:
            break
    
    # Calculate overall functionality
    total_crit = sum(d['criticality'] for d in dependency_graph.values())
    functional_crit = sum(
        data['criticality'] * (1.0 - stress[node])
        for node, data in dependency_graph.items()
    )
    
    return functional_crit / total_crit if total_crit > 0 else 0.0
```

### 7.3 Outcome Classification

```python
def classify_outcome(
    final_active: int,
    functionality: float,
    cascade_triggered: bool,
    final_phase: int
) -> OutcomeCategory:
    """
    Classify final outcome per ODD protocol.
    """
    if cascade_triggered:
        return OutcomeCategory.CATASTROPHIC_FAILURE
    
    if final_active >= 4 and functionality >= 0.8:
        return OutcomeCategory.STRUCTURAL_SUCCESS
    
    if final_active >= 2 and functionality >= 0.4:
        return OutcomeCategory.PARTIAL_SUCCESS
    
    if final_active >= 1 and functionality >= 0.2:
        return OutcomeCategory.GRACEFUL_DEGRADATION
    
    return OutcomeCategory.ORDERLY_DISSOLUTION
```

---

## 8. VALIDATION STATUS

*Updated per review findings (January 2026)*

### 8.1 Verification (Phase 1) — ✓ Complete

| Test | Status | Evidence |
|------|--------|----------|
| Perfect trust → 100% success | ✓ Pass | consortium_abm_verification.py |
| Zero trust → ≥95% failure | ✓ Pass | consortium_abm_verification.py |
| Single agent survival | ✓ Pass | Edge case tests |
| Mass defection handling | ✓ Pass | Stress tests |
| Boundary conditions | ✓ Pass | Full test suite |

### 8.2 Pattern Calibration (Phase 2) — ✓ Complete

| Pattern | Historical Case | Model Result | Status |
|---------|----------------|--------------|--------|
| Sunk cost lock-in | ECSC 1951 | 86.9% success | ✓ Calibrated |
| Early fragility | EDC 1954 | High early defection | ✓ Calibrated |
| Bilateral friction | China-Japan 2010 | Pattern matched | ✓ Calibrated |
| Prolonged tension | Japan-Korea 2019 | Pattern matched | ✓ Calibrated |

**Important:** This is *calibration* (finding parameters that match patterns), not *validation* (demonstrating predictive accuracy).

### 8.3 Statistical Analysis (Phase 3) — ✓ Complete

| Analysis | Status | Result |
|----------|--------|--------|
| Bootstrap confidence intervals | ✓ Done | [+39.6pp, +44.7pp] |
| Mechanism ablation | ✓ Done | Sunk cost dominant (+16.6pp) |
| Trust sensitivity | ✓ Done | Threshold identified (0.54 → 0.18) |
| Extreme bounds | ✓ Done | Effect robust across trust range |

### 8.4 External Validation (Phase 4) — ⏳ Partial

| Component | Status | Timeline |
|-----------|--------|----------|
| Expert elicitation | ⏳ Planned | +60 days |
| Out-of-sample test | ⏳ Planned | +90 days |
| Structural uncertainty | ⏳ Planned | +180 days |

**Current authorization:** Exploratory use only. Decision-grade pending Phase 4 completion.

---

## 9. STRUCTURAL ASSUMPTIONS

*See STRUCTURAL_ASSUMPTIONS.md for full documentation.*

### Load-Bearing Assumptions

| # | Assumption | Robustness | Impact |
|---|------------|------------|--------|
| 1 | Probabilistic defection decision | Not tested | High |
| 2 | Discrete phase structure | Not tested | Medium |
| 3 | Sunk cost reduces defection | Sensitivity tested | High |
| 4 | Trust evolves linearly | Not tested | Medium |
| 5 | IID shock process | Not tested | Medium |
| 6 | Fixed agent types | Not tested | Low |
| 7 | Poison pill threshold | Sensitivity tested | Medium |
| 8 | Bilateral-consortium linkage | Integration tested | Medium |

### Structural Uncertainty Envelope (Estimated)

| Finding | Point Estimate | Plausible Range |
|---------|---------------|-----------------|
| Mechanism effect | +42pp | +15pp to +60pp |
| Sunk cost contribution | +16.6pp | +5pp to +25pp |
| Trust threshold shift | 36pp | 15pp to 50pp |

*These ranges reflect expert judgment about alternative specifications, not computed bounds.*

---

## 10. KNOWN LIMITATIONS

1. **No learning across runs:** Agents don't adapt strategies
2. **Simplified domestic politics:** Binary veto vs. continuous pressure
3. **No negotiation:** Agents can't renegotiate terms
4. **Static dependency graph:** Architecture fixed at initialization
5. **No partial defection:** Exit is all-or-nothing
6. **IID shocks:** Real crises cluster and correlate
7. **Fixed agent types:** Real actors evolve over time
8. **Linear mechanisms:** Real effects may have thresholds

---

## 11. REPRODUCIBILITY

### 11.1 Code Repository

- Location: `selene_complete_standalone/`
- Language: Python 3.10+
- Dependencies: Standard library only (no external packages required)

### 11.2 Random Seeds

- All published results use documented seeds (0-99 for 100-run batches)
- Seeds stored in config files
- Reproducible via: `python run_simulation.py --seed <N>`

### 11.3 Documentation

| Document | Purpose |
|----------|---------|
| This ODD Protocol | Model specification |
| PARAMETER_PROVENANCE.md | Parameter sources |
| STRUCTURAL_ASSUMPTIONS.md | Load-bearing assumptions |
| CONDITIONS_OF_USE.md | Authorized uses |
| VALIDATION_CHECKLIST_STATUS.md | Methodology status |

---

## 12. RESULTS SUMMARY (v2.1)

### NULL vs FULL Model Comparison

```
                    NULL Model    FULL Model    Difference
Structural Success     19.2%        61.4%        +42.2pp
Partial Success        24.1%        22.3%         -1.8pp
Graceful Degradation   12.4%         8.1%         -4.3pp
Catastrophic Failure   44.3%         8.2%        -36.1pp

Statistical significance: p < 0.001
Bootstrap 95% CI: [+39.6pp, +44.7pp]
```

### Mechanism Ablation

| Mechanism | Individual Effect | Rank |
|-----------|------------------|------|
| Sunk Cost Lock-In | +16.6pp | 1 |
| Wealth Effects | +15.2pp | 2 |
| Escrow/Forfeiture | +9.0pp | 3 |
| Audit Trust | -0.8pp | 4 |
| Poison Pill | -5.8pp | 5 |
| **Combined** | **+41.2pp** | — |

*Synergy: Combined effect exceeds sum of individual effects.*

---

## APPENDIX A: Configuration Files

See `config/` directory:
- `selene_default.yaml` — Standard configuration
- `selene_high_trust.yaml` — Optimistic scenario
- `selene_low_trust.yaml` — Pessimistic scenario
- `selene_weak_pill.yaml` — Alternative mechanism design

---

## APPENDIX B: Change Log from v2.0

| Item | v2.0 | v2.1 |
|------|------|------|
| Status | "Validated & Decision-Ready" | "Exploratory Analysis Tool" |
| Validation claims | Overclaimed | Correctly characterized |
| Structural assumptions | Implicit | Documented |
| Parameter provenance | Incomplete | Complete |
| Use conditions | Undefined | Specified |

---

*This ODD protocol follows Grimm et al. (2020) standards for agent-based model documentation.*  
*Revised January 2026 per review findings.*
