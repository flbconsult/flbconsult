#!/usr/bin/env python3
"""
EU AI Act Classifier — Module 04
=================================
Classifies an AI system across the four risk tiers of the EU AI Act (2024/1689),
generates an Article 11 / Annex IV technical documentation skeleton,
and flags Article 5 prohibited practices.

Usage:
    python eu_ai_act_classifier.py --interactive
    python eu_ai_act_classifier.py --system-name "CV Screening Tool" --sector hr --output doc_skeleton.md
    python eu_ai_act_classifier.py --demo

References:
    EU AI Act, Regulation (EU) 2024/1689
    ISO/IEC 42001:2023
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from textwrap import dedent
from typing import List, Optional, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# Data models
# ─────────────────────────────────────────────────────────────────────────────

class RiskTier(Enum):
    PROHIBITED = "PROHIBITED (Article 5)"
    HIGH_RISK = "HIGH-RISK (Article 6 + Annex III)"
    LIMITED_RISK = "LIMITED RISK (Article 50 — transparency obligations)"
    MINIMAL_RISK = "MINIMAL RISK (no mandatory requirements)"


@dataclass
class ClassificationResult:
    tier: RiskTier
    annex_iii_category: Optional[str]
    rationale: str
    art5_flags: List[str]
    art63_reclassification_possible: bool
    documentation_requirements: List[str]
    recommended_actions: List[str]


ANNEX_III_CATEGORIES = {
    "biometrics": {
        "label": "§1 — Biometrics",
        "description": "Remote biometric ID, categorisation systems, emotion recognition",
        "examples": ["face recognition", "emotion detection", "biometric access control"],
    },
    "critical_infrastructure": {
        "label": "§2 — Critical Infrastructure",
        "description": "Safety components for digital infrastructure, road traffic, utilities",
        "examples": ["network routing AI", "grid management AI", "traffic control AI"],
    },
    "education": {
        "label": "§3 — Education & Vocational Training",
        "description": "Access/admission decisions, student assessment, learning evaluation",
        "examples": ["exam grading AI", "admissions screening", "learning progress AI"],
    },
    "hr": {
        "label": "§4 — Employment & Workers Management",
        "description": "Recruitment, promotion, task allocation, performance monitoring",
        "examples": ["CV screening", "interview analysis", "performance scoring"],
    },
    "essential_services": {
        "label": "§5 — Essential Private & Public Services",
        "description": "Credit scoring, insurance risk, emergency services, benefits eligibility",
        "examples": ["credit scoring", "insurance underwriting AI", "benefit eligibility"],
    },
    "law_enforcement": {
        "label": "§6 — Law Enforcement",
        "description": "Risk assessment, polygraphs, crime prediction, profiling",
        "examples": ["recidivism risk scoring", "crime prediction", "forensic AI"],
    },
    "migration": {
        "label": "§7 — Migration & Border Control",
        "description": "Lie detection, irregular migration risk, document authenticity",
        "examples": ["border control AI", "asylum risk assessment"],
    },
    "justice": {
        "label": "§8 — Justice & Democratic Processes",
        "description": "Legal research AI, judicial decision support, election analysis",
        "examples": ["judicial decision AI", "election prediction AI"],
    },
}

ART5_PROHIBITED_PRACTICES = [
    {
        "id": "5.1.a",
        "label": "Subliminal manipulation",
        "question": "Does the system use subliminal techniques (below perception threshold) to distort behaviour causing harm?",
        "keywords": ["subliminal", "subconscious manipulation", "hidden persuasion"],
    },
    {
        "id": "5.1.b",
        "label": "Exploitation of vulnerabilities",
        "question": "Does the system exploit vulnerabilities of specific groups (children, elderly, disabled) to distort behaviour causing harm?",
        "keywords": ["vulnerable populations", "children targeting", "cognitive impairment"],
    },
    {
        "id": "5.1.c",
        "label": "Social scoring by public authority",
        "question": "Is this a public authority social scoring system rating citizens for detrimental treatment?",
        "keywords": ["social credit", "citizen scoring", "government trust score"],
    },
    {
        "id": "5.1.d",
        "label": "Real-time biometric identification (law enforcement)",
        "question": "Does the system perform real-time remote biometric identification in public spaces for law enforcement without authorisation?",
        "keywords": ["real-time face recognition", "live biometric surveillance", "public space identification"],
    },
    {
        "id": "5.1.e",
        "label": "Biometric categorisation for sensitive attributes",
        "question": "Does the system infer race, political opinion, trade union membership, religion, or sexual orientation from biometrics?",
        "keywords": ["race inference", "religion inference", "political opinion biometric"],
    },
    {
        "id": "5.1.f",
        "label": "Emotion recognition in workplace/education",
        "question": "Does the system infer emotions of workers or students in workplace or educational settings?",
        "keywords": ["workplace emotion detection", "student emotion", "employee sentiment AI"],
    },
    {
        "id": "5.1.g",
        "label": "Facial recognition database scraping",
        "question": "Is this system building facial recognition databases by scraping internet or CCTV footage?",
        "keywords": ["biometric database scraping", "facial recognition harvesting"],
    },
    {
        "id": "5.1.h",
        "label": "Predictive policing based solely on profiling",
        "question": "Does the system predict criminal offences based solely on profiling without individual assessment?",
        "keywords": ["predictive policing", "crime prediction profiling"],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Classification engine
# ─────────────────────────────────────────────────────────────────────────────

class AIActClassifier:

    def __init__(self):
        self.system_name = "Unknown System"
        self.sector = None
        self.answers = {}

    def run_interactive(self) -> ClassificationResult:
        """Run an interactive classification session."""
        print("\n" + "═" * 65)
        print("  EU AI Act Classifier — Risk Tier Assessment")
        print("  Regulation (EU) 2024/1689 | Module 04 — flbconsult")
        print("═" * 65)

        self.system_name = input("\n▸ System name: ").strip() or "Unnamed AI System"

        print("\n── STEP 1: Article 5 Screen (Prohibited Practices) ──────────")
        art5_flags = self._screen_art5()
        if art5_flags:
            return ClassificationResult(
                tier=RiskTier.PROHIBITED,
                annex_iii_category=None,
                rationale=f"System triggers {len(art5_flags)} prohibited practice(s) under Article 5: "
                          + ", ".join(f"Art. {f}" for f in art5_flags),
                art5_flags=art5_flags,
                art63_reclassification_possible=False,
                documentation_requirements=[
                    "Article 5 prohibition applies — system must NOT be placed on the market or put into service.",
                    "Legal counsel review mandatory before any further development.",
                ],
                recommended_actions=[
                    "STOP development immediately.",
                    "Engage legal counsel for a full Art. 5 review.",
                    "Evaluate whether a redesign can move outside the prohibited scope.",
                ],
            )

        print("\n── STEP 2: High-Risk Classification (Article 6 + Annex III) ──")
        annex3_cat = self._classify_annex3()

        if annex3_cat:
            reclassify = self._check_reclassification()
            if reclassify:
                return self._build_result(RiskTier.LIMITED_RISK, annex3_cat, art5_flags,
                                          reclassified=True)
            return self._build_result(RiskTier.HIGH_RISK, annex3_cat, art5_flags)

        print("\n── STEP 3: Limited-Risk Check (Article 50) ───────────────────")
        is_limited = self._check_limited_risk()
        if is_limited:
            return self._build_result(RiskTier.LIMITED_RISK, None, art5_flags)

        return self._build_result(RiskTier.MINIMAL_RISK, None, art5_flags)

    def _screen_art5(self) -> List[str]:
        flags = []
        for practice in ART5_PROHIBITED_PRACTICES:
            ans = input(f"\n  Art. {practice['id']} — {practice['label']}\n"
                        f"  {practice['question']} [y/N]: ").strip().lower()
            if ans == "y":
                flags.append(practice["id"])
        return flags

    def _classify_annex3(self) -> Optional[str]:
        print("\n  Select the primary deployment sector / use-case:")
        sectors = list(ANNEX_III_CATEGORIES.keys())
        for i, key in enumerate(sectors, 1):
            cat = ANNEX_III_CATEGORIES[key]
            print(f"  {i:2}. {cat['label']}: {cat['description']}")
        print(f"  {len(sectors)+1:2}. None of the above")

        choice = input("\n  Enter number: ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(sectors):
                self.sector = sectors[idx]
                return self.sector
        except ValueError:
            pass
        return None

    def _check_reclassification(self) -> bool:
        print("\n  ── Art. 6.3 Reclassification Check ──────────────────────────")
        print("  An Annex III system MAY be reclassified to limited risk if BOTH conditions are met:")
        print("  (a) It does not make autonomous decisions with significant adverse effect on persons.")
        print("  (b) Provider can demonstrate it does not pose significant risk of harm.")

        a = input("\n  (a) Is the system purely advisory (human always makes the final decision)? [y/N]: ").strip().lower()
        b = input("  (b) Have you conducted a documented self-assessment showing no significant harm risk? [y/N]: ").strip().lower()

        if a == "y" and b == "y":
            print("\n  ✔ Art. 6.3 reclassification appears applicable.")
            print("    → Requires formal self-assessment document + notification to market surveillance authority.")
            return True
        return False

    def _check_limited_risk(self) -> bool:
        print("\n  Does the system interact directly with natural persons (chatbot, virtual assistant)? [y/N]: ", end="")
        is_chatbot = input().strip().lower() == "y"
        print("  Does the system generate text, audio, or visual content (deepfake, AIGC)? [y/N]: ", end="")
        is_aigc = input().strip().lower() == "y"
        return is_chatbot or is_aigc

    def _build_result(self, tier: RiskTier, annex3_cat: Optional[str],
                      art5_flags: List[str], reclassified: bool = False) -> ClassificationResult:

        cat_label = ANNEX_III_CATEGORIES[annex3_cat]["label"] if annex3_cat else "N/A"

        if tier == RiskTier.HIGH_RISK:
            rationale = f"System falls under Annex III {cat_label}. Full Chapter III Section 2 requirements apply."
            docs = [
                "Art. 9 — Risk management system (continuous lifecycle)",
                "Art. 10 — Data governance and management",
                "Art. 11 + Annex IV — Technical documentation (9 categories)",
                "Art. 12 — Logging and audit trail capabilities",
                "Art. 13 — Transparency + instructions for use",
                "Art. 14 — Human oversight measures",
                "Art. 15 — Accuracy, robustness, cybersecurity",
                "Art. 17 — Quality management system",
                "Art. 72 — Post-market monitoring plan",
            ]
            actions = [
                f"Run ai_act_conformity_checker.py --system-type high-risk --sector {annex3_cat or 'general'}",
                "Assign a named compliance owner (ideally: CTO or Chief AI Officer)",
                "Integrate Annex IV documentation into your MLOps pipeline",
                "Implement Art. 12 logging before production deployment",
                "Conduct Art. 9 risk assessment and document residual risks",
            ]
        elif tier == RiskTier.LIMITED_RISK:
            if reclassified:
                rationale = (f"System initially classified as Annex III {cat_label} but Art. 6.3 "
                             "reclassification applies. Transparency obligations (Art. 50) remain.")
            else:
                rationale = "System subject to transparency obligations (Art. 50) only."
            docs = [
                "Art. 50 — Transparency obligations (disclosure, labelling)",
                "Art. 6.3 self-assessment document (if reclassified from Annex III)",
                "Notification to market surveillance authority (if Art. 6.3 reclassification)",
            ]
            actions = [
                "Implement AI disclosure mechanism for end-users",
                "Ensure AIGC labelling if system generates synthetic content",
                "Document the Art. 6.3 self-assessment and archive it",
            ]
        else:
            rationale = "System presents minimal risk. No mandatory AI Act requirements."
            docs = ["Voluntary: apply EU AI Act Code of Practice for GPAI (Art. 56)"]
            actions = [
                "Consider voluntary alignment with NIST AI RMF and ISO/IEC 42001",
                "Monitor AI Act developments — minimal risk classification can change with use-case evolution",
            ]

        return ClassificationResult(
            tier=tier,
            annex_iii_category=cat_label if annex3_cat else None,
            rationale=rationale,
            art5_flags=art5_flags,
            art63_reclassification_possible=reclassified,
            documentation_requirements=docs,
            recommended_actions=actions,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Annex IV skeleton generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_annex_iv_skeleton(system_name: str, sector: str, result: ClassificationResult) -> str:
    today = date.today().isoformat()
    return dedent(f"""
    # Technical Documentation — Annex IV (EU AI Act 2024/1689)

    **System name:** {system_name}
    **Sector:** {sector or 'N/A'}
    **Classification:** {result.tier.value}
    **Document version:** 1.0 — {today}
    **Owner:** [CTO / Chief AI Officer name]

    ---

    ## 1. General Description (Annex IV §1)

    ### 1.1 Intended purpose
    > [Describe the specific purpose for which the AI system is intended, including the specific context
    > and conditions of use. Reference the intended deployers and affected persons.]

    ### 1.2 System version and release date
    - Model version: [e.g., v2.3.1]
    - Release date: {today}
    - Previous versions: [list]

    ### 1.3 Interaction with hardware/software
    > [Describe hardware requirements, cloud dependencies, APIs, and integration points.]

    ---

    ## 2. Description of System Components (Annex IV §2)

    ### 2.1 Hardware components
    > [GPU/CPU requirements, memory, network bandwidth]

    ### 2.2 Software components
    - Runtime: [Python x.x, CUDA x.x]
    - Key libraries: [list with versions]
    - Pre-trained models used: [model name, provider, version, license]

    ### 2.3 Input data specification
    > [Describe all input data types, formats, expected distributions, and known edge cases.]

    ### 2.4 Output data specification
    > [Describe outputs: scores, classifications, generated text, etc. Include confidence measures.]

    ---

    ## 3. Development Process (Annex IV §3)

    ### 3.1 Design choices and key decisions
    > [Describe the key architectural decisions: model family, training approach, evaluation strategy.]

    ### 3.2 Training methodology
    - Training data: [describe — see §6 for full data governance]
    - Training compute: [FLOPs, hardware, duration]
    - Optimisation: [loss function, optimizer, hyperparameters]

    ### 3.3 Known limitations identified during development
    > [Document failure modes, edge cases, and performance degradation conditions.]

    ---

    ## 4. Monitoring, Functioning and Control (Annex IV §4)

    > [Describe how the system is monitored in production: metrics, alerting thresholds,
    > dashboard references, responsible team.]

    ---

    ## 5. Risk Management System (Annex IV §5 — Art. 9)

    ### 5.1 Risk identification
    > [List identified risks across the system lifecycle.]

    | Risk ID | Risk Description | Likelihood | Severity | Reversibility |
    |---------|-----------------|------------|----------|---------------|
    | R-001   | [e.g., Biased outputs for protected group X] | Medium | High | Medium |
    | R-002   | | | | |

    ### 5.2 Mitigation measures implemented
    > [For each risk, describe the technical or organisational control.]

    ### 5.3 Residual risks
    > [Document risks that remain after mitigation and how they are communicated (Art. 13).]

    ---

    ## 6. Data Governance (Annex IV §6 — Art. 10)

    ### 6.1 Training dataset
    - Source: [internal / third-party / synthetic]
    - Volume: [records/tokens]
    - Collection period: [dates]
    - Consent/legal basis: [GDPR basis]
    - Known biases: [documented biases and mitigation]

    ### 6.2 Validation dataset
    - Source: [held-out / external benchmark]
    - Volume: [records]
    - Representativeness: [coverage of intended use population]

    ### 6.3 Test dataset
    - Source: [held-out / external]
    - Performance metrics: [accuracy, F1, MAPE, etc.]
    - Disaggregated performance: [by gender, age, geography, etc.]

    ---

    ## 7. Logging Capabilities (Annex IV §7 — Art. 12)

    > [Describe logging implementation: what is logged, retention policy, access controls,
    > audit trail format, integration with SIEM if applicable.]

    ---

    ## 8. Instructions for Use (Annex IV §8 — Art. 13)

    ### 8.1 System capabilities
    > [Plain-language description of what the system can and cannot do.]

    ### 8.2 Known limitations and risks to communicte to deployers
    > [List residual risks that deployers must be made aware of.]

    ### 8.3 Performance metrics
    - Overall accuracy: [metric]
    - Accuracy by subgroup: [table]
    - Known failure conditions: [list]

    ---

    ## 9. Human Oversight Measures (Annex IV §9 — Art. 14)

    ### 9.1 Override mechanism
    > [Describe the human override capability: who can override, how, with what audit trail.]

    ### 9.2 Halt/stop procedure
    > [Describe the system halt procedure and responsible role.]

    ### 9.3 Training for oversight personnel
    > [Describe training requirements for persons responsible for oversight.]

    ---

    ## Approval and Version Control

    | Version | Date | Author | Change Description | Approved By |
    |---------|------|--------|--------------------|-------------|
    | 1.0 | {today} | [Author] | Initial documentation | [Approver] |

    ---
    *Generated by eu_ai_act_classifier.py — flbconsult/04-eu-ai-act*
    """).strip()


# ─────────────────────────────────────────────────────────────────────────────
# Demo mode
# ─────────────────────────────────────────────────────────────────────────────

def run_demo():
    """Demonstrate classification of three example systems."""
    demos = [
        {
            "name": "LLM-based CV Screening Tool",
            "description": "Automatically scores and ranks job candidates based on CV content",
            "sector": "hr",
            "expected_tier": RiskTier.HIGH_RISK,
        },
        {
            "name": "Internal Meeting Summariser",
            "description": "Summarises internal meeting transcripts for distribution",
            "sector": None,
            "expected_tier": RiskTier.LIMITED_RISK,
        },
        {
            "name": "Real-Estate AVM with RICS Human Review Gate",
            "description": "Automated valuation with mandatory RICS surveyor validation before output",
            "sector": "essential_services",
            "expected_tier": RiskTier.LIMITED_RISK,  # Art. 6.3 reclassification
        },
    ]

    print("\n" + "═" * 65)
    print("  EU AI Act Classifier — DEMO MODE")
    print("  Three representative enterprise AI systems")
    print("═" * 65)

    for i, demo in enumerate(demos, 1):
        print(f"\n{'─'*65}")
        print(f"  Demo {i}: {demo['name']}")
        print(f"  {demo['description']}")
        print(f"  Sector: {demo['sector'] or 'General purpose'}")
        print(f"  Expected tier: {demo['expected_tier'].value}")

        # Simple deterministic classification for demo
        if demo["sector"] in ANNEX_III_CATEGORIES:
            cat = ANNEX_III_CATEGORIES[demo["sector"]]
            tier_str = "HIGH-RISK" if demo["expected_tier"] == RiskTier.HIGH_RISK else "LIMITED RISK (Art. 6.3 reclassification)"
            print(f"\n  Classification: {tier_str}")
            print(f"  Annex III category: {cat['label']}")
            if demo["expected_tier"] == RiskTier.LIMITED_RISK:
                print("  Note: Art. 6.3 reclassification applicable — human-in-the-loop gate documented.")
        else:
            print(f"\n  Classification: {demo['expected_tier'].value}")

    print(f"\n{'─'*65}")
    print("  Run with --interactive for a full guided assessment of your system.")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="EU AI Act Risk Tier Classifier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python eu_ai_act_classifier.py --interactive
  python eu_ai_act_classifier.py --demo
  python eu_ai_act_classifier.py --interactive --output annex_iv_skeleton.md
        """
    )
    parser.add_argument("--interactive", action="store_true",
                        help="Run interactive classification questionnaire")
    parser.add_argument("--demo", action="store_true",
                        help="Run demo with three example systems")
    parser.add_argument("--output", metavar="FILE",
                        help="Save Annex IV skeleton to FILE (requires --interactive)")

    args = parser.parse_args()

    if args.demo:
        run_demo()
        return

    if args.interactive:
        classifier = AIActClassifier()
        result = classifier.run_interactive()

        print("\n" + "═" * 65)
        print("  CLASSIFICATION RESULT")
        print("═" * 65)
        print(f"\n  Tier:      {result.tier.value}")
        if result.annex_iii_category:
            print(f"  Annex III: {result.annex_iii_category}")
        print(f"\n  Rationale: {result.rationale}")

        if result.art5_flags:
            print(f"\n  ⚠️  PROHIBITED PRACTICES FLAGGED: {', '.join(result.art5_flags)}")

        print("\n  Required documentation:")
        for d in result.documentation_requirements:
            print(f"    • {d}")

        print("\n  Recommended actions:")
        for a in result.recommended_actions:
            print(f"    → {a}")

        if args.output and result.tier in (RiskTier.HIGH_RISK, RiskTier.LIMITED_RISK):
            skeleton = generate_annex_iv_skeleton(classifier.system_name, classifier.sector or "", result)
            with open(args.output, "w") as f:
                f.write(skeleton)
            print(f"\n  ✔ Annex IV skeleton written to: {args.output}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
