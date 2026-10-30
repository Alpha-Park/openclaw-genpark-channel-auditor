# -*- coding: utf-8 -*-
from client import OpenClawGenParkChannelAuditor

auditor = OpenClawGenParkChannelAuditor()

# 1. Shapley Value Attribution
channels = ["SEO", "Social_Ads", "Newsletter"]
coalition_vals = {
    "": 0.0,
    "SEO": 100.0,
    "Social_Ads": 60.0,
    "Newsletter": 30.0,
    "SEO,Social_Ads": 190.0,
    "Newsletter,SEO": 150.0,
    "Newsletter,Social_Ads": 110.0,
    "Newsletter,SEO,Social_Ads": 260.0
}
shapley = auditor.compute_shapley_attribution(channels, coalition_vals)
print(f"Grand Coalition Value: ${shapley['grand_coalition_value']}")
for c, share in shapley['attribution_shares'].items():
    print(f"  {c}: {share*100:.1f}% (Shapley Value: ${shapley['shapley_values'][c]})")

# 2. Markov Chain Removal Effects
journeys = [
    ["SEO", "Social_Ads"],
    ["SEO", "Newsletter", "Social_Ads"],
    ["Social_Ads", "SEO"],
    ["Newsletter", "SEO"]
]
markov = auditor.compute_markov_removal_effects(journeys)
print(f"\nMarkov Attribution Weights: {markov['markov_attribution_weights']}")

# 3. Incrementality Lift
lift = auditor.audit_incrementality_lift(test_conversions=450.0, control_conversions=320.0, test_spend=12000.0, control_spend=8000.0)
print(f"\nIncrementality Lift: +{lift['lift_percentage']}% (Z-Score: {lift['z_score']}, StatSig: {lift['is_statistically_significant_95']})")
