# EU AI Act — Classification Framework & Conformity Assessment for Enterprise AI Systems

**Module 04 — Paper 1 · ~4 500 words · 20 references**

> *« The AI Act does not regulate AI. It regulates the risk that AI systems impose on people. That distinction changes everything about how a CTO should approach compliance. »*

---

## Abstract

The EU Artificial Intelligence Act (Regulation 2024/1689), fully applicable from August 2026, introduces a risk-tiered governance framework for AI systems operating in the European Union. This paper provides a CTO-oriented classification methodology across the four risk tiers, a detailed analysis of the eight Annex III high-risk categories, a treatment of prohibited practices under Article 5, and a practical framework for managing the conformity assessment process without sacrificing innovation velocity. The paper draws on field experience from AI deployments in healthcare (AP-HP), real-estate valuation (KHOME), and HR automation (People First Technologies).

---

## 1. The Risk Pyramid: Four Tiers, Not a Binary

The AI Act's architecture is fundamentally a **risk pyramid** with four levels. Most compliance discussions collapse this into a binary (high-risk / not high-risk), which is analytically wrong and operationally dangerous.

### 1.1 Prohibited Practices (Article 5)

Article 5 enumerates AI practices that are **absolutely prohibited** — no conformity assessment, no exception for legitimate purpose. The eight prohibited categories in the final text include:

- **Subliminal or manipulative techniques** that distort behaviour in ways persons cannot resist, causing harm (Art. 5.1.a)
- **Exploitation of vulnerabilities** of specific groups (children, elderly, disabled) to distort behaviour causing harm (Art. 5.1.b)
- **Social scoring** by public authorities — rating natural persons based on behaviour or personality traits to produce detrimental or unjustified treatment (Art. 5.1.c)
- **Real-time remote biometric identification** in publicly accessible spaces for law enforcement (Art. 5.1.d), with narrow exceptions for targeted searches of missing persons, terrorism prevention, and prosecution of specific serious crimes
- **Biometric categorisation** to infer sensitive attributes (race, political opinion, trade union membership, religious belief, sexual orientation) (Art. 5.1.e)
- **Emotion recognition** in workplace and educational settings (Art. 5.1.f)
- **Facial recognition databases** assembled by scraping from the internet or CCTV (Art. 5.1.g)
- **Predictive policing** based solely on profiling (Art. 5.1.h)

**CTO implication:** before any risk-tier classification exercise, a rapid Article 5 screen is mandatory. Systems that touch HR sentiment analysis, customer emotion inference, or biometric processing in physical spaces must pass this screen first.

### 1.2 High-Risk AI Systems (Article 6 + Annex III)

High-risk status is assigned on two tracks:

**Track A — Safety components (Art. 6.1):** AI systems that are themselves safety components of products covered by Union harmonisation legislation listed in Annex I (medical devices, machinery, civil aviation, rail systems, etc.) and which require a third-party conformity assessment under that legislation. These systems inherit high-risk status from their product category.

**Track B — Standalone high-risk applications (Art. 6.2 + Annex III):** AI systems listed in the eight Annex III categories, regardless of whether they are embedded in a regulated product.

A critical nuance introduced in the final text: an Annex III system **may be reclassified to lower risk** if it meets both conditions of Art. 6.3 — (a) it is not intended to make decisions with significant adverse effect on persons, and (b) the provider demonstrates through a self-assessment that the system does not pose a significant risk. This reclassification must be documented and made available to national competent authorities upon request (Art. 6.3).

### 1.3 Limited-Risk AI Systems

Systems subject to **transparency obligations only** (Art. 50): chatbots must disclose they are AI; deepfakes must be labelled; AI-generated content must be machine-readable as such. Obligations are lighter but non-trivial for consumer-facing systems.

### 1.4 Minimal-Risk AI Systems

The vast majority of AI systems fall here — AI spam filters, AI-powered video games, AI recommender systems for entertainment. No mandatory requirements beyond good practice and voluntary codes of conduct.

---

## 2. The Eight Annex III Categories: A CTO's Taxonomy

### Category 1 — Biometrics (Annex III §1)
Remote biometric identification systems, biometric categorisation systems, emotion recognition systems. The real-time prohibition of Art. 5 leaves this category primarily applying to post-hoc or batch biometric processing (e.g., access control with face recognition in controlled environments, verification systems). **Sector relevance:** physical security, HRM time & attendance.

### Category 2 — Critical Infrastructure (Annex III §2)
AI systems used for safety components in management and operation of critical digital infrastructure, road traffic, water/gas/electricity supply. **Sector relevance:** telecom operators, utilities, transport. Notable: the definition of "safety component" is deliberately broad — an AI that optimises network routing in a way that could cause outages qualifies.

### Category 3 — Education and Vocational Training (Annex III §3)
Systems that determine access to, or admission into, educational institutions; assessment of learning outcomes; evaluation of students. **Sector relevance:** ed-tech, corporate learning platforms. An LLM-based exam grader that affects progression is high-risk.

### Category 4 — Employment, Workers Management and Access to Self-Employment (Annex III §4)
Systems used for recruitment (CV screening, interview analysis), promotion decisions, task allocation, and performance monitoring. **This is the highest-frequency high-risk category for enterprise AI in 2026.** Any LLM-based HR platform doing automated CV filtering or performance scoring falls here. **Sector relevance:** People First Technologies (HR × LLM/RAG) is a direct example.

### Category 5 — Essential Private and Public Services (Annex III §5)
Credit scoring and creditworthiness assessment; life and health insurance risk assessment; emergency services dispatch prioritisation; benefit eligibility determination by public authorities. **Sector relevance:** financial services, insurance, public sector.

### Category 6 — Law Enforcement (Annex III §6)
Risk assessment of persons for criminal offences; polygraphs; reliability assessment of evidence; crime prediction systems; profiling in criminal investigations. **Sector relevance:** minimal for commercial CTOs, high for public-sector DSI/RSSI.

### Category 7 — Migration, Asylum and Border Control (Annex III §7)
Lie detection systems for border control; risk assessment of irregular migration; document authenticity examination. **Sector relevance:** government and public-sector IT.

### Category 8 — Administration of Justice and Democratic Processes (Annex III §8)
AI systems assisting courts in legal research, judicial decisions, or election outcome prediction. **Sector relevance:** legaltech, govtech.

---

## 3. The GPAI Dimension: General-Purpose AI Models (Articles 51–56)

The AI Act introduces a distinct regulatory track for **General-Purpose AI (GPAI) models** — foundation models that can be fine-tuned or prompted for a wide range of downstream tasks. This is the track that governs GPT-4, Claude, Gemini, Llama, Mistral, and their successors.

The key distinction for enterprise CTOs: **GPAI providers** (Anthropic, OpenAI, Meta, Mistral) carry compliance obligations; **GPAI deployers** (enterprises building on these models) inherit residual obligations through the value chain.

**Systemic risk models** (Art. 51) — GPAI models with training compute exceeding 10^25 FLOPs or demonstrating high-impact capabilities — face additional obligations: adversarial testing, incident reporting to the Commission, cybersecurity measures, and energy efficiency disclosure.

**CTO implication:** when an enterprise fine-tunes a GPAI model on proprietary data, it becomes a **provider of a derived AI system** and may inherit high-risk status if the downstream use falls under Annex III. The contractual due-diligence chain (provider → deployer → user) must be explicitly mapped.

---

## 4. The Article 9 Risk Management System

For High-Risk AI systems, Article 9 mandates a **continuous risk management system** — not a one-time assessment, but a lifecycle process. The six required elements are:

1. **Risk identification and analysis** — identify known and reasonably foreseeable risks the system may pose in its intended use and reasonably foreseeable misuse
2. **Risk estimation and evaluation** — considering the severity, probability and reversibility of harm
3. **Residual risk evaluation** after implementation of risk mitigation measures
4. **Testing** — to verify conformity with Art. 9 requirements, including testing on real-world conditions
5. **Residual risk communication** — in the instructions for use (Art. 13)
6. **Review and update** — at each substantial modification and periodically throughout the lifecycle

The Art. 9 risk management system must be **documented** (feeds into Annex IV), **reviewed by the quality management system** (Art. 17), and maintained throughout the product lifecycle. It is not a legal deliverable — it is a **living technical document** that the CTO's team owns.

---

## 5. Annex IV: Technical Documentation Requirements

Article 11 requires providers of high-risk AI systems to establish and maintain technical documentation that demonstrates conformity with the requirements of Chapter III Section 2. Annex IV specifies nine categories of required documentation:

1. General description of the AI system (intended purpose, version, release date)
2. Description of components (hardware, software, data, pre-trained models used)
3. Description of the development process
4. Description of the monitoring, functioning and control system
5. Description of the risk management system (Art. 9)
6. Description of data management (training, validation, test datasets — including data governance and examination procedures per Art. 10)
7. Description of the logging capabilities (Art. 12)
8. Instructions for use (Art. 13)
9. Description of the human oversight measures (Art. 14)

**CTO architectural implication:** Annex IV is not a documentation artefact to be produced at audit. It is a **template for MLOps pipeline gates**. Each item in Annex IV corresponds to a CI/CD stage that should produce the required documentation as a build artefact. This is the only way to keep Annex IV current at the pace of model iteration.

---

## 6. The Art. 6.3 Reclassification Strategy

The most underused provision of the AI Act for enterprise CTOs is **Article 6.3**, which allows an Annex III system to be reclassified to limited risk if it meets both conditions:

- The system does not make autonomous decisions with significant adverse effect on a natural person's health, safety, fundamental rights, or legal status
- The provider documents through self-assessment that the system does not pose a significant risk of harm

This reclassification is not automatic — it requires a documented self-assessment that must be retained and made available to national competent authorities upon request — there is no proactive notification obligation. But it opens a legitimate architecture path: **introducing a human decision gate** that makes the AI system advisory rather than decisional removes it from high-risk status.

**Example:** an AVM system that produces a valuation range and presents it to a human expert who validates before any lending decision is communicated to the borrower can legitimately argue for reclassification, provided the human decision gate is genuine (not a rubber-stamp). At KHOME, this architectural choice was made explicitly for RICS compliance — it has the secondary benefit of avoiding high-risk status.

---

## 7. Operationalising Compliance: The CTO's Three-Phase Approach

### Phase 1 — Inventory and Classification (Weeks 1–4)
Produce an AI system inventory. For each system: apply the Art. 5 screen, then the Art. 6 / Annex III classification. Document the classification rationale. This is an architectural judgment, not a legal judgment — engage the CTO function, not only legal counsel.

### Phase 2 — Gap Analysis Against Chapter III Requirements (Weeks 4–12)
For high-risk systems: assess current state against the 47-item checklist (see `code/ai_act_conformity_checker.py`). Prioritise findings by: (a) severity of the gap and (b) speed to remediate. Most enterprises find their largest gaps in data governance (Art. 10), logging (Art. 12), and post-market monitoring (Art. 72).

### Phase 3 — Continuous Compliance Integration (Ongoing)
Integrate Annex IV documentation into the MLOps pipeline. Integrate Art. 9 risk events into the incident management system. Automate Art. 72 post-market monitoring metrics. Establish a human oversight review cadence for Art. 14.

---

## 8. The Innovation Velocity Tension

The central operational risk of AI Act compliance is **over-classification**: a risk-averse legal team that classifies every LLM application as high-risk, triggering full Annex IV requirements, will add 3–6 months to every AI project. This is not compliance — it is compliance theatre.

The CTO's role is to **own the classification decision** and defend it technically. Three principles:

1. **The Act regulates use-case risk, not model capability.** A powerful LLM used to summarise internal meeting notes is minimal risk. The same model used to score job applicants is Annex III cat. 4. The model is identical; the regulatory status differs entirely by deployment context.

2. **Architecture shapes regulatory status.** Human-in-the-loop design, explainability measures, confidence thresholds, and scope limitations are not just safety features — they are regulatory levers that can shift a system from high-risk to limited-risk.

3. **Compliance infrastructure is a competitive moat.** Enterprises that build Art. 9 / Annex IV compliance into their MLOps pipelines in 2025–2026 will deploy AI faster in 2027–2028 than competitors who treat compliance as an afterthought. The upfront investment amortises across every subsequent AI system.

---

## References

1. EU. (2024). *Regulation (EU) 2024/1689 of the European Parliament and of the Council — Artificial Intelligence Act*. OJ L, 2024/1689.
2. ISO/IEC 42001:2023. *Information technology — Artificial intelligence — Management system*.
3. NIST. (2023). *AI Risk Management Framework (AI RMF 1.0)*. NIST AI 100-1.
4. ANSSI. (2024). *Recommandations de sécurité pour les systèmes fondés sur l'IA générative*. Agence nationale de la sécurité des systèmes d'information.
5. ENISA. (2023). *Multilayer Framework for Good Cybersecurity Practices for AI*. ENISA Report.
6. EDPB. (2023). *Opinion 28/2023 on certain data protection aspects related to the processing of personal data in the context of AI models*. European Data Protection Board.
7. AI HLEG. (2019). *Ethics Guidelines for Trustworthy AI*. European Commission.
8. Floridi, L. et al. (2018). *AI4People — An Ethical Framework for a Good AI Society*. Minds and Machines, 28(4).
9. Goodman, B., Flaxman, S. (2017). *EU regulations on algorithmic decision-making and a "right to explanation"*. AI Magazine, 38(3).
10. Wachter, S., Mittelstadt, B., Russell, C. (2017). *Counterfactual Explanations without Opening the Black Box: Automated Decisions and the GDPR*. Harvard Journal of Law & Technology, 31(2).
11. Doshi-Velez, F., Kim, B. (2017). *Towards a rigorous science of interpretable machine learning*. arXiv:1702.08608.
12. Mittelstadt, B. et al. (2016). *The ethics of algorithms: Mapping the debate*. Big Data & Society, 3(2).
13. Binns, R. (2018). *Fairness in Machine Learning: Lessons from Political Philosophy*. FAT* 2018.
14. Veale, M., Borgesius, F. Z. (2021). *Demystifying the Draft EU Artificial Intelligence Act*. Computer Law Review International, 22(4).
15. Laux, J., Wachter, S., Mittelstadt, B. (2024). *Three Pathways to Lay Governance of Artificial Intelligence in the EU*. European Journal of Law and Technology.
16. RICS. (2023). *Automated Valuation Models (AVMs) — Professional Statement*. Royal Institution of Chartered Surveyors.
17. Hadfield-Menell, D. et al. (2017). *The Off-Switch Game*. IJCAI 2017.
18. Kop, M. (2021). *EU Artificial Intelligence Act: The European Approach to AI*. Transatlantic Antitrust and IPR Developments, Stanford-Vienna.
19. Mökander, J., Floridi, L. (2021). *Ethics-Based Auditing to Develop Trustworthy AI*. Minds and Machines, 31.
20. Palomares, I. et al. (2021). *Advances in Consensus Reaching in AI Ethics*. Information Fusion, 66.
