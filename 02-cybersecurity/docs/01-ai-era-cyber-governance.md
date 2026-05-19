# Cybersecurity Governance in the AI Era
### An integrated mapping of ISO 27005 · NIST CSF 2.0 · NIST AI RMF · EU AI Act · DORA · ISO/IEC 42001

**Author.** Franck Bongard — ISO 27005 Risk Manager (PECB), École de Guerre Économique, M2 IA Mines-Télécom Paris.
**Status.** Working paper, v1.0, April 2026.
**Audience.** CISO, CIO, CTO, Risk officers, Board members, Audit committees.

---

## Abstract

By 2026, an EU-headquartered enterprise that deploys Generative AI in production must satisfy at least **six overlapping governance instruments**: ISO/IEC 27005 (risk management), ISO/IEC 27001 (ISMS), NIST CSF 2.0 (control framework), NIST AI RMF (AI-specific risk function), the EU AI Act (regulatory obligations), DORA (operational resilience for financial entities), and increasingly ISO/IEC 42001 (AI management system). Treated separately, these produce a *compliance theatre* — duplicated controls, distinct audit trails, and an exhausted security team. Treated as one **integrated control matrix**, they reduce to roughly 60 distinct control families. This paper presents that mapping, and argues for three operating principles: (1) ISO 27005 as the *risk register backbone*; (2) NIST AI RMF as the *AI-specific function overlay*; (3) DORA / AI Act as *external assertions* drawn from (1) and (2). The Python tools shipped with this paper materialise the mapping in code.

---

## 1. The fragmentation problem

A real-life example, from a 2025 pre-DORA engagement: a French neo-bank's risk register held **234 controls**. After a 6-week audit, **41% of these controls duplicated each other** under different framework labels — the same MFA control reported as ISO 27001 A.5.17, NIST CSF PR.AA-01, and DORA Art. 9. The duplication was the symptom; the cause was the absence of a single canonical control taxonomy.

The same fragmentation now hits the AI layer:

- **ISO/IEC 42001** (AI management system, 2023) prescribes governance, accountability, lifecycle.
- **NIST AI RMF** (2023) prescribes *Govern*, *Map*, *Measure*, *Manage* functions.
- **EU AI Act** (2024) imposes regulatory categories: prohibited, high-risk, limited, minimal.
- **NIST CSF 2.0** (2024) elevates *Govern* to a sixth function — closing the prior gap with AI RMF.

Each of these is internally coherent. None of them is jointly enforceable without an integration layer.

---

## 2. The integrated control matrix

I use a 6-axis × 10-control-family matrix that collapses the redundancy. The axes are:

| Axis | Label | Source frameworks |
|---|---|---|
| **A** | Identify & Govern | ISO 27001 A.5, NIST CSF Govern + Identify, NIST AI RMF Govern + Map, ISO 42001 §6 |
| **B** | Protect (Identity, Data, Apps) | ISO 27001 A.5–A.8, NIST CSF Protect, ANSSI ZTNA |
| **C** | Detect & Observe | ISO 27001 A.8.16, NIST CSF Detect, OpenTelemetry traces (LLM extension) |
| **D** | Respond & Recover (PCA/PRA) | ISO 22301, NIST CSF Respond + Recover, DORA Art. 11–14 |
| **E** | AI-Specific Controls | NIST AI RMF Measure + Manage, ISO 42001 §7–§10, EU AI Act Art. 8–17 |
| **F** | Third-Party & Supply-Chain | ISO 27036, DORA Art. 28–30, EU AI Act Art. 25 (general-purpose AI providers) |

Within each axis, the **10 control families** are: *access*, *cryptography*, *secure development*, *vulnerability management*, *logging*, *incident response*, *backup & continuity*, *physical & supplier*, *privacy*, and — new in 2026 — *AI lifecycle*.

This 6×10 grid is **60 control families** total. Compared to 234 line items, it is auditable in a 1-day workshop with the CISO, the architecture team, and Legal.

The Python tool [`code/iso27005_risk_calculator.py`](../code/iso27005_risk_calculator.py) operationalises the matrix: each risk in the register references one or more matrix cells, and the residual-risk computation aggregates control effectiveness across cells. Auditors get a **single risk view** instead of three.

---

## 3. Three operating principles

### 3.1 ISO 27005 as the *risk register backbone*

ISO/IEC 27005:2022 is methodologically clean: define context → identify assets → identify threats and vulnerabilities → estimate likelihood and impact → evaluate against criteria → treat. It is the only standard among the six that **mandates a quantitative or semi-quantitative method**, and it integrates naturally with the COSO ERM framework used by Boards.

In every CISO/CTO mandate I have led — Vocalcom, Vivoka, AP-HP, KHOME — I have used ISO 27005 as the *single source of truth for risk*. NIST CSF, NIST AI RMF, DORA and the AI Act then *consume* this register; they don't recreate it. This is the single most impactful design decision of an integrated programme.

### 3.2 NIST AI RMF as the *AI-specific function overlay*

NIST AI RMF (2023) introduces four functions: **Govern, Map, Measure, Manage**. Each AI use case in the register inherits these functions as additional metadata:

- **Govern**: ownership, accountability, escalation path.
- **Map**: classify the use case (EU AI Act risk class, sector, data sensitivity).
- **Measure**: evaluation suite, drift monitoring, fairness tests.
- **Manage**: incident response runbook, kill-switch criteria.

NIST AI RMF is **not** a list of controls — it is a *function* that overlays the existing ISO 27005 register. This non-substitutive design is what makes it implementable.

### 3.3 DORA / AI Act as *external assertions* drawn from (1) and (2)

DORA mandates ICT third-party risk management (Art. 28–30), incident classification and reporting (Art. 17–23), digital operational resilience testing (Art. 24–27), and information sharing (Art. 45). The AI Act mandates conformity assessments (Art. 43), post-market monitoring (Art. 72), and CE marking for high-risk systems.

In a well-designed programme, **these are reports, not parallel processes**. The same risk register feeds:

- DORA's *register of information* (Art. 28(3)).
- The AI Act's *technical documentation* (Annex IV).
- ISO 42001's AIMS audit trail.
- The Board's quarterly cyber dashboard.

A single tool — see [`code/dora_compliance_mapper.py`](../code/dora_compliance_mapper.py) — can extract the DORA-specific view; a second tool extracts the AI Act view. The risk register is queried, not duplicated.

---

## 4. Five new threat classes the matrix must cover in 2026

Beyond classical IT threats, an AI-augmented SI faces a recognisable set of new hostile actions. I summarise them here; they are detailed in [the second paper](./02-llm-threat-modeling.md):

1. **Prompt injection** (direct and indirect) — Greshake et al., 2023 [arXiv:2302.12173].
2. **Training-data extraction & memorisation leaks** — Carlini et al., 2021 (USENIX Security '21).
3. **Model supply-chain attacks** — compromised weights, poisoned fine-tuning datasets, malicious model cards.
4. **Multi-tenant data leakage via embedding spaces** — under-discussed in the literature, observed in production.
5. **Agentic-tool misuse** — the agent has more authority than its prompt suggests. Exploits the gap between the model's safety training and the tool ACL.

Each maps to a row of the matrix (Axis E). Each has an OWASP LLM Top-10 (2025) entry. None is covered by classical NIST 800-53 controls without explicit extension.

---

## 5. Concrete recommendations

For a Tier-1 enterprise (CAC 40, large CHU, regulated finance) I recommend a programme in four phases over 12–18 months:

| Phase | Duration | Deliverables |
|---|---|---|
| **Phase 1 — Inventory** | 6 weeks | Asset register (incl. AI use cases), data classification, current control mapping to the 6×10 matrix. |
| **Phase 2 — Gap analysis** | 4 weeks | Per-cell residual-risk scoring (ISO 27005), DORA gap report, AI Act classification per use case. |
| **Phase 3 — Remediation** | 6–12 months | Prioritised investment plan; AI-specific controls deployed (eval-on-PR, prompt-injection probes, agentic kill-switches, LLM trace store wired to SOC). |
| **Phase 4 — Continuous assurance** | ongoing | ISO 42001 certification (optional but increasingly Board-expected), DORA TLPT exercises, EU AI Act post-market monitoring. |

Funding signal: in the most efficient programmes I have led, **AI-specific controls represent 15–25% of total cyber budget** by year 2 of an AI-Native transition. Below 10% indicates a control gap; above 30% usually indicates duplication with ISO 27001 controls that should be rationalised.

---

## 6. Conclusion

An integrated cyber-AI governance programme is not free, but it is **substantially cheaper and more credible** than the alternative — running parallel ISO, NIST, DORA and AI Act streams. The investment pays back when an auditor, a regulator, or — increasingly — a customer's procurement function asks: *show me how you govern your AI risks*. A single, queryable risk register, mapped to the six frameworks, answers that question in 30 minutes. A federation of spreadsheets does not.

The Python tools shipped alongside this paper are deliberately small: they prove the matrix is computable, not just describable.

---

## References

1. ANSSI. (2024). *Recommandations de sécurité pour un SI fondé sur l'IA générative*.
2. Carlini, N. et al. (2021). *Extracting Training Data from Large Language Models*. USENIX Security '21.
3. CNIL. (2024). *AI How-to Sheets for GDPR Compliance*.
4. EU. (2022). *Regulation (EU) 2022/2554 — DORA*.
5. EU. (2024). *Regulation (EU) 2024/1689 — Artificial Intelligence Act*.
6. Greshake, K. et al. (2023). *Not what you've signed up for: Compromising real-world LLM-integrated apps with indirect prompt injection*. arXiv:2302.12173.
7. ISO/IEC 27001:2022 — *Information security management systems — Requirements*.
8. ISO/IEC 27005:2022 — *Information security risk management*.
9. ISO/IEC 42001:2023 — *AI management system*.
10. ISO/IEC 23894:2023 — *AI Risk Management Guidance*.
11. MITRE ATLAS (2024) — *Adversarial Threat Landscape for AI Systems*.
12. NIST. (2023). *AI Risk Management Framework 1.0*. NIST AI 100-1.
13. NIST. (2024). *Cybersecurity Framework 2.0*. NIST CSWP 29.
14. NIST. (2024). *AI 600-1 — Generative AI Profile*.
15. OWASP. (2025). *Top 10 for Large Language Model Applications*.
16. Shevlane, T. et al. (2023). *Model evaluation for extreme risks*. arXiv:2305.15324.

---

*Citation: Bongard, F. (2026). Cybersecurity Governance in the AI Era. Working paper.*
