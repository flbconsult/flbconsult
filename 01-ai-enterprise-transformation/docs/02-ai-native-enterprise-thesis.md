# What is an AI-Native Enterprise?
### A definition, three diagnostic tests, and a comparison with cloud-native

**Author.** Franck Bongard — CIO/CTO, Member of the *HUB France IA* Healthcare Committee.
**Status.** Thesis paper, v1.0, April 2026.

---

## Abstract

The term *AI-Native* has, in 2026, suffered the same fate as *cloud-native* did circa 2018: it is invoked everywhere, defined nowhere, and increasingly used as a marketing layer over operationally conventional firms. This paper proposes a **non-marketing definition**: an *AI-Native* enterprise is one whose **operating model**, **data architecture**, and **decision rights** were redesigned so that learning systems are not a service consumed by humans, but a **production substrate** through which value is created. I derive three diagnostic tests, and I compare the AI-Native transition to the prior cloud-native and mobile-first transitions to ground expectations on duration, capex, and organisational pain.

---

## 1. Why a definition matters

In 2018, *cloud-native* was diluted by vendors selling lift-and-shift as transformation. The Cloud Native Computing Foundation eventually settled the matter with a precise definition (containers + microservices + immutable infra + declarative APIs). Until that definition existed, CIOs paid for "cloud-native programmes" that were, on inspection, virtual-machine consolidations.

The same dilution is now affecting *AI-Native*. In KHOME and People First engagements, I have repeatedly observed organisations describe themselves as *"AI-first"* or *"AI-Native"* while their actual production system is:

- A monolith with a chatbot bolted on.
- A data warehouse with one ML model running monthly.
- A fleet of LLM API calls without any evaluation harness.

These organisations are AI-Augmented at best (Stage 2 of the maturity model in [the framework paper](./01-enterprise-ai-transformation-framework.md)). The risk of mis-labelling them is not semantic — it is strategic: leadership over-estimates the firm's defensive position against competitors who *are* AI-Native.

---

## 2. A definition

> An **AI-Native enterprise** is one in which:
>
> 1. **Decision rights** have been redesigned so that, for at least one core value-producing process, *humans review exceptions* rather than approve every instance.
> 2. **Data flow** is organised as a closed loop: products generate data → data trains/evaluates models → improved models change product behaviour → behaviour generates new data. The loop's velocity is a board-level KPI.
> 3. **Software-engineering practice** treats *prompts*, *evaluation suites*, and *model artifacts* as first-class versioned objects under MLOps governance — equivalent in dignity to source code and database schemas.

This is restrictive on purpose. By this definition, **most BigTech firms** are AI-Native; **most banks** are not (yet); **most healthcare systems** are explicitly forbidden by regulation from reaching condition (1) without a human-in-the-loop, and therefore can at most be *AI-Embedded* (Stage 4) — a perfectly defensible position.

---

## 3. Three diagnostic tests

I have used these in due-diligence engagements; each can be answered in a 60-minute conversation with the head of engineering.

### Test 1 — *The 30-day-removal test*

> *If we removed all LLM/ML services for 30 days, which products would degrade — and by how much?*

An AI-Native firm cannot answer "none" or "marginal degradation". The Netflix-recommendation thought experiment (Iansiti & Lakhani, 2020) is the canonical example: remove the recommendation engine for 30 days and the firm's churn metric breaks. AI is not a feature, it is a dependency.

### Test 2 — *The eval-on-PR test*

> *Does every production change to a prompt, model, or retrieval pipeline trigger an automated evaluation suite before merge?*

A "no" here means the firm is at most Stage 3 in description but Stage 2 in practice. Without eval-on-PR, the firm is one bad merge away from a quality regression visible to customers.

### Test 3 — *The exception-handling test*

> *In your most AI-driven workflow, what fraction of cases are reviewed individually by a human?*

If the answer is ≥ 70%, the firm has automated the cosmetic part of the workflow and the human is still doing the work. If the answer is ≤ 5–10% (and the cases reviewed are *exceptions* — uncertain, contested, regulated), the workflow is AI-Native.

---

## 4. AI-Native vs cloud-native: what's the same, what's different

| Dimension | Cloud-Native (2014–2020) | AI-Native (2024–2030) |
|---|---|---|
| Trigger technology | Containers, Kubernetes, IaC | Foundation models, RAG, agentic frameworks |
| Operating-model shift | Dev → DevOps | Product/Eng → Eval-driven product engineering |
| Critical new role | SRE | Evaluation engineer + AI risk officer |
| Failure mode (early) | Lift-and-shift "fake cloud-native" | Chatbot-on-monolith "fake AI-native" |
| Capex curve | Predictable (well-known unit economics) | **Unstable** — inference cost down 10× / 18 months but volume up faster |
| Regulatory backdrop | Data residency, GDPR | EU AI Act, DORA, NIST AI RMF, ISO/IEC 42001 |
| Time-to-mature | ~6 years observed for incumbents | Plausibly 4–7 years; compressed by foundation-model leverage |

**Two important asymmetries:**

- *AI-Native is harder to fake long-term.* The data-flywheel either exists or it doesn't. You can ship containers without microservices; you cannot fake a feedback loop that compounds. The market eventually punishes pretenders.

- *AI-Native is more politically loaded.* AI Act, DORA, sectorial regulation, and reputational risk turn every transition decision into a multi-stakeholder negotiation. CIOs/CTOs who succeeded cloud-native by stealth will not succeed AI-Native by stealth.

---

## 5. Three sectorial reads

### Healthcare (AP-HP context)

Regulation (HDS, EU AI Act high-risk classification for diagnostic AI) places a **structural ceiling** at Stage 4 (AI-Embedded). Reaching Stage 5 in clinical decision-making is, today, prohibited — and rightly so. But administrative workflows (scheduling, coding, billing, supply chain) can reach Stage 5 without ethical concern. The strategic question is not *"how do we become AI-Native in healthcare?"* but *"which sub-systems can be AI-Native, and which must remain AI-Embedded with a human in the loop?"*

### Financial services (KHOME / Crédit Agricole context)

DORA mandates third-party ICT risk management — and an LLM provider *is* a critical third party. AVMs and credit-scoring under EU AI Act are high-risk. AI-Native trajectories in finance must therefore satisfy three constraints simultaneously: (a) explainability of decisions; (b) operational resilience of providers; (c) sectorial fairness and non-discrimination tests. This pushes towards multi-provider architectures, on-prem inference for the most critical workloads, and a strong evaluation discipline.

### B2B SaaS (Vocalcom context)

The least regulated, most directly competitive context. Here, the AI-Native question is existential: a competitor reaching Stage 5 first will out-iterate the others by an order of magnitude. The strategic move is to industrialise MLOps and evaluation **before** the product surface area justifies it — because by the time it does, the catch-up is too costly.

---

## 6. A note on agentic systems

By April 2026, multi-agent architectures (Anthropic, OpenAI, LangGraph) are mature enough for narrow production deployment but not for unconstrained orchestration of business processes. My current recommendation to KHOME and to advisory clients is: **single-agent, tool-using systems** for revenue-touching workflows; **multi-agent simulations** for back-office automation where errors are recoverable. The line will move — but in 2026, the engineering tax of multi-agent reliability still exceeds its productivity premium for most enterprises [Anthropic, *Building effective agents*, 2024].

---

## 7. Conclusion

*AI-Native* is not a marketing label — it is an operating-model property. The three diagnostic tests above let a board, a recruiter, or a CTO peer separate genuine transitions from PowerPoint transitions. The transition is hard, regulated, expensive, and worth it for the firms that survive the data-flywheel race. For the rest, AI-Embedded (Stage 4) is a perfectly defensible — and often more profitable — destination.

The strategic mistake is not failing to become AI-Native. It is **not making the choice consciously.**

---

## References

1. Anthropic. (2024). *Building effective agents*. Engineering blog.
2. Bommasani, R. et al. (2021). *On the Opportunities and Risks of Foundation Models*. arXiv:2108.07258.
3. Brynjolfsson, E., Li, D., Raymond, L. R. (2023). *Generative AI at Work*. NBER 31161.
4. CNCF. (2018). *Cloud Native Definition v1.0*.
5. Davenport, T., Mittal, N. (2022). *How to Become an AI-Fueled Organization*. HBR.
6. EU. (2022). *DORA — Regulation (EU) 2022/2554*.
7. EU. (2024). *AI Act — Regulation (EU) 2024/1689*.
8. Iansiti, M., Lakhani, K. R. (2020). *Competing in the Age of AI*. HBR Press.
9. ISO/IEC 42001:2023 — *AI Management Systems*.
10. Lewis, P. et al. (2020). *Retrieval-Augmented Generation*. arXiv:2005.11401.
11. NIST. (2023). *AI Risk Management Framework 1.0*. NIST AI 100-1.
12. OpenAI. (2024). *Model Spec*.
13. Sculley, D. et al. (2015). *Hidden Technical Debt in ML Systems*. NIPS.
14. Westerman, G., Bonnet, D., McAfee, A. (2014). *Leading Digital*. HBR Press.

---

*Citation: Bongard, F. (2026). What is an AI-Native Enterprise?. Working paper.*
