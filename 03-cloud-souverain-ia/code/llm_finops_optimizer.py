"""
LLM FinOps Optimiser
====================

Routes LLM traffic across providers under (quality, cost, residency) constraints.

Inspiration: Vocalcom Move2Cloud FinOps playbook (€210k/yr savings via right-sizing,
applied to the LLM era). Three first-class disciplines:

  1. Per-tenant token-budget rate limits.
  2. Provider routing by quality threshold + cost + residency.
  3. Cost anomaly detection (rolling z-score).

Usage
-----
    python llm_finops_optimizer.py --demo

Author: Franck Bongard, 2026.
License: MIT.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# --------------------------------------------------------------------------
# Provider catalogue
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Provider:
    name: str
    quality: float           # 0..1 — proxy of capability on the relevant benchmark suite
    cost_per_1k_input: float # $ per 1k input tokens
    cost_per_1k_output: float
    residency: str           # 'EEA', 'US', 'CH', 'multi'
    sovereign: bool = False  # SecNumCloud-aligned or local-only deployment

PROVIDERS: List[Provider] = [
    Provider("Frontier-US-Tier1",  quality=0.96, cost_per_1k_input=3.00, cost_per_1k_output=15.00, residency="US"),
    Provider("Frontier-US-Tier2",  quality=0.92, cost_per_1k_input=1.00, cost_per_1k_output=5.00,  residency="US"),
    Provider("Mid-EU",             quality=0.85, cost_per_1k_input=0.40, cost_per_1k_output=1.20,  residency="EEA"),
    Provider("OpenWeights-EU-host",quality=0.80, cost_per_1k_input=0.10, cost_per_1k_output=0.30,  residency="EEA", sovereign=True),
    Provider("OpenWeights-on-prem",quality=0.75, cost_per_1k_input=0.05, cost_per_1k_output=0.15,  residency="EEA", sovereign=True),
]

# --------------------------------------------------------------------------
# Routing
# --------------------------------------------------------------------------

@dataclass
class Request:
    tenant: str
    prompt_tokens: int
    expected_output_tokens: int
    quality_threshold: float       # 0..1
    residency_allowlist: List[str] # e.g. ['EEA']
    sovereign_required: bool = False
    is_pii: bool = False

@dataclass
class RoutingDecision:
    request: Request
    provider: Optional[Provider]
    cost: float
    rejected_reasons: List[str] = field(default_factory=list)


def route(req: Request, providers: List[Provider] = PROVIDERS) -> RoutingDecision:
    rejected: List[str] = []
    candidates: List[Provider] = []
    for p in providers:
        if p.quality < req.quality_threshold:
            rejected.append(f"{p.name}: quality {p.quality} < threshold {req.quality_threshold}")
            continue
        if p.residency not in req.residency_allowlist and "multi" not in req.residency_allowlist:
            rejected.append(f"{p.name}: residency {p.residency} not in {req.residency_allowlist}")
            continue
        if req.sovereign_required and not p.sovereign:
            rejected.append(f"{p.name}: not sovereign-aligned")
            continue
        if req.is_pii and p.residency == "US":
            rejected.append(f"{p.name}: PII data, US residency disallowed")
            continue
        candidates.append(p)

    if not candidates:
        return RoutingDecision(request=req, provider=None, cost=0.0, rejected_reasons=rejected)

    cost_of = lambda p: (
        req.prompt_tokens / 1000 * p.cost_per_1k_input
        + req.expected_output_tokens / 1000 * p.cost_per_1k_output
    )
    best = min(candidates, key=cost_of)
    return RoutingDecision(request=req, provider=best, cost=cost_of(best), rejected_reasons=rejected)


# --------------------------------------------------------------------------
# Per-tenant budget tracker
# --------------------------------------------------------------------------

@dataclass
class TenantBudget:
    tenant: str
    monthly_cap_usd: float
    spent_this_month: float = 0.0

    def can_spend(self, amount: float) -> bool:
        return self.spent_this_month + amount <= self.monthly_cap_usd

    def charge(self, amount: float) -> None:
        self.spent_this_month += amount


class BudgetRegistry:
    def __init__(self) -> None:
        self.budgets: Dict[str, TenantBudget] = {}

    def set_budget(self, tenant: str, cap: float) -> None:
        self.budgets[tenant] = TenantBudget(tenant, cap)

    def authorise(self, tenant: str, amount: float) -> bool:
        b = self.budgets.get(tenant)
        if not b:
            return True  # no budget configured
        if not b.can_spend(amount):
            return False
        b.charge(amount)
        return True


# --------------------------------------------------------------------------
# Cost anomaly detection
# --------------------------------------------------------------------------

def anomaly_score(history: List[float], current: float) -> float:
    """Rolling z-score over the last N points."""
    if len(history) < 5:
        return 0.0
    mean = statistics.mean(history)
    stdev = statistics.pstdev(history) or 1e-6
    return (current - mean) / stdev


# --------------------------------------------------------------------------
# Demo
# --------------------------------------------------------------------------

def demo_requests() -> List[Request]:
    return [
        Request(tenant="acme-fr", prompt_tokens=2_000, expected_output_tokens=400,
                quality_threshold=0.85, residency_allowlist=["EEA"]),
        Request(tenant="acme-fr", prompt_tokens=15_000, expected_output_tokens=2_000,
                quality_threshold=0.90, residency_allowlist=["EEA"], is_pii=True),
        Request(tenant="acme-fr", prompt_tokens=500, expected_output_tokens=120,
                quality_threshold=0.70, residency_allowlist=["EEA"], sovereign_required=True),
        Request(tenant="globex-uk", prompt_tokens=8_000, expected_output_tokens=1_000,
                quality_threshold=0.95, residency_allowlist=["US", "EEA"]),
        Request(tenant="globex-uk", prompt_tokens=1_000, expected_output_tokens=300,
                quality_threshold=0.92, residency_allowlist=["multi"]),
    ]


def main() -> int:
    p = argparse.ArgumentParser(description="LLM FinOps optimiser.")
    p.add_argument("--demo", action="store_true")
    args = p.parse_args()
    requests = demo_requests()

    registry = BudgetRegistry()
    registry.set_budget("acme-fr", 100.0)
    registry.set_budget("globex-uk", 50.0)

    cost_history: List[float] = []
    total_optimal = 0.0
    total_naive = 0.0          # naive = always Tier-1 frontier
    naive = next(p for p in PROVIDERS if p.name == "Frontier-US-Tier1")

    print("=" * 92)
    print(f"{'TENANT':<12} {'PROVIDER':<22} {'QUALITY':>7} {'COST':>10} {'NAIVE':>10} {'SAVINGS':>10} {'ANOMALY':>8}")
    print("-" * 92)
    for r in requests:
        decision = route(r)
        if decision.provider is None:
            print(f"{r.tenant:<12} REJECTED — {decision.rejected_reasons[0] if decision.rejected_reasons else ''}")
            continue
        if not registry.authorise(r.tenant, decision.cost):
            print(f"{r.tenant:<12} BUDGET REJECTED")
            continue

        naive_cost = (r.prompt_tokens / 1000 * naive.cost_per_1k_input
                      + r.expected_output_tokens / 1000 * naive.cost_per_1k_output)
        savings = naive_cost - decision.cost

        z = anomaly_score(cost_history, decision.cost)
        cost_history.append(decision.cost)
        total_optimal += decision.cost
        total_naive += naive_cost
        flag = "⚠️" if abs(z) > 2 else ""
        print(f"{r.tenant:<12} {decision.provider.name:<22} "
              f"{decision.provider.quality:>7.2f} "
              f"{decision.cost:>10.4f} {naive_cost:>10.4f} "
              f"{savings:>10.4f} {z:>+7.2f} {flag}")

    print("-" * 92)
    print(f"{'TOTAL':<35} {total_optimal:>10.4f} {total_naive:>10.4f} {total_naive-total_optimal:>10.4f}")
    if total_naive > 0:
        print(f"\nOptimisation savings: {(1 - total_optimal/total_naive)*100:.0f}% "
              f"vs naive single-provider routing.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
