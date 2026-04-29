"""
Data Residency Analyser
=======================

Verifies a multi-cloud architecture for GDPR Art. 44 + EU AI Act + sectorial
residency constraints (HDS, SecNumCloud, RICS).

Approach: load a graph of components (front-end, app, DB, vector DB, LLM
provider, fail-over targets) and a data-flow specification. For each path
through the graph, check the residency invariants hold.

Usage
-----
    python data_residency_analyzer.py --architecture multi-region-failover

Author: Franck Bongard, 2026.
License: MIT.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set

# --------------------------------------------------------------------------
# Domain types
# --------------------------------------------------------------------------

@dataclass
class Component:
    name: str
    region: str        # 'EEA-FR', 'EEA-DE', 'US', 'CH', 'UK', 'failover-US', etc.
    role: str          # 'frontend', 'app', 'db', 'vector', 'llm', 'cache', 'log'
    pii_capable: bool = False
    secnumcloud: bool = False


@dataclass
class DataFlow:
    flow_id: str
    description: str
    data_class: str               # 'public', 'internal', 'confidential', 'pii', 'phi'
    path: List[str]               # ordered list of component names
    sectorial: Set[str] = field(default_factory=set)   # e.g. {'hds', 'rics'}


@dataclass
class Finding:
    severity: str    # 'INFO', 'WARN', 'CRITICAL'
    flow_id: str
    rule: str
    detail: str


# --------------------------------------------------------------------------
# Constraints
# --------------------------------------------------------------------------

EEA_REGIONS = {"EEA-FR", "EEA-DE", "EEA-NL", "EEA-IE", "EEA-ES"}


def is_eea(region: str) -> bool:
    return region in EEA_REGIONS or region.startswith("EEA")


def analyse(components: Dict[str, Component], flows: List[DataFlow]) -> List[Finding]:
    findings: List[Finding] = []
    for flow in flows:
        for comp_name in flow.path:
            comp = components.get(comp_name)
            if comp is None:
                findings.append(Finding("CRITICAL", flow.flow_id, "missing_component",
                                        f"path references unknown component '{comp_name}'"))
                continue

            # Rule 1: GDPR Art. 44 — PII / PHI must stay in EEA unless adequacy framework
            if flow.data_class in {"pii", "phi"} and not is_eea(comp.region):
                findings.append(Finding(
                    "CRITICAL", flow.flow_id, "gdpr_44",
                    f"{comp.name} is in {comp.region} but flow carries {flow.data_class.upper()} "
                    f"data — GDPR Art. 44 transfer constraints apply.",
                ))

            # Rule 2: HDS — French health data needs HDS-certified hosting (typ. EEA-FR)
            if "hds" in flow.sectorial and comp.region != "EEA-FR":
                findings.append(Finding(
                    "CRITICAL", flow.flow_id, "hds",
                    f"{comp.name} ({comp.region}) processes HDS-flagged data; certification typically EEA-FR.",
                ))

            # Rule 3: SecNumCloud requirement
            if "secnumcloud" in flow.sectorial and not comp.secnumcloud:
                findings.append(Finding(
                    "CRITICAL", flow.flow_id, "secnumcloud",
                    f"{comp.name} is not SecNumCloud-certified.",
                ))

            # Rule 4: RICS / KHOME real-estate data — EEA strongly preferred for AVM evidence
            if "rics" in flow.sectorial and not is_eea(comp.region):
                findings.append(Finding(
                    "WARN", flow.flow_id, "rics",
                    f"{comp.name} ({comp.region}) handles RICS-aligned data — EEA preferred for audit.",
                ))

            # Rule 5: AI Act Art. 10 — high-risk training data quality / governance
            if flow.data_class == "pii" and comp.role == "llm" and not is_eea(comp.region):
                findings.append(Finding(
                    "WARN", flow.flow_id, "ai_act_extraterritorial",
                    f"{comp.name} is an LLM in {comp.region}; check Art. 25 obligations for general-purpose AI providers.",
                ))

            # Rule 6: Failover hygiene — fail-over to non-EEA region for PII is risky
            if "failover" in comp.region.lower() and not is_eea(comp.region) and flow.data_class in {"pii", "phi"}:
                findings.append(Finding(
                    "CRITICAL", flow.flow_id, "failover_residency",
                    f"{comp.name} fails over to {comp.region} for {flow.data_class.upper()} data — "
                    "incident-time GDPR violation risk.",
                ))

    return findings


# --------------------------------------------------------------------------
# Architecture presets
# --------------------------------------------------------------------------

def architecture_multi_region_failover() -> tuple[Dict[str, Component], List[DataFlow]]:
    components = {
        "front":     Component("front",     "EEA-FR", "frontend"),
        "app":       Component("app",       "EEA-FR", "app", pii_capable=True),
        "db_primary":Component("db_primary","EEA-FR", "db",  pii_capable=True),
        "db_failover":Component("db_failover","failover-US", "db", pii_capable=True),
        "vector":    Component("vector",    "EEA-DE", "vector"),
        "llm":       Component("llm",       "US",     "llm"),
        "cache":     Component("cache",     "EEA-FR", "cache"),
    }
    flows = [
        DataFlow("F1", "Customer chat with PII",
                 data_class="pii",
                 path=["front", "app", "vector", "llm", "cache"]),
        DataFlow("F2", "Async log ingestion (anonymised)",
                 data_class="internal",
                 path=["app", "db_primary"]),
        DataFlow("F3", "DR fail-over from primary",
                 data_class="pii",
                 path=["app", "db_failover"]),
    ]
    return components, flows


def architecture_hds_compliant() -> tuple[Dict[str, Component], List[DataFlow]]:
    components = {
        "portal":    Component("portal",  "EEA-FR", "frontend"),
        "app":       Component("app",     "EEA-FR", "app", pii_capable=True, secnumcloud=False),
        "db_hds":    Component("db_hds",  "EEA-FR", "db",  pii_capable=True),
        "llm_eu":    Component("llm_eu",  "EEA-FR", "llm", secnumcloud=True),
    }
    flows = [
        DataFlow("F1", "Clinician request on patient record",
                 data_class="phi",
                 path=["portal", "app", "db_hds", "llm_eu"],
                 sectorial={"hds"}),
    ]
    return components, flows


PRESETS = {
    "multi-region-failover": architecture_multi_region_failover,
    "hds-compliant": architecture_hds_compliant,
}


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

def render(findings: List[Finding]) -> str:
    if not findings:
        return "✅ No residency findings. Architecture is compliant on the rules covered."
    out = ["=" * 80, f"Residency Findings — {len(findings)} entry(ies)", "=" * 80]
    for f in findings:
        out.append(f"  [{f.severity:<8}] flow={f.flow_id:<5} rule={f.rule:<22} {f.detail}")
    out.append("=" * 80)
    n_crit = sum(1 for x in findings if x.severity == "CRITICAL")
    n_warn = sum(1 for x in findings if x.severity == "WARN")
    out.append(f"Summary: {n_crit} CRITICAL · {n_warn} WARN")
    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser(description="Data residency analyser.")
    p.add_argument("--architecture", choices=list(PRESETS.keys()),
                   default="multi-region-failover")
    p.add_argument("--out", type=Path, default=Path("residency_findings.json"))
    args = p.parse_args()

    components, flows = PRESETS[args.architecture]()
    findings = analyse(components, flows)
    print(render(findings))

    args.out.write_text(json.dumps([
        {"severity": f.severity, "flow_id": f.flow_id, "rule": f.rule, "detail": f.detail}
        for f in findings
    ], indent=2, ensure_ascii=False))
    print(f"\n[json] {args.out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
