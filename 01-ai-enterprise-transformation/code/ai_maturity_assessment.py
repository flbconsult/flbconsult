"""
AI Maturity Assessment
======================

Executable companion to the paper *Enterprise AI Transformation Framework*
(`docs/01-enterprise-ai-transformation-framework.md`).

Scores an organisation on 6 dimensions, maps the result to a stage of the
5-stage maturity model (AI-Curious → AI-Native), and emits:

  * a JSON report
  * a radar chart (matplotlib)
  * a prioritised set of next-step recommendations.

Usage
-----
    python ai_maturity_assessment.py --interactive
    python ai_maturity_assessment.py --input sample_responses.json --no-chart

Author: Franck Bongard, 2026.
License: MIT.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

# --------------------------------------------------------------------------
# Model
# --------------------------------------------------------------------------

DIMENSIONS: Dict[str, str] = {
    "data_fabric": "Data fabric, lineage, governance, table formats",
    "talent": "AI/ML talent density, role design, evaluation engineers",
    "mlops": "MLOps, model registry, traces, prompt versioning",
    "evaluation": "Evaluation suites, eval-on-PR, gold datasets",
    "governance": "AI Act, DORA, NIST AI RMF, sectorial compliance",
    "change_mgmt": "Change management, operating-model redesign",
}

# Each question is a (dimension, statement) pair scored 0..4 (Likert-like).
QUESTIONS: List[Tuple[str, str]] = [
    ("data_fabric", "We have a unified data catalogue with lineage and ownership."),
    ("data_fabric", "Production data uses open table formats (Iceberg/Delta/Hudi)."),
    ("data_fabric", "Access to PII data is governed by short-lived, IAM-federated credentials."),
    ("talent", "We have a Head of AI Engineering distinct from the Head of Data."),
    ("talent", "We employ at least one full-time Evaluation Engineer."),
    ("talent", "Senior AI engineers ship to production weekly, not monthly."),
    ("mlops", "Every prompt and model in production is versioned in a registry."),
    ("mlops", "We have an LLM trace store retaining at least 30 days of calls."),
    ("mlops", "Per-tenant cost telemetry on AI workloads is available to FinOps."),
    ("evaluation", "Every PR touching prompts or retrieval triggers a gold-set eval."),
    ("evaluation", "We measure faithfulness, relevance and prompt-injection resistance."),
    ("evaluation", "Cost-per-correct-answer is reported as a board-level KPI."),
    ("governance", "AI Act high-risk classification has been performed on every product."),
    ("governance", "DORA / sectorial third-party risk has been formally assessed for our LLM providers."),
    ("governance", "An ISO/IEC 42001 / NIST AI RMF programme is in place or in flight."),
    ("change_mgmt", "≥10% of the AI programme budget is allocated to change-management."),
    ("change_mgmt", "Operating model has been formally redesigned for the AI workflow."),
    ("change_mgmt", "Humans review *exceptions*, not *every instance*, in our most AI-driven process."),
]

STAGE_THRESHOLDS = [
    (0.20, "Stage 0 — AI-Curious", "Ad-hoc experimentation."),
    (0.40, "Stage 1 — AI-Sandboxed", "Sanctioned playground; data still siloed."),
    (0.60, "Stage 2 — AI-Augmented", "At least one process re-engineered around an LLM."),
    (0.75, "Stage 3 — AI-Industrialised", "MLOps + evaluation harness + observability."),
    (0.90, "Stage 4 — AI-Embedded", "AI is a customer-facing product feature, SLA-bound."),
    (1.01, "Stage 5 — AI-Native", "Operating model is a closed data-flywheel."),
]


@dataclass
class AssessmentResult:
    by_dimension: Dict[str, float]
    overall: float
    stage_label: str
    stage_summary: str
    recommendations: List[str] = field(default_factory=list)


# --------------------------------------------------------------------------
# Scoring logic
# --------------------------------------------------------------------------

def score(responses: Dict[int, int]) -> AssessmentResult:
    """
    `responses` is a dict {question_index -> 0..4}.
    Returns aggregated scores, stage and recommendations.
    """
    by_dim_raw: Dict[str, List[int]] = {d: [] for d in DIMENSIONS}
    for idx, (dim, _) in enumerate(QUESTIONS):
        if idx in responses:
            by_dim_raw[dim].append(responses[idx])

    by_dimension = {
        dim: (sum(vals) / (4 * len(vals))) if vals else 0.0
        for dim, vals in by_dim_raw.items()
    }
    overall = sum(by_dimension.values()) / len(by_dimension)

    stage_label = stage_summary = ""
    for thr, label, summary in STAGE_THRESHOLDS:
        if overall < thr:
            stage_label, stage_summary = label, summary
            break

    # Recommendations: the two weakest dimensions get prioritised guidance.
    weakest = sorted(by_dimension.items(), key=lambda kv: kv[1])[:2]
    recos = [_recommendation(dim, sc) for dim, sc in weakest if sc < 0.75]

    return AssessmentResult(
        by_dimension=by_dimension,
        overall=overall,
        stage_label=stage_label,
        stage_summary=stage_summary,
        recommendations=recos,
    )


def _recommendation(dim: str, current: float) -> str:
    library = {
        "data_fabric": (
            "Invest 1 quarter in a data-catalogue + lineage tool (DataHub / Unity Catalog) "
            "and migrate the most-queried tables to an open table format. Target: lineage "
            "coverage ≥ 80% on revenue-critical data within 6 months."
        ),
        "talent": (
            "Create the Evaluation Engineer role explicitly; do not assume it will emerge "
            "from data-science generalists. Hire one before scaling LLM use cases."
        ),
        "mlops": (
            "Deploy an LLM trace store (Langfuse, Phoenix or self-hosted) and a prompt "
            "registry. Without these, you cannot debug regressions or audit cost."
        ),
        "evaluation": (
            "Build a domain gold dataset (200–500 cases). Wire eval-on-PR into CI. This is "
            "the single highest-leverage investment to escape the pilot trap."
        ),
        "governance": (
            "Run an EU AI Act classification workshop with Legal, Risk and Engineering on "
            "every customer-facing product. Output: a high-risk register and a DORA "
            "third-party action plan."
        ),
        "change_mgmt": (
            "Reframe the AI programme as an operating-model redesign, not a tool rollout. "
            "Allocate ≥ 10% of the programme budget to change-management, training, and "
            "exception-review workflows."
        ),
    }
    return f"[{dim}] (current score: {current:.0%}) — {library[dim]}"


# --------------------------------------------------------------------------
# I/O
# --------------------------------------------------------------------------

def interactive() -> Dict[int, int]:
    print("AI Maturity Assessment — answer each statement on 0..4")
    print("  0 = strongly disagree  ·  4 = strongly agree\n")
    responses: Dict[int, int] = {}
    for i, (dim, statement) in enumerate(QUESTIONS):
        while True:
            raw = input(f"[{i+1:02d}/{len(QUESTIONS)}] ({dim}) {statement}\n  > ").strip()
            if raw in {"0", "1", "2", "3", "4"}:
                responses[i] = int(raw)
                break
            print("  please enter an integer between 0 and 4")
    return responses


def from_file(path: Path) -> Dict[int, int]:
    data = json.loads(path.read_text())
    return {int(k): int(v) for k, v in data.items()}


def render_text(result: AssessmentResult) -> str:
    bar = lambda v: "█" * int(round(v * 20)) + "·" * (20 - int(round(v * 20)))
    out = [
        "",
        "=" * 72,
        f"OVERALL MATURITY  {result.overall:.0%}   →   {result.stage_label}",
        f"  {result.stage_summary}",
        "=" * 72,
        "",
        "Per-dimension score:",
    ]
    for dim, label in DIMENSIONS.items():
        s = result.by_dimension[dim]
        out.append(f"  {dim:<14} {bar(s)}  {s:>5.0%}   {label}")
    if result.recommendations:
        out.extend(["", "Top recommendations:"])
        out.extend(f"  {i+1}. {r}" for i, r in enumerate(result.recommendations))
    return "\n".join(out)


def render_radar(result: AssessmentResult, out_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError:
        print("[chart] matplotlib not installed; skipping radar chart.", file=sys.stderr)
        return

    labels = list(DIMENSIONS.keys())
    values = [result.by_dimension[d] for d in labels]
    angles = [n / len(labels) * 2 * math.pi for n in range(len(labels))]
    angles += angles[:1]
    values += values[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.20)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["25%", "50%", "75%", "100%"])
    ax.set_ylim(0, 1)
    ax.set_title(f"AI Maturity — {result.stage_label}", pad=20)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"[chart] saved to {out_path}")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run the AI Maturity Assessment.")
    p.add_argument("--interactive", action="store_true", help="Prompt the user.")
    p.add_argument("--input", type=Path, help="JSON file with {idx:score} responses.")
    p.add_argument("--output", type=Path, default=Path("maturity_report.json"))
    p.add_argument("--chart", type=Path, default=Path("maturity_radar.png"))
    p.add_argument("--no-chart", action="store_true")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.interactive:
        responses = interactive()
    elif args.input:
        responses = from_file(args.input)
    else:
        # Built-in demo: a Stage-3 organisation.
        responses = {i: (3 if i % 3 else 2) for i in range(len(QUESTIONS))}
        print("[demo] running on a synthetic 'Stage-3' organisation\n")

    result = score(responses)
    print(render_text(result))

    args.output.write_text(json.dumps(
        {
            "overall": result.overall,
            "stage": result.stage_label,
            "by_dimension": result.by_dimension,
            "recommendations": result.recommendations,
        },
        indent=2,
    ))
    print(f"\n[json] report written to {args.output}")
    if not args.no_chart:
        render_radar(result, args.chart)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
