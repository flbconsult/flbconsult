"""
Vendor Concentration Risk Index (VCRI)
======================================

Quantitative companion to the paper
*Vendor Concentration Risk in AI Infrastructure — A Governance Framework for 2027*
(`docs/03-vendor-concentration-risk-framework.md`).

Scores an enterprise's dependency on a strategic vendor across six axes:

    1. Switching Cost            (engineering effort + opportunity cost to migrate)
    2. Alternatives Maturity     (how ready are credible competitors; inverted)
    3. Geopolitical Exposure     (sanction risk, export controls, dual-use)
    4. Roadmap Dependency        (reliance on vendor's 2027-2030 R&D trajectory)
    5. Ecosystem Lock-in         (CUDA kernels, custom pipelines, framework gravity)
    6. Exit Time                 (calendar months to achieve full switch)

Aggregates to a Vendor Concentration Risk Index (VCRI) in [0, 30]. The index
is designed to feed DORA Art. 28 registers and Board-level risk documentation
without pretending to false precision.

Usage
-----
    python vendor_concentration_risk.py --preset nvidia-cuda-training
    python vendor_concentration_risk.py --preset openai-llm-exclusive
    python vendor_concentration_risk.py --input my_vendor.json
    python vendor_concentration_risk.py --preset-all

Author: Franck Bongard, 2026.
License: MIT.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

# ---------------------------------------------------------------------------
# Domain types
# ---------------------------------------------------------------------------

AXES: Dict[str, str] = {
    "switching_cost":        "Engineering effort + opportunity cost to migrate to a comparable alternative",
    "alternatives_maturity": "Readiness of credible competitors (inverted — lower maturity = higher risk)",
    "geopolitical_exposure": "Sanction risk, export controls, dual-use classification, home-jurisdiction risk",
    "roadmap_dependency":    "Reliance of 2027-2030 plan on vendor's announced R&D trajectory",
    "ecosystem_lock_in":     "Depth of accumulated proprietary artefacts (CUDA, pipelines, tooling, skills)",
    "exit_time":             "Calendar months to achieve full switch under an emergency scenario",
}

SCORE_BANDS = [
    (7,  "Low",      "Document, review annually."),
    (14, "Medium",   "Document, map to DORA/NIS2 register, review bi-annually, build contractual exit clauses."),
    (20, "High",     "Document in Board risk register, mandate active alternative-building roadmap, contractual audit + exit."),
    (30, "Critical", "Board-level escalation. Material concentration risk. Consider active diversification programmes."),
]


@dataclass
class Vendor:
    name: str
    layer: str  # 'compute' / 'cloud' / 'model-api' / 'developer-tooling' / 'data'
    scores: Dict[str, int] = field(default_factory=dict)
    notes: Dict[str, str] = field(default_factory=dict)
    weights: Dict[str, float] | None = None  # optional per-axis weights

    def axis_value(self, axis: str) -> int:
        return int(self.scores.get(axis, 0))

    def weighted_score(self, axis: str) -> float:
        w = (self.weights or {}).get(axis, 1.0)
        return self.axis_value(axis) * w

    def vcri(self) -> float:
        total_weight = sum((self.weights or {}).get(a, 1.0) for a in AXES)
        if total_weight == 0:
            return 0.0
        raw = sum(self.weighted_score(a) for a in AXES)
        # normalise so a fully-weighted VCRI stays on the 0-30 scale
        normalised = raw * (len(AXES) / total_weight)
        return round(normalised, 1)

    def band(self) -> tuple[str, str]:
        v = self.vcri()
        for threshold, label, guidance in SCORE_BANDS:
            if v <= threshold:
                return label, guidance
        return SCORE_BANDS[-1][1], SCORE_BANDS[-1][2]


# ---------------------------------------------------------------------------
# Preset profiles — illustrative, per paper §4
# ---------------------------------------------------------------------------

PRESETS: Dict[str, Vendor] = {
    "nvidia-cuda-training": Vendor(
        name="NVIDIA / CUDA training stack",
        layer="compute",
        scores={
            "switching_cost":        5,
            "alternatives_maturity": 4,
            "geopolitical_exposure": 3,
            "roadmap_dependency":    5,
            "ecosystem_lock_in":     5,
            "exit_time":             4,
        },
        notes={
            "switching_cost":        "5-10 years of accumulated CUDA skills + kernels",
            "alternatives_maturity": "AMD MI350 competitive raw perf; Google TPU locked to GCP",
            "geopolitical_exposure": "US export controls on high-end GPUs; TSMC fab concentration",
            "roadmap_dependency":    "Enterprise 2028 plans assume Rubin / Rubin Ultra velocity",
            "ecosystem_lock_in":     "CUDA + cuDNN + TensorRT + ONNX pathways",
            "exit_time":             "12-18 months at scale",
        },
    ),
    "hyperscaler-multi-region": Vendor(
        name="Multi-region hyperscaler (AWS primary, Azure secondary)",
        layer="cloud",
        scores={
            "switching_cost":        3,
            "alternatives_maturity": 2,
            "geopolitical_exposure": 3,
            "roadmap_dependency":    2,
            "ecosystem_lock_in":     3,
            "exit_time":             3,
        },
        notes={
            "switching_cost":        "Containerised workloads; Terraform IaC",
            "alternatives_maturity": "Azure + GCP + OCI are credible at enterprise scale",
            "geopolitical_exposure": "US CLOUD Act; EU-US DPF fragility",
            "roadmap_dependency":    "Hyperscaler services broadly compatible across providers",
            "ecosystem_lock_in":     "Managed services (DynamoDB, S3 variants) create friction",
            "exit_time":             "6-12 months at enterprise scale",
        },
    ),
    "openai-llm-exclusive": Vendor(
        name="Single-provider frontier LLM API (hypothetical OpenAI-exclusive)",
        layer="model-api",
        scores={
            "switching_cost":        2,
            "alternatives_maturity": 1,
            "geopolitical_exposure": 3,
            "roadmap_dependency":    4,
            "ecosystem_lock_in":     3,
            "exit_time":             2,
        },
        notes={
            "switching_cost":        "Prompt engineering is portable; code uses abstractions",
            "alternatives_maturity": "Anthropic, Google, Meta, Mistral all production-ready",
            "geopolitical_exposure": "US-based provider; data processing jurisdiction",
            "roadmap_dependency":    "Copilot features priced on GPT-5+ capabilities",
            "ecosystem_lock_in":     "Assistants API, structured outputs, fine-tuning artefacts",
            "exit_time":             "1-3 months for well-architected systems",
        },
    ),
    "eu-sovereign-stack": Vendor(
        name="EU-sovereign stack (OVHcloud + Mistral + Scaleway)",
        layer="cloud+model-api",
        scores={
            "switching_cost":        2,
            "alternatives_maturity": 3,
            "geopolitical_exposure": 1,
            "roadmap_dependency":    4,
            "ecosystem_lock_in":     2,
            "exit_time":             2,
        },
        notes={
            "switching_cost":        "Open-weights models; standard APIs",
            "alternatives_maturity": "Fewer true-sovereign alternatives at frontier capability",
            "geopolitical_exposure": "EU-based, aligned with regulatory home jurisdiction",
            "roadmap_dependency":    "Frontier gap vs. US labs is real and must be accepted",
            "ecosystem_lock_in":     "Mostly open-standard; open-weights preserve portability",
            "exit_time":             "1-3 months",
        },
    ),
    "on-prem-open-source": Vendor(
        name="On-premise open-source stack (Llama + vLLM + Kubernetes)",
        layer="compute+model",
        scores={
            "switching_cost":        1,
            "alternatives_maturity": 1,
            "geopolitical_exposure": 0,
            "roadmap_dependency":    2,
            "ecosystem_lock_in":     1,
            "exit_time":             1,
        },
        notes={
            "switching_cost":        "Fully portable; open weights + standard runtimes",
            "alternatives_maturity": "Multiple open-weight alternatives at any given capability tier",
            "geopolitical_exposure": "Self-hosted; data stays in-perimeter",
            "roadmap_dependency":    "Community roadmap; less single-vendor dependency",
            "ecosystem_lock_in":     "Standard container + orchestration",
            "exit_time":             "< 1 month for most workloads",
        },
    ),
}


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_vendor(v: Vendor) -> str:
    out = ["=" * 92, f"VENDOR: {v.name}", f"Layer : {v.layer}", "=" * 92]
    out.append(f"{'AXIS':<26} {'SCORE':>6}  {'WEIGHT':>7}  NOTE")
    out.append("-" * 92)
    for axis in AXES:
        score = v.axis_value(axis)
        w = (v.weights or {}).get(axis, 1.0)
        note = v.notes.get(axis, "")
        bar = "█" * score + "·" * (5 - score)
        out.append(f"{axis:<26} {score}/5 {bar}  {w:>5.2f}   {note[:48]}")
    out.append("-" * 92)
    band, guidance = v.band()
    out.append(f"  VCRI : {v.vcri():>5.1f} / 30     →  {band}")
    out.append(f"  Guidance : {guidance}")
    out.append("=" * 92)
    return "\n".join(out)


def render_comparison(vendors: List[Vendor]) -> str:
    out = ["", "=" * 92, "COMPARISON (sorted by VCRI descending)", "=" * 92]
    header = f"{'VENDOR':<60} {'LAYER':<20} {'VCRI':>6}  BAND"
    out.append(header)
    out.append("-" * len(header))
    sorted_v = sorted(vendors, key=lambda x: -x.vcri())
    for v in sorted_v:
        band, _ = v.band()
        out.append(f"{v.name[:60]:<60} {v.layer[:20]:<20} {v.vcri():>6.1f}  {band}")
    out.append("=" * 92)
    # concentration summary
    critical = [v for v in vendors if v.vcri() > 20]
    high = [v for v in vendors if 14 < v.vcri() <= 20]
    if critical:
        out.append(f"\n⚠  {len(critical)} vendor(s) in CRITICAL band — Board escalation required")
    if high:
        out.append(f"→  {len(high)} vendor(s) in HIGH band — require documented mitigation plan")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# JSON I/O
# ---------------------------------------------------------------------------

def vendor_from_json(path: Path) -> Vendor:
    data = json.loads(path.read_text(encoding="utf-8"))
    return Vendor(
        name=data["name"],
        layer=data.get("layer", "unknown"),
        scores={k: int(v) for k, v in data.get("scores", {}).items()},
        notes=data.get("notes", {}),
        weights={k: float(v) for k, v in data.get("weights", {}).items()} if "weights" in data else None,
    )


def vendor_to_dict(v: Vendor) -> dict:
    return {
        "name": v.name,
        "layer": v.layer,
        "scores": v.scores,
        "notes": v.notes,
        "weights": v.weights,
        "vcri": v.vcri(),
        "band": v.band()[0],
        "guidance": v.band()[1],
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Vendor Concentration Risk Index (VCRI).")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--preset", choices=list(PRESETS.keys()),
                   help="Run against a named preset profile.")
    g.add_argument("--preset-all", action="store_true",
                   help="Score all preset profiles and print the comparison table.")
    g.add_argument("--input", type=Path,
                   help="Score a vendor described in a JSON file.")
    p.add_argument("--out", type=Path, default=Path("vcri_report.json"),
                   help="Where to write the JSON report (default: ./vcri_report.json).")
    p.add_argument("--list-axes", action="store_true",
                   help="Print the axis definitions and exit.")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.list_axes:
        print("VCRI axes (score each 0–5):\n")
        for axis, desc in AXES.items():
            print(f"  {axis:<26} {desc}")
        return 0

    if args.preset_all:
        vendors = list(PRESETS.values())
        for v in vendors:
            print(render_vendor(v))
            print()
        print(render_comparison(vendors))
        args.out.write_text(
            json.dumps([vendor_to_dict(v) for v in vendors], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\n[json] written to {args.out}")
        return 0

    if args.input:
        v = vendor_from_json(args.input)
    elif args.preset:
        v = PRESETS[args.preset]
    else:
        # Default demo
        v = PRESETS["nvidia-cuda-training"]
        print("[demo] no --preset or --input provided; running on 'nvidia-cuda-training'\n")

    print(render_vendor(v))
    args.out.write_text(
        json.dumps(vendor_to_dict(v), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n[json] written to {args.out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
