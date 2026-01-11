# Calibration Case: 2010 Japan-China Rare Earth Crisis
## Data Extraction Template

**Status:** Template — values to be filled from sources  
**Target:** Tune model parameters until output distribution matches historical pattern

---

## 1. CASE OVERVIEW

| Field | Value |
|-------|-------|
| **Case Name** | 2010 Rare Earth Crisis |
| **Start Date** | September 7, 2010 (fishing boat collision) |
| **Peak Restriction** | ~October 2010 |
| **De-escalation Begins** | ~November 2010 |
| **Near-Normalization** | ~February 2011 |
| **Total Duration** | ~5-6 months acute phase |
| **Long-term Effect** | Japan diversification initiatives (ongoing years) |

**Narrative Summary:**
Japanese Coast Guard detained Chinese fishing boat captain near Senkaku/Diaoyu islands. China responded with informal rare earth export restrictions. Japan released captain. Restrictions gradually eased. Japan accelerated supply chain diversification.

---

## 2. START PARAMETERS (t=0, September 2010)

### 2.1 State A: Japan

| Parameter | Model Variable | Value | Source | Notes |
|-----------|----------------|-------|--------|-------|
| GDP (trillion USD) | `gdp` | ___ | World Bank | |
| Trade openness | `trade_openness` | ___ | Trade/GDP ratio | |
| Regime type | `regime_type` | `democracy` | Fixed | |
| Leader | — | Naoto Kan (DPJ) | — | |
| Leader tenure (years) | `leader_tenure` | ___ | Kan took office June 2010 | ~3 months |
| Approval rating | `approval_rating` | ___ | NHK/Asahi polling Sept 2010 | |
| Nationalism index | `nationalism_index` | ___ | Proxy needed | See section 3 |
| Escalation threshold | `escalation_threshold` | ___ | To be calibrated | |
| De-escalation threshold | `de_escalation_threshold` | ___ | To be calibrated | |
| Retaliation propensity | `retaliation_propensity` | ___ | To be calibrated | |

### 2.2 State B: China

| Parameter | Model Variable | Value | Source | Notes |
|-----------|----------------|-------|--------|-------|
| GDP (trillion USD) | `gdp` | ___ | World Bank | |
| Trade openness | `trade_openness` | ___ | Trade/GDP ratio | |
| Regime type | `regime_type` | `autocracy` | Fixed | |
| Leader | — | Hu Jintao | — | |
| Leader tenure (years) | `leader_tenure` | ___ | Hu in power since 2002 | ~8 years |
| Approval rating | `approval_rating` | ___ | Not directly measurable | Use 0.7 default |
| Nationalism index | `nationalism_index` | ___ | Proxy needed | See section 3 |
| Escalation threshold | `escalation_threshold` | ___ | To be calibrated | |
| De-escalation threshold | `de_escalation_threshold` | ___ | To be calibrated | |
| Retaliation propensity | `retaliation_propensity` | ___ | To be calibrated | |

### 2.3 Sector Dependencies (Rare Earths Focus)

| Parameter | Model Variable | Value | Source | Notes |
|-----------|----------------|-------|--------|-------|
| Japan RE imports from China (billion USD) | `b_exports_to_a` | ___ | UN Comtrade / METI | |
| China RE exports to Japan (% of China total) | — | ___ | Context for self-harm | |
| Japan RE import dependence on China (%) | — | ___ | METI reports | Key vulnerability metric |
| Japan substitution time (months) | `a_substitution_time` | ___ | Estimate based on 2010-2015 diversification | |
| Japan substitution cost premium | `a_substitution_cost` | ___ | Price differential Australia/US vs China | |
| Criticality score (Japan) | `a_criticality_score` | ___ | RE used in electronics, EVs, defense | |
| Political salience (Japan) | `a_political_salience` | ___ | Media coverage proxy | |
| Self-harm coefficient (China) | `b_restriction_self_harm` | ___ | Impact on Chinese RE exporters | |

### 2.4 Third Party Status (September 2010)

| Party | Alignment | Active at Start? | Intervention Threshold | Source |
|-------|-----------|------------------|------------------------|--------|
| USA | Pro-Japan (___ ) | No | ___ | Clinton statements came later |
| EU | Neutral-slight Japan (___ ) | No | ___ | |
| ASEAN | Neutral (___ ) | No | ___ | |

---

## 3. PROXY INDICATORS (For Hard-to-Measure Variables)

### 3.1 Nationalism Index

**Japan:**
| Indicator | Value Sept 2010 | Source | Weight |
|-----------|-----------------|--------|--------|
| % believing Senkaku "definitely Japanese" | ___ | Pew/Genron polling | 0.3 |
| Anti-China sentiment (unfavorable %) | ___ | Pew Global Attitudes | 0.3 |
| Protest activity level | ___ | News archives | 0.2 |
| Diet hawkish statements (count) | ___ | Parliamentary records | 0.2 |

**Composite formula:** `nationalism_index = weighted average, normalized to 0-1`

**China:**
| Indicator | Value Sept 2010 | Source | Weight |
|-----------|-----------------|--------|--------|
| Anti-Japan protest incidents | ___ | News archives | 0.4 |
| Weibo/forum sentiment (if available) | ___ | Social media archives | 0.3 |
| Official media hawkish editorials | ___ | People's Daily, Global Times | 0.3 |

### 3.2 Political Salience

| Indicator | Japan Value | China Value | Source |
|-----------|-------------|-------------|--------|
| Front-page stories on RE (count, Oct 2010) | ___ | ___ | News archives |
| Diet/NPC mentions | ___ | ___ | Parliamentary records |
| Industry association statements | ___ | ___ | Keidanren, CCPIT |

---

## 4. OBSERVED OUTCOME TIMELINE

Fill in actual restriction levels and events:

| Date | Event | Estimated Friction Level | Source |
|------|-------|--------------------------|--------|
| Sept 7 | Collision incident | 0.0 | News |
| Sept 8-12 | Captain detained | 0.0 | News |
| Sept 13-19 | Informal RE slowdown reported | ___ | Industry reports |
| Sept 20-24 | Customs delays expand | ___ | Reuters, industry |
| Sept 24 | Japan releases captain | — | News |
| Oct 1-15 | Restrictions continue despite release | ___ | Trade data |
| Oct 15-31 | Peak restriction period | ___ | Trade data |
| Nov 1-15 | Gradual easing begins | ___ | Trade data |
| Dec 2010 | Partial normalization | ___ | Trade data |
| Feb 2011 | Near-normal trade | ___ | Trade data |
| 2011-2015 | Japan diversification accelerates | — | METI policy docs |

**Friction Level Estimation:**

```
0.0 = Normal trade
0.2 = Minor delays/scrutiny
0.4 = Significant slowdown
0.6 = Major disruption  
0.8 = Near-embargo
1.0 = Full embargo
```

---

## 5. OUTCOME PATTERN TO MATCH

Based on historical record, model should produce:

| Metric | Expected Range | Tolerance |
|--------|----------------|-----------|
| Peak friction level | 0.6 - 0.9 | ±0.15 |
| Time to peak (steps/months) | 1-2 months | ±1 month |
| Time to de-escalation start | 2-3 months | ±1 month |
| Time to near-normalization | 5-7 months | ±2 months |
| Final outcome category | `normalization` or `stable_interdependence` | — |
| Japan diversification at end | 0.1 - 0.3 (started but not complete) | ±0.1 |
| Probability of escalation spiral | < 20% | Model should rarely spiral |
| Probability of full decoupling | < 10% | Didn't happen historically |

---

## 6. DATA SOURCES CHECKLIST

### Trade Data
- [ ] UN Comtrade (comtrade.un.org) — RE trade flows 2009-2011
- [ ] METI trade statistics (meti.go.jp)
- [ ] USGS Rare Earth reports (pubs.usgs.gov)
- [ ] China Customs statistics (if accessible)

### Political Data
- [ ] NHK/Asahi/Yomiuri polling archives — Kan approval Sept-Oct 2010
- [ ] Pew Global Attitudes — Japan-China mutual perceptions 2010
- [ ] Genron NPO annual Japan-China survey

### News/Event Data
- [ ] Reuters/AP archives — incident timeline
- [ ] Nikkei archives — industry impact reporting
- [ ] People's Daily/Global Times — Chinese official framing

### Academic Sources
- [ ] "The 2010 Rare Earth Crisis" — multiple papers exist
- [ ] CSIS/Brookings analyses from 2010-2011
- [ ] RIETI (Japan) policy analyses

### Industry Reports
- [ ] Keidanren statements
- [ ] Japan Rare Earths Industry Association
- [ ] Price data: Metal Pages, Asian Metal

---

## 7. PARAMETER CALIBRATION TARGETS

After data collection, these are the parameters to tune:

| Parameter | Initial Guess | Calibration Range | Priority |
|-----------|---------------|-------------------|----------|
| `jpn_nationalism_index` | 0.5 | 0.4 - 0.7 | High |
| `chn_nationalism_index` | 0.65 | 0.5 - 0.8 | High |
| `jpn_escalation_threshold` | 0.35 | 0.2 - 0.5 | High |
| `chn_escalation_threshold` | 0.25 | 0.15 - 0.4 | High |
| `jpn_de_escalation_threshold` | 0.5 | 0.4 - 0.7 | Medium |
| `chn_de_escalation_threshold` | 0.6 | 0.4 - 0.7 | Medium |
| `coercion_coefficient` | 0.3 | 0.2 - 0.5 | Medium |
| `weakness_signal_coefficient` | 0.2 | 0.1 - 0.4 | Medium |
| `a_substitution_time` | 36 | 24 - 48 | Low (known-ish) |
| `shock_probabilities.territorial_incident` | 0.02 | 0.01 - 0.05 | Low |

**Calibration Method:**
1. Set measurable parameters from data
2. Run 500 simulations
3. Compare output distribution to observed pattern
4. Adjust tunable parameters
5. Repeat until fit

---

## 8. SUCCESS CRITERIA

Model is **calibrated** when:

- [ ] Median peak friction within 0.15 of observed
- [ ] 70%+ of runs show de-escalation within 6 months
- [ ] < 20% of runs end in escalation spiral
- [ ] < 10% of runs end in full decoupling
- [ ] Diversification trajectory plausible (Japan starts diversifying)

Model is **validated** when:

- [ ] Passes calibration on 2010 case
- [ ] AND produces plausible results on 2012 Senkaku case (out-of-sample)
- [ ] AND sensitivity analysis shows reasonable parameter stability

---

## 9. OUTPUT FILE STRUCTURE

After calibration:

```
calibration/
├── cases/
│   ├── rare_earth_2010/
│   │   ├── parameters.yaml      # Extracted start conditions
│   │   ├── observed_timeline.csv # Actual friction over time
│   │   ├── sources.md           # Data provenance
│   │   └── calibration_results.json
│   └── senkaku_2012/
│       └── ... (validation case)
├── tuned_parameters.yaml        # Final calibrated values
└── calibration_report.md        # Methods and results
```

---

## 10. NEXT ACTIONS

| Step | Task | Owner | Status |
|------|------|-------|--------|
| 1 | Pull 2010 RE trade data from UN Comtrade | ___ | ⬜ |
| 2 | Find Kan approval polling Sept-Oct 2010 | ___ | ⬜ |
| 3 | Compile incident timeline from news archives | ___ | ⬜ |
| 4 | Estimate friction levels from trade disruption reports | ___ | ⬜ |
| 5 | Calculate nationalism proxies | ___ | ⬜ |
| 6 | Fill in this template | ___ | ⬜ |
| 7 | Run calibration script | ___ | ⬜ |
| 8 | Document results | ___ | ⬜ |

---

*Template version: 1.0*
*Created: January 2026*
