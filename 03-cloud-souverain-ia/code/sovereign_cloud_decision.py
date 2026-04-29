"""
Sovereign Cloud Decision Tool
=============================

Quantitative companion to the paper *Sovereign Cloud in 2026 — Necessary,
but Not Sufficient* (`docs/01-sovereign-cloud-2026-thesis.md`).

Scores a workload along 8 axes and returns one of three archetypes:

  A) sovereign-mandatory     — regulation forces sovereign / SecNumCloud / on-prem
  B) sovereign-preferable    — sovereign by default, hyperscaler with strong controls
  C) hyperscaler-rational    — hyperscaler with sovereign-by-design posture

Author: Franck Bongard, 2026.
License: MIT.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

# --------------------------------------------------------------------------
# Domain types
# --------------------------------------------------------------------------

AXES = [
    "data_classification",
    "regulatory_exposure",
    "latency_locality",
    "gpu_ai_compute",
    "reversibility_cost",
    "tco_pressure",
    "supply_chain_risk",
    "business_continuity",
]

AXIS_DESCRIPTION = {
    "data_classification":
        "0=public, 1=internal, 2=confidential, 3=sensitive, 4=PII/PHI, 5=regulated (HDS, OIV)",
    "regulatory_exposure":
        "0=none, 1=GDPR-baseline, 2=DORA, 3=AI Act high-risk, 4=HDS, 5=SecNumCloud-mandatory",
    "latency_locality":
        "0=async batch, 1=WAN, 2=LAN, 3=metro, 4=edge < 50 ms, 5=edge < 10 ms",
    "gpu_ai_compute":
        "0=none, 1=light inference, 2=heavy inference, 3=fine-tune, 4=foundation training",
    "reversibility_cost":
        "0=open standards, 5=deeply locked-in to managed services",
    "tco_pressure":
        "0=cost insensitive, 5=acute cost pressure (typical SaaS at scale)",
    "supply_chain_risk":
        "0=neutral, 5=acute geopolitical / sanction exposure",
    "business_continuity":
        "0=non-critical, 5=tier-1 critical (RTO < 1h, RPO ≈ 0, regulator-tested)",
}


@dataclass
class Workload:
    name: str
    scores: Dict[str, int] = field(default_factory=dict)

    def get(self, axis: str) -> int:
        return int(self.scores.get(axis, 0))


# --------------------------------------------------------------------------
# Decision logic
# --------------------------------------------------------------------------

def archetype(w: Workload) -> tuple[str, List[str]]:
    rationale: List[str] = []

    # Rule 1: regulation forces sovereign
    if w.get("regulatory_exposure") >= 4 or w.get("data_classification") >= 5:
        rationale.append(
            f"Regulatory exposure {w.get('regulatory_exposure')}/5 + "
            f"data classification {w.get('data_classification')}/5 "
            f"=> sovereign-mandatory."
        )
        return "A — sovereign-mandatory", rationale

    # Rule 2: heavy GPU forces hyperscaler economics
    if w.get("gpu_ai_compute") >= 3 and w.get("data_classification") <= 2:
        rationale.append(
            f"GPU/AI compute {w.get('gpu_ai_compute')}/4 with low data sensitivity "
            f"=> hyperscaler-rational on economics."
        )
        return "C — hyperscaler-rational", rationale

    # Rule 3: strategic IP / mid-sensitivity / DORA-critical
    if (w.get("regulatory_exposure") >= 2
            or w.get("data_classification") >= 3
            or w.get("supply_chain_risk") >= 4):
        rationale.append(
            "Mid-to-high sensitivity or regulatory exposure or supply-chain risk "
            "=> sovereign-preferable; hyperscaler acceptable with strong sovereign-by-design controls."
        )
        return "B — sovereign-preferable", rationale

    # Rule 4: default hyperscaler-rational
    rationale.append(
        "Low sensitivity, low regulatory exposure, no GPU lock-in => hyperscaler-rational."
    )
    return "C — hyperscaler-rational", rationale


def specific_recommendations(w: Workload, archetype_label: str) -> List[str]:
    recs: List[str] = []
    if archetype_label.startswith("A"):
        recs += [
            "Choose a SecNumCloud-certified provider OR on-premise.",
            "Document the regulatory basis in the risk register (ISO 27005).",
            "Run annual TLPT under DORA Art. 26 if applicable.",
        ]
    elif archetype_label.startswith("B"):
        recs += [
            "Hyperscaler with: customer-managed keys (BYOK), EU-only residency clauses, exit plan funded.",
            "Plan multi-provider portability drill at least once a year.",
            "Add the LLM provider (if any) to the DORA register of information (Art. 28(3)).",
        ]
    else:
        recs += [
            "Hyperscaler in EU region.",
            "Apply sovereign-by-design posture: encryption, residency, contracts; do not pay sovereign-cloud premium.",
            "Cap reversibility cost at 90 days / 1× annual run cost.",
        ]
    if w.get("gpu_ai_compute") >= 2:
        recs.append("Reserve GPU capacity ≥ 6 months in advance; consider mixed providers for redundancy.")
    if w.get("supply_chain_risk") >= 3:
        recs.append("Maintain a hot-standby on a second provider for critical interfaces.")
    return recs


# --------------------------------------------------------------------------
# Presets
# --------------------------------------------------------------------------

PRESETS: Dict[str, Workload] = {
    "healthcare-ehr": Workload(
        name="EHR / SIH (clinical, HDS-regulated)",
        scores={
            "data_classification": 5, "regulatory_exposure": 4,
            "latency_locality": 3, "gpu_ai_compute": 1,
            "reversibility_cost": 4, "tco_pressure": 2,
            "supply_chain_risk": 2, "business_continuity": 5,
        },
    ),
    "real-estate-avm": Workload(
        name="Real-estate AVM scoring (KHOME)",
        scores={
            "data_classification": 3, "regulatory_exposure": 3,
            "latency_locality": 2, "gpu_ai_compute": 2,
            "reversibility_cost": 3, "tco_pressure": 3,
            "supply_chain_risk": 2, "business_continuity": 4,
        },
    ),
    "saas-cdn": Workload(
        name="Public SaaS website + CDN",
        scores={
            "data_classification": 1, "regulatory_exposure": 1,
            "latency_locality": 4, "gpu_ai_compute": 0,
            "reversibility_cost": 2, "tco_pressure": 4,
            "supply_chain_risk": 1, "business_continuity": 3,
        },
    ),
    "foundation-training": Workload(
        name="Foundation-model fine-tuning on public data",
        scores={
            "data_classification": 0, "regulatory_exposure": 0,
            "latency_locality": 0, "gpu_ai_compute": 4,
            "reversibility_cost": 3, "tco_pressure": 5,
            "supply_chain_risk": 1, "business_continuity": 1,
        },
    ),
    "hr-llm-copilot": Workload(
        name="HR copilot (PII, fine-tuned on internal corpus)",
        scores={
            "data_classification": 4, "regulatory_exposure": 2,
            "latency_locality": 2, "gpu_ai_compute": 2,
            "reversibility_cost": 4, "tco_pressure": 3,
            "supply_chain_risk": 3, "business_continuity": 4,
        },
    ),
}


# --------------------------------------------------------------------------
# I/O
# --------------------------------------------------------------------------

def render(w: Workload, label: str, rationale: List[str], recs: List[str]) -> str:
    out = ["=" * 80, f"Sovereign Cloud Decision — {w.name}", "=" * 80]
    out.append("Scores:")
    for axis in AXES:
        out.append(f"  {axis:<22} {w.get(axis)}/5    ({AXIS_DESCRIPTION[axis]})")
    out += ["", f"ARCHETYPE: {label}", "", "Rationale:"]
    out += [f"  - {r}" for r in rationale]
    out += ["", "Concrete recommendations:"]
    out += [f"  • {r}" for r in recs]
    out += ["=" * 80]
    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser(description="Sovereign cloud decision tool.")
    p.add_argument("--workload-preset", choices=list(PRESETS.keys()),
                   default="real-estate-avm")
    p.add_argument("--input", type=Path,
                   help="JSON {\"name\":..., \"scores\":{axis:int,...}} overriding the preset.")
    p.add_argument("--out", type=Path, default=Path("decision.json"))
    args = p.parse_args()

    if args.input:
        data = json.loads(args.input.read_text())
        wl = Workload(name=data["name"], scores=data["scores"])
    else:
        wl = PRESETS[args.workload_preset]

    label, rationale = archetype(wl)
    recs = specific_recommendations(wl, label)
    print(render(wl, label, rationale, recs))

    args.out.write_text(json.dumps({
        "workload": wl.name,
        "scores": wl.scores,
        "archetype": label,
        "rationale": rationale,
        "recommendations": recs,
    }, indent=2, ensure_ascii=False))
    print(f"\n[json] {args.out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
