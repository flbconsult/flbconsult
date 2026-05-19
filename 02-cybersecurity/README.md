# 02 — Cybersecurity in the AI Era

> *« Sécurité par conception, conformité par défaut. »*

🇬🇧 **English** · 🇫🇷 [Français](#fr)

---

## Strategic question

> **How do ISO 27005, NIST AI RMF, DORA and the EU AI Act combine to govern an enterprise SI augmented by Generative AI — without producing a compliance theatre that slows the business?**

Cybersecurity in 2026 is no longer about endpoint protection or perimeter defence. It is about **governing learning systems** that are simultaneously a productivity asset, an attack surface, and a regulated artifact. This section provides the conceptual map and the operational toolkit.

## Contents

| File | Type | What you'll find |
|---|---|---|
| [`docs/01-ai-era-cyber-governance.md`](./docs/01-ai-era-cyber-governance.md) | Paper · 4 200 words · 16 references | Mapping of ISO 27005 → NIST CSF 2.0 → NIST AI RMF → EU AI Act → DORA → ISO/IEC 42001. The integrated control matrix I use in due-diligence. |
| [`docs/02-llm-threat-modeling.md`](./docs/02-llm-threat-modeling.md) | Paper · 3 600 words · 12 references | Adapting STRIDE and LINDDUN to LLM-driven systems. OWASP LLM Top-10 (2023/2025) integrated. Field examples from People First and KHOME. |
| [`code/iso27005_risk_calculator.py`](./code/iso27005_risk_calculator.py) | Python · CLI | ISO 27005:2022 quantitative risk calculator: assets × threats × vulnerabilities × controls → residual risk + treatment recommendation. |
| [`code/llm_threat_modeler.py`](./code/llm_threat_modeler.py) | Python · CLI | STRIDE/LINDDUN-for-LLM threat-modelling assistant. Generates a threat catalogue and OWASP LLM Top-10 mapping for a given architecture. |
| [`code/dora_compliance_mapper.py`](./code/dora_compliance_mapper.py) | Python · CLI | Maps a list of ICT third parties (incl. LLM providers) to the DORA five pillars; emits a gap-analysis CSV. |
| [`code/requirements.txt`](./code/requirements.txt) | Pinned deps | Standard-library only by design. |

## Key references

- ISO/IEC 27005:2022 — *Information security risk management*.
- ISO/IEC 27001:2022 — *Information security management systems — Requirements*.
- ISO/IEC 42001:2023 — *AI management system*.
- NIST CSF 2.0 (2024) — *Cybersecurity Framework*.
- NIST AI RMF 1.0 (2023) — *AI Risk Management Framework*.
- EU. (2022). *DORA — Regulation (EU) 2022/2554*.
- EU. (2024). *AI Act — Regulation (EU) 2024/1689*.
- ANSSI. (2024). *Recommandations de sécurité pour un SI fondé sur l'IA générative*.
- OWASP. (2025). *Top 10 for Large Language Model Applications*.
- Greshake, K. et al. (2023). *Not what you've signed up for: Compromising real-world LLM-integrated apps with indirect prompt injection*. arXiv:2302.12173.
- Carlini, N. et al. (2021). *Extracting Training Data from Large Language Models*. USENIX Security '21.
- MITRE ATLAS. (2024). *Adversarial Threat Landscape for AI Systems*.

## How to run the code

```bash
cd code
python iso27005_risk_calculator.py --demo
python llm_threat_modeler.py --architecture rag-customer-facing
python dora_compliance_mapper.py --providers providers.json
```

---

<a id="fr"></a>

## 🇫🇷 Version française

### Question stratégique

> **Comment ISO 27005, NIST AI RMF, DORA et l'EU AI Act se combinent-ils pour gouverner un SI augmenté par l'IA générative — sans produire un théâtre de conformité qui ralentit le business ?**

### Mes éléments d'expérience qui nourrissent cette section

- **ISO 27005 Risk Manager** (PECB, 2022–2029) — méthodologie au cœur de cette section.
- **École de Guerre Économique** — Cyber Stratégie des Entreprises (2020).
- **Vocalcom (2022–2023)** — création PSSI/PCA, SOC 24/7, **certification ISO 27001 obtenue**.
- **AP-HP (2024)** — exercice **CRYPTEX4** (simulation cyberattaque majeure JO 2024) ; gestion de crise PRA après perte des deux datacenters le 3 août 2024.
- **Comsec (2003–2006)** — pentests, social engineering, sécurisation de sites sensibles avec biométrie.
- **HDS, RGPD, SecNumCloud, DORA, NIS2** — mises en conformité réalisées sur 6 missions différentes.

### Trois principes de gouvernance que je défends en 2026

1. **Le LLM provider EST un tiers critique au sens DORA.** Inutile de chercher de subtilité juridique — un GPT-5 / Claude / Gemini en production sur un parcours bancaire est un tiers critique. Le contrat, les SLA, les plans de sortie, les tests de résilience opérationnelle doivent être à la hauteur.
2. **La conformité IA Act se sous-traite mal.** Externaliser la classification *risque inacceptable / haut risque / risque limité / risque minimal* à une équipe juridique sans co-pilotage technique produit des décisions architecturales mal informées et coûteuses à corriger.
3. **Le SOC 24/7 doit voir les traces LLM.** Sans observabilité des appels LLM (Langfuse, Phoenix, traces OpenTelemetry étendues), le SOC est aveugle à la moitié de la surface d'attaque applicative en 2026.
