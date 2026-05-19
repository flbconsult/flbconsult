# Sovereign Cloud in 2026 — Necessary, but Not Sufficient
### A workload-classified thesis on the relevance of *cloud souverain* in the AI era

**Author.** Franck Bongard — CIO/CTO, ISO 27005 Risk Manager.
**Status.** Working paper, v1.0, April 2026.
**Audience.** Boards, CIO/CTO, regulators, public-sector buyers.

---

## Abstract

The question *"does sovereign cloud still matter?"* has become unanswerable as posed. After six cloud-transformation engagements (Vocalcom Move2Cloud, ANS-SAMU, AP-HP, MyBrain, Vivoka, KHOME) and at the intersection of three legal regimes (Schrems II [CJEU, 2020], the US CLOUD Act [2018], and the EU Data Act [2023]), I argue that the decision must be made **per workload archetype**. I propose three archetypes — *sovereign-mandatory*, *sovereign-preferable*, *hyperscaler-rational* — and a quantitative scoring grid (8 axes) that matches a given workload to one archetype. The grid is materialised in `code/sovereign_cloud_decision.py`. The paper closes with three operational doctrines for an EU-headquartered enterprise in 2026.

---

## 1. Why the binary debate is harmful

In French executive committees in 2024–2026, the sovereign-cloud question is too often framed as binary: *for or against*. This framing is harmful because it conflates four distinct concerns:

1. **Legal extraterritoriality.** The US CLOUD Act [2018] and FISA Section 702 give US authorities lawful access to data held by US-headquartered providers, **regardless of where it is stored**. Schrems II [CJEU, 2020] invalidated the EU-US Privacy Shield on this basis. EU-US Data Privacy Framework (2023) restores limited adequacy but is, like its predecessors, structurally fragile.
2. **Operational supply-chain risk.** A provider that can be cut off by geopolitical action is a supply-chain risk independent of its data-protection posture.
3. **Vendor lock-in.** Concentration risk on a single hyperscaler is not solved by switching to another — it is solved by **reversibility and portability** by design.
4. **Industrial policy.** Whether to support European cloud providers as a matter of policy is a legitimate question, but it is **separate** from the operational question of where to host a given workload.

Conflating these four concerns produces ideological positions where calculation should suffice.

---

## 2. The eight axes of the decision grid

A workload should be scored along the following axes:

| # | Axis | What it captures | Score 0..5 |
|---|---|---|---|
| 1 | **Data classification** | Public · Internal · Confidential · Sensitive · Regulated (HDS, OIV/OSE) | higher = more sensitive |
| 2 | **Regulatory exposure** | DORA, AI Act high-risk, HDS, SecNumCloud, NIS2, CRA, EU Data Act | higher = more constrained |
| 3 | **Latency / locality need** | Edge / RT < 50 ms · LAN · WAN · async | higher = more local |
| 4 | **GPU & AI compute need** | None · Inference < 7B · Inference 7–70B · Training fine-tune · Training pre-train | higher = more GPU |
| 5 | **Reversibility cost** | Open standards · proprietary APIs · deeply integrated managed services | higher = more locked-in |
| 6 | **Cost (TCO over 5 yr)** | Sovereign baseline = 1.0 · hyperscaler typically 0.6–0.8 (compute) · 1.0–1.5 (egress) | quantitative |
| 7 | **Supply-chain risk** | Geopolitics, sanctions, key-person dependencies | higher = more risk |
| 8 | **Business continuity** | RTO / RPO targets, regulatory PCA/PRA testing requirements | higher = more demanding |

The Python tool `code/sovereign_cloud_decision.py` aggregates these scores into a single recommendation; the rationale is shown to the board. **No score is determinative on its own.** A workload with regulatory exposure 5 (HDS-clinical) goes to a sovereign provider regardless of cost; a workload with GPU need 5 (foundation-model pre-training) goes to a hyperscaler regardless of preference.

---

## 3. The three workload archetypes

### Archetype A — *Sovereign-mandatory*

**Examples:** Personal health records under HDS (clinical, not anonymised), data of operators of vital importance under LPM, defence and intelligence workloads, certain regalian functions (taxation, civil status).

**Decision:** SecNumCloud-certified provider (OVH, Cloud Temple, 3DS Outscale, and — depending on qualification scope — Bleu (Microsoft/Orange/Capgemini JV, milestone J1 passed) and S3NS (Google/Thales JV, qualified Dec. 2025)) **or** on-premise. Cost premium over hyperscaler is in the +20% to +40% range, accepted by regulation.

**Field reference:** AP-HP HDS workload during my Orbis programme — non-negotiable for clinical SIH data. Hyperscaler used only for non-clinical, anonymised analytical workloads.

### Archetype B — *Sovereign-preferable*

**Examples:** Strategic IP (proprietary models fine-tuned on company corpus), DORA-critical financial workloads, HR systems with extended PII, R&D pipelines for patentable inventions.

**Decision:** Sovereign by default, hyperscaler only with **strong sovereign-by-design** controls — customer-managed keys, EU-only residency contractually enforced, exit plan funded, multi-provider redundancy. The cost premium is justified by (i) reduced CLOUD Act exposure, (ii) reduced concentration risk, (iii) stronger reversibility narrative for procurement.

**Field reference:** Vivoka — choice of OVH for NLP/NLU IP at a stage where 6 patents were being filed; the decision was about **strategic IP exposure**, not technology.

### Archetype C — *Hyperscaler-rational*

**Examples:** Generic AI workloads on public or already-published data; CDN; all-purpose compute (microservices, websites, batch jobs); GPU training (a hyperscaler is structurally cheaper *and* faster); model inference on non-sensitive data.

**Decision:** Hyperscaler with sovereign-by-design *posture* (encryption, residency, contractualisation) but no sovereign-cloud premium paid. Sovereign cloud here is, in 2026, a *bad investment*: it costs more **and** it does not cover the risk (data is not sensitive).

**Field reference:** Vocalcom Move2Cloud — 570 customer tenants on AWS multi-zone, with €210k/year savings via FinOps. Sovereign cloud would have removed the savings and added zero risk reduction (data is operational telephony metadata, not regalian).

---

## 4. Three doctrines for 2026

### Doctrine 1 — *Sovereign-by-design before sovereign-by-vendor*

A hyperscaler workload with (a) customer-managed encryption keys, (b) EU-only residency contractually enforced, (c) DORA-grade exit plan, (d) cross-provider portability validated by drill, achieves **80% of the sovereignty effect at 30% of the cost**. Push every Archetype B workload through this filter before paying a sovereign-cloud premium.

### Doctrine 2 — *Reversibility is a contractual and architectural property, not a vendor brand*

The Vocalcom Move2Cloud taught me this concretely: a clean exit plan from AWS is more valuable than choosing OVH for political reasons. **Reversibility cost** (axis 5) should be capped — for any single workload — at 90 days and 1× annual run cost. Above this threshold, the workload is *de facto* locked-in regardless of the provider's marketing.

### Doctrine 3 — *AI-specific workloads need a separate cloud strategy*

Foundation-model training is structurally cheaper on hyperscalers (GPU economics, dedicated networks, optimised compilers). Pretending otherwise produces inflated R&D budgets without sovereignty gain. The right play in 2026: **train on hyperscaler GPUs with synthetic or public data; deploy inference on a sovereign edge for sensitive applications**. The training cost is incurred once; the inference residency matters every day.

This doctrine is consistent with the Patterson et al. (2021) and Hoffmann et al. (2022) compute-economics literature: training is 10–100× more compute-intensive than inference, and the marginal cost of moving training elsewhere is not justified by the residency benefit.

---

## 5. Three uncomfortable observations

1. **Most "sovereign cloud" deployments I have audited are sovereign in name only.** Either they use a sovereign provider but rely on US-controlled software dependencies (typical in JV constructs), or they tick the SecNumCloud box without the architectural reversibility that makes the certificate operationally meaningful.
2. **The EU AI Act is the new sovereignty frontier**, more than data residency. The Act applies extraterritorially (Art. 2): a US-built foundation model deployed in the EU triggers the obligations. Sovereignty in 2026 is increasingly about **model sovereignty** (training data, weights provenance, conformity assessment) rather than data centres.
3. **The carbon argument is misused on both sides.** Patterson et al. (2021) show that hyperscaler regions are often more carbon-efficient than national alternatives due to PUE and energy mix. Sustainability and sovereignty are not the same axis; conflating them weakens both arguments.

---

## 6. Conclusion

Sovereign cloud in 2026 is **necessary but not sufficient**. It is necessary for Archetype A workloads, where regulation makes the decision. It is preferable for Archetype B, where the strategic-IP rationale outweighs the cost premium. It is irrational for Archetype C, where the additional cost has no compensating risk reduction. Conflating the three archetypes is the fastest way to spend €10M on a sovereign-cloud programme that solves no operational problem.

The Python tools shipped with this paper let a CIO, a CTO or a board run the calculation per workload — and put the conversation back where it belongs: in spreadsheets, not on op-eds.

---

## References

1. ANSSI. (2024). *Référentiel SecNumCloud v3.2*.
2. ANSSI. (2024). *Recommandations de sécurité pour un SI fondé sur l'IA générative*.
3. CJEU. (2020). *Schrems II — C-311/18*.
4. CNIL. (2023). *Doctrine sur les transferts internationaux post Schrems II*.
5. DINUM / Premier Ministre. (2021, mis à jour 2024). *Doctrine «Cloud au centre» — Circulaire du Premier Ministre relative à la politique de l'État en matière de cloud informatique*. Direction interministérielle du numérique.
6. EU. (2022). *DORA — Regulation (EU) 2022/2554*.
7. EU. (2023). *Data Act — Regulation (EU) 2023/2854*.
8. EU. (2024). *AI Act — Regulation (EU) 2024/1689*.
9. EU. (2024). *Cyber Resilience Act — Regulation (EU) 2024/2847*.
10. Gartner. (2024). *Magic Quadrant for Strategic Cloud Platform Services*.
11. Hoffmann, J. et al. (2022). *Training Compute-Optimal Large Language Models*. arXiv:2203.15556.
12. ANSSI. (2024). *Prestataires qualifiés SecNumCloud — liste officielle*. Agence nationale de la sécurité des systèmes d'information. https://www.ssi.gouv.fr/entreprise/qualifications/prestataires-de-services-de-confiance-qualifies/
13. NIST. (2024). *Cybersecurity Framework 2.0*.
14. OECD. (2023). *Cross-border data flows and digital sovereignty*.
15. Patterson, D. et al. (2021). *Carbon Emissions and Large Neural Network Training*. arXiv:2104.10350.
16. US. (2018). *CLOUD Act — Clarifying Lawful Overseas Use of Data*.
17. Wachter, S. et al. (2019). *A right to reasonable inferences*. Columbia Business Law Review.
18. World Economic Forum. (2024). *Data Free Flow with Trust*.

---

*Citation: Bongard, F. (2026). Sovereign Cloud in 2026 — Necessary, but Not Sufficient. Working paper.*
