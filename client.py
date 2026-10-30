# -*- coding: utf-8 -*-
"""
OpenClaw GenPark Channel Auditor - Cooperative Game Shapley Value & Markov Chain Touchpoint Auditor
Standard Library only: math, itertools, typing.
Calculates cooperative game-theoretic Shapley values across multi-touch marketing coalitions,
evaluates first-order Markov chain transition state removal effects, and audits incrementality lift.
"""

import math
import itertools
from typing import Dict, List, Any

class OpenClawGenParkChannelAuditor:
    def __init__(self):
        pass

    def compute_shapley_attribution(self, channels: List[str],
                                    coalition_values: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculates exact axiomatic Shapley values across all 2^N coalition permutations:
        phi_i(v) = sum_{S subset N \ {i}} [ |S|!(|N| - |S| - 1)! / |N|! ] * [ v(S union {i}) - v(S) ]
        """
        N = len(channels)
        if N == 0:
            return {"shapley_values": {}, "total_value": 0.0}

        def get_val(s_tuple):
            # Sort keys to match coalition_values dict
            key = ",".join(sorted(s_tuple))
            return coalition_values.get(key, 0.0)

        shapley = {c: 0.0 for c in channels}
        fact_N = math.factorial(N)

        for i in channels:
            other_channels = [c for c in channels if c != i]
            # Enumerate all subsets S of other_channels
            for s_len in range(len(other_channels) + 1):
                weight = (math.factorial(s_len) * math.factorial(N - s_len - 1)) / fact_N
                for S in itertools.combinations(other_channels, s_len):
                    v_without_i = get_val(S)
                    v_with_i = get_val(S + (i,))
                    marginal_contrib = v_with_i - v_without_i
                    shapley[i] += weight * marginal_contrib

        grand_coalition_val = get_val(tuple(channels))
        total_attributed = sum(shapley.values())

        # Attribution shares
        attribution_shares = {}
        for c, val in shapley.items():
            attribution_shares[c] = round(val / max(1e-6, total_attributed), 4)

        return {
            "channels_count": N,
            "grand_coalition_value": round(grand_coalition_val, 2),
            "shapley_values": {c: round(v, 4) for c, v in shapley.items()},
            "attribution_shares": attribution_shares,
            "efficiency_axiom_verified": abs(total_attributed - grand_coalition_val) < 1e-4
        }

    def compute_markov_removal_effects(self, paths: List[List[str]],
                                       conversion_weights: List[float] = None) -> Dict[str, Any]:
        """
        Constructs first-order Markov transition graph across customer touchpoint journeys
        and computes the Removal Effect R_i for each marketing channel.
        """
        weights = conversion_weights or [1.0] * len(paths)
        transitions = {} # (state_from, state_to) -> count
        channels = set()

        for path, w in zip(paths, weights):
            augmented = ["START"] + path + ["CONVERSION"]
            for i in range(len(augmented) - 1):
                u, v = augmented[i], augmented[i + 1]
                if u != "START" and u != "CONVERSION":
                    channels.add(u)
                transitions[(u, v)] = transitions.get((u, v), 0.0) + w

        # Build normalized transition probabilities
        from_totals = {}
        for (u, _), count in transitions.items():
            from_totals[u] = from_totals.get(u, 0.0) + count

        prob = {}
        for (u, v), count in transitions.items():
            prob[(u, v)] = count / from_totals[u]

        # Calculate baseline probability P(START -> CONVERSION) via simulation / absorption
        def get_conversion_prob(removed_channel=None):
            # Solve absorption or simplified 3-step path approximation
            conv_prob = 0.0
            for path, w in zip(paths, weights):
                if removed_channel and removed_channel in path:
                    continue
                # Probability of this path
                p_path = 1.0
                augmented = ["START"] + path + ["CONVERSION"]
                for i in range(len(augmented) - 1):
                    u, v = augmented[i], augmented[i + 1]
                    p_path *= prob.get((u, v), 0.0)
                conv_prob += p_path * w
            return conv_prob

        base_conv = get_conversion_prob(None)
        removal_effects = {}
        sorted_channels = sorted(list(channels))

        for c in sorted_channels:
            without_c = get_conversion_prob(c)
            effect = (base_conv - without_c) / max(1e-6, base_conv)
            removal_effects[c] = round(max(0.0, effect), 4)

        total_effect = sum(removal_effects.values())
        markov_weights = {c: round(v / max(1e-6, total_effect), 4) for c, v in removal_effects.items()}

        return {
            "total_journeys_evaluated": len(paths),
            "unique_channels": sorted_channels,
            "baseline_conversion_index": round(base_conv, 4),
            "removal_effects": removal_effects,
            "markov_attribution_weights": markov_weights
        }

    def audit_incrementality_lift(self, test_conversions: float, control_conversions: float,
                                 test_spend: float, control_spend: float) -> Dict[str, Any]:
        """
        Audits synthetic control incrementality: incremental ROAS (iROAS) and statistical significance.
        """
        incr_conversions = test_conversions - control_conversions
        incr_spend = test_spend - control_spend

        lift_pct = (incr_conversions / max(1.0, control_conversions)) * 100.0
        iroas = incr_conversions / max(0.01, incr_spend) if incr_spend > 0 else 0.0

        # Simple standard error of difference
        se = math.sqrt((test_conversions + control_conversions) / max(1.0, test_conversions * control_conversions))
        z_score = incr_conversions / max(1e-4, math.sqrt(test_conversions + control_conversions))

        is_stat_sig = abs(z_score) >= 1.96

        return {
            "test_conversions": test_conversions,
            "control_conversions": control_conversions,
            "incremental_conversions": round(incr_conversions, 2),
            "lift_percentage": round(lift_pct, 2),
            "incremental_spend_usd": round(incr_spend, 2),
            "incremental_roas": round(iroas, 2),
            "z_score": round(z_score, 3),
            "is_statistically_significant_95": is_stat_sig
        }
