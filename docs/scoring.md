# Evidence scoring

PhyThera scores **evidence support**, not clinical efficacy.

Scores are stored on a 0–1 scale and displayed as 0–100 in the frontend.

## 1. Modern Evidence Score

Modern evidence is derived from PubMed records retrieved through NCBI E-Utilities.

### Outcome direction
| Direction | Score |
|---|---:|
| Supportive | 1.00 |
| Mixed | 0.50 |
| Not supportive | 0.00 |
| Unclear | excluded from score |

### Indication relation
| Relation | Weight |
|---|---:|
| Exact match | 1.00 |
| Partial overlap | 0.85 |
| Related | 0.50 |
| Unrelated | 0.00 |

### Evidence families
Publications are grouped into evidence families to reduce double-counting of multiple publications from the same underlying study.

Review-layer weights:
- systematic review/meta-analysis: 1.00
- systematic review: 0.90

Trial-layer weights:
- primary trial report: 1.00
- continuation/follow-up report: 0.70

When both layers are available:
- Review layer: 60%
- Trial layer: 40%

If only one layer is available, its available weight is normalized to 100%.

## 2. Traditional Support Score

The prototype regulatory/traditional support scale is:

| EMA/HMPC context | Score |
|---|---:|
| Well-established use | 1.00 |
| Traditional use | 0.75 |
| Documented medicinal use | 0.50 |
| Documented absence of support | 0.00 |
| Source unavailable / unusable | `null` |

A missing EMA/HMPC source is **not** interpreted as negative evidence.

## 3. Evidence Score

Base weights:
- Modern Evidence: 70%
- Traditional Support: 30%

Available weights are renormalized when a component is missing.

Examples:

```text
Modern 0.80 + Traditional 0.75
= 0.70 × 0.80 + 0.30 × 0.75
= 0.785

Modern 0.80 + Traditional unavailable
= 0.80

Modern unavailable + Traditional 0.75
= 0.75
```

This is a missing-aware evidence-ranking score. It is **not** a percentage efficacy, probability of benefit, or treatment recommendation.

## 4. Evidence Category

Current prototype rules:

- **Established**: Modern ≥ 0.60 and Evidence Score ≥ 0.70
- **Traditional**: strong traditional/regulatory support with limited or unavailable modern evidence
- **Emerging**: Modern ≥ 0.40 but not Established
- **Evidence gap**: available evidence remains below those thresholds
- **Unclassified**: insufficient usable information

## 5. Source Convergence

Cross-cultural mapping is deliberately separate from clinical evidence.

Mapping categories are converted deterministically:

| Mapping category | Score |
|---|---:|
| Strong overlap | 1.00 |
| Partial overlap | 0.60 |
| Distinct concepts | 0.00 |
| No meaningful mapping | 0.00 |
| Not assessable | `null` |

A convergence score says **how similar documented use concepts are**, not whether the plant is clinically effective.

## 6. Research Opportunity

Research Opportunity is a heuristic classification using the available modern, traditional/regulatory and convergence signals. Missing dimensions remain missing and are not converted to negative evidence.

The current categories are:
- High
- Moderate
- Low
- None
- Unclassified

## Versioning

The prototype stores version identifiers with its scoring logic so that future rule changes can be distinguished from earlier calculations.
