from __future__ import annotations
import math

def percentile_score(value, low, high):
    if high == low: return 50
    return max(0, min(100, round(100*(value-low)/(high-low))))

def weighted_score(features: dict, weights: dict):
    total = sum(abs(v) for v in weights.values()) or 1
    return round(sum(features.get(k,0)*w for k,w in weights.items())/total, 2)

DEFAULT_WEIGHTS = {
    'provider_density': .22,
    'utilization': .20,
    'reimbursement_variability': .18,
    'trial_density': .14,
    'commercial_activity': .10,
    'safety_momentum': -.10,
    'breach_exposure': -.06,
}

def market_attractiveness(features):
    return weighted_score(features, DEFAULT_WEIGHTS)
