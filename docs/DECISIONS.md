# Decision log

| Choice | Decision and reasoning | Kanishk's view |
|---|---|---|
| Model/provider | OpenAI is the default; Anthropic is selectable from environment configuration. Model names are configurable. | |
| Vision input | Image inputs use provider vision APIs. PDF pages are rasterized to PNG and submitted to the vision model so scanned pages and layout are supported. | |
| Schema design | One Pydantic v2 model per document; every scalar uses a value/confidence wrapper to make uncertainty visible. | |
| Retry behavior | One retry only after schema/JSON validation errors; provider errors are logged and returned as structured errors. | |
| Name threshold | YAML fuzzy ratio threshold 85, provisional pending product validation. | |
| LTV cap | YAML 90%, provisional; checked against invoice on-road price. | |
| FOIR cap | YAML 50%, provisional; existing EMI debits divided by net monthly income. | |
| IDV tolerance | YAML 20%, provisional; relative difference against invoice on-road price. This is a rough document check, not valuation logic. | |
| Salary tolerance | YAML 5%, provisional; average statement salary credits compared with slip net pay. | |
| Recommendation | Any failed document check yields Reject; any missing/flagged check yields Manual review; all pass yields Auto-approve docs only. | |
| Synthetic corpus | Seeded sample values and synthetic PAN prefix ZZ; no Aadhaar documents or real personal data. | |
| Noisy scans | About one quarter of generated documents also get PNG variants with mild rotation, blur, and downsampling. | |
| Business case | Placeholder assumptions are explicitly labelled; calculated savings show a theoretical upper bound, not measured impact. | |
