# Threat Modelling for LLM-Driven Systems
### Adapting STRIDE and LINDDUN to Generative AI

**Author.** Franck Bongard — ISO 27005 Risk Manager.
**Status.** Working paper, v1.0, April 2026.

---

## Abstract

Classical threat-modelling frameworks — STRIDE [Howard & LeBlanc, 2002] and LINDDUN [Deng et al., 2011] — were designed for client-server applications with deterministic logic. They under-cover an architecture in which the central component is a stochastic, prompt-conditioned model that can be steered by adversarial inputs hidden in *retrieved content*. This paper proposes operational extensions of STRIDE and LINDDUN for LLM-driven systems, mapped to the OWASP LLM Top-10 (2025) and to MITRE ATLAS. The proposed extensions are then materialised in a Python threat-modelling assistant (`code/llm_threat_modeler.py`).

---

## 1. Why classical frameworks fall short

STRIDE classifies threats as Spoofing / Tampering / Repudiation / Information disclosure / Denial of service / Elevation of privilege. LINDDUN classifies privacy threats as Linkability / Identifiability / Non-repudiation / Detectability / Disclosure of information / Unawareness / Non-compliance. Both assume:

- A clear **trust boundary** between user input and processing logic.
- **Deterministic** processing.
- **Static** code as the locus of vulnerability.

LLM systems break all three assumptions:

1. **Trust boundaries leak.** Indirect prompt injection [Greshake et al., 2023] embeds malicious instructions in *retrieved* content the user never sees, blurring the boundary between data and control.
2. **Stochastic outputs.** The same input can produce different outputs; the same exploit can fail 9 times and succeed once. Detection must be statistical, not binary.
3. **The model itself is the vulnerability.** Memorisation [Carlini et al., 2021], jailbreaks, and emergent capabilities [Wei et al., 2022] cannot be patched by fixing application code.

---

## 2. STRIDE-LLM: an extended threat catalogue

I propose six **LLM-specific extensions** of STRIDE, each mapped to the OWASP LLM Top-10 (2025).

| STRIDE classical | STRIDE-LLM extension | OWASP LLM 2025 | Example field exploit |
|---|---|---|---|
| **S**poofing | *Identity injection via retrieved content* | LLM01 (Prompt Injection) | Adversarial document in a RAG corpus impersonates the system role and overrides instructions. |
| **T**ampering | *Model output manipulation via injection* | LLM01, LLM06 (Excessive Agency) | An attacker controls a calendar invite the agent reads; the agent then exfiltrates emails because the invite says so. |
| **R**epudiation | *Trace plausible-deniability* | LLM05 (Improper Output Handling) | Lack of LLM trace store; abuse cannot be reconstructed for forensics. |
| **I**nformation disclosure | *Training-data extraction* | LLM02 (Sensitive Info Disclosure), LLM10 (Vector and Embedding Weaknesses) | Carlini et al. (2021) extract verbatim training data via crafted prompts. |
| **D**enial of service | *Token-amplification, recursion* | LLM04 (Resource Exhaustion), LLM10 | Adversary triggers expensive long-context generation to exhaust per-tenant quota and budget. |
| **E**levation of privilege | *Tool-use authority escalation* | LLM06 (Excessive Agency) | Agent with read-only tool list is convinced to call a write tool exposed as part of a different agent's MCP. |

These six extensions cover the bulk of incident classes I have observed in field engagements at People First and KHOME, plus the cases reported by ANSSI's 2024 GenAI guidance.

---

## 3. LINDDUN-LLM: privacy-specific extensions

The LINDDUN privacy taxonomy is more directly portable, with three notable extensions:

- **L**inkability via embeddings: vector representations leak structural information about the underlying data even when retrieval is access-controlled. Mitigation: per-tenant embedding spaces, or strong access control on the vector index.
- **I**dentifiability via memorisation: a model fine-tuned on PII can be coerced into reciting it. Mitigation: differential privacy in fine-tuning, output filters, training-data audit.
- **N**on-compliance via *cross-jurisdictional inference*: model deployed in EU, inference routed to a US region by failover, GDPR Art. 44 violated. Mitigation: hard residency constraints in the inference router; see Section 03 of this portfolio.

---

## 4. The MITRE ATLAS mapping

MITRE ATLAS (2024) provides a TTPs-style taxonomy specific to ML/AI. Useful subset for LLM systems:

- **Reconnaissance:** AML.T0000 *Search Open ML Repos*, AML.T0001 *Acquire ML Artifacts*.
- **Initial access:** AML.T0049 *Exploit Public-Facing Application*, AML.T0051 *LLM Prompt Injection*.
- **Execution:** AML.T0053 *LLM Plugin Compromise*.
- **Impact:** AML.T0048 *External Harms*, AML.T0034 *Cost Harvesting*.

In an integrated programme, MITRE ATLAS techniques are mapped onto the STRIDE-LLM rows above, giving a **double indexing**: one CISO-friendly (STRIDE-LLM) and one red-team-friendly (ATLAS).

---

## 5. The threat-modelling assistant

The Python tool `code/llm_threat_modeler.py` consumes a YAML/JSON description of an LLM architecture (components, data flows, tools, retrieval sources) and emits:

1. The applicable STRIDE-LLM threats.
2. The applicable LINDDUN-LLM privacy threats.
3. The OWASP LLM Top-10 mapping.
4. A prioritised mitigation plan with reference controls from ANSSI's 2024 GenAI guidance.

A typical use is in **architecture review boards** at the *design* stage — when the cost of redesigning is still hours, not weeks.

---

## 6. Three field examples

### 6.1 RAG over a customer-facing knowledge base (People First context)

**Risk:** Indirect prompt injection via support tickets ingested into the RAG corpus.
**Mitigation:** (a) Source-of-truth allow-list for the ingestion pipeline; (b) instruction-following hardening in the system prompt; (c) `prompt_injection` evaluator wired into the eval harness from Section 01; (d) per-document trust scores influencing retrieval.

### 6.2 Real-estate AVM with LLM-generated rationale (KHOME context)

**Risk:** Hallucinated comparable-properties in the rationale; non-explainability under EU AI Act high-risk requirements.
**Mitigation:** (a) Forced citation enforcement (cf. `rag_pipeline.py` of Section 01); (b) human-in-the-loop on every output above a delta threshold; (c) audit log of rationale + retrieved evidence for each AVM result.

### 6.3 Multi-agent back-office automation

**Risk:** Authority creep across agents; one agent's tool list reachable via another agent's prompt.
**Mitigation:** (a) Per-agent IAM with minimal tool ACLs; (b) explicit "negotiation" protocol between agents with audit trail; (c) bounded recursion depth; (d) red-team probes for tool misuse in CI.

---

## 7. Conclusion

Threat modelling for LLM systems is not an exotic discipline; it is the application of mature techniques (STRIDE, LINDDUN, ATLAS) to a new substrate. The differences are real: stochastic outputs, leaky trust boundaries, the model as a vulnerability surface. But the engineering rigour required is the same as for any high-stakes architecture review.

The work I am doing at KHOME — and led at People First — strongly suggests that **LLM threat modelling, performed at design time, costs less than 0.5% of programme budget and prevents at least one Sev-1 incident per year**. That is the most underrated cyber-investment of 2026.

---

## References

1. ANSSI. (2024). *Recommandations de sécurité pour un SI fondé sur l'IA générative*.
2. Carlini, N. et al. (2021). *Extracting Training Data from Large Language Models*. USENIX Security '21.
3. Deng, M. et al. (2011). *A privacy threat analysis framework: supporting the elicitation and fulfillment of privacy requirements*. Requirements Engineering 16(1).
4. Greshake, K. et al. (2023). *Not what you've signed up for: Compromising real-world LLM-integrated apps with indirect prompt injection*. arXiv:2302.12173.
5. Howard, M., LeBlanc, D. (2002). *Writing Secure Code*. Microsoft Press.
6. MITRE ATLAS. (2024). *Adversarial Threat Landscape for AI Systems*.
7. NIST. (2024). *AI 600-1 — Generative AI Profile*.
8. OWASP. (2025). *Top 10 for Large Language Model Applications*.
9. Shevlane, T. et al. (2023). *Model evaluation for extreme risks*. arXiv:2305.15324.
10. Shumailov, I. et al. (2023). *The Curse of Recursion: Training on Generated Data Makes Models Forget*. arXiv:2305.17493.
11. Wei, J. et al. (2022). *Emergent Abilities of Large Language Models*. arXiv:2206.07682.
12. Zou, A. et al. (2023). *Universal and Transferable Adversarial Attacks on Aligned Language Models*. arXiv:2307.15043.

---

*Citation: Bongard, F. (2026). Threat Modelling for LLM-Driven Systems. Working paper.*
