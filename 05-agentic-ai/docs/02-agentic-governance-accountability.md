# Governing Autonomous Agents in the Enterprise: Accountability, DORA, and the AI Act

**Module 05 — Paper 2 · ~3 800 words · 14 references**

> *« Accountability for an agent's actions cannot be deferred to the model. The CTO signs the architecture. »*

---

## Abstract

This paper addresses the governance gap that emerges when enterprises deploy autonomous AI agents in production. It applies the NIST AI RMF Govern function to agentic systems, maps DORA obligations to orchestrator-as-ICT-third-party scenarios, analyses the EU AI Act classification of autonomous agents (particularly under Annex III §4 for HR and §5 for financial services), and proposes a human-in-the-loop design framework that is operationally meaningful rather than cosmetic. The paper argues that the accountability chain for an autonomous agent must be explicitly designed — it does not emerge automatically from the governance frameworks built for deterministic software systems.

---

## 1. Why Existing Governance Frameworks Are Insufficient for Agents

Existing enterprise IT governance frameworks — ISO 27001, ITIL, COBIT, DORA — were designed for systems that do what they are told. A database executes the query submitted. A microservice processes the request according to its interface contract. The governance question is: "did the system behave as specified?"

An autonomous agent operates differently. Given a goal ("find the three best suppliers for component X and negotiate a 10% discount"), the agent:
1. Decides *which tools* to call (web search, procurement database, email)
2. Decides *what queries* to issue to each tool
3. Decides *what actions* to take based on results (send an email, update a record)
4. Decides *when it is done*

The governance question is no longer "did the system behave as specified?" but "did the system pursue the right goal, in the right way, with acceptable side-effects?" This is a fundamentally different question — and none of the existing frameworks provide a ready-made answer.

---

## 2. NIST AI RMF Applied to Agentic Systems

The NIST AI RMF (2023) organises AI risk management around four functions: **Govern, Map, Measure, Manage**. The Govern function — which establishes the policies, roles, and accountability structures — is the most critical and most underimplemented for agentic AI.

### 2.1 Govern 1.1 — Organisational Policies

NIST AI RMF Govern 1.1 requires that policies, processes, and procedures are in place across the AI lifecycle. For agentic systems, this means:

- A **classification policy** for agent autonomy levels (read-only advisory, supervised action, autonomous action with approval gate, fully autonomous) — analogous to a data classification policy.
- A **tool approval policy** that governs which external tools can be integrated into agents, with what security review, and under what conditions.
- An **incident definition policy** that specifies what constitutes an "AI incident" for an agent (unexpected action, cost overrun, data leak through prompt injection, regulatory breach).

### 2.2 Govern 1.7 — Risk Ownership

"Processes and procedures are in place for teams to track, document, and communicate AI risks." For agents, this requires **named risk ownership** at three levels:

- **Agent architect** (usually: CTO / principal engineer): owns the agent's architecture, tool design, and blast radius constraints.
- **Agent operator** (usually: business owner): owns the operational deployment, the human oversight process, and the incident escalation.
- **Model provider** (usually: contractual): owns the foundation model behaviour, safety mitigations, and model card disclosures.

The risk that is most frequently unowned: the **orchestration layer** between the model provider's API and the enterprise's business systems. This is where most agent-related incidents occur, and it is the exclusive responsibility of the enterprise CTO.

### 2.3 Measure — Agentic-Specific Metrics

Standard AI evaluation metrics (accuracy, F1, BLEU) are insufficient for agents. Production agentic systems require:

- **Task completion rate:** percentage of assigned tasks successfully completed without human intervention.
- **Unintended action rate:** percentage of tasks where the agent took at least one action outside the scope defined by the policy engine.
- **Escalation rate:** percentage of tasks escalated to human review (too high = agent is overly conservative; too low = potential under-escalation of risky actions).
- **Mean blast radius per task:** average number of external systems touched per task execution (proxy for potential side-effect scope).
- **Prompt injection detection rate:** percentage of tasks where external content contained injection attempts, and the fraction successfully blocked.

---

## 3. DORA and the Orchestrator-as-ICT-Third-Party Problem

The Digital Operational Resilience Act (DORA, EU 2022/2554) classifies ICT third-party service providers by criticality and imposes proportionate obligations on financial entities that depend on them. The question for enterprise CTOs deploying agentic AI in financial services: **when is an LLM orchestrator a critical ICT third-party dependency under DORA?**

### 3.1 The Classification Analysis

DORA Art. 31 classifies an ICT third-party as "critical" based on: systemic impact if the service fails, number of financial entities using it, substitutability, and interdependencies. For an LLM orchestrator:

- If the agent automates a **core banking function** (credit decisioning, fraud detection, trade execution), the dependency on the LLM provider (Anthropic, OpenAI, Azure OpenAI) meets the criticality threshold.
- If the agent handles only **non-critical back-office tasks** (meeting summarisation, internal knowledge search), it likely does not.

**Practical implication:** a financial entity deploying a LangGraph orchestrator that calls Claude/GPT to process customer credit applications has a critical ICT third-party relationship with the LLM provider. This triggers DORA Art. 28 obligations: due diligence, contractual provisions, exit strategy, operational resilience testing.

### 3.2 The Audit Trail Obligation

DORA Art. 12 (ICT Business Continuity) and Art. 17 (ICT-related Incident Management) effectively require that ICT incidents — including AI agent misbehaviours — be traceable, reportable, and analysable. The audit logger (`agent_audit_logger.py`) is designed specifically to produce DORA-compatible traces.

### 3.3 Operational Resilience Testing for Agents

DORA Art. 24–25 (Digital Operational Resilience Testing) requires regular testing of ICT systems, including advanced penetration testing (TLPT) for critical systems. For agent systems, this should include:
- **Prompt injection red team exercises** (manual and automated)
- **Tool failure simulation** (what happens when a critical tool is unavailable?)
- **Cost runaway simulation** (what happens when an agent enters a loop?)
- **Adversarial task injection** (can a malicious task submitted by an internal user cause the agent to exfiltrate data?)

---

## 4. EU AI Act Classification of Autonomous Agents

The EU AI Act (2024/1689) does not have a dedicated provision for "agentic AI" — the concept was not mature enough at drafting time. However, autonomous agents deployed in enterprise contexts will be classified under existing provisions:

### 4.1 Annex III §4 — Employment and HR Agents

An agent that autonomously allocates tasks to workers, monitors performance, or screens candidates is squarely within Annex III §4. The fact that the system is agentic (it decides its own action sequence) rather than a static scoring model does not reduce its risk classification — it arguably increases it, because the agent can take actions that no single static model could.

**Key Art. 14 challenge:** "effectively overseeable" is harder to satisfy for an agent than for a static classifier, because the agent's decision-making process is distributed across multiple reasoning steps. The oversight interface must show the agent's reasoning chain, not just its final recommendation.

### 4.2 Annex III §5 — Financial Services Agents

Agents that interact with credit assessment, insurance underwriting, or essential financial services fall under §5. For DORA-regulated financial entities, this creates a regulatory double-bind: the agent is simultaneously a DORA ICT third-party dependency and an EU AI Act high-risk system.

**Compliance strategy:** build the Art. 9 risk management system and the DORA ICT risk framework as a unified artefact, not two separate compliance exercises. The DORA incident management process and the AI Act post-market monitoring (Art. 72) process should be the same process.

### 4.3 The GPAI Orchestrator Question

If the enterprise fine-tunes a foundation model for orchestration purposes, or if it deploys a GPAI model (GPT-5, Claude 4, Gemini 2 Ultra) as the orchestrator of a high-risk agentic system, does the enterprise become a **provider** of a GPAI model under Art. 51? The answer depends on whether the customised orchestrator is made available to third parties. For internal deployment only, the enterprise is a **deployer**, not a provider — a critical distinction for compliance burden.

---

## 5. Human-in-the-Loop Design: Meaningful, Not Cosmetic

The most common governance failure in enterprise agentic AI deployments is a **cosmetic HITL gate**: a human is nominally "in the loop" but:
- The presented decision context is incomprehensible (raw JSON tool output)
- The time pressure makes genuine review impossible (approval must be granted in < 30 seconds)
- There is no meaningful "reject" option (the system will retry until approved)
- Rejections are not logged or reviewed

A meaningful HITL gate requires four design elements:

### 5.1 Decision Context Rendering

Before asking a human to approve an agent action, the oversight interface must display:
- **What the agent is proposing to do** (plain language, not a tool call signature)
- **Why** (the agent's reasoning for this action, extracted from the ReAct thought)
- **What alternatives were considered** (if Plan-and-Execute: the alternatives the planner evaluated)
- **What the estimated consequences are** (the tool's reversibility classification and estimated impact)

### 5.2 Genuine Rejection Path

A rejection must: (a) halt the specific action, (b) log the rejection with the reviewer's reason, (c) optionally redirect the agent with a correction ("don't email the customer; instead, flag for human review"). Without (a)–(c), the "rejection" option is not a real control.

### 5.3 Timeout with Safe Default

HITL gates must have a timeout. On timeout, the safe default is always **halt, not proceed**. The agent is suspended and the task is queued for next available human reviewer. This is an architectural constraint that must be explicit in the policy engine.

### 5.4 Oversight Quality Monitoring

The HITL process must itself be monitored:
- Rejection rate (too low may signal rubber-stamping)
- Time-to-decision (too fast may signal inadequate review)
- Post-hoc outcome tracking (were approved actions that led to incidents different from rejected actions in retrospect?)

---

## 6. Accountability Chains in Multi-Agent Systems

When a **supervisor agent** instructs a **sub-agent** to take an action that causes harm, who is accountable? This is not an abstract philosophical question — it is a practical governance question that must be resolved before any multi-agent system goes to production.

**Principle 1 — Accountability does not fragment.** The fact that an action was taken by a sub-agent does not reduce the accountability of the orchestrator that instructed it, or of the enterprise that deployed both. In the AI Act framework, the "provider" of the system (the enterprise deploying the multi-agent orchestration) is accountable for the behaviour of the entire system, including sub-agents.

**Principle 2 — The policy engine is the governance anchor.** In the architecture implemented in `agent_policy_engine.py`, the policy engine is the single authoritative source for what any agent in the system is permitted to do. Accountability for any action traces to: (a) the policy that permitted it, (b) the engineer who configured that policy, (c) the CTO who approved the policy framework.

**Principle 3 — HITL checkpoints create legal clarity.** Every human approval of an agent action is a documented decision by a named individual at a specific time. This creates an audit trail that resolves the accountability question for that specific action. This is not an argument for minimising HITL — it is an argument for designing HITL checkpoints strategically, at the highest-consequence decision points.

---

## References

1. NIST. (2023). *AI Risk Management Framework (AI RMF 1.0)*. NIST AI 100-1.
2. EU. (2022). *Regulation (EU) 2022/2554 — DORA*. European Parliament and Council.
3. EU. (2024). *Regulation (EU) 2024/1689 — AI Act*. Art. 6, 9, 14, Annex III §4, §5.
4. OWASP. (2025). *OWASP Top 10 for LLM Applications — LLM08: Excessive Agency*. OWASP.
5. Greshake, K. et al. (2023). *Not what you've signed up for: Compromising real-world LLM-integrated apps with indirect prompt injection*. arXiv:2302.12173.
6. Russell, S. (2019). *Human Compatible: Artificial Intelligence and the Problem of Control*. Viking Press.
7. Hadfield-Menell, D. et al. (2016). *Cooperative Inverse Reinforcement Learning*. NeurIPS 2016.
8. Weidinger, L. et al. (2021). *Ethical and social risks of harm from Language Models*. arXiv:2112.04359.
9. ENISA. (2024). *AI Cybersecurity Considerations for Agentic Systems* (draft). ENISA.
10. MITRE ATLAS. (2024). *Adversarial ML Threat Matrix — Agentic AI Attack Patterns*. MITRE.
11. EBA. (2023). *Guidelines on the use of machine learning models in financial services*. EBA/GL/2023/06.
12. Stiennon, N. et al. (2020). *Learning to summarize with human feedback*. NeurIPS 2020.
13. Amodei, D. et al. (2016). *Concrete Problems in AI Safety*. arXiv:1606.06565.
14. Anthropic. (2024). *Claude's Constitution: Agentic and Tool-Use Safety Guidelines*. Anthropic.
