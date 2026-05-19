# 04 — EU AI Act : Classification, Conformité & Explicabilité des Systèmes IA

> *« Classifier un système IA sous l'EU AI Act n'est pas un exercice juridique — c'est une décision d'architecture. »*

🇬🇧 **English** · 🇫🇷 [Français](#fr)

---

## Strategic question

> **How does a CTO operationalise EU AI Act Article 9 conformity assessment for High-Risk AI systems — without creating a compliance theatre that blocks innovation?**

The EU AI Act entered full application in August 2026. For a CTO operating in healthcare, finance, or HR, this is not a legal abstraction: it directly shapes which AI systems can be deployed, how they must be documented, and what technical controls must be in place before go-live.

This section provides the conceptual framework and the operational toolkit to navigate the Act without outsourcing the technical judgment to a legal team.

## Contents

| File | Type | What you'll find |
| --- | --- | --- |
| [`docs/01-eu-ai-act-classification-framework.md`](docs/01-eu-ai-act-classification-framework.md) | Paper · 4 500 words · 20 references | Classification methodology across the four risk tiers (Prohibited / High-Risk / Limited / Minimal). Annex III deep-dive (8 high-risk categories). Prohibited practices (Art. 5). GPAI models (Art. 51–55). Tension between compliance and innovation velocity. |
| [`docs/02-xai-regulated-sectors.md`](docs/02-xai-regulated-sectors.md) | Paper · 3 800 words · 16 references | Explainability requirements (Art. 13–14): transparency, human oversight, accuracy. SHAP, LIME, mechanistic interpretability for LLMs. AVM scoring explainability (RICS + AI Act). Reconciling GDPR Art. 22 (right to explanation) with AI Act Art. 13. |
| [`code/eu_ai_act_classifier.py`](code/eu_ai_act_classifier.py) | Python · CLI | Classifies an AI system across the four risk tiers via 12 guided questions; generates the Article 11 / Annex IV technical documentation skeleton; flags Art. 5 prohibited practices. |
| [`code/xai_explainability_toolkit.py`](code/xai_explainability_toolkit.py) | Python · CLI | SHAP feature attribution for tabular models + token-level attribution for LLM outputs. Produces a regulatory-narrative report + visualisation. Directly applicable to AVM models (KHOME use-case). |
| [`code/ai_act_conformity_checker.py`](code/ai_act_conformity_checker.py) | Python · CLI | Gap analysis against Annex IV (technical documentation) + Art. 9 (risk management system): 47-item checklist with RED/AMBER/GREEN status + remediation guidance. |
| [`code/requirements.txt`](code/requirements.txt) | Pinned deps | Minimal dependencies for reproducibility. |

## Key references

- EU. (2024). *Regulation (EU) 2024/1689 — AI Act*. European Parliament and Council.
- ISO/IEC 42001:2023 — *Artificial intelligence management system*.
- NIST. (2023). *AI Risk Management Framework (AI RMF 1.0)*. NIST AI 100-1.
- Lundberg, S. M., Lee, S.-I. (2017). *A unified approach to interpreting model predictions (SHAP)*. NeurIPS.
- Ribeiro, M. T. et al. (2016). *"Why Should I Trust You?": Explaining the predictions of any classifier (LIME)*. KDD.
- ANSSI. (2024). *Recommandations de sécurité pour les systèmes fondés sur l'IA générative*.
- ENISA. (2023). *Multilayer Framework for Good Cybersecurity Practices for AI*.
- Goodman, B., Flaxman, S. (2017). *EU regulations on algorithmic decision-making and a "right to explanation"*. AI Magazine.
- Arrieta, A. B. et al. (2020). *Explainable Artificial Intelligence (XAI): Concepts, taxonomies, opportunities and challenges*. Information Fusion, 58.
- Wachter, S., Mittelstadt, B., Russell, C. (2017). *Counterfactual Explanations without Opening the Black Box*. Harvard JOLT.
- AI HLEG. (2019). *Ethics Guidelines for Trustworthy AI*. European Commission.
- RICS. (2023). *Automated Valuation Models (AVMs) — Professional Statement*.
- Doshi-Velez, F., Kim, B. (2017). *Towards a rigorous science of interpretable machine learning*. arXiv:1702.08608.
- Floridi, L. et al. (2018). *AI4People — An Ethical Framework for a Good AI Society*. Minds and Machines.
- European Data Protection Board. (2023). *Guidelines on AI and Data Protection*.

> Full bibliography in [`docs/references.bib`](docs/references.bib).

## How to run the code

```bash
cd code
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python eu_ai_act_classifier.py --interactive          # classify your AI system, get Annex IV skeleton
python xai_explainability_toolkit.py --demo           # SHAP + token attribution on sample data
python ai_act_conformity_checker.py --system-type high-risk  # full 47-item gap analysis
```

---

## 🇫🇷 Version française

### Question stratégique

> **Comment un CTO opérationnalise-t-il l'évaluation de conformité Article 9 de l'EU AI Act pour ses systèmes IA à haut risque — sans créer un théâtre de conformité qui bloque l'innovation ?**

L'EU AI Act est pleinement applicable depuis août 2026. Pour un CTO opérant en santé, finance ou RH, ce n'est pas une abstraction juridique : il conditionne directement quels systèmes IA peuvent être déployés, comment ils doivent être documentés, et quels contrôles techniques doivent être en place avant la mise en production.

### Mes éléments d'expérience qui nourrissent cette section

- **KHOME (2026)** — modèles AVM de valorisation immobilière : classification Annexe III Art. 6 §2 (décisions à impact significatif sur des personnes physiques), explicabilité RICS + RGPD Art. 22, construction de la documentation Annexe IV.
- **AP-HP (2024)** — réflexion sur le déploiement d'IA dans un SI hospitalier HDS : classification high-risk (dispositif médical assisté par IA, Annexe III cat. 1), contraintes Art. 22 + Art. 14 (surveillance humaine).
- **People First Technologies (2024–2026)** — plateforme RH × LLM/RAG : classification Annexe III cat. 4 (emploi et gestion des travailleurs), conformité Art. 9 et Art. 13.
- **Mandat juré expert** — *"Concevoir et implémenter une solution d'IA"* (CPNEFP Branche BET) : évaluation de la conformité AI Act comme critère de certification intégré.

### Trois convictions que je défends en 2026

1. **La classification AI Act n'est pas un exercice juridique — c'est une décision d'architecture.** Un juriste peut vous dire si vous êtes en Annexe III. Seul un CTO peut décider si l'architecture peut légitimement éviter ce périmètre (ex. : humain dans la boucle renforcé, restriction du scope décisionnel, modèle non-déterministe clairement étiqueté).
2. **L'explicabilité (Art. 13–14) n'est pas l'interprétabilité au sens ML.** L'AI Act exige que *l'utilisateur final affecté* comprenne la logique de la décision — pas que le data scientist puisse déboguer le modèle. Un dashboard SHAP brut n'est pas une réponse conforme : il faut une narrative réglementaire compréhensible par un non-expert.
3. **La documentation Annexe IV se construit en continu, pas à l'audit.** Les entreprises qui la créent *après* le déploiement sous pression réglementaire produisent de la paperasse ; celles qui l'intègrent dans leur MLOps (comme artefact de pipeline) produisent de la valeur et de la traçabilité.
