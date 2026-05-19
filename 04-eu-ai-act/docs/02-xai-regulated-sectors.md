# Explainable AI in Regulated Sectors: From SHAP to Regulatory Narrative

**Module 04 — Paper 2 · ~3 800 words · 16 references**

> *« An explanation that only a data scientist can understand is not an explanation under the AI Act — it is a technical artefact. »*

---

## Abstract

Articles 13 and 14 of the EU AI Act impose transparency and human oversight requirements on high-risk AI systems that go beyond what the ML community typically means by "interpretability". This paper maps the gap between ML explainability methods (SHAP, LIME, counterfactual explanations, mechanistic interpretability) and the regulatory requirements of the AI Act, GDPR Article 22, and sector-specific norms (RICS for real-estate AVMs, EBA guidelines for credit scoring). It proposes a three-layer explainability architecture that satisfies both the data scientist (debugging), the compliance officer (audit), and the affected natural person (right to explanation). Field examples are drawn from automated valuation models (KHOME) and LLM-based HR scoring (People First Technologies).

---

## 1. What the AI Act Actually Requires: Articles 13 and 14

### 1.1 Article 13 — Transparency and Provision of Information to Deployers

Article 13 requires that high-risk AI systems be designed and developed to ensure that their operation is **sufficiently transparent** to enable deployers to interpret the system's output and use it appropriately. The instructions for use must include:

- The intended purpose, level of accuracy and robustness, including any known limitations
- Performance metrics on specific groups of persons (Art. 13.3.b.iv) — a requirement that directly implies disaggregated fairness reporting
- Human oversight measures (Art. 13.3.e)
- **Description of the input data** and the system's sensitivity to that input

This is not a post-hoc explanation requirement for individual decisions. It is a **system-level transparency** requirement: the deployer must understand how the system behaves, including at the edges.

### 1.2 Article 14 — Human Oversight

Article 14 requires that high-risk AI systems be designed to be **effectively overseen by natural persons** during the period of use. The human oversight measures must enable deployers to:

- Understand the capabilities and limitations of the system (Art. 14.4.a)
- Monitor the operation for anomalies and dysfunctions (Art. 14.4.b)
- **Disregard, override or reverse** the output of the system (Art. 14.4.c)
- **Intervene on or stop** the system through a "halt" button or similar procedure (Art. 14.4.e)

The phrase "understand the capabilities and limitations" in Art. 14.4.a is the link to explainability. A system that produces a confidence score without explaining what drives that score does not enable genuine oversight.

### 1.3 The GDPR Art. 22 Intersection

GDPR Article 22 gives data subjects the right not to be subject to **solely automated decisions** that produce legal or similarly significant effects, with exceptions. When an exception applies (explicit consent, contractual necessity, Member State law), Art. 22.3 requires the data controller to provide **meaningful information about the logic involved** and explain the expected outcome.

The AI Act and GDPR Art. 22 are **complementary, not alternative**: Art. 22 governs the individual's right to explanation; AI Act Art. 13–14 govern the system-level transparency for deployers and oversight persons. A high-risk AI system in the credit or HR space must satisfy both.

---

## 2. The ML Explainability Landscape: What Exists and What It Covers

### 2.1 Model-Agnostic Local Methods

**SHAP (SHapley Additive exPlanations)** — Lundberg & Lee (2017) — computes the contribution of each feature to a specific prediction using Shapley values from cooperative game theory. SHAP satisfies the axioms of local accuracy, missingness, and consistency. It is the most widely deployed production explainability method as of 2026.

*Regulatory coverage:* SHAP addresses Art. 13 (input sensitivity) and partially addresses the individual explanation component of GDPR Art. 22. Its limitation is that raw SHAP values require domain knowledge to interpret. A credit applicant presented with a SHAP waterfall chart showing "feature_43_employment_duration: −0.23" has not received a meaningful explanation.

**LIME (Local Interpretable Model-agnostic Explanations)** — Ribeiro et al. (2016) — builds a locally faithful linear approximation of the model in the neighbourhood of a specific prediction. More intuitive for end-users but less theoretically grounded than SHAP and less stable across similar inputs.

*Regulatory coverage:* similar to SHAP. Better for generating human-readable explanations; less rigorous for audit trails.

**Counterfactual Explanations** — Wachter et al. (2017) — "What would need to change for this decision to be different?" Directly actionable for the affected person: "If your debt-to-income ratio had been below 35%, the application would have been approved."

*Regulatory coverage:* the strongest method for GDPR Art. 22 individual explanations. Less useful for system-level Art. 13 transparency.

### 2.2 Attention Mechanisms and LLM Attribution

For transformer-based models (LLMs, BERT-family), attention weights were initially proposed as explanations. Research has since shown (Jain & Wallace 2019; Wiegreffe & Pinter 2019) that attention is not reliably explanatory — high attention to a token does not necessarily mean that token causally drives the output.

More reliable for LLMs:
- **Integrated Gradients** (Sundararajan et al. 2017) — computes the gradient of the output with respect to each input token, integrated along the path from a baseline
- **SHAP for transformers** — using partition or text SHAP (shap library ≥ 0.42)
- **Influence functions** — compute which training examples most influenced a specific prediction (computationally expensive but useful for audit)

### 2.3 Mechanistic Interpretability

An emerging research direction (Anthropic, DeepMind, EleutherAI) that attempts to understand the **internal circuits** of neural networks — which neurons, heads, and circuits implement specific capabilities. As of 2026, mechanistic interpretability remains primarily a research tool, not a production compliance method. However, for GPAI model providers, it is becoming a due-diligence expectation.

### 2.4 Global Methods: Feature Importance and Partial Dependence

Global feature importance (permutation importance, mean |SHAP|), partial dependence plots (PDPs), and accumulated local effects (ALEs) provide system-level transparency that directly maps to Art. 13.3.b requirements. These are relatively straightforward to generate and should be standard MLOps pipeline outputs for any high-risk system.

---

## 3. The Three-Layer Explainability Architecture

A production-grade explainability system for a regulated AI application must address three distinct audiences with three different explanation formats:

### Layer 1 — Model Developer (Debugging Layer)
**Purpose:** identify model failures, feature leakage, distribution shift, fairness issues.
**Methods:** SHAP summary plots, dependence plots, LIME stability analysis, disaggregated accuracy by subgroup.
**Format:** Python notebooks, Jupyter/MLflow artefacts, integrated in the MLOps pipeline.
**Regulatory mapping:** supports Annex IV §3 (development process), Art. 10 (data governance), Art. 9 (risk management).

### Layer 2 — Compliance Officer / Auditor (Audit Layer)
**Purpose:** demonstrate compliance with Art. 13, Art. 10 (data quality), and GDPR Art. 22.
**Methods:** global feature importance with statistical confidence intervals, fairness metrics by protected characteristic (demographic parity, equalised odds, individual fairness), counterfactual analysis showing decision boundary sensitivity, model cards (Mitchell et al. 2019).
**Format:** structured compliance report (PDF/HTML), audit trail, version-controlled artefact.
**Regulatory mapping:** directly maps to Annex IV §7 (logging), Art. 13 (transparency), Art. 72 (post-market monitoring).

### Layer 3 — Affected Natural Person (End-User Layer)
**Purpose:** satisfy the individual's right to understand a decision affecting them.
**Methods:** plain-language counterfactual explanation, key factors in natural language, actionable recommendations.
**Format:** conversational summary (max 3 sentences), potentially LLM-generated from SHAP values.
**Regulatory mapping:** GDPR Art. 22.3 (meaningful information about logic), AI Act Art. 13.1 (comprehensibility for deployers who relay to subjects).

---

## 4. AVM Explainability: The KHOME Case

Automated Valuation Models (AVMs) for real-estate pricing are a paradigmatic high-risk AI use-case that illustrates the three-layer architecture in practice.

### Regulatory context
Under RICS PS 1/2023 (Automated Valuation Models Professional Statement), AVMs used in regulated valuation contexts must: state their accuracy metrics (mean absolute percentage error — MAPE — by property type and geography), declare known limitations, and ensure that a qualified surveyor reviews AVM outputs before they are communicated as valuations. This RICS requirement is structurally identical to Art. 14 (human oversight) and Art. 13 (transparency).

### The explainability challenge
Real-estate valuation models in 2026 typically combine: gradient boosting on tabular features (location, size, construction year, amenities), spatial autocorrelation models (kriging or spatial lag), and increasingly LLM-based processing of free-text property descriptions. Each component requires a different explainability approach.

**For the tabular component:** SHAP TreeExplainer provides fast, exact Shapley values. Top drivers for a specific valuation: "proximity to public transport: +€45K, year built 1987 vs. 2015: −€32K, surface area 95m²: +€28K".

**For the spatial component:** LISA (Local Indicators of Spatial Association) maps visualise local spatial autocorrelation — "this property benefits from a high-value neighbourhood cluster in the 15th arrondissement".

**For the LLM text component:** token-level SHAP with the text SHAP variant identifies which phrases in the property description drove value (e.g., "parquet flooring original" → positive signal; "partial renovation" → uncertainty discount).

**The regulatory narrative (Layer 3):** "Your property has been valued at €485,000. The three primary drivers of this estimate are its location in a high-demand neighbourhood (contributes approximately €45,000 above the baseline), its surface area of 95m² (contributes +€28,000), and its 1987 construction year which is below the current new-build premium (reduces value by approximately €32,000 relative to equivalent new construction). This estimate was reviewed and validated by a RICS-qualified surveyor."

---

## 5. LLM-Based HR Scoring: Explainability Under Annex III Cat. 4

HR applications of LLMs (CV screening, performance scoring, promotion recommendations) fall under Annex III Category 4 and face the full weight of Chapter III Section 2 requirements. The explainability challenge is compounded by the opacity of generative models.

### The fundamental problem
A CV screening LLM produces a score and a rationale. The rationale is generated by the same model that produced the score — it may be a post-hoc rationalisation rather than a faithful explanation of the scoring computation. This is the **faithfulness problem** in LLM explainability, and it is directly relevant to Art. 13.

### Three mitigation strategies

**Strategy 1 — Structured feature extraction + transparent scoring.** Rather than letting the LLM score directly, use it to extract structured features (years of experience in domain X, educational background Y, project scale Z) and score against a transparent rubric. SHAP on the rubric scores provides genuine Layer 2 explanations.

**Strategy 2 — Faithfulness testing.** For any LLM that generates explanations, apply faithfulness tests: does removing the feature the model claims was decisive actually change the score? LIME-style perturbation tests can verify this.

**Strategy 3 — Human-in-the-loop gate.** Ensure that no LLM HR score directly produces a hiring/rejection decision without human review. This satisfies Art. 14.4.c (override capability) and, combined with documentation, may support Art. 6.3 reclassification to limited-risk.

---

## 6. Integrating Explainability into MLOps

Explainability is not a module to be added after a model is trained. For compliance with Art. 9 (risk management lifecycle) and Art. 72 (post-market monitoring), explainability must be:

1. **Trained in**, not bolted on: model architecture choices (tree-based vs. neural, calibrated vs. uncalibrated probabilities) affect explainability quality. A logistic regression or gradient boosted trees model with engineered features is often a better compliance choice than a black-box deep network, even if its AUC is marginally lower.

2. **Tested as part of CI/CD:** each model version should generate a standard explainability report as a build artefact. SHAP global importance, fairness metrics, and counterfactual examples should be tracked across versions with alerting on significant drift.

3. **Monitored in production:** SHAP feature importance distributions should be monitored in production. Significant drift in the relative importance of features between training and production is a signal of data drift that also impacts the accuracy of explanations.

4. **Versioned alongside the model:** the Annex IV documentation, including the explainability report, is a versioned artefact tied to a specific model version. Model registry (MLflow, SageMaker) should store these artefacts natively.

---

## References

1. Lundberg, S. M., Lee, S.-I. (2017). *A unified approach to interpreting model predictions*. NeurIPS 30.
2. Ribeiro, M. T., Singh, S., Guestrin, C. (2016). *"Why Should I Trust You?": Explaining the predictions of any classifier*. KDD 2016.
3. Wachter, S., Mittelstadt, B., Russell, C. (2017). *Counterfactual Explanations without Opening the Black Box*. Harvard JOLT, 31(2).
4. Sundararajan, M., Taly, A., Yan, Q. (2017). *Axiomatic Attribution for Deep Networks*. ICML 2017.
5. Jain, S., Wallace, B. C. (2019). *Attention is not Explanation*. NAACL 2019.
6. Wiegreffe, S., Pinter, Y. (2019). *Attention is not not Explanation*. EMNLP 2019.
7. Mitchell, M. et al. (2019). *Model Cards for Model Reporting*. FAccT 2019.
8. Doshi-Velez, F., Kim, B. (2017). *Towards a rigorous science of interpretable machine learning*. arXiv:1702.08608.
9. Arrieta, A. B. et al. (2020). *Explainable Artificial Intelligence (XAI): Concepts, taxonomies, opportunities and challenges*. Information Fusion, 58.
10. Goodman, B., Flaxman, S. (2017). *EU regulations on algorithmic decision-making and a "right to explanation"*. AI Magazine, 38(3).
11. EU. (2024). *Regulation (EU) 2024/1689 — AI Act*, Art. 13, 14, 72.
12. RICS. (2023). *Automated Valuation Models (AVMs) — Professional Statement PS 1/2023*.
13. EBA. (2022). *Guidelines on credit institutions' credit risk management practices — use of ML models in IRB systems (EBA/GL/2022/05)*. European Banking Authority.
14. Rudin, C. (2019). *Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead*. Nature Machine Intelligence, 1.
15. Slack, D. et al. (2020). *Fooling LIME and SHAP: Adversarial attacks on post hoc explanation methods*. AIES 2020.
16. Chen, H. et al. (2020). *True to the Model or True to the Data?* arXiv:2006.16234.
