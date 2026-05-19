# Agentic AI in the Enterprise: Architecture Patterns and Design Principles

**Module 05 — Paper 1 · ~4 500 words · 18 references**

> *« The difference between a RAG system and an agentic system is not sophistication — it is autonomy. And autonomy changes everything about governance. »*

---

## Abstract

This paper maps the architectural landscape of enterprise agentic AI systems as it stands in 2026. It covers the core building blocks (planning, memory, tool use, multi-agent orchestration), the principal orchestration topologies (hierarchical, peer-to-peer, hybrid), the memory architecture choices that determine an agent's effective capability horizon, and the blast radius minimisation patterns that distinguish production-grade deployments from proof-of-concept systems. The paper concludes with a practical framework comparison of LangGraph, CrewAI, AutoGen, and the Anthropic Agent SDK. Field experience from People First Technologies, KHOME, and AP-HP informs the applied sections.

---

## 1. From RAG to Agents: The Regime Change

A RAG pipeline (Module 01) is a **read-only, single-turn, deterministic-ish** system: a query comes in, relevant documents are retrieved, the LLM generates a grounded response. The system cannot initiate actions, cannot modify external state, cannot plan over multiple steps, and its outputs are consumed by a human who then decides what to do.

An **agentic system** is categorically different on all four dimensions:

| Dimension | RAG | Agentic AI |
|-----------|-----|------------|
| Action | Read-only | Read + Write + Execute |
| Turns | Single | Multi-step, self-directed |
| Determinism | High (same retrieval, similar output) | Lower (planning produces variable sequences) |
| Autonomy | Zero (human decides next step) | Partial to full |

This regime change is not incremental — it is architectural. A RAG governance framework (data quality, retrieval relevance, hallucination rate) is necessary but radically insufficient for an agentic system. The additional failure modes include: action side-effects, cascading errors across tool calls, prompt injection through external data sources (Greshake et al. 2023), infinite loops, cost explosion, and — in the worst case — irreversible real-world actions taken on incorrect premises.

---

## 2. The Four Core Agentic Building Blocks

### 2.1 Planning

Planning is the agent's ability to decompose a high-level goal into a sequence of executable steps. Two dominant patterns in 2026:

**ReAct (Yao et al. 2023)** — Reason + Act interleaved. The agent produces a Thought ("I need to retrieve the latest sales figures"), an Action ("call get_sales_data(period='Q1-2026')"), an Observation (the tool output), and then a new Thought. The loop continues until the agent produces a final Answer. ReAct is the most widely deployed planning pattern because it is robust, interpretable, and compatible with all major LLMs.

**Reflexion (Shinn et al. 2023)** — Adds a self-reflection step after each failed attempt. The agent evaluates what went wrong and updates its strategy before retrying. Reflexion significantly improves performance on complex multi-step tasks but increases token consumption and latency.

**Plan-and-Execute** — Separates planning from execution: a planner agent first produces a complete task graph, then executor agents execute each step. Advantages: cleaner separation of concerns, easier to audit; disadvantages: the initial plan becomes stale as execution proceeds.

**For enterprise use:** ReAct remains the most operationally proven. Plan-and-Execute is preferred for complex workflows with predictable structure (e.g., multi-step data processing pipelines). Reflexion is best reserved for tasks where quality is more important than latency (research, legal analysis).

### 2.2 Memory

An agent's memory architecture determines what it can "know" and "remember" across a session and across sessions:

**In-context memory** — Everything the agent knows is in the context window. Simple but limited: modern LLMs have 128K–1M token windows, but attention quality degrades on very long contexts, and the cost per call scales linearly with context length. Suitable for single-session tasks.

**Episodic memory** — A persistent store (vector database or key-value store) of past interactions, indexed by recency and relevance. The agent retrieves relevant past episodes before each turn. Enables multi-session continuity but requires careful management of what is stored (PII, sensitive decision rationale).

**Semantic memory** — A knowledge graph or RAG corpus that the agent can query. This is Module 01 territory — the RAG pipeline serves as the agent's semantic memory. Well-understood pattern with production-grade tooling.

**Procedural memory** — Stored task plans, tool-use templates, and learned workflows that the agent can retrieve and adapt. Enables progressive specialisation of the agent on domain-specific tasks. Implemented via fine-tuning (expensive, data-hungry) or in-context few-shot examples from a retrieval store (cheaper, more flexible).

**Enterprise architectural guidance:** for most enterprise agentic deployments in 2026, the practical architecture is: in-context memory for immediate task context + episodic memory for inter-session continuity + semantic memory (RAG) for knowledge grounding. Procedural memory via fine-tuning is justified only for high-volume, latency-sensitive, specialised agents.

### 2.3 Tool Use

Tools are the mechanism by which agents act on the world. The design of the tool interface is the single most consequential decision for blast radius management.

**Tool design principles:**

1. **Least-privilege tool design.** Each tool should expose the minimum capability needed. Prefer `get_customer_order_status(order_id)` over `query_database(sql_query)`. The former has a bounded blast radius; the latter is a privilege escalation vector.

2. **Reversibility classification.** Every tool must be classified as: (a) read-only (no blast radius), (b) reversible write (can be undone: create_draft_email), (c) irreversible write (cannot be undone: send_email, delete_record, execute_payment). Irreversible tools must require human approval (see Section 4).

3. **Typed, validated inputs.** Tool inputs should be strongly typed with validation. An agent that can call `send_email(to: str, body: str)` without validation can be manipulated into sending emails to unintended recipients via prompt injection.

4. **Rate limiting and cost budgets.** Tools that call external APIs (web search, LLM inference, database queries) must have per-session and per-hour rate limits to prevent cost runaway. A misbehaving agent should not be able to trigger $10,000 in API charges before being halted.

5. **Audit logging at the tool boundary.** Every tool call and its result should be logged before execution. This enables forensic replay and is a DORA ICT incident management requirement for tools that interact with regulated systems.

### 2.4 Multi-Agent Orchestration

A single agent with a large context window and many tools can accomplish simple to moderately complex tasks. For complex, parallel, or specialised tasks, **multi-agent systems** are more capable and more maintainable:

- **Specialised agents** trained (or prompted) for specific domains outperform generalist agents on domain-specific tasks.
- **Parallel execution** across independent sub-tasks reduces wall-clock time significantly.
- **Separation of concerns** makes each agent's behaviour easier to test, debug, and audit independently.

The cost is architectural complexity: multi-agent systems introduce new failure modes (inter-agent communication errors, inconsistent shared state, cascading failures) and new governance challenges (which agent is accountable for the final outcome?).

---

## 3. Orchestration Topologies

### 3.1 Hierarchical (Orchestrator-Subagent)

A single **orchestrator agent** receives the user task, decomposes it into subtasks, and delegates each subtask to a **specialist subagent**. The orchestrator aggregates results and produces the final output.

```
User → Orchestrator
         ├── Subagent A (data retrieval)
         ├── Subagent B (analysis)
         └── Subagent C (report generation)
```

**Advantages:** clear accountability (the orchestrator is the single point of responsibility), simple to audit (all coordination flows through one node), natural place for guardrails (the orchestrator enforces the policy engine).

**Disadvantages:** orchestrator is a single point of failure; bottleneck for parallel tasks; the orchestrator must understand all subagents' capabilities.

**Best for:** most enterprise use-cases where a clear task hierarchy exists. This is the pattern implemented in `agentic_orchestrator.py`.

### 3.2 Peer-to-Peer (Swarm)

Agents communicate directly with each other without a central coordinator. Each agent has a role and can request help from others.

**Advantages:** more resilient (no single point of failure), natural for emergent problem-solving.

**Disadvantages:** much harder to audit (communication graph is complex), harder to enforce policies, higher risk of circular dependencies and infinite loops.

**Best for:** research and exploration tasks where the solution path is unknown. **Not recommended for regulated enterprise contexts** without robust guardrails and extensive testing.

### 3.3 Hybrid

A hierarchical backbone with peer-to-peer communication within specialised sub-teams. The most common production pattern in 2026 for complex enterprise workflows.

```
User → Orchestrator
         ├── Team A (Research Agents — peer-to-peer within team)
         ├── Team B (Analysis Agents — peer-to-peer within team)
         └── Review Agent (validates before final output)
```

---

## 4. Blast Radius Minimisation

Blast radius is the maximum damage that an agent can cause if it malfunctions, is manipulated via prompt injection, or follows incorrect instructions. Controlling blast radius is the central safety challenge of agentic AI in enterprise settings.

### 4.1 The Irreversibility Detector

Before any tool call, the orchestrator should classify the action as reversible or irreversible. This classification can be hardcoded in the tool definition or evaluated dynamically by a small, fast classification model.

If the action is irreversible **and** above a configurable risk threshold, execution is paused and a human-in-the-loop approval is required. See `agent_policy_engine.py` for the implementation.

### 4.2 Budget Constraints

Every agent execution should be bounded by hard budget limits:
- **Maximum steps:** the maximum number of ReAct iterations before the agent is halted and escalated to human review.
- **Token budget:** maximum total tokens consumed per task execution (controls LLM API cost).
- **Tool call budget:** maximum calls to each external tool per session (prevents rate-limit violations and cost runaway).
- **Time budget:** wall-clock timeout per task.

These are not soft limits that the agent can reason its way around. They are hard limits enforced by the orchestrator framework, outside the agent's context window.

### 4.3 Prompt Injection Defence

Indirect prompt injection (Greshake et al. 2023) is the primary adversarial attack vector for agentic systems: malicious instructions embedded in external content (web pages, documents, emails, database records) that the agent processes as part of its task. The injected instructions attempt to redirect the agent's behaviour.

Defence layers:
1. **Input sanitisation:** strip HTML tags, truncate inputs to expected lengths, normalise unicode.
2. **Source attribution:** the agent's prompt should include the source of each piece of external content and explicit instructions not to follow instructions from untrusted sources.
3. **Output validation:** a secondary lightweight model validates the agent's planned action against the original user intent before execution.
4. **Least-privilege tool design:** even if an injection succeeds, limited tool permissions bound the damage.

### 4.4 Sensitive Data Guardrails

Agents that process documents or database records may encounter sensitive data (PII, financial data, medical records). The orchestrator should implement:
- **Data classification at tool output:** classify the sensitivity of tool outputs before passing them to the next step.
- **Data minimisation:** pass only the fields necessary for the next tool call, not entire records.
- **Context window scrubbing:** before logging agent traces, redact sensitive data patterns (email addresses, credit card numbers, healthcare identifiers).

---

## 5. Framework Comparison (2026)

| Framework | Orchestration Model | Memory | Primary Language | Best For |
|-----------|-------------------|--------|-----------------|----------|
| **LangGraph** | Stateful graph (nodes + edges) | In-context + external | Python | Complex stateful workflows with conditional routing |
| **CrewAI** | Role-based hierarchical | In-context | Python | Task-oriented multi-agent with clear role separation |
| **AutoGen** | Conversation-based | In-context | Python | Research and exploration, flexible dialogue |
| **Claude Agent SDK** | Tool-use + MCP | In-context | Python/TypeScript | Anthropic-native, MCP ecosystem integration |
| **LlamaIndex Workflows** | Event-driven | In-context | Python | Document-heavy RAG + agent hybrid |

**CTO recommendation for regulated enterprise contexts:** LangGraph for complex stateful pipelines (its graph model makes state transitions explicit and auditable); CrewAI for simpler team-based workflows; Claude Agent SDK + MCP for Anthropic-stack deployments with rich tool ecosystems.

---

## References

1. Yao, S. et al. (2023). *ReAct: Synergizing Reasoning and Acting in Language Models*. ICLR 2023.
2. Shinn, N. et al. (2023). *Reflexion: Language Agents with Verbal Reinforcement Learning*. NeurIPS 2023.
3. Wang, L. et al. (2023). *A Survey on Large Language Model based Autonomous Agents*. arXiv:2308.11432.
4. Xi, Z. et al. (2023). *The Rise and Potential of Large Language Model Based Agents*. arXiv:2309.07864.
5. Wei, J. et al. (2022). *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. NeurIPS 2022.
6. Greshake, K. et al. (2023). *Not what you've signed up for: Compromising real-world LLM-integrated apps with indirect prompt injection*. arXiv:2302.12173.
7. Chase, H. (2023). *LangChain and LangGraph Documentation*. LangChain Inc.
8. Wu, Q. et al. (2023). *AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation*. arXiv:2308.08155.
9. Anthropic. (2024). *Tool Use and Agentic Patterns — Claude Documentation*. Anthropic.
10. OWASP. (2025). *OWASP Top 10 for LLM Applications — LLM08: Excessive Agency*. OWASP Foundation.
11. Minsky, M. (1986). *The Society of Mind*. Simon & Schuster. [foundational multi-agent thinking]
12. Park, J. S. et al. (2023). *Generative Agents: Interactive Simulacra of Human Behavior*. UIST 2023.
13. Sumers, T. et al. (2023). *Cognitive Architectures for Language Agents*. arXiv:2309.02427.
14. Russell, S. (2019). *Human Compatible: Artificial Intelligence and the Problem of Control*. Viking Press.
15. Hadfield-Menell, D. et al. (2016). *Cooperative Inverse Reinforcement Learning*. NeurIPS 2016.
16. Anthropic. (2024). *Model Context Protocol (MCP) — Specification v1.0*. Anthropic.
17. Li, G. et al. (2023). *CAMEL: Communicative Agents for "Mind" Exploration of Large Scale Language Model Society*. NeurIPS 2023.
18. Significant Gravitas. (2023). *Auto-GPT: An Autonomous GPT-4 Experiment*. GitHub.
