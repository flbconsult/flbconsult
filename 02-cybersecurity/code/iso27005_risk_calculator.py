"""
ISO 27005:2022 Risk Calculator
==============================

Quantitative implementation of the ISO/IEC 27005:2022 risk-management process.

Formula
-------
For each (asset × threat × vulnerability) tuple:

    inherent_risk  = asset_value × likelihood × impact          (1..125 scale)
    residual_risk  = inherent_risk × (1 − Σ control_effectiveness)
                     bounded to [0, inherent_risk]

The residual risk is matched against a treatment matrix:

    < 8       Accept
    8..24     Monitor + accept formally
    24..50    Reduce — additional controls required
    > 50      Avoid / Transfer — escalate to risk committee

Author: Franck Bongard, ISO 27005 Risk Manager (PECB).
License: MIT.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List

# --------------------------------------------------------------------------
# Domain types
# --------------------------------------------------------------------------

@dataclass
class Control:
    name: str
    effectiveness: float  # 0..1
    framework_refs: List[str] = field(default_factory=list)


@dataclass
class Risk:
    risk_id: str
    asset: str
    threat: str
    vulnerability: str
    asset_value: int        # 1..5
    likelihood: int         # 1..5
    impact: int             # 1..5
    controls: List[Control] = field(default_factory=list)

    def inherent_risk(self) -> int:
        return self.asset_value * self.likelihood * self.impact

    def control_strength(self) -> float:
        """1 - product(1 - e_i) — independent residual model."""
        product = 1.0
        for c in self.controls:
            product *= 1.0 - max(0.0, min(1.0, c.effectiveness))
        return 1.0 - product

    def residual_risk(self) -> float:
        return max(0.0, self.inherent_risk() * (1.0 - self.control_strength()))


# --------------------------------------------------------------------------
# Treatment decision
# --------------------------------------------------------------------------

def treatment(residual: float) -> str:
    if residual < 8:
        return "ACCEPT — record in residual-risk register."
    if residual < 24:
        return "MONITOR — formal acceptance by risk owner; quarterly review."
    if residual < 50:
        return "REDUCE — additional controls required before next audit."
    return "AVOID / TRANSFER — escalate to risk committee, consider insurance."


# --------------------------------------------------------------------------
# Heatmap rendering (text-only; no external dep)
# --------------------------------------------------------------------------

def render_text_report(risks: List[Risk]) -> str:
    lines = ["=" * 88, "ISO 27005 Risk Register", "=" * 88]
    header = f"{'ID':<6} {'ASSET':<24} {'INHERENT':>9} {'RESIDUAL':>9} {'TREATMENT'}"
    lines.append(header)
    lines.append("-" * len(header))
    for r in risks:
        lines.append(
            f"{r.risk_id:<6} {r.asset[:24]:<24} "
            f"{r.inherent_risk():>9} {r.residual_risk():>9.1f}  {treatment(r.residual_risk())}"
        )
    # aggregate
    total_inh = sum(r.inherent_risk() for r in risks)
    total_res = sum(r.residual_risk() for r in risks)
    lines += [
        "-" * len(header),
        f"{'TOTAL':<31} {total_inh:>9} {total_res:>9.1f}",
        "",
        f"Risk-reduction ratio: {(1 - total_res / max(1, total_inh)) * 100:.1f}%",
        "=" * 88,
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Demo register — AI-augmented enterprise SI
# --------------------------------------------------------------------------

def demo_register() -> List[Risk]:
    iam_mfa = Control(
        name="IAM MFA + privileged access management",
        effectiveness=0.65,
        framework_refs=["ISO 27001 A.5.17", "NIST CSF PR.AA-01", "DORA Art. 9"],
    )
    soc24 = Control(
        name="SOC 24/7 + LLM trace store",
        effectiveness=0.45,
        framework_refs=["ISO 27001 A.8.16", "NIST CSF DE.CM-01"],
    )
    eval_harness = Control(
        name="Eval-on-PR + prompt-injection probe",
        effectiveness=0.55,
        framework_refs=["NIST AI RMF Measure", "ISO 42001 §7.4"],
    )
    pca = Control(
        name="Tested PCA/PRA, multi-region failover",
        effectiveness=0.70,
        framework_refs=["ISO 22301", "DORA Art. 11"],
    )
    return [
        Risk(
            risk_id="R-001",
            asset="Customer-facing RAG chatbot",
            threat="Indirect prompt injection",
            vulnerability="Untrusted documents in retrieval corpus",
            asset_value=4, likelihood=4, impact=4,
            controls=[eval_harness, soc24],
        ),
        Risk(
            risk_id="R-002",
            asset="AVM scoring model (KHOME)",
            threat="Hallucinated comparables",
            vulnerability="Insufficient grounding + no human-in-the-loop",
            asset_value=5, likelihood=3, impact=5,
            controls=[eval_harness],
        ),
        Risk(
            risk_id="R-003",
            asset="LLM provider (Tier-1 hyperscaler)",
            threat="Provider outage / cost surge",
            vulnerability="Single-vendor lock-in",
            asset_value=4, likelihood=2, impact=4,
            controls=[pca],
        ),
        Risk(
            risk_id="R-004",
            asset="Embedding store (multi-tenant)",
            threat="Cross-tenant inference leak",
            vulnerability="Shared vector index, weak per-tenant isolation",
            asset_value=5, likelihood=2, impact=5,
            controls=[iam_mfa],
        ),
        Risk(
            risk_id="R-005",
            asset="Internal LLM copilot",
            threat="Training-data extraction (Carlini et al. 2023)",
            vulnerability="Memorisation of fine-tuning PII",
            asset_value=4, likelihood=2, impact=5,
            controls=[],
        ),
    ]


# --------------------------------------------------------------------------
# I/O
# --------------------------------------------------------------------------

def export_json(risks: List[Risk], path: Path) -> None:
    payload = []
    for r in risks:
        d = asdict(r)
        d["inherent_risk"] = r.inherent_risk()
        d["residual_risk"] = r.residual_risk()
        d["treatment"] = treatment(r.residual_risk())
        payload.append(d)
    path.write_text(json.dumps(payload, indent=2))


def export_csv(risks: List[Risk], path: Path) -> None:
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "asset", "threat", "inherent", "residual", "treatment", "controls"])
        for r in risks:
            w.writerow([
                r.risk_id, r.asset, r.threat,
                r.inherent_risk(), f"{r.residual_risk():.1f}",
                treatment(r.residual_risk()),
                ";".join(c.name for c in r.controls),
            ])


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description="ISO 27005 risk calculator.")
    p.add_argument("--demo", action="store_true", help="Run on demo register.")
    p.add_argument("--json", type=Path, default=Path("risk_register.json"))
    p.add_argument("--csv", type=Path, default=Path("risk_register.csv"))
    args = p.parse_args()

    risks = demo_register() if args.demo or True else []  # demo by default
    print(render_text_report(risks))

    export_json(risks, args.json)
    export_csv(risks, args.csv)
    print(f"\n[exports] {args.json} · {args.csv}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
