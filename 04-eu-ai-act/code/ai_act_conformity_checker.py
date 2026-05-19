#!/usr/bin/env python3
"""
EU AI Act Conformity Checker — Module 04
==========================================
47-item gap analysis against Annex IV + Article 9 requirements
for High-Risk AI systems. Outputs RED/AMBER/GREEN status with
remediation guidance.

Usage:
    python ai_act_conformity_checker.py --demo
    python ai_act_conformity_checker.py --interactive --system-type high-risk
    python ai_act_conformity_checker.py --interactive --output gap_analysis.md

References: EU AI Act (2024/1689), ISO/IEC 42001:2023, NIST AI RMF 1.0
"""

import argparse
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class Status(Enum):
    GREEN = "✅ GREEN"
    AMBER = "⚠️  AMBER"
    RED = "❌ RED"
    NA = "⬜ N/A"


@dataclass
class CheckItem:
    item_id: str
    article: str
    category: str
    requirement: str
    status: Status = Status.RED
    evidence: str = ""
    remediation: str = ""
    priority: str = "high"  # high | medium | low


CHECKLIST: List[Dict] = [
    # ── Art. 9 — Risk Management System ──────────────────────────────────────
    {"id": "ART9-01", "article": "Art. 9.1", "category": "Risk Management",
     "requirement": "A risk management system is established and maintained as a continuous iterative process throughout the lifecycle.",
     "remediation": "Define a risk management process owner; establish regular review cadence (minimum: at each model version update).",
     "priority": "high"},
    {"id": "ART9-02", "article": "Art. 9.2.a", "category": "Risk Management",
     "requirement": "Known and reasonably foreseeable risks are identified and analysed.",
     "remediation": "Conduct a structured risk identification workshop (STRIDE, FMEA, or equivalent) and document all identified risks.",
     "priority": "high"},
    {"id": "ART9-03", "article": "Art. 9.2.b", "category": "Risk Management",
     "requirement": "Risks are estimated and evaluated, including for reasonably foreseeable misuse.",
     "remediation": "Add misuse scenarios to risk register; assign likelihood and severity scores per ISO 27005 or equivalent.",
     "priority": "high"},
    {"id": "ART9-04", "article": "Art. 9.4", "category": "Risk Management",
     "requirement": "Risk management measures are implemented and residual risks are acceptable.",
     "remediation": "Document residual risk acceptance decisions with named accountable officer.",
     "priority": "high"},
    {"id": "ART9-05", "article": "Art. 9.6", "category": "Risk Management",
     "requirement": "Testing is performed against pre-defined metrics, including on real-world data or in simulated conditions.",
     "remediation": "Define test suite with acceptance criteria before production deployment; archive test results.",
     "priority": "high"},
    # ── Art. 10 — Data Governance ─────────────────────────────────────────────
    {"id": "ART10-01", "article": "Art. 10.2", "category": "Data Governance",
     "requirement": "Training, validation, and test datasets are subject to appropriate data governance and management practices.",
     "remediation": "Implement a data card for each dataset (source, volume, preprocessing, known biases).",
     "priority": "high"},
    {"id": "ART10-02", "article": "Art. 10.2.e", "category": "Data Governance",
     "requirement": "Training data is examined for possible biases that could affect health, safety, or fundamental rights.",
     "remediation": "Run automated bias audit (e.g., AI Fairness 360, Fairlearn) across protected characteristics; document findings.",
     "priority": "high"},
    {"id": "ART10-03", "article": "Art. 10.3", "category": "Data Governance",
     "requirement": "Training, validation and test data are relevant, sufficiently representative, and free of errors to the best extent possible.",
     "remediation": "Document representativeness assessment; perform data quality tests (completeness, consistency, accuracy).",
     "priority": "high"},
    {"id": "ART10-04", "article": "Art. 10.5", "category": "Data Governance",
     "requirement": "Special category data used only where strictly necessary; specific safeguards implemented.",
     "remediation": "Conduct GDPR DPIA for special category data; document legal basis and technical safeguards.",
     "priority": "medium"},
    # ── Art. 11 + Annex IV — Technical Documentation ─────────────────────────
    {"id": "ANX4-01", "article": "Annex IV §1", "category": "Technical Documentation",
     "requirement": "General system description including intended purpose is documented.",
     "remediation": "Create and version the Annex IV technical documentation skeleton (use eu_ai_act_classifier.py --output).",
     "priority": "high"},
    {"id": "ANX4-02", "article": "Annex IV §2", "category": "Technical Documentation",
     "requirement": "System components (hardware, software, pre-trained models) are documented with versions.",
     "remediation": "Maintain a component inventory with versions, licenses, and provenance.",
     "priority": "high"},
    {"id": "ANX4-03", "article": "Annex IV §3", "category": "Technical Documentation",
     "requirement": "Development process description including key design choices is documented.",
     "remediation": "Document architecture decisions (ADRs); include rationale for model family choice.",
     "priority": "medium"},
    {"id": "ANX4-04", "article": "Annex IV §5", "category": "Technical Documentation",
     "requirement": "Risk management system documentation is included in technical file.",
     "remediation": "Export risk register as Annex IV §5 artefact; link to evidence.",
     "priority": "high"},
    {"id": "ANX4-05", "article": "Annex IV §6", "category": "Technical Documentation",
     "requirement": "Data governance description included (training, validation, test data).",
     "remediation": "Attach data cards and bias audit report to technical file.",
     "priority": "high"},
    {"id": "ANX4-06", "article": "Annex IV §7", "category": "Technical Documentation",
     "requirement": "Logging capabilities described in technical documentation.",
     "remediation": "Document logging architecture: what is logged, schema, retention, access.",
     "priority": "medium"},
    {"id": "ANX4-07", "article": "Annex IV §8", "category": "Technical Documentation",
     "requirement": "Instructions for use (Art. 13) are attached to technical file.",
     "remediation": "Draft instructions for use covering capabilities, limitations, performance metrics.",
     "priority": "high"},
    {"id": "ANX4-08", "article": "Annex IV §9", "category": "Technical Documentation",
     "requirement": "Human oversight measures (Art. 14) are described in technical file.",
     "remediation": "Document override mechanism, halt procedure, and oversight personnel training.",
     "priority": "high"},
    # ── Art. 12 — Logging ─────────────────────────────────────────────────────
    {"id": "ART12-01", "article": "Art. 12.1", "category": "Logging",
     "requirement": "System automatically logs events at a level appropriate to the risk.",
     "remediation": "Implement structured logging for all inference calls; include input hash, output, confidence, timestamp, user ID.",
     "priority": "high"},
    {"id": "ART12-02", "article": "Art. 12.2", "category": "Logging",
     "requirement": "Logging capabilities enable tracing back to specific inputs.",
     "remediation": "Ensure logs are queryable by input characteristics; test audit trail end-to-end.",
     "priority": "high"},
    {"id": "ART12-03", "article": "Art. 12.4", "category": "Logging",
     "requirement": "Logs are kept for minimum period required (at least 6 months for Annex III cat. 1-7).",
     "remediation": "Configure log retention policy; implement immutable storage (WORM) for audit logs.",
     "priority": "medium"},
    # ── Art. 13 — Transparency ────────────────────────────────────────────────
    {"id": "ART13-01", "article": "Art. 13.1", "category": "Transparency",
     "requirement": "System is sufficiently transparent for deployers to interpret outputs appropriately.",
     "remediation": "Implement Layer 2 (audit) and Layer 3 (end-user) explanations per XAI toolkit.",
     "priority": "high"},
    {"id": "ART13-02", "article": "Art. 13.3.b", "category": "Transparency",
     "requirement": "Instructions for use include performance metrics including for specific groups of persons.",
     "remediation": "Generate disaggregated performance report by age, gender, geography; attach to instructions.",
     "priority": "high"},
    {"id": "ART13-03", "article": "Art. 13.3.e", "category": "Transparency",
     "requirement": "Instructions include human oversight measures and how to implement them.",
     "remediation": "Document step-by-step oversight procedures for deployers.",
     "priority": "medium"},
    # ── Art. 14 — Human Oversight ─────────────────────────────────────────────
    {"id": "ART14-01", "article": "Art. 14.1", "category": "Human Oversight",
     "requirement": "System is designed to be effectively overseen during operation.",
     "remediation": "Implement oversight dashboard with alerting on anomalies.",
     "priority": "high"},
    {"id": "ART14-02", "article": "Art. 14.4.c", "category": "Human Oversight",
     "requirement": "Deployers can disregard, override, or reverse the output.",
     "remediation": "Implement override capability with audit trail; test and document the mechanism.",
     "priority": "high"},
    {"id": "ART14-03", "article": "Art. 14.4.e", "category": "Human Oversight",
     "requirement": "Deployers can halt or stop the system via a clearly identified procedure.",
     "remediation": "Implement and document kill switch / emergency stop procedure.",
     "priority": "high"},
    {"id": "ART14-04", "article": "Art. 14.5", "category": "Human Oversight",
     "requirement": "Oversight is assigned to natural persons with competence, authority, and resources.",
     "remediation": "Define oversight role description; assign named person; document in RACI.",
     "priority": "medium"},
    # ── Art. 15 — Accuracy, Robustness, Cybersecurity ───────────────────────
    {"id": "ART15-01", "article": "Art. 15.1", "category": "Accuracy & Robustness",
     "requirement": "System achieves appropriate accuracy level declared in instructions for use.",
     "remediation": "Define accuracy KPIs; implement automated regression testing on each model update.",
     "priority": "high"},
    {"id": "ART15-02", "article": "Art. 15.3", "category": "Accuracy & Robustness",
     "requirement": "System is resilient to errors, faults, and inconsistencies that may occur in inputs.",
     "remediation": "Implement input validation; test with adversarial examples and out-of-distribution inputs.",
     "priority": "high"},
    {"id": "ART15-04", "article": "Art. 15.5", "category": "Accuracy & Robustness",
     "requirement": "Cybersecurity measures protect against adversarial attacks including prompt injection.",
     "remediation": "Implement prompt injection defences; integrate with OWASP LLM Top-10 threat model (see module 02).",
     "priority": "high"},
    # ── Art. 17 — Quality Management System ──────────────────────────────────
    {"id": "ART17-01", "article": "Art. 17.1", "category": "Quality Management",
     "requirement": "A quality management system covering AI Act requirements is in place.",
     "remediation": "Extend existing ISO 9001/27001 QMS to cover AI Act requirements; or implement ISO/IEC 42001.",
     "priority": "medium"},
    {"id": "ART17-02", "article": "Art. 17.1.g", "category": "Quality Management",
     "requirement": "Post-market monitoring system is covered by the QMS.",
     "remediation": "Define post-market monitoring plan: metrics, frequency, responsible team, escalation path.",
     "priority": "medium"},
    # ── Art. 72 — Post-Market Monitoring ─────────────────────────────────────
    {"id": "ART72-01", "article": "Art. 72.1", "category": "Post-Market Monitoring",
     "requirement": "A post-market monitoring plan is established and implemented.",
     "remediation": "Define monitoring KPIs (drift, accuracy, fairness, incident rate); implement dashboards.",
     "priority": "high"},
    {"id": "ART72-02", "article": "Art. 72.2", "category": "Post-Market Monitoring",
     "requirement": "Serious incidents are reported to national market surveillance authority.",
     "remediation": "Implement incident reporting SOP; define 'serious incident' threshold for AI system.",
     "priority": "high"},
    # ── GDPR Art. 22 intersection ─────────────────────────────────────────────
    {"id": "GDPR22-01", "article": "GDPR Art. 22.3", "category": "GDPR Intersection",
     "requirement": "Where solely automated decisions affect natural persons, meaningful explanation is available upon request.",
     "remediation": "Implement Layer 3 (end-user) explanation capability; document the procedure in privacy notice.",
     "priority": "high"},
    {"id": "GDPR22-02", "article": "GDPR Art. 35", "category": "GDPR Intersection",
     "requirement": "DPIA conducted for high-risk processing involving AI.",
     "remediation": "Conduct DPIA jointly with DPO; document output and residual risks.",
     "priority": "high"},
]


# ─────────────────────────────────────────────────────────────────────────────
# Checker engine
# ─────────────────────────────────────────────────────────────────────────────

class ConformityChecker:

    def __init__(self):
        self.items: List[CheckItem] = [
            CheckItem(
                item_id=c["id"],
                article=c["article"],
                category=c["category"],
                requirement=c["requirement"],
                remediation=c["remediation"],
                priority=c["priority"],
            )
            for c in CHECKLIST
        ]

    def run_interactive(self) -> List[CheckItem]:
        print("\n" + "═" * 65)
        print("  EU AI Act Conformity Checker — Gap Analysis")
        print(f"  {len(self.items)} requirements | Annex IV + Art. 9, 10, 12-15, 17, 72")
        print("═" * 65)
        print("\nFor each requirement, enter: G (green/met), A (amber/partial), R (red/not met), N (not applicable)")
        print("Press Enter to skip (defaults to RED for unanswered high-priority items)\n")

        for item in self.items:
            print(f"\n[{item.item_id}] {item.article} — {item.category} [{item.priority.upper()}]")
            print(f"  {item.requirement}")
            ans = input("  Status [G/A/R/N]: ").strip().upper()
            evidence = ""
            if ans == "G":
                item.status = Status.GREEN
                evidence = input("  Evidence reference (optional): ").strip()
            elif ans == "A":
                item.status = Status.AMBER
                evidence = input("  What is partially in place? ").strip()
            elif ans == "N":
                item.status = Status.NA
            else:
                item.status = Status.RED
            item.evidence = evidence

        return self.items

    def run_demo(self) -> List[CheckItem]:
        """Simulate a typical enterprise in year-1 of compliance."""
        import random
        random.seed(2026)
        # Typical pattern: documentation and logging gaps are common
        common_gaps = {"ART10-02", "ANX4-03", "ART12-03", "ART72-01",
                       "ART72-02", "ART17-01", "ART17-02", "GDPR22-01"}
        for item in self.items:
            if item.item_id in common_gaps:
                item.status = Status.RED
            elif random.random() < 0.25:
                item.status = Status.AMBER
                item.evidence = "Partial implementation in progress"
            else:
                item.status = Status.GREEN
                item.evidence = "Documented and reviewed"
        return self.items

    def generate_report(self, system_name: str = "AI System") -> str:
        by_status = {Status.GREEN: [], Status.AMBER: [], Status.RED: [], Status.NA: []}
        for item in self.items:
            by_status[item.status].append(item)

        total = len([i for i in self.items if i.status != Status.NA])
        green = len(by_status[Status.GREEN])
        amber = len(by_status[Status.AMBER])
        red = len(by_status[Status.RED])
        score = int(100 * (green + 0.5 * amber) / total) if total else 0

        lines = [
            "═" * 65,
            f"  EU AI Act Conformity Report — {system_name}",
            "═" * 65,
            f"  Overall score: {score}/100",
            f"  ✅ GREEN: {green}  ⚠️ AMBER: {amber}  ❌ RED: {red}  ⬜ N/A: {len(by_status[Status.NA])}",
            "",
        ]

        # Group by category
        categories = {}
        for item in self.items:
            categories.setdefault(item.category, []).append(item)

        for cat, items in categories.items():
            cat_red = sum(1 for i in items if i.status == Status.RED)
            cat_amber = sum(1 for i in items if i.status == Status.AMBER)
            cat_green = sum(1 for i in items if i.status == Status.GREEN)
            lines.append(f"  ── {cat} ({'❌' if cat_red > 0 else '⚠️' if cat_amber > 0 else '✅'}) "
                        f"G:{cat_green} A:{cat_amber} R:{cat_red}")
            for item in items:
                lines.append(f"     [{item.status.value}] {item.item_id} {item.article}")
                if item.status in (Status.RED, Status.AMBER):
                    lines.append(f"       → {item.remediation}")
                if item.evidence:
                    lines.append(f"       Evidence: {item.evidence}")

        # Priority actions
        red_high = [i for i in by_status[Status.RED] if i.priority == "high"]
        if red_high:
            lines += ["", "  ── PRIORITY ACTIONS (RED + HIGH) ──────────────────────────"]
            for i, item in enumerate(red_high[:5], 1):
                lines.append(f"  {i}. [{item.item_id}] {item.requirement}")
                lines.append(f"     Fix: {item.remediation}")

        lines.append("═" * 65)
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="EU AI Act Conformity Checker — 47-item gap analysis")
    parser.add_argument("--demo", action="store_true", help="Run demo with simulated responses")
    parser.add_argument("--interactive", action="store_true", help="Run interactive gap analysis")
    parser.add_argument("--system-type", default="high-risk", help="System type (for report header)")
    parser.add_argument("--output", help="Save report to file")
    args = parser.parse_args()

    checker = ConformityChecker()
    system_name = args.system_type

    if args.demo:
        checker.run_demo()
    elif args.interactive:
        system_name = input("System name: ").strip() or "AI System"
        checker.run_interactive()
    else:
        parser.print_help()
        return

    report = checker.generate_report(system_name)
    print("\n" + report)

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"\n  Report saved to: {args.output}")


if __name__ == "__main__":
    main()
