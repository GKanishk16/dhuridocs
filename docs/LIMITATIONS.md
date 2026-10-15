# Limitations

- The corpus is synthetic and far cleaner and more repetitive than lender submissions. It does not represent the long tail of document layouts, handwriting, stamps, folds, glare, partial pages, or mobile capture artifacts.
- Only English text is generated. Regional languages, transliteration, and mixed-script documents are not evaluated.
- PAN strings are deliberately synthetic and begin with ZZ. No Aadhaar is generated or requested.
- The provided evaluation report is an inventory baseline until predictions are recorded. It makes no claim of model accuracy, precision, recall, latency, or cost. The requested worst-failure ranking is unavailable until a real model run populates predictions.
- Estimated LLM spend and latency need actual runs and provider billing/token data; they are not fabricated.
- This prototype does not detect forged or tampered documents, verify GSTIN/PAN against government sources, check bank authenticity, or validate insurer policies.
- PDF pages are sent as rasterized images; long PDFs can increase latency and token/image cost.
- Confidence is model-reported and uncalibrated; it must not be interpreted as statistical certainty.
- The fuzzy name matcher, LTV, FOIR and IDV rules are provisional product choices. Validate policy thresholds with credit, compliance, operations, and legal teams.
- FOIR uses observed bank EMI debits only and does not infer obligations absent from the sampled months.
- A document-level recommendation is not loan underwriting, an eligibility decision, or adverse-action rationale.
- Upload handling is a local prototype, with no authentication, access control, retention policy, encryption, or production privacy controls.
