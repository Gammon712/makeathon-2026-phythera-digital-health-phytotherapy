# Data and source policy

## Source principle

Automated ingestion is enabled only for sources whose machine access and reuse have been explicitly approved for the intended workflow.

For sources without confirmed permission:
- automated retrieval is blocked by default,
- existing lawful records may be displayed only where appropriate,
- the workflow should otherwise skip that source.

## Provenance

Source URLs and source identifiers are kept separate from PhyThera's derived interpretations and scores.

## Repository data policy

This public repository intentionally does **not** include:
- API keys or credentials,
- a production Supabase dump,
- complete copies of third-party source documents,
- bulk copies of PubMed abstracts,
- private/local workflow metadata,
- internal n8n instance identifiers,
- personal filesystem paths or terminal histories.

The repository contains code, schema, workflow definitions, scoring rules and documentation necessary to understand and reproduce the architecture with appropriately licensed or permitted data.

## PubMed / NCBI

The ingestion architecture uses NCBI E-Utilities rather than scraping PubMed pages. Users reproducing the pipeline should follow current NCBI usage policies, identify their tool/contact where required, and respect request-rate limits.

## EMA/HMPC

Source documents remain attributable to EMA/HMPC and any other applicable rights holders. Repository code does not transfer rights to third-party source content.
