# Prototype limitations

PhyThera is an EthnoHack research prototype.

Known limitations at submission time include:

1. **Incomplete source coverage.** Not every plant has comparable European and traditional-source profiles.
2. **Cross-cultural mapping is conditional.** Source Convergence is `Not assessed` when one comparison layer is unavailable.
3. **Publication-level persistence is incomplete.** For some prototype profiles, PubMed-derived scoring was calculated during the workflow but the individual study records were not fully persisted for later display.
4. **Normalized evidence/safety tables are partially materialized.** Newer workflows store rich structured information primarily in `extraction_runs`; the frontend therefore uses validated extraction profiles as a fallback.
5. **No systematic human review has yet been completed.** Human review is planned for future versions.
6. **AI extraction can make errors.** Structured outputs retain validation metadata and source provenance, but are not a substitute for expert source review.
7. **Evidence Score is not efficacy.** It is a ranking of available evidence support for a plant–indication profile.
8. **Traditional support is not clinical proof.** Regulatory/traditional documentation is shown as a distinct evidence dimension.
9. **Cross-cultural convergence is not efficacy.** It only reflects semantic similarity of documented use concepts.
10. **The frontend includes provenance-consistency checks.** Inconsistent cross-workflow mappings are ignored rather than presented as valid evidence.

The system is intended for research, demonstration and evidence navigation, not diagnosis, treatment recommendation or clinical decision support.
