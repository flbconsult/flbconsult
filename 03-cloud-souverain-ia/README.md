# 03 — Cloud Transformation & Sovereign Cloud in 2026

> *« Ne jamais signer un contrat hyperscaler sans clause de réversibilité chiffrée. »*

🇬🇧 **English** · 🇫🇷 [Français](#fr)

---

## Strategic question

> **Does sovereign cloud (*cloud souverain*) still make sense in 2026, when AI workloads structurally pull toward US-based hyperscalers — or is it a costly political posture?**

This section answers without ideological shortcuts. The honest answer is: **it depends on the workload, the regulatory exposure, and the data flow** — and the framework provided here makes that decision quantitatively, not rhetorically.

## Contents

| File | Type | What you'll find |
|---|---|---|
| [`docs/01-sovereign-cloud-2026-thesis.md`](./docs/01-sovereign-cloud-2026-thesis.md) | Thesis · 4 800 words · 18 references | The 2026 case (and limits) of sovereign cloud — Schrems II, FISA 702, CLOUD Act, EU Data Act, AI Act extraterritoriality. Three workload archetypes (sovereign-mandatory, sovereign-preferable, hyperscaler-rational). |
| [`docs/02-cloud-ia-co-evolution.md`](./docs/02-cloud-ia-co-evolution.md) | Paper · 3 600 words · 14 references | How AI workloads reshape cloud architecture: GPU economics, inference networks, data gravity, FinOps for LLMs. Implications for the make-or-buy decision in 2026. |
| [`code/sovereign_cloud_decision.py`](./code/sovereign_cloud_decision.py) | Python · CLI | Quantitative decision framework: scores a workload across 8 axes (data class, regulatory exposure, latency, cost, GPU need, reversibility, supply-chain risk, business continuity) → recommendation. |
| [`code/llm_finops_optimizer.py`](./code/llm_finops_optimizer.py) | Python · CLI | LLM cost optimiser: routes traffic to the cheapest provider that satisfies quality + residency constraints. Inspired by Vocalcom's 210 K€/yr savings playbook. |
| [`code/data_residency_analyzer.py`](./code/data_residency_analyzer.py) | Python · CLI | Verifies that a multi-cloud architecture respects GDPR Art. 44 + EU AI Act + sectorial residency constraints (HDS, SecNumCloud, RICS). |
| [`code/requirements.txt`](./code/requirements.txt) | Pinned deps | Standard-library only. |

## Key references

- ANSSI. (2024). *Référentiel SecNumCloud v3.2*.
- CJEU. (2020). *Schrems II — C-311/18*.
- US. (2018). *CLOUD Act — Clarifying Lawful Overseas Use of Data*.
- EU. (2023). *Regulation (EU) 2023/2854 — Data Act*.
- EU. (2024). *Regulation (EU) 2024/1689 — AI Act* (extraterritorial scope, Art. 2).
- EU. (2024). *Regulation (EU) 2024/903 — Interoperability of public services (IDA-NG)*.
- Patterson, D. et al. (2021). *Carbon Emissions and Large Neural Network Training*. arXiv:2104.10350.
- Hoffmann, J. et al. (2022). *Training Compute-Optimal Large Language Models* (Chinchilla). arXiv:2203.15556.
- DGFiP / French Treasury. (2024). *Doctrine «Cloud au centre»* (revised).
- Gartner. (2024). *Magic Quadrant for Strategic Cloud Platform Services*.
- Microsoft / Bleu, Orange / S3NS — operational reports on EU sovereign-cloud joint ventures.

## How to run

```bash
cd code
python sovereign_cloud_decision.py --workload-preset healthcare-ehr
python llm_finops_optimizer.py --demo
python data_residency_analyzer.py --architecture multi-region-failover
```

---

<a id="fr"></a>

## 🇫🇷 Version française

### Question stratégique

> **Le *cloud souverain* a-t-il encore du sens en 2026, alors que les charges IA tirent structurellement vers les hyperscalers américains — ou est-ce une posture politique coûteuse ?**

Ma réponse, après six missions de transformation cloud (Vocalcom Move2Cloud, AP-HP, ANS / 87 SAMU, KHOME) :

**Ni « tout hyperscaler », ni « tout souverain ».** En 2026, l'arbitrage ne se règle plus à coup d'idéologie, mais par **classification rigoureuse des charges de travail**. Les outils Python livrés avec cette section font cet arbitrage *par calcul*, pas par opinion.

### Trois archétypes de charges de travail (détaillés dans le papier 1)

1. **Souverain obligatoire** — données de santé HDS *non anonymisées*, OIV/OSE/OES sous LPM, certaines fonctions régaliennes. Pas d'arbitrage : SecNumCloud ou hébergement public certifié.
2. **Souverain préférable** — IP stratégique (modèles fine-tunés sur corpus métier), données financières DORA-critiques, données RH avec PII étendu. Le surcoût d'un cloud souverain (typiquement +20 à +40%) est légitime au regard du risque CLOUD Act / FISA 702.
3. **Hyperscaler rationnel** — workloads d'IA générique sur des données déjà publiques, calcul GPU intensif (entraînement de modèles), CDN, *all-purpose compute*. Le cloud souverain est ici un mauvais investissement : il coûte plus cher *et* il ne couvre pas le risque (la donnée n'est pas sensible).

### Mes éléments d'expérience qui nourrissent cette section

- **Vocalcom (2022–2023)** — Move2Cloud AWS multi-zones, **570 clients en production migrés**, **−35 % de coûts infrastructure**, **210 K€/an économisés** par optimisation FinOps.
- **AP-HP (2024)** — programme Orbis, datacenter privé HDS + hyperscaler en hybride, gestion de crise PRA après perte des deux datacenters le 3 août 2024.
- **ANS / 87 SAMU (2023)** — migration cloud à chaud sans interruption sur SI vital (30M d'appels/an).
- **My Brain Technologies (2020–2021)** — architecture **bi-cloud AWS-Azure** avec PCA réalisé.
- **Vivoka (2021–2022)** — choix OVH (souverain) pour l'IP NLP/NLU à enjeu brevets.
- **KHOME (2026)** — AWS RDS sur architecture régulée RICS/DORA — décision motivée par latence et FinOps, sécurité couverte par chiffrement client + résidence EU.

### Ma position en une phrase

> **Le cloud souverain est *nécessaire* mais pas *suffisant* en 2026 ; les charges IA, elles, sont *suffisamment* couvertes par un hyperscaler avec architecture sovereign-by-design (chiffrement client, résidence EU, contractualisation DORA), *sauf* sur les workloads où la donnée elle-même est régalienne.**
