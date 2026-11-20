# Phase 7 — Checkpoint Evidence Summary

Generated: 2026-11-20T06:38:45.310447+00:00

## Phase evaluation status

### G1 — PARTIAL

- **Gold Cases:** 60
- **Final Successes:** 60
- **Product Accuracy:** 0.9
- **Normalized Issue Accuracy:** 0.4666666666666667
- **Normalized Issue Macro F1:** 0.3443722943722944
- **Limitation:** Manual severity and vulnerability annotations remain incomplete.

### G2 — PARTIAL

- **Strict Result Set Matches:** 13/18
- **Semantic Equivalences Accepted:** 5
- **Limitation:** Unanswerable refusal evidence still requires verification.

### G3 — PARTIAL

- **Answerable Questions:** 17
- **Mean Recall At 5:** 0.25644972668600646
- **Mean Recall At 10:** 0.3929931395040015
- **Mrr:** 0.7990196078431372
- **Citation Validity:** 164/167 (98.20%)
- **Opus Proxy Review:** 14 ACCEPT, 3 REVISE
- **Limitation:** Independent human review and judge calibration are incomplete.

### G4 — PARTIAL

- **Guard Injection Checks:** 10/10
- **Pii Synthetic Checks:** 8/8
- **Limitation:** End-to-end graph execution and human rubric are incomplete.

## Baselines, ablations and calibration

- **B0:** NOT_FOUND
- **B1:** NOT_FOUND
- **B2:** NOT_FOUND
- **A1:** NOT_FOUND
- **A2:** NOT_FOUND
- **judge_calibration:** NOT_VERIFIED
- **checkpoint_cost_per_request:** NOT_AVAILABLE
- **checkpoint_latency_comparison:** INCOMPLETE

## Failure analysis

- Documented failure cases: 3
- CSV: `/home/sagemaker-user/complaintiq/eval/results/PHASE7_FINAL_VALIDATION/phase7_three_failure_analyses.csv`

## Limitations

- Missing baseline and ablation evidence has not been fabricated.
- Cost per request is unavailable.
- Latency measurements are not a complete B0/B1/B2 comparison.
- Opus proxy ratings are not independent human ratings.
- G4 guard tests do not establish end-to-end agent quality.

## Execution constraints

- No Bedrock inference.
- No agent execution.
- No S3 operations.
- No original evaluation records modified.

**Overall status: PHASE7_PARTIAL_EVIDENCE_CONSOLIDATED**