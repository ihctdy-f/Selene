# Parameter Provenance Documentation

**Document Type:** Technical Reference  
**Version:** 1.0  
**Date:** January 2026

---

## Classification System

All model parameters are classified into three tiers:

| Tier | Definition | Documentation Standard |
|------|------------|----------------------|
| **Empirical** | Measured or estimated from data | Source citation required |
| **Theoretical** | Derived from domain knowledge | Reasoning documented |
| **Stipulated** | Assumed for exploration | Flagged for sensitivity |

---

## Consortium Model Parameters

### Agent Type Parameters

#### Track A Core (EU, Ukraine)

| Parameter | Value | Tier | Provenance |
|-----------|-------|------|------------|
| `base_defection_prob` | 0.35 | Theoretical | Higher than associates due to major power strategic calculations; informed by historical defection rates in multilateral organizations |
| `sunk_cost_sensitivity` | 0.03 | Stipulated | Assumed strong lock-in for core participants; explored range [0.01, 0.05] |
| `shock_sensitivity` | 0.15 | Theoretical | Core nations have more exposure to domestic political pressures |

#### Track B Core (China, Russia)

| Parameter | Value | Tier | Provenance |
|-----------|-------|------|------------|
| `base_defection_prob` | 0.45 | Theoretical | Higher baseline reflecting lower institutional trust heritage; consistent with Sino-Russian partnership patterns |
| `sunk_cost_sensitivity` | 0.04 | Stipulated | Assumed medium lock-in; explored range [0.02, 0.06] |
| `shock_sensitivity` | 0.20 | Theoretical | More sensitive to geopolitical shocks based on recent history |

#### Associate (UAE, India)

| Parameter | Value | Tier | Provenance |
|-----------|-------|------|------------|
| `base_defection_prob` | 0.30 | Theoretical | Lower than core due to less strategic stake; associates have exit options |
| `sunk_cost_sensitivity` | 0.05 | Stipulated | Weak lock-in; explored range [0.03, 0.07] |
| `shock_sensitivity` | 0.10 | Theoretical | Lower exposure to great power tensions |

#### Tenant (US/NASA)

| Parameter | Value | Tier | Provenance |
|-----------|-------|------|------------|
| `base_defection_prob` | 0.20 | Empirical | NASA partnerships historically stable; ISS partnership tenure as reference |
| `sunk_cost_sensitivity` | 0.06 | Stipulated | Minimal lock-in given commercial alternatives |
| `shock_sensitivity` | 0.12 | Theoretical | Moderate; congressional funding cycles create vulnerability |

#### Private (SpaceX)

| Parameter | Value | Tier | Provenance |
|-----------|-------|------|------------|
| `base_defection_prob` | 0.15 | Theoretical | Commercial actors optimize for ROI; lower defection when profitable |
| `sunk_cost_sensitivity` | N/A | — | No sunk cost mechanism for private actors |
| `shock_sensitivity` | 0.08 | Theoretical | Insulated from political shocks; responds to market signals |

### Mechanism Parameters

#### Escrow/Forfeiture (Module A)

| Parameter | Value | Tier | Provenance |
|-----------|-------|------|------------|
| `escrow_rate` | 0.10 | Stipulated | Assumed 10% of contribution held in escrow; policy choice |
| `forfeiture_deterrent` | 0.15 | Theoretical | Deterrent effect estimated from contract theory literature on penalties |
| `redistribution_factor` | 0.80 | Stipulated | 80% of forfeited escrow redistributed to remainers |

#### Wealth Effects (Module B)

| Parameter | Value | Tier | Provenance |
|-----------|-------|------|------------|
| `wealth_accumulation_rate` | 0.12 | Theoretical | Based on estimated lunar resource value appreciation; speculative |
| `wealth_stake_coefficient` | 0.20 | Stipulated | Defection reduction per unit wealth stake; explored [0.10, 0.30] |

#### Poison Pill (Module D)

| Parameter | Value | Tier | Provenance |
|-----------|-------|------|------------|
| `cascade_threshold` | 2 | Stipulated | ≥2 late defections trigger collapse; design parameter |
| `late_phase_definition` | Phase 3+ | Stipulated | "Late" defined as Phase 3 or later |
| `cascade_probability` | 0.70 | Theoretical | Given trigger, 70% collapse probability; based on institutional fragility literature |

#### Audit Trust (Module C)

| Parameter | Value | Tier | Provenance |
|-----------|-------|------|------------|
| `trust_increment` | 0.05 | Theoretical | Successful phase completion increases trust by 0.05; informed by cooperation experiments |
| `trust_decay` | 0.02 | Stipulated | Trust decays slowly without positive signals |
| `audit_threshold` | 0.85 | Stipulated | 85% compliance required for trust increment |

### Sunk Cost Parameters

| Parameter | Value | Tier | Provenance |
|-----------|-------|------|------------|
| `phase_cost_increment` | €10B | Stipulated | Each phase adds €10B sunk cost; order-of-magnitude estimate |
| `lock_in_coefficient` | 0.12 | Theoretical | Per-phase reduction in defection probability; informed by ECSC calibration |

### Shock Parameters

| Parameter | Value | Tier | Provenance |
|-----------|-------|------|------------|
| `shock_probability` | 0.08 | Empirical | ~8% annual probability of major geopolitical shock; based on historical crisis frequency 1950-2020 |
| `shock_intensity_range` | [0.05, 0.25] | Empirical | Shock magnitude range calibrated to crisis severity distributions |
| `shock_correlation` | 0.00 | Stipulated | Shocks assumed IID; simplification acknowledged |

---

## Bilateral Model Parameters

### De-escalation Configuration

| Parameter | Value | Tier | Provenance |
|-----------|-------|------|------------|
| `maintenance_cost` | 0.04 | Theoretical | Cost of maintaining restrictions; informed by trade war literature |
| `time_accel` | 0.15 | Stipulated | Time compression factor for simulation |
| `grace_period` | 4 | Stipulated | Months before de-escalation pressure builds |
| `pressure_rate` | 0.08 | Theoretical | Rate of de-escalation pressure accumulation |
| `duration_sens` | 0.10 | Theoretical | Sensitivity to dispute duration |
| `friction_thresh` | 0.35 | Stipulated | Threshold for friction to trigger mechanisms |
| `max_pressure` | 0.50 | Stipulated | Maximum de-escalation pressure cap |
| `fatigue_rate` | 0.05 | Theoretical | Rate of public fatigue with dispute |
| `gdp_thresh` | 2.0 | Empirical | GDP loss threshold for policy change; informed by 2010 rare earth case |
| `max_fatigue` | 0.40 | Stipulated | Maximum fatigue level |
| `bleed_rate` | 0.012 | Theoretical | Rate of friction bleeding over time |
| `intensity_thresh` | 0.40 | Stipulated | Intensity threshold for de-escalation |
| `friction_memory_decay` | 0.88 | Theoretical | Memory decay rate; informed by dispute duration studies |

### Agent Profile Parameters (2010 Case)

| Parameter | Value | Tier | Provenance |
|-----------|-------|------|------------|
| Japan `retaliation_propensity` | 0.05 | Empirical | Japan did not retaliate in 2010; calibrated to observed behavior |
| Japan `escalation_threshold` | 0.95 | Empirical | DPJ government highly reluctant to escalate |
| China `de_escalation_threshold` | 0.45 | Empirical | China backed down under international pressure; calibrated to outcome |
| China `restriction_intensity` (RE) | 0.70 | Empirical | Estimated restriction level during embargo |

### Agent Profile Parameters (2019 Case)

| Parameter | Value | Tier | Provenance |
|-----------|-------|------|------------|
| Japan `retaliation_propensity` | 0.30 | Empirical | Abe government initiated controls; calibrated |
| Korea `retaliation_propensity` | 0.65 | Empirical | Moon government responded strongly; calibrated |
| Both `escalation_threshold` | 0.30-0.45 | Empirical | Both sides willing to act; calibrated to timeline |

### Sector Dependency Parameters

| Sector | Parameter | Value | Tier | Source |
|--------|-----------|-------|------|--------|
| Rare Earths (2010) | China market share | 0.93 | Empirical | USGS data, 2010 |
| Rare Earths (2010) | Japan substitution time | 24 months | Empirical | Post-embargo diversification timeline |
| Semiconductors (2019) | Japan market share (materials) | 0.85 | Empirical | Industry reports |
| Semiconductors (2019) | Korea criticality | 0.90 | Empirical | Industry concentration data |

---

## ECSC Calibration Parameters

| Parameter | Value | Tier | Provenance |
|-----------|-------|------|------------|
| Member trust levels | 0.60-0.75 | Theoretical | Post-war reconstruction context; Marshall Plan backing |
| `governance_lock` | 0.40 | Theoretical | Supranational High Authority; strong institutional commitment |
| `economic_benefit` | 0.25 | Empirical | Immediate tariff reduction benefits; documented historical gains |
| `marshall_plan_support` | 0.60 multiplier | Empirical | US backing reduced early defection risk |
| Base defection (major) | 0.06 | Calibrated | Adjusted to produce 85-95% success rate |
| Base defection (minor) | 0.03 | Calibrated | Small nations more cooperative historically |

---

## Sensitivity Classification

### High Sensitivity (Results Significantly Change)

- `base_defection_prob` (all agent types)
- `trust_level` (initial)
- `sunk_cost_sensitivity`
- `lock_in_coefficient`

### Medium Sensitivity

- `shock_probability`
- `escrow_rate`
- `wealth_stake_coefficient`
- `cascade_threshold`

### Low Sensitivity

- `trust_increment`
- `audit_threshold`
- `phase_cost_increment` (within order of magnitude)

---

## Documentation Notes

### Empirical Parameters
All empirical parameters include source citations in code comments. Ranges reflect measurement uncertainty where applicable.

### Theoretical Parameters
Theoretical derivations are documented in accompanying memos. Alternative theoretical justifications exist for many parameters; sensitivity analysis explores consequences.

### Stipulated Parameters
Stipulated parameters are exploration choices. Results should be interpreted conditionally: "If [parameter] = [value], then [outcome]." Sensitivity sweeps provide robustness checks.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | January 2026 | Initial comprehensive documentation |
