# ComplaintIQ — Phase 7 Failure Analysis

Generated UTC: 2026-11-20T06:37:44.266323+00:00

This report presents three representative failure cases selected from existing G1 and G3 evaluation records.

No model inference or agent execution was performed.

---

## FA-01 — Product misclassification

- Evaluation phase: G1
- Case ID: 23053378
- Expected result: Credit card
- Actual result: Checking or savings account
- Evidence: The saved G1 failure record marks product_correct as false.
- Observed impact: The predicted product does not match the expected product for this complaint.
- Recommended improvement: Review product-boundary examples and improve classification distinction between the expected and predicted product.
- Source: `eval/results/G1_final_closure/G1_closure_20261116T172209Z/G1_failure_analysis.csv`

---

## FA-02 — Issue misclassification

- Evaluation phase: G1
- Case ID: 23304250
- Expected result: Improper use of your report
- Actual result: Credit monitoring or identity theft protection services
- Evidence: The saved G1 failure record marks product_correct as true and issue_correct_normalized as false.
- Observed impact: The product was classified correctly, but the normalized complaint issue was classified incorrectly.
- Recommended improvement: Improve issue taxonomy disambiguation and test similar complaint narratives against the normalized issue labels.
- Source: `eval/results/G1_final_closure/G1_closure_20261116T172209Z/G1_failure_analysis.csv`

---

## FA-03 — Unsupported regulatory claims

- Evaluation phase: G3
- Case ID: G3-04
- Expected result: Claims supported by supplied evidence and citations
- Actual result: REVISE
- Evidence: The G3 failure record has passed=False and records 3 unsupported-claim entries.
- Observed impact: The answer contained regulatory statements that the evaluation evidence did not adequately support.
- Recommended improvement: Restrict regulatory assertions to retrieved evidence, verify citation-to-claim alignment, and abstain when supporting evidence is insufficient.
- Source: `/home/sagemaker-user/complaintiq/eval/results/G3_failure_analysis.csv`

### Unsupported claim details

["The claim regarding 12 CFR 1005.9(c)(3) stating that 'A preauthorized transfer between two accounts of the same consumer at the same institution is subject to the 12 CFR 1005.9(c)(1) rule (preauthorized transfers), not the 12 CFR 1005.9(c)(2) rule on intra-institutional transfers' is not supported. The cited evidence [exam_manual_v2_2012_page_0704_chunk_0001] is truncated mid-sentence ('A preauthorized transfer between two a') and does not establish the 1005.9(c)(3) rule or its content as described.", "The 'Foreign-Initiated Transfers' section cites 12 CFR 1005.9(c)(3)/truncated content, but the cited evidence does not mention foreign-initiated transfers at all. This claim is fabricated from truncated text.", "The 'Modified Initial Disclosures' section cites 12 CFR 1005.18(c)(1)(i), but the cited evidence [exam_manual_v2_2012_page_0705_chunk_0001] only references modifications to 12 CFR 1005.7(b) and does not cite or support 1005.18(c)(1)(i). The specific regulatory citation 1005.18(c)(1)(i) is not supported by the evidence."]

### Original evaluation feedback

The draft contains regulatory statements with citations that are not supported by the cited evidence. (1) The section on preauthorized intra-institutional transfers attributes a specific rule to 12 CFR 1005.9(c)(3), but the evidence [exam_manual_v2_2012_page_0704_chunk_0001] is truncated at 'A preauthorized transfer between two a' and does not support this characterization. Remove or clearly mark this as unknown. (2) The 'Foreign-Initiated Transfers' subsection claims special rules for transfers initiated outside the U.S., which does not appear anywhere in the cited evidence; remove it. (3) The 'Modified Initial Disclosures' section cites 12 CFR 1005.18(c)(1)(i), a citation not found in the supplied evidence; the evidence only supports modifications under 1005.7(b). Correct the citation to match the evidence or remove the specific subsection reference. Once these unsupported/invalid-citation items are corrected, the remainder (passbook, quarterly, intra-account documentation, alternative to periodic statements, and the limitation note) is adequately supported.

---

## Limitations

- These are representative historical failures, not new test executions.
- Recommendations are proposed improvements, not verified fixes.
- These three cases do not establish completion of all checkpoint requirements.
- Baseline and ablation comparisons remain unavailable.