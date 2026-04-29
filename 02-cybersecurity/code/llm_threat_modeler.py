"""
LLM Threat Modeler
==================

Companion to the paper *Threat Modelling for LLM-Driven Systems*
(`docs/02-llm-threat-modeling.md`).

Consumes a JSON description of an LLM architecture and emits:

  * STRIDE-LLM threats with severity scoring
  * LINDDUN-LLM privacy threats
  * OWASP LLM Top-10 (2025) mapping
  * Mitigation plan with framework references (ANSSI, NIST AI RMF)

Usage
-----
    python llm_threat_modeler.py --architecture rag-customer-facing
    python llm_threat_modeler.py --input my_architecture.json

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
# Threat library
# --------------------------------------------------------------------------

@dataclass
class Threat:
    code: str
    name: str
    stride_class: str          # S/T/R/I/D/E
    owasp_llm_2025: str        # e.g. "LLM01"
    description: str
    triggers: List[str]        # architecture properties that activate this threat
    mitigations: List[str]
    references: List[str] = field(default_factory=list)


THREAT_LIBRARY: List[Threat] = [
    Threat(
        code="STR-LLM-01",
        name="Indirect prompt injection via retrieved content",
        stride_class="S/T",
        owasp_llm_2025="LLM01",
        description=(
            "Adversarial instructions embedded in retrieved documents override the "
            "system prompt and cause the model to act on attacker intent."
        ),
        triggers=["rag", "external_corpus", "user_generated_corpus"],
        mitigations=[
            "Per-document trust scores influencing retrieval",
            "Instruction-following hardening in system prompt",
            "Eval-on-PR with prompt-injection probe set",
            "ANSSI: cloisonnement données / instructions",
        ],
        references=["arXiv:2302.12173 (Greshake et al. 2023)", "OWASP LLM01"],
    ),
    Threat(
        code="STR-LLM-02",
        name="Tool authority escalation in agentic system",
        stride_class="E",
        owasp_llm_2025="LLM06",
        description=(
            "Agent equipped with multiple tools is convinced via prompt manipulation "
            "to invoke a tool with broader privileges than its design intent."
        ),
        triggers=["agentic", "tools", "multi_agent"],
        mitigations=[
            "Per-agent IAM with minimal tool ACLs",
            "Explicit human approval for state-mutating tools",
            "Bounded recursion depth + cost ceiling",
            "Red-team probes for tool misuse in CI",
        ],
        references=["OWASP LLM06", "Anthropic, Building Effective Agents (2024)"],
    ),
    Threat(
        code="STR-LLM-03",
        name="Training-data / context memorisation leak",
        stride_class="I",
        owasp_llm_2025="LLM02",
        description=(
            "Model recites verbatim sensitive data from fine-tuning or system prompt "
            "in response to crafted queries."
        ),
        triggers=["fine_tuned", "system_prompt_with_secrets"],
        mitigations=[
            "No secrets or PII in system prompt",
            "Output filters (regex + classifier) on responses",
            "Differential privacy in fine-tuning",
            "Audit of training data for PII",
        ],
        references=["Carlini et al. (2023) USENIX 21", "OWASP LLM02"],
    ),
    Threat(
        code="STR-LLM-04",
        name="Token-amplification denial of service",
        stride_class="D",
        owasp_llm_2025="LLM04",
        description=(
            "Adversary submits inputs that trigger long-context or recursive generation, "
            "exhausting per-tenant quota and budget."
        ),
        triggers=["long_context", "agentic"],
        mitigations=[
            "Per-tenant token-budget rate limit",
            "Max-output-token cap per request",
            "Cost telemetry and anomaly detection",
            "Recursion-depth limits in agentic flows",
        ],
        references=["OWASP LLM04"],
    ),
    Threat(
        code="STR-LLM-05",
        name="LLM trace plausible deniability (forensics gap)",
        stride_class="R",
        owasp_llm_2025="LLM05",
        description=(
            "Lack of structured LLM call traces prevents post-incident reconstruction."
        ),
        triggers=["any_llm"],
        mitigations=[
            "LLM trace store with 90-day retention (Langfuse/Phoenix)",
            "Trace ID propagated through all tool calls",
            "SOC 24/7 access to LLM traces",
        ],
        references=["NIST AI RMF Measure"],
    ),
    Threat(
        code="LIN-LLM-01",
        name="Cross-tenant linkability via shared embedding space",
        stride_class="-",
        owasp_llm_2025="LLM10",
        description=(
            "Vector representations leak structural information across tenants when "
            "embeddings share a single index without strong isolation."
        ),
        triggers=["multi_tenant", "vector_index"],
        mitigations=[
            "Per-tenant embedding spaces or strict ACLs on the vector index",
            "Encryption-at-rest with per-tenant keys (BYOK)",
            "Audit of cross-tenant query patterns",
        ],
        references=["OWASP LLM10", "LINDDUN — Linkability"],
    ),
    Threat(
        code="LIN-LLM-02",
        name="Cross-jurisdictional inference (residency violation)",
        stride_class="-",
        owasp_llm_2025="-",
        description=(
            "EU-deployed system fails over to a US region during incident, breaching "
            "GDPR Art. 44 transfer constraints."
        ),
        triggers=["multi_region_failover", "eu_personal_data"],
        mitigations=[
            "Hard residency constraints in the inference router",
            "Pre-approved EEA-only failover targets",
            "Standard Contractual Clauses with provider for emergency cases only",
        ],
        references=["GDPR Art. 44", "ANSSI Recommandations 2024"],
    ),
]

# --------------------------------------------------------------------------
# Architecture presets
# --------------------------------------------------------------------------

ARCHITECTURE_PRESETS: Dict[str, dict] = {
    "rag-customer-facing": {
        "name": "Customer-facing RAG chatbot",
        "properties": [
            "rag", "external_corpus", "user_generated_corpus",
            "multi_tenant", "vector_index", "any_llm",
        ],
    },
    "agentic-back-office": {
        "name": "Multi-agent back-office automation",
        "properties": [
            "agentic", "tools", "multi_agent", "long_context", "any_llm",
        ],
    },
    "internal-copilot": {
        "name": "Internal employee copilot fine-tuned on company corpus",
        "properties": [
            "fine_tuned", "system_prompt_with_secrets", "any_llm",
            "multi_region_failover", "eu_personal_data",
        ],
    },
}


# --------------------------------------------------------------------------
# Engine
# --------------------------------------------------------------------------

def applicable_threats(architecture_props: List[str]) -> List[Threat]:
    props = set(architecture_props)
    return [t for t in THREAT_LIBRARY if any(trig in props for trig in t.triggers)]


def render_report(arch_name: str, threats: List[Threat]) -> str:
    out = ["=" * 80, f"Threat Model — {arch_name}", "=" * 80]
    out.append(f"{len(threats)} applicable threat(s)\n")
    for t in threats:
        out.extend([
            f"### [{t.code}] ({t.stride_class} · OWASP {t.owasp_llm_2025}) {t.name}",
            f"   {t.description}",
            "   Mitigations:",
            *[f"     - {m}" for m in t.mitigations],
            "   References: " + ", ".join(t.references),
            "",
        ])
    return "\n".join(out)


def export_json(arch_name: str, threats: List[Threat], path: Path) -> None:
    payload = {
        "architecture": arch_name,
        "n_threats": len(threats),
        "threats": [
            {
                "code": t.code, "name": t.name,
                "stride_class": t.stride_class,
                "owasp_llm_2025": t.owasp_llm_2025,
                "mitigations": t.mitigations,
                "references": t.references,
            }
            for t in threats
        ],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description="LLM Threat Modeler.")
    p.add_argument("--architecture", choices=list(ARCHITECTURE_PRESETS.keys()),
                   default="rag-customer-facing")
    p.add_argument("--input", type=Path,
                   help="JSON file with {\"name\":..., \"properties\":[...]} overriding the preset.")
    p.add_argument("--out", type=Path, default=Path("threat_model.json"))
    args = p.parse_args()

    if args.input:
        spec = json.loads(args.input.read_text())
    else:
        spec = ARCHITECTURE_PRESETS[args.architecture]

    threats = applicable_threats(spec["properties"])
    print(render_report(spec["name"], threats))
    export_json(spec["name"], threats, args.out)
    print(f"\n[json] {args.out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
