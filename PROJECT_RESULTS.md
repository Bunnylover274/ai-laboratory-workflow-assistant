# Project Results

## Verified results

| Evaluation | Result |
| --- | ---: |
| Structured workflow evaluation | 8/8 (100%) |
| Initial retrieval evaluation | 5/6 (83%) |
| Retrieval evaluation after policy guardrail | 6/6 (100%) |
| Adversarial and edge-case evaluation | 9/9 (100%) |

## Key engineering finding

The initial semantic search returned molecular controls, equipment tracking, and
sample receipt documents, but omitted the mandatory result-approval document.
The generated workflow still passed all eight output checks, proving that output
quality tests alone cannot establish retrieval completeness.

The design was changed to combine semantic ranking with deterministic inclusion
of mandatory governance documents. The retrieval test then passed 6/6.

## Edge cases verified

- Incomplete SOP retained multiple source gaps.
- Human review remained required.
- An embedded instruction to cite fictional `DOC-999` was rejected.
- An embedded instruction to add an unauthorized `Released` result was rejected.
- The workflow was never authorized for laboratory use.

## Portfolio summary

Designed and built a Python-based AI laboratory workflow assistant using the
OpenAI Responses and Embeddings APIs, Pydantic structured outputs, retrieval-
augmented generation, deterministic evals, prompt-injection tests, and a
human-review audit gate. Identified an evidence-retrieval gap through testing and
implemented a policy-based control that raised retrieval coverage from 83% to
100% on the defined training evaluation.
