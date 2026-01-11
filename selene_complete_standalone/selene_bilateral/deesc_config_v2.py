#!/usr/bin/env python3
"""
De-escalation Config V2
=======================
Fixed thresholds so all 4 mechanisms contribute meaningfully.

Mechanism Contributions (during peak friction):
- Time-Decay:    ~15%  (cost of maintaining restrictions)
- Intl-Pressure: ~40%  (third-party pressure + reputation)
- Econ-Fatigue:  ~10%  (builds over time, ~37% post-peak)
- Memory:        ~35%  (accumulated grievance + peak reputation)

Different mechanisms dominate at different phases:
- PEAK: Intl pressure + time costs push for de-escalation
- POST-PEAK: Economic fatigue + memory sustain the peace
"""

DEESCALATION_CONFIG_V2 = {
    # Time-decay: Costs of maintaining restrictions
    "maintenance_cost": 0.35,      # Base cost per month
    "time_accel": 0.30,            # How fast costs accelerate
    "grace_period": 1,             # Months before costs start
    
    # International pressure: Third parties + reputation
    "pressure_rate": 0.15,         # Base pressure from friction
    "duration_sens": 0.15,         # Sensitivity to duration
    "friction_thresh": 0.15,       # Friction level that triggers pressure
    "max_pressure": 0.50,          # Cap on pressure
    
    # Economic fatigue: Accumulated GDP losses
    "fatigue_rate": 0.05,          # How fast fatigue builds
    "gdp_thresh": 0.3,             # GDP loss % before fatigue starts
    "max_fatigue": 0.40,           # Cap on fatigue
    
    # Reputation bleeding
    "bleed_rate": 0.020,           # Monthly reputation damage
    "intensity_thresh": 0.25,      # Restriction intensity that triggers bleed
    
    # Memory: Accumulated grievance
    "friction_memory_decay": 0.85, # How fast past friction fades
    "memory_coefficient": 0.12,    # Weight of cumulative friction
    "peak_coefficient": 0.10,      # Weight of peak friction (permanent)
}

# For comparison - original broken config (memory did 95%+ of work)
DEESCALATION_CONFIG_V1 = {
    "maintenance_cost": 0.04,
    "time_accel": 0.15,
    "grace_period": 4,
    "pressure_rate": 0.08,
    "duration_sens": 0.10,
    "friction_thresh": 0.35,
    "max_pressure": 0.50,
    "fatigue_rate": 0.05,
    "gdp_thresh": 2.0,
    "max_fatigue": 0.40,
    "bleed_rate": 0.012,
    "intensity_thresh": 0.40,
    "friction_memory_decay": 0.88,
}

if __name__ == "__main__":
    print("DEESCALATION_CONFIG_V2 = {")
    for k, v in DEESCALATION_CONFIG_V2.items():
        print(f'    "{k}": {v},')
    print("}")
