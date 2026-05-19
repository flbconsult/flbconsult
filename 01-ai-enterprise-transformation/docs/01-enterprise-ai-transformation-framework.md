# Enterprise AI Transformation Framework
### A pragmatic 5-stage maturity model and six transformation levers

**Author.** Franck Bongard — CIO/CTO, M2 IA Mines-Télécom Paris (2025).
**Status.** Working paper, v1.0, April 2026.
**Audience.** CIO, CTO, COO, transformation directors, board members.

---

## Abstract

Most large-scale enterprise AI programmes underperform [Westerman et al., 2014; McKinsey, 2024]. This paper argues that the root cause is a category error: organisations treat AI adoption as a **technology rollout** when it is in fact a **production-system redesign**. Drawing on field engagements at AP-HP, Vocalcom, Vivoka and KHOME, and on a literature spanning the *Foundation Models* report [Bommasani et al., 2021], the *AI Risk Management Framework* [NIST, 2023], and the empirical work of Brynjolfsson and colleagues [Brynjolfsson et al., 2023], I propose a **5-stage maturity model** and **six transformation levers**. The model deliberately separates *AI-Augmented* (stage 3) from *AI-Native* (stage 5) — a distinction that, in my experience, decides whether the programme produces durable economic value or vanity copilots.

---

## 1. Why most "AI transformations" stall

In every transition I have led — Vocalcom's Move2Cloud (2022), AP-HP's Orbis migration (2024), KHOME's AI-Native pivot (2026) — three failure patterns recur. They are mirrored in the literature:

1. **The pilot trap.** Brynjolfsson et al. [2023] document that early-stage Generative AI deployments often boost productivity by 14% on average but **40% in the lowest-performing quartile**. The temptation is to declare victory and stay in pilot mode. Yet the productivity gains observed in pilots erode without (i) data-pipeline industrialisation, (ii) evaluation harnesses, and (iii) a re-thought operating model. Pilots that don't graduate to a production *system* slowly decay.

2. **Tech-first transformations.** Iansiti and Lakhani [2020] insist that AI-driven competition reshapes the **operating model**, not just the toolset. Most programmes I have audited inverted this — they bought a copilot license, then tried to retrofit business processes around it.

3. **Evaluation deficit.** Liang et al. [2022] (HELM) and Es et al. [2023] (RAGAS) demonstrate that without continuous, multi-dimensional evaluation, LLM-driven systems silently regress. In my experience, **fewer than 1 in 5** enterprise AI deployments have a production evaluation harness on day one. The rest discover hallucinations through customer complaints.

The maturity model below is built to avoid these traps.

---

## 2. The 5-stage maturity model

| Stage | Name | Defining trait | Typical KPI |
|---|---|---|---|
| **0** | AI-Curious | Ad-hoc experimentation by individuals; no IT or legal awareness. | Number of ChatGPT bookmarks. |
| **1** | AI-Sandboxed | Sanctioned playground (private LLM, internal RAG demo). Data still siloed. | # employees with sandbox access. |
| **2** | AI-Augmented (process-level) | One business process re-engineered around an LLM (e.g. ticket triage, RH care management). | Process-level productivity delta (Brynjolfsson et al.'s 14–40% range). |
| **3** | AI-Industrialised | MLOps pipeline, evaluation harness, observability, cost telemetry, security review board. | Mean time to deploy a new model · Drift alerts/month. |
| **4** | AI-Embedded | AI is a product feature exposed to customers; SLA-bound; subject to AI Act / DORA / sectorial regulation. | Hallucination rate on sample · Time-to-mitigate prompt injection. |
| **5** | **AI-Native** | The **operating model itself** is a feedback loop: products generate data → data improves models → better models attract users → larger data flywheel. | Data-flywheel velocity (cf. §3) · % decisions where humans review *exceptions* rather than approve *each*. |

**Three observations.**

- The jump from **Stage 2 → Stage 3** is the most under-funded transition in my experience. It requires investments (MLOps, evaluation, governance) whose ROI is invisible to a P&L-driven CFO. The CIO/CTO must reframe it as **insurance against productivity regression**.
- **Stage 4 ≠ Stage 5.** A bank can embed an LLM-powered chatbot (Stage 4) without ever becoming AI-Native. AI-Native is an *organisational* property, not a technical one.
- The **AI Act** [EU, 2024] and **DORA** [EU, 2022] effectively make Stage 3 governance mandatory for any regulated EU organisation deploying high-risk AI by August 2026.

---

## 3. The six transformation levers

Each lever is necessary; none alone is sufficient.

### 3.1. Data fabric — *the unsexy prerequisite*

Without a unified data-access layer (data warehouse + lake + governance metadata + lineage), every AI use case rebuilds its data pipeline from scratch. The cost compounds. At Agodev (2008–2020), I shipped HDS-compliant SaaS only after rebuilding the data layer with **HL7 FHIR**-aligned schemas. Lesson: build the fabric **before** the use case, even if the use case is the budget justification.

**Reference architecture choices in 2026:**
- Storage: open table formats (Iceberg, Delta, Hudi).
- Governance: OpenLineage + a catalogue (DataHub, Unity Catalog).
- Identity: short-lived credentials, IAM federation, per-table RBAC.

### 3.2. Talent design — *not just hiring*

The labour-market literature [Acemoglu & Restrepo, 2022; Brynjolfsson et al., 2023] suggests Generative AI compresses the productivity gap **between juniors and experts** more than it amplifies it. This has a counter-intuitive implication for AI-Native enterprises: hire fewer, more senior people, and use AI to deliver junior-level throughput. At KHOME, I am restructuring the engineering team along this thesis — fewer roles, broader scope, higher technical density.

**Roles that must exist by Stage 3:**
- A **Head of AI Engineering** distinct from the Head of Data.
- An **AI Risk Officer** (often shared with the CISO in mid-size firms).
- Dedicated **Evaluation Engineers** — a discipline that did not exist in 2022 and which I argue is the *QA of LLM systems*.

### 3.3. MLOps & observability — *the cost of being wrong fast*

Sculley et al. [2015] famously diagnosed the **"hidden technical debt in ML systems"** — most of the system is glue code, configuration, and monitoring, not the model. The 2026 LLM equivalent: most of the system is the **prompt registry, the evaluation harness, the cost telemetry, and the rate-limiting layer**.

A minimum AI-industrialised stack:
- A model-registry (MLflow, Weights & Biases) extended to LLM artifacts (prompt versions + system prompts).
- A trace store (Langfuse, Phoenix) capturing every LLM call.
- A **gold-set evaluation suite** running on every prompt or model change.
- Per-tenant cost telemetry — see Section 03 of this portfolio for the FinOps logic.

### 3.4. Evaluation-first culture

This is the lever most often skipped. RAGAS [Es et al., 2023] formalised the trio *faithfulness · answer-relevancy · context-precision*; HELM [Liang et al., 2022] adds robustness, fairness, calibration. In production, I always extend with three custom evaluators:

- **Domain factuality** — sample-and-verify against a curated source of truth (HDS-validated corpus for healthcare, RICS for KHOME).
- **Prompt-injection resistance** — see Section 02 of this portfolio for the threat model.
- **Cost-per-correct-answer** — reframes accuracy in CFO-readable units.

### 3.5. Governance & regulatory alignment

Stage 4 and beyond are unreachable without a governance answer to:

- **EU AI Act** [EU, 2024] — high-risk classification, conformity assessment, post-market monitoring.
- **DORA** [EU, 2022] for financial entities — ICT third-party risk (an LLM provider *is* a critical third party).
- **NIST AI RMF** [NIST, 2023] as a US-aligned governance baseline.
- Sectorial: **HDS** for French healthcare, **RICS** for real estate (KHOME), **ISO/IEC 42001** as the AI management-system standard.

The CIO/CTO must own this conversation jointly with Legal and Risk. Outsourcing it to compliance is a recipe for a Stage-3 ceiling.

### 3.6. Change management & operating-model redesign

Westerman et al. [2014] and Davenport & Mittal [2023] converge on a single empirical regularity: digital programmes that fund the *people* side at < 10% of programme budget systematically underperform. At AP-HP, the August 2024 dual-datacenter loss was — beyond a technical event — a stress test of the *operating model* of the IT organisation. Continuity held because of pre-existing PCA drills; it would not have held had we been mid-AI-transformation with a half-trained operating model.

---

## 4. Field anti-patterns

Patterns I have observed in 4 separate engagements, named here for diagnostic value:

| Anti-pattern | Symptom | Counter-move |
|---|---|---|
| **The "Demo-Driven Roadmap"** | The roadmap follows the latest vendor demo. Strategy is reactive. | Anchor every line item to a measurable business KPI. |
| **The "Single-Vendor LLM Lock-in"** | Strategic hyperscaler dependency for the model layer. | Multi-provider by design (LangChain / LlamaIndex abstractions, OpenAI + Anthropic + open-weights). See Section 03. |
| **The "Eval-Free Prod"** | LLM in production, no continuous evaluation harness. | Mandatory pre-deployment gate on a domain gold set. |
| **The "Phantom AI-Native"** | The org calls itself AI-Native; KPIs are unchanged. | Define *AI-Native* as a measurable state (Section 5 of this paper). |

---

## 5. Conclusion: from *transformation* to *redesign*

The framework I propose is unapologetically *operational*. It treats AI not as a wave to ride, but as a **structural pressure** that — like cloud-native a decade ago — forces a redesign of how the firm produces value. Stage 5 is not where everyone needs to land. But the firms that do will compete on a **data-flywheel velocity** that latecomers cannot replicate by hiring or by buying.

The Python tools shipped alongside this paper (`ai_maturity_assessment.py`, `rag_pipeline.py`, `llm_evaluation_harness.py`) are deliberate: they make the framework **executable**. A board can audit its own AI maturity in 30 minutes; an engineering team can run the RAG reference architecture in a hour; a risk committee can adopt the evaluation harness as a Stage-3 gate.

---

## References

1. Acemoglu, D., Restrepo, P. (2022). *Tasks, Automation, and the Rise in US Wage Inequality*. Econometrica 90(5).
2. Bommasani, R. et al. (2021). *On the Opportunities and Risks of Foundation Models*. arXiv:2108.07258.
3. Brynjolfsson, E., Li, D., Raymond, L. R. (2023). *Generative AI at Work*. NBER Working Paper 31161.
4. Davenport, T. H., Mittal, N. (2023). *All-in on AI: How Smart Companies Win Big with Artificial Intelligence*. HBR Press.
5. EU. (2022). *Regulation (EU) 2022/2554 — DORA — Digital Operational Resilience Act*.
6. EU. (2024). *Regulation (EU) 2024/1689 — Artificial Intelligence Act*.
7. Es, S. et al. (2023). *RAGAS: Automated Evaluation of Retrieval Augmented Generation*. arXiv:2309.15217.
8. Iansiti, M., Lakhani, K. R. (2020). *Competing in the Age of AI*. HBR Press.
9. ISO/IEC 42001:2023 — *Artificial intelligence — Management system*.
10. Lewis, P. et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. arXiv:2005.11401.
11. Liang, P. et al. (2022). *Holistic Evaluation of Language Models (HELM)*. arXiv:2211.09110.
12. McKinsey & Co. (2024). *The state of AI in early 2024*.
13. NIST. (2023). *AI Risk Management Framework (AI RMF 1.0)*. NIST AI 100-1.
14. Sculley, D. et al. (2015). *Hidden Technical Debt in Machine Learning Systems*. NIPS 2015.
15. Vaswani, A. et al. (2017). *Attention Is All You Need*. arXiv:1706.03762.
16. Westerman, G., Bonnet, D., McAfee, A. (2014). *Leading Digital*. HBR Press.
17. OpenAI. (2024). *Model Spec*. https://cdn.openai.com/spec/model-spec-2024.html.
18. Anthropic. (2024). *Building effective agents*. Technical report.

---

*Citation: Bongard, F. (2026). Enterprise AI Transformation Framework. Working paper. https://github.com/<your-handle>/franck-bongard*
