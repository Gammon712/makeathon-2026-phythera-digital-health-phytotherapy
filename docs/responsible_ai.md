# Responsible AI and scientific guardrails

PhyThera follows one core principle:

> **AI where it helps. Deterministic logic where it matters.**

## AI-assisted tasks
LLMs are used for:
- structured extraction from complex regulatory or traditional-source documents,
- semantic comparison of source-specific traditional-use concepts.

## Deterministic tasks
Rule-based code is used for:
- scoring,
- evidence-category classification,
- missing-data handling,
- source-convergence scoring,
- source-policy enforcement,
- provenance consistency checks.

## Guardrails
- Missing evidence is not automatically negative evidence.
- Traditional use is not presented as proof of clinical efficacy.
- Cross-cultural convergence is not presented as proof of clinical efficacy.
- Source provenance is retained separately from derived scores.
- Mapping records can be rejected by the frontend when linked extraction runs do not match the selected plant.
- Automated traditional-source ingestion is blocked unless machine retrieval has been explicitly authorized.
- No systematic human-review stage has yet been completed for the prototype; the public interface therefore makes no human-review claim.

## Human oversight
Human review is a planned future stage. The current prototype should be interpreted as an automated evidence-navigation research system, not as a validated clinical knowledge base.
