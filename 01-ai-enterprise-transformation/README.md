# 01 — Enterprise AI Transformation & AI-Native Companies

> *« Le LLM est un composant, pas une stratégie. »*

🇬🇧 **English** · 🇫🇷 [Français](#fr)

---

## Strategic question

In 2026, the question is no longer **"should we adopt Generative AI?"** — every CAC 40 / Fortune 500 has already deployed at least one copilot. The real question is:

> **What does it mean to be *AI-Native* — not *AI-augmented* — and is that transition achievable for an incumbent without rebuilding from scratch?**

This section answers it on three levels.

## Contents

| File | Type | What you'll find |
|---|---|---|
| [`docs/01-enterprise-ai-transformation-framework.md`](./docs/01-enterprise-ai-transformation-framework.md) | Paper · 4 600 words · 18 references | A 5-stage maturity model (*AI-Curious → AI-Native*), six transformation levers, four anti-patterns observed in field engagements (AP-HP, KHOME, People First). Builds on Davenport & Mittal (HBR 2022), Iansiti & Lakhani (HBR 2020), Brynjolfsson et al. (NBER 2023). |
| [`docs/02-ai-native-enterprise-thesis.md`](./docs/02-ai-native-enterprise-thesis.md) | Thesis · 3 800 words · 14 references | Definition of *AI-Native* (data-flywheel, agentic ops, evaluation-first culture), comparison with cloud-native and mobile-first transitions, why most "AI transformation" programmes are actually IT-modernisation programmes in disguise. |
| [`code/ai_maturity_assessment.py`](./code/ai_maturity_assessment.py) | Python · CLI | Executable maturity assessment that scores an organisation across 6 dimensions (data, talent, MLOps, evaluation, governance, change-management) and outputs a radar chart + recommendations. |
| [`code/rag_pipeline.py`](./code/rag_pipeline.py) | Python · reference architecture | Production-grade RAG pipeline: chunking, hybrid retrieval (BM25 + dense), re-ranking, citation enforcement, evaluation hooks. ~250 lines, runs offline on a sample corpus. |
| [`code/llm_evaluation_harness.py`](./code/llm_evaluation_harness.py) | Python · evaluation framework | LLM-as-a-judge + rule-based evaluators (faithfulness, relevance, toxicity, prompt-injection resistance). Inspired by RAGAS and HELM. |
| [`code/requirements.txt`](./code/requirements.txt) | Pinned deps | All dependencies pinned for reproducibility. |

## Key references

- Brynjolfsson, E., Li, D., Raymond, L. R. (2023). *Generative AI at Work*. NBER Working Paper 31161.
- Iansiti, M., Lakhani, K. R. (2020). *Competing in the Age of AI*. Harvard Business Review Press.
- Bommasani, R. et al. (2021). *On the Opportunities and Risks of Foundation Models*. arXiv:2108.07258.
- Lewis, P. et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. arXiv:2005.11401.
- Davenport, T., Mittal, N. (2022). *How to Become an AI-Fueled Organization*. HBR.
- NIST (2023). *AI Risk Management Framework (AI RMF 1.0)*. NIST AI 100-1.
- Liang, P. et al. (2022). *Holistic Evaluation of Language Models (HELM)*. arXiv:2211.09110.
- Es, S. et al. (2023). *RAGAS: Automated Evaluation of Retrieval Augmented Generation*. arXiv:2309.15217.

> Full bibliography in [`docs/references.bib`](./docs/references.bib).

## How to run the code

```bash
cd code
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python ai_maturity_assessment.py --interactive       # answer 18 questions, get a radar chart
python rag_pipeline.py --query "What is AI-Native?"  # runs RAG on the sample corpus
python llm_evaluation_harness.py --demo              # runs the full evaluation suite
```

---

<a id="fr"></a>

## 🇫🇷 Version française

### Question stratégique

En 2026, la question n'est plus **« faut-il adopter l'IA générative ? »** — toute entreprise du CAC 40 / Fortune 500 a déjà déployé au moins un copilote. La vraie question est :

> **Que signifie être *AI-Native* — et non *IA-augmenté* — et cette transition est-elle réalisable pour un acteur établi sans tout reconstruire ?**

Cette section répond sur trois niveaux : un **modèle de maturité** à 5 stades (papier 1), une **thèse sur l'entreprise AI-Native** (papier 2), et **trois implémentations Python** (auto-évaluation, RAG, évaluation LLM).

### Mes éléments d'expérience qui nourrissent cette section

- **KHOME (2026)** — pilotage de la transformation AI-Native pour la valorisation immobilière, avec contraintes RICS / DORA / RGPD sur les modèles AVM.
- **People First Technologies (2024–2026)** — industrialisation d'une plateforme RAG/LLM RH (architecture AWS, MLOps, CI/CD).
- **Vivoka (2021–2022)** — 6 brevets NLP/NLU déposés, chaire industrielle INRIA.
- **AP-HP (2024)** — réflexion sur l'usage de l'IA dans un SI hospitalier critique sous contrainte HDS.
