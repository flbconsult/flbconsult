# How AI Reshapes Cloud Architecture
### Co-evolution of cloud and AI workloads, 2022–2026

**Author.** Franck Bongard — CIO/CTO.
**Status.** Working paper, v1.0, April 2026.

---

## Abstract

Generative AI is not just *another workload* on cloud infrastructure — it is a forcing function that reshapes the cloud's economic and architectural assumptions. This paper documents four shifts visible from the field: (1) **GPU economics** displace CPU economics as the dominant cost line; (2) **inference networks** displace data-warehouse pipelines as the critical latency surface; (3) **data gravity** intensifies — but on *retrieval indexes and caches*, not on warehouses; (4) **FinOps for LLMs** is a new discipline, not an extension of the old one. I argue that these shifts justify revisiting the make-or-buy and the sovereign-vs-hyperscaler decisions every 12 months in 2026, instead of every 3 years as was customary.

---

## 1. GPU economics displace CPU economics

For the last fifteen years, cloud cost was a CPU + storage + egress story. In 2026, for any AI-augmented enterprise, **GPU spend is the largest line item**, ahead of compute or storage in roughly half of the engagements I have audited.

Empirical observations:

- The price-performance curve of GPU inference has improved ~10× per 18 months (per Hoffmann et al., 2022, and operational reports from major hyperscalers, 2023–2025).
- But **inference volume has grown faster than that price-performance**, so absolute spend has *increased* despite per-token cost dropping.
- Reserved capacity (1-year and 3-year) on H100/H200 / equivalent is sold out 6–12 months in advance with major providers.

**Architectural implication.** Cloud architecture decisions that used to be CPU-driven (instance family, region selection, cost optimisation) are now GPU-driven. A region selection that ignored GPU availability in 2022 was acceptable; in 2026 it determines whether a roadmap is achievable.

**Field illustration.** At KHOME, the architectural decision to keep a critical AVM workload on a hyperscaler was driven primarily by GPU availability for batch evaluation runs, not by the data-residency calculation alone. Sovereign providers in 2026 do not yet match hyperscalers on GPU SLAs.

---

## 2. Inference networks displace data-warehouse pipelines as the critical surface

Pre-2022 cloud architecture revolved around the data warehouse: ELT pipelines, batch jobs, BI dashboards. The latency-critical path was *data → warehouse → dashboard*.

Post-2024, in any AI-Augmented enterprise, the latency-critical path is **user request → retrieval index → LLM provider → user response**. Engineering attention shifts from Airflow DAGs to **inference routers, retry policies, prompt caches, structured output validators**.

**Implication for cloud spend.** A line of cost — *LLM API calls* — that did not exist in 2022 is, in 2026, frequently 30–50% of a SaaS company's hosted-services bill. Containing it requires (a) per-tenant cost telemetry, (b) caching, (c) routing across providers, (d) model right-sizing. See `code/llm_finops_optimizer.py`.

---

## 3. Data gravity migrates to indexes and caches

The "data gravity" thesis (Dave McCrory, 2010) said that as data accumulates in one location, the cost of moving applications elsewhere grows. In 2026, the gravity has migrated **from the warehouse to the retrieval index and the prompt cache**.

Concretely:

- Embedding indexes (vector DBs) become the new lock-in. Re-embedding a 10 TB corpus on a different model costs significant compute and time.
- Prompt caches (Anthropic, OpenAI) reduce cost 2–10× and create a *behavioural* lock-in: the latency benefit is real, hard to reproduce on a different provider, and visible to end-users.

**Implication.** Reversibility planning in 2026 must specifically address: (i) embedding portability (compute + time + cost), (ii) prompt-cache loss penalties on migration, (iii) fine-tuned model artifact transfer.

---

## 4. FinOps for LLMs is a new discipline

Classical FinOps (the FinOps Foundation framework) was built for predictable, instance-level pricing. LLM workloads have three properties that break the classical playbook:

- **Per-call non-determinism**: token counts vary per call, even for "the same" use case. Budgets are statistical, not allocative.
- **Quality-cost trade-off**: choosing GPT-class vs Claude-class vs open-weights changes both quality and cost in non-linear ways.
- **Self-similar cost structure**: agentic systems can recursively call themselves, generating cost-amplification scenarios that classical autoscaling does not anticipate.

The Python tool `code/llm_finops_optimizer.py` materialises three new disciplines: (1) **per-tenant token-budget rate limits**, (2) **provider routing** by quality + cost + residency, (3) **alerting on cost anomalies**.

**Field reference.** Vocalcom's €210k/yr saving (2022) was achieved on classical FinOps levers (right-sizing, reserved instances, region optimisation). The 2026 equivalent — for a SaaS company spending 30% of its bill on LLM APIs — would require LLM-specific FinOps to land similar savings.

---

## 5. Implications for the make-or-buy decision

These four shifts affect the make-or-buy in three counterintuitive ways:

| Shift | Effect on make-or-buy |
|---|---|
| GPU economics displace CPU | Argues *against* in-house training (hyperscaler GPU prices fall faster than amortisation of in-house clusters). |
| Inference networks dominate latency | Argues *for* multi-provider abstraction layers (LangChain, LlamaIndex, custom router) — the abstraction has measurable ROI. |
| Data gravity in indexes & caches | Argues *for* keeping the embedding layer portable, with periodic re-embedding drills as part of PCA/PRA. |
| FinOps for LLMs | Argues *for* hiring or developing LLM FinOps as a dedicated practice — generic FinOps engineers under-perform on this workload. |

---

## 6. Three forecasts for 2026–2028

I make these forecasts cautiously, with the standard caveat that AI infrastructure economics are unstable.

1. **Inference cost will fall 5–10× more by end-2027**, but the bill will not. New use cases are absorbing the savings. CFOs who plan budgets on a "deflation hypothesis" will be wrong.
2. **Sovereign-cloud GPU offerings will close part of the gap with hyperscalers but not all of it**. Expect Archetype-A workloads to remain on sovereign for regulation reasons, while Archetype-C workloads stay on hyperscalers for economics — and the middle ground (Archetype B) to be where the political battle plays out.
3. **EU AI Act extraterritoriality will create a new contractual layer** between LLM providers and EU enterprises — a *DORA-for-AI* by 2027–2028, formalising the third-party assertions that today are negotiated bilaterally.

---

## 7. Conclusion

The cloud and AI infrastructure stacks are no longer separable. A 2026 cloud strategy that does not explicitly model GPU economics, inference networks, data gravity on indexes, and LLM-specific FinOps is a 2022 strategy with a 2026 label. The toolkit shipped with this section — sovereign-cloud decision, FinOps optimiser, residency analyser — is built to make that strategy explicit, defensible to a Board, and revisable annually.

---

## References

1. Anthropic. (2024). *Claude pricing & prompt caching*. Public documentation.
2. ANSSI. (2024). *Référentiel SecNumCloud v3.2*.
3. EU. (2024). *AI Act — Regulation (EU) 2024/1689*.
4. EU. (2023). *Data Act — Regulation (EU) 2023/2854*.
5. FinOps Foundation. (2024). *FinOps Framework v2024*.
6. Gartner. (2024). *Magic Quadrant for Strategic Cloud Platform Services*.
7. Hoffmann, J. et al. (2022). *Training Compute-Optimal Large Language Models*. arXiv:2203.15556.
8. Kaplan, J. et al. (2020). *Scaling Laws for Neural Language Models*. arXiv:2001.08361.
9. McCrory, D. (2010). *Data Gravity in the Clouds*. Technical note.
10. McKinsey. (2024). *State of AI in early 2024*.
11. NIST. (2024). *Cybersecurity Framework 2.0*.
12. Patterson, D. et al. (2021). *Carbon Emissions and Large Neural Network Training*. arXiv:2104.10350.
13. Schwartz, R. et al. (2020). *Green AI*. Communications of the ACM.
14. World Economic Forum. (2024). *Future of Jobs Report*.

---

*Citation: Bongard, F. (2026). How AI Reshapes Cloud Architecture. Working paper.*
