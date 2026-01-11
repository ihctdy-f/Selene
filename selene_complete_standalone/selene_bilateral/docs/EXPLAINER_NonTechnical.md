# Understanding the Japan-China Trade Friction Simulator
## A Non-Technical Guide to Reading the Results

---

## What Is This?

This is a **scenario exploration tool** — a "what if?" machine that runs hundreds of imaginary Japan-China trade disputes to see how different conditions lead to different outcomes.

It is **not** a crystal ball. It doesn't predict "there will be a trade war in 2026." 

Instead, it answers questions like:
- "If nationalism rises in both countries, what patterns become more likely?"
- "Does US involvement make escalation more or less likely?"
- "How long until supply chain diversification makes the dispute moot?"

---

## How It Works (Simple Version)

```
┌─────────────────────────────────────────────────────────────┐
│                     ONE SIMULATION RUN                       │
│                                                             │
│   Start: Japan & China trading normally                     │
│      ↓                                                      │
│   Each Month:                                               │
│   • Random events happen (incidents, elections, etc.)       │
│   • Each side decides: restrict trade more? less? hold?     │
│   • Pain accumulates, supply chains slowly adjust           │
│      ↓                                                      │
│   End: After 4 years, classify what happened                │
│                                                             │
│   Run this 100 times → See distribution of outcomes         │
└─────────────────────────────────────────────────────────────┘
```

---

## The Six Possible Endings

| Outcome | What It Means | Real-World Analog |
|---------|---------------|-------------------|
| **Stable Interdependence** | Tensions stayed low, trade continued normally | Japan-China 2000s |
| **Managed Competition** | High tension but no breakdown — a "cold" trade relationship | US-China 2023-24 |
| **Gradual Decoupling** | Both sides slowly built alternatives, drifted apart | EU-Russia energy (post-2022) |
| **Escalation Spiral** | Tit-for-tat restrictions heading toward crisis | Could have been 2010 rare earths if not de-escalated |
| **Asymmetric Lock-in** | One side diversified, the other got stuck dependent | Hypothetical |
| **Political Rupture** | Domestic political crisis ended the game early | Rare |

---

## Reading the Results Table

```
Scenario                 Stable    Managed   Decoupling   Spiral
─────────────────────────────────────────────────────────────────
japan_china_default       20%       14%        22%         43%
japan_china_high_tension   0%        0%        98%          2%
japan_china_stabilization 75%        9%         0%         16%
```

**How to read this:**

Under "default" conditions (today's approximate reality):
- 20 out of 100 simulated disputes stayed calm
- 43 out of 100 escalated into a spiral
- The remaining 36 ended somewhere in between

Under "high tension" (hawkish leaders, high nationalism):
- 98 out of 100 ended in gradual decoupling
- Almost none stayed stable

Under "stabilization" (pragmatic leaders, low nationalism):
- 75 out of 100 stayed calm
- Only 16 escalated

---

## Key Insight

> **The same two economies, same trade dependencies, same third parties — but different leadership postures produce wildly different outcomes.**

This is the main takeaway: **political variables matter more than economic structure** for determining whether a dispute escalates or stabilizes.

---

## What The "Averages" Row Means

```
Scenario                 Peak Friction   GDP Loss A   GDP Loss B
────────────────────────────────────────────────────────────────
japan_china_default           0.72         19.8         37.8
japan_china_high_tension      0.98        176.6        184.1
japan_china_stabilization     0.18          0.3          0.6
```

| Metric | What It Measures | Scale |
|--------|------------------|-------|
| **Peak Friction** | Highest average restriction level reached | 0 = free trade, 1 = full embargo |
| **GDP Loss A/B** | Cumulative economic pain (model units, not real $) | Higher = more damage |
| **Div A/B** | How much each side diversified supply chains | 0 = no change, 1 = fully independent |

**Note:** GDP Loss numbers are *relative*, not calibrated to real dollars. Use them to compare scenarios, not to claim "a trade war would cost $X billion."

---

## What This Model Does NOT Do

| ❌ Does Not | ✅ Does |
|-------------|---------|
| Predict specific events or dates | Show which conditions lead to which patterns |
| Give precise economic damage estimates | Compare relative severity across scenarios |
| Account for black swans (war, pandemic) | Model known political-economic dynamics |
| Replace expert judgment | Structure expert discussions with data |

---

## How Conclusions Are Reached

When we say "high nationalism increases decoupling probability," here's the backing:

```
Evidence Chain:
1. Ran 100 simulations with nationalism = 0.5 → 22% decoupling
2. Ran 100 simulations with nationalism = 0.75 → 98% decoupling
3. All other parameters held constant
4. Difference is statistically significant (p < 0.01)
5. Mechanism is traceable: higher nationalism → lower de-escalation threshold 
   → longer restriction duration → more diversification time → decoupling
```

This is **scenario analysis**, not prediction. The claim is "IF nationalism is high, THEN decoupling becomes much more likely" — not "nationalism WILL rise" or "decoupling WILL happen."

---

## Limitations To Mention When Sharing

1. **Not calibrated to historical data** — parameters are estimates, not fitted values
2. **4-year horizon** — longer projections would need different model structure
3. **Two-actor focus** — doesn't model spillovers to Korea, Taiwan, ASEAN in detail
4. **No black swans** — assumes no war, no pandemic, no regime collapse
5. **Relative not absolute** — GDP loss numbers are for comparison, not dollar estimates

---

## When To Use This

✅ **Good for:**
- Structuring scenario planning workshops
- Identifying key variables that drive outcomes
- Comparing "what if?" policy options
- Communicating uncertainty ranges to decision-makers

❌ **Not good for:**
- Precise forecasting
- Regulatory cost-benefit analysis requiring dollar figures
- Short-term (< 1 year) predictions
- Situations where black swan events are the main concern

---

## Glossary

| Term | Meaning |
|------|---------|
| **ABM** | Agent-Based Model — simulates individual actors making decisions |
| **Friction** | Level of trade restrictions (0-1 scale) |
| **Diversification** | Building alternative supply chains to reduce dependence |
| **Escalation spiral** | Each side responds to the other's restrictions with more restrictions |
| **Audience cost** | Political cost to a leader of backing down after public escalation |
| **Third party** | External actors (US, EU, ASEAN) who influence the bilateral dispute |

---

*Document version: January 2026*
*Model version: selene_bilateral v0.1*
