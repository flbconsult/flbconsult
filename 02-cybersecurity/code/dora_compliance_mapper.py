"""
DORA Third-Party Compliance Mapper
==================================

Maps a list of ICT third-party providers (incl. LLM providers, hyperscalers,
SaaS) onto the five pillars of DORA — Regulation (EU) 2022/2554 — and emits
a CSV gap-analysis suitable for the Register of Information (Art. 28(3)).

The five DORA pillars implemented here:
    P1  ICT risk management framework         (Art. 5–16)
    P2  ICT-related incident management       (Art. 17–23)
    P3  Digital operational resilience testing (Art. 24–27)
    P4  Management of ICT third-party risk    (Art. 28–30)
    P5  Information sharing                   (Art. 45)

Author: Franck Bongard, 2026.
License: MIT.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

# --------------------------------------------------------------------------
# Domain types
# --------------------------------------------------------------------------

PILLARS: Dict[str, str] = {
    "P1": "ICT risk management framework (Art. 5–16)",
    "P2": "ICT-related incident management (Art. 17–23)",
    "P3": "Digital operational resilience testing (Art. 24–27)",
    "P4": "Management of ICT third-party risk (Art. 28–30)",
    "P5": "Information sharing (Art. 45)",
}

DORA_REQUIREMENTS = {
    "P1": [
        "documented ICT risk management framework",
        "annual review by management body",
    ],
    "P2": [
        "incident classification per RTS",
        "major-incident reporting in regulator's window",
    ],
    "P3": [
        "annual TLPT (Threat-Led Penetration Testing) for critical providers",
        "scenario-based digital operational resilience tests",
    ],
    "P4": [
        "register of information for all ICT third parties",
        "exit / reversibility plan",
        "concentration-risk analysis",
    ],
    "P5": [
        "participation in information-sharing arrangements (e.g. FS-ISAC, CERT-FR)",
    ],
}


@dataclass
class Provider:
    name: str
    type: str                              # e.g. 'LLM', 'IaaS', 'SaaS'
    criticality: int                       # 1..5 (5 = critical at the DORA sense)
    region: str
    has_register_entry: bool = False
    has_exit_plan: bool = False
    has_tlpt_scope: bool = False
    incident_runbook: bool = False
    info_sharing: bool = False

    def gap_score(self) -> Dict[str, str]:
        return {
            "P4-register":     "OK" if self.has_register_entry else "GAP",
            "P4-exit":         "OK" if self.has_exit_plan else "GAP",
            "P3-tlpt":         "OK" if (self.has_tlpt_scope or self.criticality < 4) else "GAP",
            "P2-runbook":      "OK" if self.incident_runbook else "GAP",
            "P5-info-sharing": "OK" if self.info_sharing else ("GAP" if self.criticality >= 4 else "N/A"),
        }


# --------------------------------------------------------------------------
# Demo data — typical 2026 stack of an AI-augmented bank
# --------------------------------------------------------------------------

def demo_providers() -> List[Provider]:
    return [
        Provider(
            name="Hyperscaler — AWS Frankfurt",
            type="IaaS",
            criticality=5, region="EEA",
            has_register_entry=True, has_exit_plan=True,
            has_tlpt_scope=True, incident_runbook=True, info_sharing=True,
        ),
        Provider(
            name="LLM Provider — Tier-1 (US)",
            type="LLM",
            criticality=5, region="US",
            has_register_entry=True, has_exit_plan=False,
            has_tlpt_scope=False, incident_runbook=True, info_sharing=False,
        ),
        Provider(
            name="LLM Provider — EU sovereign",
            type="LLM",
            criticality=4, region="EEA",
            has_register_entry=True, has_exit_plan=True,
            has_tlpt_scope=False, incident_runbook=True, info_sharing=False,
        ),
        Provider(
            name="Vector DB SaaS",
            type="SaaS",
            criticality=4, region="EEA",
            has_register_entry=True, has_exit_plan=True,
            has_tlpt_scope=False, incident_runbook=False, info_sharing=False,
        ),
        Provider(
            name="Trace store (managed)",
            type="SaaS",
            criticality=3, region="EEA",
            has_register_entry=False, has_exit_plan=False,
            has_tlpt_scope=False, incident_runbook=False, info_sharing=False,
        ),
    ]


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

def render(providers: List[Provider]) -> str:
    out = ["=" * 92, "DORA Third-Party Compliance — Gap Analysis", "=" * 92]
    header = (
        f"{'PROVIDER':<32} {'CRIT':>4} {'REGION':<6}  "
        f"{'P4-reg':<7} {'P4-exit':<8} {'P3-tlpt':<8} {'P2-rb':<6} {'P5-share':<8}"
    )
    out += [header, "-" * len(header)]
    for p in providers:
        g = p.gap_score()
        out.append(
            f"{p.name[:32]:<32} {p.criticality:>4} {p.region:<6}  "
            f"{g['P4-register']:<7} {g['P4-exit']:<8} {g['P3-tlpt']:<8} "
            f"{g['P2-runbook']:<6} {g['P5-info-sharing']:<8}"
        )
    # aggregate gap stats
    all_gaps = [v for p in providers for v in p.gap_score().values()]
    n_gap = sum(1 for v in all_gaps if v == "GAP")
    n_total = sum(1 for v in all_gaps if v != "N/A")
    out += [
        "-" * len(header),
        f"Compliance ratio: {(n_total - n_gap) / max(1, n_total) * 100:.0f}% "
        f"({n_gap} gap(s) over {n_total} applicable controls)",
        "=" * 92,
    ]
    # critical findings
    critical_gaps = [
        (p.name, k) for p in providers if p.criticality >= 4
        for k, v in p.gap_score().items() if v == "GAP"
    ]
    if critical_gaps:
        out += ["", "CRITICAL FINDINGS (criticality ≥ 4):"]
        for name, ctrl in critical_gaps:
            out.append(f"  - {name}: {ctrl}")
    return "\n".join(out)


def export_csv(providers: List[Provider], path: Path) -> None:
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "name", "type", "criticality", "region",
            "P4-register", "P4-exit", "P3-tlpt", "P2-runbook", "P5-info-sharing",
        ])
        for p in providers:
            g = p.gap_score()
            w.writerow([
                p.name, p.type, p.criticality, p.region,
                g["P4-register"], g["P4-exit"], g["P3-tlpt"],
                g["P2-runbook"], g["P5-info-sharing"],
            ])


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="DORA third-party compliance mapper.")
    parser.add_argument("--providers", type=Path,
                        help="JSON file with a list of providers (overrides demo).")
    parser.add_argument("--csv", type=Path, default=Path("dora_gaps.csv"))
    args = parser.parse_args()

    if args.providers:
        raw = json.loads(args.providers.read_text())
        providers = [Provider(**r) for r in raw]
    else:
        providers = demo_providers()

    print(render(providers))
    export_csv(providers, args.csv)
    print(f"\n[csv] {args.csv}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
