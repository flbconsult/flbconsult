# 05 — Systèmes Agentiques en Entreprise : Architecture, Gouvernance & Blast Radius

> *« Un agent IA n'est pas un chatbot qui appelle des outils — c'est un processus autonome qui peut prendre des décisions irréversibles. Gouverner l'un sans l'autre, c'est rater le changement de régime. »*

🇬🇧 **English** · 🇫🇷 [Français](#fr)

---

## Strategic question

> **When an AI agent can call APIs, write and execute code, and take irreversible actions on behalf of the enterprise — how do you architect for safety, auditability, and controlled blast radius?**

In 2026, Retrieval-Augmented Generation (Module 01) is table stakes. The frontier is **agentic AI**: autonomous systems that plan multi-step tasks, call external tools, maintain memory across sessions, and orchestrate other agents. LangGraph, CrewAI, AutoGen, and the Model Context Protocol (MCP) are in production across Fortune 500 companies.

The governance and security implications are an order of magnitude more complex than RAG. An agent that summarises documents is low-risk. An agent that sends emails, commits code, transfers funds, or modifies infrastructure configuration is a different category of system — and most enterprises are deploying both without distinguishing between them.

## Contents

| File | Type | What you'll find |
| --- | --- | --- |
| [`docs/01-agentic-enterprise-architecture.md`](docs/01-agentic-enterprise-architecture.md) | Paper · 4 500 words · 18 references | Orchestration topologies (hierarchical, peer-to-peer, hybrid). Memory architectures (in-context, episodic, semantic, procedural). Tool design principles. Blast radius minimisation patterns. Framework comparison: LangGraph vs. CrewAI vs. AutoGen vs. Claude Agents SDK. |
| [`docs/02-agentic-governance-accountability.md`](docs/02-agentic-governance-accountability.md) | Paper · 3 800 words · 14 references | Governance of autonomous agents: NIST AI RMF applied to agentic systems. Human-in-the-loop design (approval, interruption, override). Accountability chains in multi-agent systems. DORA + agentic AI: when an orchestrator calls a regulated third-party API. EU AI Act classification of autonomous agents. |
| [`code/agentic_orchestrator.py`](code/agentic_orchestrator.py) | Python · reference architecture | Multi-agent reference implementation: planner + specialist agents + guardrails (token budget, max steps, irreversibility detector, human-in-the-loop gate). ~300 lines, demo corpus included. |
| [`code/agent_policy_engine.py`](code/agent_policy_engine.py) | Python · CLI | Declarative policy engine for agent permissions: YAML-based rules constraining which tools an agent can call, under what conditions, with what approval workflow. Inspired by ABAC/PBAC models. |
| [`code/agent_audit_logger.py`](code/agent_audit_logger.py) | Python · CLI | Structured OpenTelemetry-compatible audit logger for agent traces: captures tool calls, intermediate reasoning steps, HITL checkpoints, token costs. Exportable to SIEM (Splunk, Datadog, Elastic). |
| [`code/requirements.txt`](code/requirements.txt) | Pinned deps | Core dependencies. LangGraph optional for production use. |

## Key references

- Yao, S. et al. (2023). *ReAct: Synergizing Reasoning and Acting in Language Models*. ICLR 2023.
- Shinn, N. et al. (2023). *Reflexion: Language Agents with Verbal Reinforcement Learning*. NeurIPS 2023.
- Wang, L. et al. (2023). *A Survey on Large Language Model based Autonomous Agents*. arXiv:2308.11432.
- Xi, Z. et al. (2023). *The Rise and Potential of Large Language Model Based Agents: A Survey*. arXiv:2309.07864.
- Wei, J. et al. (2022). *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. NeurIPS 2022.
- Significant Gravitas (2023). *Auto-GPT: An Autonomous GPT-4 Experiment*. GitHub.
- Anthropic. (2024). *Claude's Model Specification — Safety, Agentic Behaviour and Tool Use*. Anthropic.
- OWASP. (2025). *Top 10 for Large Language Model Applications — Excessive Agency (LLM08)*. OWASP.
- NIST. (2023). *AI Risk Management Framework (AI RMF 1.0) — Govern 1.1–1.7*. NIST.
- EU. (2024). *AI Act — Art. 6, Annex III §4 (automated task allocation and monitoring)*. 2024/1689.
- Chase, H. (2023). *LangChain: Building applications with LLMs*. LangChain Documentation.
- Wu, Q. et al. (2023). *AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation*. arXiv:2308.08155.
- Hadfield-Menell, D. et al. (2016). *Cooperative Inverse Reinforcement Learning*. NeurIPS 2016.
- Russell, S. (2019). *Human Compatible: Artificial Intelligence and the Problem of Control*. Viking Press.

> Full bibliography in [`docs/references.bib`](docs/references.bib).

## How to run the code

```bash
cd code
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python agentic_orchestrator.py --demo               # run multi-agent demo task
python agent_policy_engine.py --demo                # show policy evaluation for sample agent actions
python agent_audit_logger.py --demo                 # generate and display a sample audit trace
python agent_audit_logger.py --replay trace.jsonl   # replay an agent trace with analysis
```

---

## 🇫🇷 Version française

### Question stratégique

> **Quand un agent IA peut appeler des APIs, écrire et exécuter du code, et prendre des actions irréversibles au nom de l'entreprise — comment architecturer pour la sécurité, l'auditabilité, et le contrôle du rayon de destruction ?**

En 2026, le RAG (Module 01) est acquis. La frontière est l'IA agentique : des systèmes autonomes qui planifient des tâches multi-étapes, appellent des outils externes, maintiennent une mémoire entre sessions, et orchestrent d'autres agents. Ces systèmes sont en production dans les grands groupes, mais souvent sans cadre de gouvernance adapté — parce que les frameworks de gouvernance existants (ISO 27001, DORA, AI Act) ont été conçus pour des systèmes déterministes et non pour des agents autonomes qui décident de leurs propres prochaines actions.

### Mes éléments d'expérience qui nourrissent cette section

- **People First Technologies (2024–2026)** — industrialisation d'une plateforme RAG/LLM RH : l'étape suivante naturelle est l'agentification (agent de sourcing, agent d'onboarding, agent d'évaluation continue). J'ai piloté l'architecture en anticipant ce passage.
- **KHOME (2026)** — AI-Native transformation : les agents IA sont au cœur de l'automatisation du cycle de valorisation (collecte de données marché, analyse comparative, génération de rapports AVM). Le contrôle du blast radius sur les données RICS-certifiées est une contrainte opérationnelle réelle.
- **AP-HP (2024)** — exploration des agents d'orchestration de workflow hospitalier (ordonnancement, planification de blocs opératoires) : les exigences HDS et les enjeux de sécurité patient imposent une approche human-in-the-loop irréductible.
- **Vocalcom (2022–2023)** — API-first architecture sur 570 tenants cloud : les patterns de contrôle d'accès et de blast radius que j'ai mis en place pour les webhooks clients sont directement réutilisables pour la gouvernance d'agents.

### Trois principes architecturaux que je défends en 2026

1. **Le blast radius est une contrainte de conception, pas un paramètre de déploiement.** Un agent qui peut envoyer des emails ET modifier une base de données ET appeler une API de paiement a un blast radius catastrophique si mal configuré. La règle d'or : chaque agent doit avoir les permissions minimales pour accomplir sa tâche, et toute action irréversible doit passer par un gate humain documenté.
2. **L'auditabilité des agents est un prérequis DORA, pas un nice-to-have.** Un agent LLM orchestrateur qui appelle une API bancaire tierce est un ICT third-party dependency au sens DORA. La trace d'exécution doit être aussi rigoureuse que les logs d'un pipeline financier.
3. **Le "human in the loop" doit être conçu pour être utile, pas cosmétique.** Un gate humain qui présente à l'opérateur une décision d'agent incompréhensible n'est pas une mesure de sécurité — c'est un rubber stamp. L'interface de supervision doit montrer le raisonnement, les alternatives considérées, et les risques estimés.
