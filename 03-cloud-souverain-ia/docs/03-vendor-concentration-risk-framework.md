# Vendor Concentration Risk in AI Infrastructure
### A six-axis governance framework for Boards and CTOs — 2027 edition

**Author.** Franck Bongard — CIO/CTO, M2 IA Mines-Télécom Paris, ISO 27005 Risk Manager.
**Status.** Working paper, v1.0, November 2026.
**Audience.** CIO, CTO, Board members, Risk and Audit committees, Investment committees.

---

## Abstract

The NVIDIA CEO transition of November 12, 2026 made visible, to Boards, what CTOs have known for three years: **concentration risk on AI infrastructure is now a governance-level issue, not a technology-choice issue**. The vulnerability pre-existed Jensen Huang's departure; what changed on that date is its political salience. This paper argues that the classical vendor lock-in literature [Shapiro & Varian, 1999; Williamson, 1985] is a necessary but insufficient framing for AI infrastructure, which layers three new dimensions on top of the classical ones: an **ecosystem-effect** (CUDA, proprietary training pipelines, framework gravity), a **geopolitical layer** (export controls, sanction risk, dual-use classification), and a **roadmap-dependency** (performance expectations priced into enterprise plans assume vendor R&D velocity). I propose a six-axis **Vendor Concentration Risk Index (VCRI)** scoring framework, implemented in Python, that produces evidence defensible under **DORA Art. 28-30**, **NIS2 Art. 21**, **EU AI Act Art. 25**, and **the EU Data Act Chapter VI** on cloud-service switching. The framework is applied to four stylised stacks (NVIDIA/CUDA, hyperscaler-multi-region, single-provider LLM, EU-sovereign) and used to formulate three operating doctrines for 2027.

---

## 1. Why November 2026 matters — the governance event, not the news event

The resignation of Jensen Huang as CEO of NVIDIA, following reports of a personal scandal with a geopolitical dimension [NVIDIA, 2026; SEC, 2026], moved the stock 8% over two sessions and triggered a petition for his reinstatement that collected 170 000 signatures in 72 hours. The reporting focused on personality. The strategic question is elsewhere.

The strategic question, for the hundreds of enterprise CIOs now re-reading their AI infrastructure plans, is this: **what fraction of our 2027-2030 AI roadmap is implicitly priced on the assumption that a single founder-CEO continues to make generational bets on our behalf?** The answer, at most CAC 40 and Fortune 500 firms, is uncomfortable. The uncomfortable part is not NVIDIA-specific — it is structural. Every layer of the modern enterprise AI stack is dominated by one, or at most two, vendors:

- **Compute**: NVIDIA for training; NVIDIA + a thin tail of AMD / Google TPU / AWS Trainium for inference.
- **Cloud**: AWS, Azure, GCP for ~70% of workloads; a fourth-place scramble between Oracle, IBM, and sovereign EU providers for the remainder.
- **Foundation models**: OpenAI, Anthropic, Google DeepMind, Meta (open-weights) — a four-way oligopoly at the frontier, with Mistral and a handful of Chinese labs in the second tier.
- **Developer tools**: GitHub Copilot, Cursor, and a very long tail of specialised tools.

Each layer, individually, could be defended as a reasonable market structure. **Stacked**, they produce chains of dependency where a single vendor transition in any one layer propagates through the whole enterprise plan.

The literature has warned about this for decades. The regulation has mandated its documentation since January 2025 (DORA). The event of November 12, 2026 removed the last excuse of "it's hypothetical".

---

## 2. What the classical literature does — and does not — tell us

### 2.1 The three foundational texts

**Shapiro & Varian** [1999, *Information Rules*] remains the canonical treatment of lock-in and switching cost. They identify seven lock-in types (contractual, durable-equipment, brand-specific, search costs, loyalty, learning, information-and-database). All seven apply to modern AI infrastructure. The CUDA ecosystem, in particular, is a textbook case of their **"learning lock-in"** compounded by **"information-and-database lock-in"**: once your ML team has spent 5 years in CUDA, retooling to ROCm or XLA is not a matter of licensing fees but of talent re-training and model re-validation.

**Williamson** [1985, *The Economic Institutions of Capitalism*] frames vendor relationships through **transaction cost economics**. His three dimensions — asset specificity, uncertainty, and frequency — map directly onto AI infrastructure:

- **Asset specificity**: a model fine-tuned on NVIDIA hardware with CUDA kernels is a *site-specific asset* in Williamson's sense.
- **Uncertainty**: AI roadmaps have multi-year horizons and vendor R&D velocity is opaque.
- **Frequency**: unlike one-off capital goods, inference workloads are continuous — the vendor relationship is quasi-permanent.

Williamson's conclusion — that high asset specificity + high uncertainty should push the governance mode towards vertical integration or very strong contractual safeguards — translates for AI buyers into: **either internalise critical infrastructure (unlikely except for hyperscalers), or build contractual safeguards that explicitly address switching, exit, and roadmap dependency**.

**Carr** [2003, *IT Doesn't Matter*] argued that infrastructure technology eventually commoditises and ceases to confer competitive advantage. The Carr thesis is important here because it was *empirically correct for most IT infrastructure between 2000 and 2020* — storage, networking, compute, even cloud at the IaaS layer did commoditise. **Applied to AI infrastructure in 2026, however, Carr's thesis is wrong — or at least premature.** Foundation models, GPU architectures, and ML developer tooling are getting *more* differentiated, not less. CUDA gained share over ROCm between 2020 and 2026. OpenAI's API moat widened against open-weights alternatives during the same period. The economic gravity of the AI infrastructure layer is, for now, pointing the other way.

### 2.2 What classical theory misses

Three phenomena specific to AI infrastructure are under-treated or absent from the classical literature:

**(a) The ecosystem effect.** CUDA is not merely a programming interface — it is a 20-year accumulation of libraries (cuDNN, cuBLAS, TensorRT), training materials, StackOverflow answers, open-source models with CUDA-specific optimisations, and university courses. The switching cost is not the sum of individual developer re-training events; it is the sum *plus* a collective knowledge-base depreciation that no single customer can avoid by hiring aggressively.

**(b) The geopolitical layer.** In the Shapiro-Williamson era, vendor risk was largely commercial. In 2026, vendor risk includes: US export controls on high-end GPUs to China (and their periodic revisions), the EU Chips Act and its sovereign-production implications, CFIUS reviews on acquisitions of AI firms, and — as the November 12 event made vivid — the possibility that a vendor leadership change itself has a geopolitical dimension. **Geopolitics is not a risk modifier; it is a separate axis.**

**(c) The roadmap-dependency.** A classical vendor relationship is largely about today's product. An AI infrastructure relationship is substantially about **the vendor's R&D trajectory 18-36 months out**. An enterprise that priced its 2028 AI plans on NVIDIA Rubin Ultra is exposed not to NVIDIA's current performance but to NVIDIA's execution velocity over the next 24 months. This is a Williamson-style uncertainty, but of unusually high magnitude: a 20% shortfall in Rubin Ultra performance vs. roadmap translates, at scale, to tens of millions of euros in re-architecture cost or deferred use-cases.

---

## 3. The VCRI framework — six axes

I propose scoring each strategic vendor dependency on six axes, each rated 0 to 5:

| # | Axis | What it measures | Score 0 = low risk · Score 5 = critical |
|---|---|---|---|
| **1** | **Switching Cost** | Engineering effort + opportunity cost to migrate to a comparable alternative | 0 = portable standards · 5 = deep rewrites + retrained models + re-validated production |
| **2** | **Alternatives Maturity** | How ready are credible competitors to absorb the workload (inverted: lower maturity = higher risk) | 0 = multiple mature equivalents · 5 = no credible alternative at your scale |
| **3** | **Geopolitical Exposure** | Sanction risk, export-control exposure, dual-use classification, home-jurisdiction risk | 0 = neutral · 5 = acute sanction or export-control risk |
| **4** | **Roadmap Dependency** | Your 2027-2030 business plan's reliance on this vendor's announced trajectory | 0 = plan holds with current generation · 5 = plan is priced on next-gen performance |
| **5** | **Ecosystem Lock-in** | Depth of accumulated proprietary artefacts (CUDA kernels, custom training pipelines, framework-specific tooling, developer skills, data pipelines) | 0 = open standards throughout · 5 = multi-year proprietary accumulation |
| **6** | **Exit Time** | Calendar time to achieve full switch under an emergency scenario | 0 = < 1 month · 5 = > 24 months or practically infeasible |

The aggregate **Vendor Concentration Risk Index (VCRI)** is the weighted sum. For most enterprises, equal weights (1/6 each) produce a defensible first estimate. Industry-specific weights may apply: regulated finance may over-weight axes 3 and 6; defence industries may over-weight axis 3; pure consumer SaaS may over-weight axes 1 and 2.

### 3.1 Scoring bands

The VCRI index sits between 0 and 30 (sum of six axes × max 5). Interpretation bands:

- **0–7 — Low risk.** Document, review annually.
- **8–14 — Medium risk.** Document, map to DORA/NIS2 register, review bi-annually, build contractual exit clauses.
- **15–20 — High risk.** Document in Board risk register, mandate active alternative-building roadmap, ensure contractual audit + exit, consider workload portability investments.
- **21–30 — Critical.** Board-level escalation. Treat as material concentration risk for financial disclosures where applicable. Consider active diversification programmes, insurance, or strategic supplier development.

The bands are deliberately wide — the point of the VCRI is not to produce false precision, but to make concentration risk **conversable at Board level** on a consistent scale across the firm's AI stack.

### 3.2 What the framework deliberately does *not* do

- It does not weight axes by financial exposure (this belongs in the enterprise risk register and may be done upstream).
- It does not capture time-varying risk (a vendor whose geopolitical exposure jumps in 72 hours — see November 2026 — requires re-scoring).
- It does not substitute for qualitative judgment on strategic fit. A high-VCRI vendor may be the correct choice if the alternative is not building the capability at all.

---

## 4. Applying VCRI — four stylised case studies

Executable in `code/vendor_concentration_risk.py`.

### 4.1 Case A: NVIDIA / CUDA training stack

| Axis | Score | Rationale |
|---|---:|---|
| Switching Cost | 5 | CUDA kernels + 5-10 years of accumulated ML team skills |
| Alternatives Maturity | 4 | AMD MI350 competitive on raw perf but fragmented ecosystem; Google TPU locked to GCP |
| Geopolitical Exposure | 3 | US export controls on high-end GPUs; fab concentration in Taiwan/TSMC |
| Roadmap Dependency | 5 | Most enterprise 2028 plans assume Rubin/Rubin Ultra velocity |
| Ecosystem Lock-in | 5 | CUDA + cuDNN + TensorRT + ONNX pathways |
| Exit Time | 4 | 12-18 months at scale |
| **VCRI** | **26 / 30** | **Critical** |

Interpretation: Board-level concentration risk. The November 2026 CEO transition is a low-magnitude trigger that nonetheless makes the score *visible*. The mitigation path is not "replace NVIDIA" — it is to maintain a credible switch option by investing in a minority second-vendor stack (AMD or TPU) for at least 10-20% of workloads, establishing operational familiarity before necessity.

### 4.2 Case B: Multi-region hyperscaler compute (AWS primary, Azure secondary)

| Axis | Score | Rationale |
|---|---:|---|
| Switching Cost | 3 | Containerised workloads; IaC in Terraform |
| Alternatives Maturity | 2 | Azure + GCP + OCI are credible alternatives at enterprise scale |
| Geopolitical Exposure | 3 | US CLOUD Act exposure; EU-US DPF fragility |
| Roadmap Dependency | 2 | Hyperscaler services generally compatible across providers |
| Ecosystem Lock-in | 3 | Managed services (DynamoDB, S3 variants) create real friction |
| Exit Time | 3 | 6-12 months at enterprise scale |
| **VCRI** | **16 / 30** | **High** |

Interpretation: Classical hyperscaler concentration. Elevated by CLOUD Act exposure, but mitigable by: EU-only residency enforcement, BYOK, documented exit plans, and portable architectural patterns. A well-governed multi-hyperscaler stack can bring this to 10-12 in 24 months.

### 4.3 Case C: Single-provider frontier LLM API (hypothetical OpenAI-exclusive)

| Axis | Score | Rationale |
|---|---:|---|
| Switching Cost | 2 | Prompt engineering is portable; most code uses abstractions |
| Alternatives Maturity | 1 | Anthropic, Google, Meta, Mistral all production-ready |
| Geopolitical Exposure | 3 | US-based provider; data processing jurisdiction |
| Roadmap Dependency | 4 | Many copilot features priced on GPT-5+ capabilities |
| Ecosystem Lock-in | 3 | Assistants API, structured outputs, fine-tuning artefacts |
| Exit Time | 2 | 1-3 months for well-architected systems |
| **VCRI** | **15 / 30** | **High** (borderline critical on roadmap dependency axis) |

Interpretation: The surprise is that *a single-vendor LLM dependency scores lower than a CUDA stack* on this framework. Why? Because LLM alternatives are credible and switching is engineering-cheap. The real risk is roadmap-dependency: enterprises that built workflows priced on a specific vendor's 2027 capabilities are exposed to that vendor's execution velocity. Mitigation: provider-agnostic abstractions (LangChain, LlamaIndex, custom routers), continuous evaluation on multiple providers (cf. the evaluation harness in section 01 of this portfolio).

### 4.4 Case D: EU-sovereign stack (OVHcloud + Mistral + Scaleway)

| Axis | Score | Rationale |
|---|---:|---|
| Switching Cost | 2 | Open-weights models; standard APIs |
| Alternatives Maturity | 3 | Fewer true-sovereign alternatives at frontier capability |
| Geopolitical Exposure | 1 | EU-based, aligned with regulatory home jurisdiction |
| Roadmap Dependency | 4 | Frontier gap vs. US labs is real and must be accepted |
| Ecosystem Lock-in | 2 | Mostly open-standard; open-weights preserve portability |
| Exit Time | 2 | 1-3 months |
| **VCRI** | **14 / 30** | **High** |

Interpretation: Lower on geopolitics, higher on roadmap-dependency. The EU-sovereign choice trades geopolitical risk for execution-velocity risk. The trade is defensible for workloads where data residency or sovereignty-posture dominates the total value calculation; it is harder to defend for use-cases where model-capability is the primary driver. **The VCRI framework surfaces the trade-off rather than pretending it doesn't exist.**

---

## 5. Governance mapping — how the VCRI feeds existing registers

A VCRI score is useful only if it feeds existing governance artefacts. Mapping for a European enterprise:

### 5.1 DORA (Regulation (EU) 2022/2554)

- **Art. 28 — ICT third-party risk management.** VCRI entries ≥ 15 should appear in the firm's Register of Information with concentration risk explicitly flagged.
- **Art. 29 — Pre-contractual assessment.** New vendor onboarding requires VCRI scoring as part of the due-diligence pack.
- **Art. 30 — Contractual provisions.** Vendors with VCRI ≥ 15 require full Art. 30 clauses (audit rights, exit assistance, subcontracting controls, location of data processing, service levels, resilience testing cooperation). Vendors with VCRI 21+ should additionally require **transition services** of defined duration — typically 6-12 months of post-termination support.
- **Register submission.** The DORA Register of Information (template ESA) submitted annually to the ACPR in France should include VCRI scoring as an internal column, even though it is not a regulatory field — this is defensive documentation for the next audit.

### 5.2 NIS2 (Directive (EU) 2022/2555)

- **Art. 21(2)(d) — supply chain security** explicitly requires consideration of "the quality and resilience of products and services". VCRI provides a quantified input.
- **Art. 21(3) — essential and important entities.** The incident-reporting obligations apply to significant disruptions at critical suppliers. High-VCRI entries should have pre-defined notification workflows.

### 5.3 EU AI Act (Regulation (EU) 2024/1689)

- **Art. 25 — obligations of providers of general-purpose AI models.** Downstream deployers relying on a GPAI provider inherit certain obligations and risks. Documenting concentration on a single GPAI provider via VCRI supports both internal governance and contractual negotiation.
- **Art. 72 — post-market monitoring.** For high-risk AI systems, a VCRI entry for the underlying model provider is a prudent addition to the post-market monitoring plan.

### 5.4 EU Data Act (Regulation (EU) 2023/2854)

- **Chapter VI — switching between data processing services.** As of September 2027, cloud providers must support customer switching with reduced technical and contractual barriers. VCRI scoring of cloud dependencies, combined with documented exit plans, is the evidence that the firm has implemented the Chapter VI expectations. Non-prepared firms will discover the Chapter VI obligations as audit findings, not as competitive opportunities.

### 5.5 Sectorial — financial services

- **EBA/GL/2019/02** on outsourcing arrangements already requires criticality classification and contingency planning. VCRI integrates cleanly as the "concentration" metric.
- **ECB Guide to internal models** requires model risk documentation. Model risk and infrastructure risk intersect at the vendor layer; VCRI makes the intersection explicit.

---

## 6. Three doctrines for 2027

### 6.1 Doctrine 1 — Document concentration before the audit discovers it

The most common pattern in 2024-2026 audit findings is **"concentration risk unacknowledged in governance documentation"**. The remediation is cheap and the delta is large: a 30-page document, scored with a framework like VCRI, moves the file from "finding" to "monitored risk". The November 12, 2026 event will accelerate audit attention on AI infrastructure specifically. Firms that are first to produce VCRI-style documentation will defer scrutiny; firms that wait will be asked to produce the same documentation under audit timeline pressure.

### 6.2 Doctrine 2 — Build switching capability, not just contractual exit

Contractual exit clauses are easy to draft and nearly worthless in practice. Moving 200 production models from CUDA to ROCm in 90 days under audit pressure, with no prior operational experience, is not a plan — it is a hope. The defensible form of concentration-risk mitigation is **maintained operational capability on an alternative stack at 10-20% of workload volume**. This is not cheap; it may add 15-25% to AI infrastructure cost. The right framing to Boards: the cost is purchasing optionality on a quantified risk, not paying for redundant infrastructure. This framing has survived several financial crises (operational resilience spend is a cost of being in business for regulated firms) — it should survive AI infrastructure concentration too.

### 6.3 Doctrine 3 — Treat geopolitics as a separate axis, not a modifier

The strongest conclusion from the November 12, 2026 event is that geopolitical risk on AI infrastructure is no longer reducible to a "regulatory environment" item in a risk register. The classes of events that may materialise in 2027-2028 — export control revisions, CFIUS blocks on acquisitions, dual-use re-classifications, sanction actions, intelligence-community interventions — are **different in kind** from commercial vendor risk. They can crystallise in days, not quarters. They cannot be mitigated by contractual means. They require, instead, pre-positioned alternatives on different jurisdictional footings. Firms with EU-sovereign fallback capability for at least a minority of workloads will find themselves optionality-rich in a crisis; firms without will discover that rapid repatriation plans do not survive first contact with operational reality.

---

## 7. Conclusion

The NVIDIA CEO transition of November 2026 is, strategically, a modest event. The company's technical moat is structural, its roadmap is three generations deep in silicon, and its leadership transition is being handled with institutional competence [NVIDIA, 2026]. **The event matters because it made abstract risk conversable in terms that Boards understand.**

For CTOs, the right response is neither panic nor dismissal. It is to produce, within the next two to three quarters, **documented VCRI scoring for all strategic AI infrastructure dependencies**, integrated into existing DORA / NIS2 / sectorial registers, and backed by **operational switching capability** (not merely contractual exit clauses) for the entries that score high or critical. The Python tool shipped with this paper is a starting point — it is deliberately minimal (200-250 lines, no external dependencies, auditable), designed to be run in a Board workshop rather than a data-science notebook.

The underlying thesis of this portfolio is that cloud and AI infrastructure co-evolution [cf. paper 02 in this section] produces a 2027 landscape where **the infrastructure layer is the strategic layer**. Concentration risk is the first consequence of that thesis. The CTOs who treat it as a governance discipline, not a vendor-negotiation tactic, will spend the next five years building optionality. The others will spend them explaining to Boards why they did not.

---

## References

1. Carr, N. (2003). *IT Doesn't Matter*. Harvard Business Review, 81(5).
2. EBA/GL/2019/02 — *Guidelines on outsourcing arrangements*.
3. EU. (2022). *DORA — Regulation (EU) 2022/2554*.
4. EU. (2022). *NIS2 — Directive (EU) 2022/2555*.
5. EU. (2023). *Data Act — Regulation (EU) 2023/2854*.
6. EU. (2024). *AI Act — Regulation (EU) 2024/1689*.
7. Hirschman, A. O. (1945). *National Power and the Structure of Foreign Trade*. University of California Press. [Original source of the HHI concentration index.]
8. Iansiti, M., Levien, R. (2004). *The Keystone Advantage*. Harvard Business Review Press.
9. NIST. (2023). *AI Risk Management Framework 1.0*. NIST AI 100-1.
10. NIST. (2024). *Cybersecurity Framework 2.0*. NIST CSWP 29.
11. NVIDIA Corporation. (2026, November 12). *NVIDIA Announces CEO Transition*. Press release.
12. OECD. (2023). *Cross-border data flows and digital sovereignty*.
13. SEC. (2026, November 12). *NVIDIA Corporation — Form 8-K*. EDGAR filing.
14. Shapiro, C., Varian, H. R. (1999). *Information Rules: A Strategic Guide to the Network Economy*. Harvard Business School Press.
15. Williamson, O. E. (1985). *The Economic Institutions of Capitalism*. Free Press.

---

*Citation: Bongard, F. (2026). Vendor Concentration Risk in AI Infrastructure — A Governance Framework for 2027. Working paper. https://github.com/flbconsult/flbconsult/blob/main/03-cloud-souverain-ia/docs/03-vendor-concentration-risk-framework.md*
