# ComplaintIQ – AI-Powered Banking Complaints Intelligence Platform

## 1. Project Overview

**ComplaintIQ** is an AI-powered banking complaints intelligence platform designed to analyse consumer complaints, identify complaint categories, retrieve relevant regulatory requirements, investigate similar historical complaints, and generate evidence-grounded responses and analytical insights.

The platform uses Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), structured complaint data, regulatory documents, and an agent-based orchestration workflow.

The objective is to provide a structured intelligence assistant that helps users:

- Understand and classify banking complaints.
- Identify relevant banking products, issues, and sub-issues.
- Retrieve applicable regulatory provisions.
- Analyse complaint trends using structured data.
- Find similar historical complaints.
- Generate evidence-backed regulatory explanations.
- Identify potential consumer vulnerability and complaint severity.
- Produce structured reports and recommendations.
- Escalate uncertain or sensitive outputs for human review.

The system is designed with a focus on factual grounding, traceability, controlled SQL execution, PII protection, and human oversight.

---

## 2. Technology Stack

| Component | Technology |
|---|---|
| Development environment | AWS SageMaker Studio |
| Cloud provider | AWS |
| LLM provider | Amazon Bedrock |
| Worker LLM | Anthropic Claude Sonnet 4.6 |
| Judge LLM | Anthropic Claude Opus 4.8 |
| Embedding model | Amazon Titan Text Embeddings V2 |
| Programming language | Python |
| Data processing | Pandas, DuckDB |
| Vector search | FAISS |
| Embedding generation | Amazon Bedrock |
| Agent orchestration | LangGraph |
| State persistence | SQLite checkpointing |
| Evaluation | Custom Python evaluation framework |
| Dataset | CFPB Consumer Complaint Data |
| Regulatory knowledge | CFR documents and regulatory examination manuals |
| Supervisory sources | CFPB Supervisory Highlights |

### Configured Bedrock Models

The following model configuration was used during the project:

```python
MODELS = {
    "worker": "us.anthropic.claude-sonnet-4-6",
    "judge": "us.anthropic.claude-opus-4-8",
    "fast": "us.anthropic.claude-sonnet-4-6",
    "embed": "amazon.titan-embed-text-v2:0"
}
```

AWS Region:

```text
us-east-1
```

---

## 3. High-Level Architecture

The platform follows a retrieval-augmented, multi-agent architecture.

### Logical architecture

```text
                   USER REQUEST
                        |
                        v
                INPUT / GUARD NODE
                        |
                        v
                  INTENT ROUTER
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
       TRIAGE        ANALYTICS      REG_QA
          |             |             |
          v             v             v
    CLASSIFICATION   SQL AGENT    RESEARCH AGENT
          |             |             |
          v             v             v
    COMPLAINT DATA   DUCKDB       REGULATORY RAG
          |             |             |
          +-------------+-------------+
                        |
                        v
                   DRAFTER NODE
                        |
                        v
                   CRITIC NODE
                        |
              +---------+---------+
              |                   |
              v                   v
             PASS               REVISE
              |                   |
              v                   v
        HUMAN REVIEW        DRAFT REVISION
              |
       +------+------+
       |             |
       v             v
    APPROVE        REJECT
       |             |
       v             v
    PUBLISH        REFUSE
```

The actual LangGraph workflow includes guard, routing, analysis, research, drafting, critic, human-interrupt, publish, and refusal paths.

### Main knowledge sources

The platform uses two major knowledge sources:

1. **Structured complaint data**
   - Historical consumer complaints.
   - Product and issue classifications.
   - Complaint narratives and related attributes.
   - Analytical data queried through DuckDB.

2. **Regulatory and supervisory knowledge**
   - Code of Federal Regulations (CFR) documents.
   - Regulatory examination manuals.
   - CFPB Supervisory Highlights.
   - Chunked documents indexed for semantic retrieval.

---

# 4. Phase-wise Implementation

## Phase 1 – Project Foundation and Initial Setup

The project foundation was established around the ComplaintIQ banking complaints intelligence use case.

The implementation environment was based on AWS SageMaker Studio, with Amazon Bedrock selected for model inference and embeddings.

The project architecture was designed around the following requirements:

- Banking complaint analysis.
- Regulatory knowledge retrieval.
- Structured data analytics.
- LLM-based reasoning and response generation.
- Multi-agent workflow orchestration.
- Evaluation and quality measurement.
- Human-in-the-loop controls.

The project subsequently adopted a phased implementation approach, separating data preparation, retrieval, LLM integration, agent development, orchestration, and evaluation.

**Documentation note:** The detailed Phase 1 execution log and original setup checklist were not available in the retained project notes. This section documents the known foundation; add the exact initial environment setup and repository creation steps if those are required for a complete historical record.

---

## Phase 2 – Data Engineering and Knowledge Preparation

### Objective

Prepare structured complaint data and regulatory knowledge for downstream analytics and retrieval.

### 2.1 Complaint dataset preparation

The CFPB consumer complaint dataset was processed to create a clean and usable complaint data pool.

The processing pipeline included:

- Loading the source complaint dataset.
- Inspecting data fields and data types.
- Handling duplicate complaint records.
- Preparing the complaint records for structured querying.
- Separating the evaluation holdout data.
- Preparing the final analytical dataset.

### 2.2 Data validation results

The following results were recorded during Phase 2:

| Validation item | Result |
|---|---:|
| Total complaint records | 37,923 |
| Deduplicated index rows | 31,813 |
| June holdout records | 6,110 |
| Regulatory document chunks | 1,784 |
| June holdout overlap with index | 0 |

The June holdout was kept separate from the indexed complaint dataset to avoid evaluation leakage.

### 2.3 Structured data preparation

DuckDB was selected as the analytical query engine.

The prepared complaint data was made available for structured queries, including:

- Complaint volume analysis.
- Product-level analysis.
- Issue-level analysis.
- Trend analysis.
- Complaint filtering.
- Historical complaint investigation.

### 2.4 Regulatory document preparation

Regulatory documents were processed into smaller text chunks suitable for semantic search.

The knowledge corpus included:

- CFR regulatory sections.
- Regulatory examination manual content.
- Supervisory Highlights documents.

The resulting regulatory corpus contained **1,784 document chunks**.

Each chunk was associated with source-identifying information such as:

- Chunk ID.
- Source document.
- Page or section reference.
- Text content.

These identifiers were later used for evidence citations in generated answers.

### 2.5 Phase 2 validation

The following checks were performed:

- Complaint dataset processing.
- Duplicate handling.
- June holdout separation.
- Index and holdout overlap validation.
- Regulatory document chunk generation.
- Document metadata preparation.

**Phase 2 status: Completed.**

---

## Phase 3 – Retrieval-Augmented Generation (RAG)

### Objective

Implement semantic retrieval over complaint and regulatory knowledge sources.

The objective was to allow the platform to retrieve relevant historical complaints and regulatory provisions before generating an answer.

### 3.1 Embedding model

Amazon Titan Text Embeddings V2 was used to generate embeddings.

Configured model:

```text
amazon.titan-embed-text-v2:0
```

Embedding dimension:

```text
1024
```

### 3.2 Regulatory vector index

The regulatory document chunks prepared during Phase 2 were converted into embeddings and indexed using FAISS.

Index size:

```text
1,784 regulatory chunks
```

The regulatory index supports retrieval from:

- CFR provisions.
- Examination manual content.
- Supervisory Highlights.

### 3.3 Complaint vector index

Historical complaint records were also embedded and indexed.

Index size:

```text
3,000 complaint chunks
```

This enables semantic retrieval of complaints that are conceptually similar even when they do not use exactly the same wording.

### 3.4 Retrieval workflow

The retrieval workflow follows these steps:

1. Receive a user query.
2. Generate a query embedding.
3. Search the appropriate FAISS index.
4. Retrieve the most relevant chunks.
5. Return the source text and metadata.
6. Pass the retrieved evidence to downstream agent nodes.
7. Use the retrieved source identifiers for answer citations.

### 3.5 Retrieval validation

Retrieval smoke tests were executed against both knowledge sources.

The tests verified:

- Embedding generation.
- Vector index loading.
- Semantic search execution.
- Retrieval of relevant complaint records.
- Retrieval of regulatory document chunks.
- Source metadata availability.

A known limitation was identified: exact CFR citation retrieval was weaker than desired in some cases.

This became particularly important during Phase 7, where the critic identified that some retrieved regulatory chunks were truncated and did not contain the full provision needed to substantiate generated claims.

### 3.6 Phase 3 outputs

The principal outputs included:

- Regulatory FAISS index.
- Complaint FAISS index.
- Embedding generation workflow.
- Retrieval helper functions.
- Retrieval smoke-test results.

**Phase 3 status: Core implementation completed; retrieval precision and source completeness remain areas for improvement.**

---

## Phase 4 – LLM Integration and Common Model Wrapper

### Objective

Create a reusable LLM integration layer using Amazon Bedrock.

Instead of calling the Bedrock models independently from every agent, a common wrapper was implemented.

### 4.1 Model configuration

The project used separate model roles:

| Role | Model |
|---|---|
| Worker | Claude Sonnet 4.6 |
| Judge | Claude Opus 4.8 |
| Fast | Claude Sonnet 4.6 |
| Embeddings | Amazon Titan Text Embeddings V2 |

### 4.2 Common LLM wrapper

The implementation introduced reusable functions, including:

```python
llm.chat(...)
```

and:

```python
llm.chat_json(...)
```

The wrapper supports:

- Model selection.
- System and user prompts.
- Model inference through Bedrock.
- JSON-structured responses.
- Configurable token limits.
- Temperature configuration.
- Error handling.
- Retry handling.
- Response parsing.

### 4.3 Structured output handling

The JSON response functionality was designed to support schema-based outputs.

Pydantic models were used to validate structured responses from the LLM.

This was particularly important for:

- Complaint classification.
- Triage outputs.
- Critic evaluations.
- Structured agent responses.

### 4.4 Usage tracking

A usage-reporting mechanism was implemented to capture model usage information.

The implementation included:

- Token usage tracking.
- Request-level usage information.
- Latency tracking.
- SQLite-based caching.
- Retry handling.

The project also explored model pricing and cost estimation.

**Note:** The presence of usage tracking does not establish a fully validated monetary cost report. Model-specific pricing configuration and actual cost reconciliation should be verified separately.

### 4.5 Phase 4 outputs

- Common LLM wrapper.
- JSON response wrapper.
- Pydantic response validation.
- Retry handling.
- SQLite caching.
- Usage and latency tracking.

**Phase 4 status: Core implementation completed.**

---

## Phase 5 – Multi-Agent Implementation

### Objective

Implement specialized agent nodes responsible for different complaint intelligence tasks.

The architecture separates responsibilities so that each agent performs a defined operation rather than relying on one large LLM prompt.

### 5.1 Guard node

The guard node performs initial input validation and security checks.

Its responsibilities include:

- Identifying potentially sensitive inputs.
- Detecting PII patterns.
- Detecting prompt-injection attempts.
- Preventing unsafe requests from proceeding through the normal workflow.

### 5.2 Router node

The router identifies the type of request and determines the appropriate execution path.

The implemented intent categories include:

```text
TRIAGE
ANALYTICS
REG_QA
BRIEF
OUT_OF_SCOPE
```

### 5.3 Triage node

The triage node handles complaint classification and initial assessment.

Its responsibilities include:

- Understanding the complaint narrative.
- Identifying the product.
- Identifying the issue.
- Identifying the sub-issue.
- Producing structured triage information.

### 5.4 Analyst / SQL node

The analyst node handles structured complaint analytics.

DuckDB is used to execute analytical queries against the prepared complaint dataset.

Its responsibilities include:

- Generating analytical SQL.
- Executing read-only queries.
- Retrieving complaint statistics.
- Analysing complaint distributions.
- Supporting product and issue-level analysis.

A SQL guard was implemented to restrict unsafe query execution.

### 5.5 Cases node

The cases node retrieves similar historical complaints using the complaint retrieval index.

It supports:

- Similar complaint identification.
- Historical case comparison.
- Retrieval of relevant complaint narratives.
- Providing additional context for complaint investigation.

### 5.6 Research node

The research node retrieves relevant regulatory and supervisory evidence.

It uses the regulatory FAISS index and returns source chunks for downstream drafting.

The evidence contains identifiers that allow the drafter and critic to reference the original knowledge source.

### 5.7 Drafter node

The drafter node combines information from the relevant workflow components to generate a structured response.

Inputs may include:

- User request.
- Intent.
- Regulatory evidence.
- SQL results.
- Similar historical complaints.
- Existing draft and revision information.

The generated response is expected to be grounded in the supplied evidence.

### 5.8 Critic node

The critic evaluates the generated response before it can proceed.

The critic checks for:

- Unsupported regulatory statements.
- Missing or invalid citations.
- Unsupported numeric claims.
- Liability admissions on behalf of a bank.
- Allegations incorrectly presented as established facts.
- Unsupported promises or conclusions.
- Potential PII exposure.

The critic uses a separate judge model and structured response schema.

The critic's structured output includes:

```python
{
    "verdict": "PASS" or "REVISE",
    "unsupported_claims": [],
    "tone_issues": [],
    "feedback": ""
}
```

The local validation layer also checks whether citation identifiers exist in the supplied evidence.

Importantly, a valid citation ID does not automatically establish that the cited text semantically supports the associated statement.

### 5.9 Human-in-the-loop node

A human review mechanism was implemented for decisions requiring approval.

The objective is to prevent sensitive or unverified outputs from being published automatically.

### 5.10 Publish node

A publish node was implemented to handle approved outputs.

The publish functionality was restored during later evaluation bootstrap, but its presence does not mean every evaluation result was published.

### 5.11 Refusal node

A refusal path was implemented for out-of-scope or disallowed requests.

### 5.12 Phase 5 outputs

The following logical agent components were implemented:

- Guard.
- Router.
- Triage.
- Analyst SQL.
- Cases.
- Research.
- Drafter.
- Critic.
- Human interrupt.
- Publish.
- Refuse.

**Phase 5 status: Core agent implementation completed.**

---

## Phase 6 – LangGraph Orchestration and State Management

### Objective

Integrate the individual agents into a coordinated workflow using LangGraph.

### 6.1 Graph construction

The agent nodes were connected into a state-driven workflow.

The graph supports:

- Input validation.
- Intent routing.
- Conditional execution.
- Structured data analysis.
- Regulatory research.
- Similar case retrieval.
- Response drafting.
- Critic validation.
- Revision handling.
- Human review.
- Publishing or refusal.

### 6.2 Shared state

A shared state structure was implemented to pass information between nodes.

The `CIQState` structure includes fields such as:

```python
class CIQState:
    request: str
    clean_request: str
    flags: list[str]
    intent: str
    triage: dict
    similar_cases: list[dict]
    sql: str
    sql_rows: list[dict]
    evidence: list[dict]
    draft: str
    critique: dict
    revisions: int
    human_decision: dict
    report_uri: str
    trace: list[dict]
```

The actual implementation uses typed state annotations and a reducer for the trace field.

### 6.3 Conditional routing

The graph uses conditional routing to direct requests based on intent and agent results.

For example:

- Complaint classification requests are routed to triage.
- Analytical requests are routed to the SQL workflow.
- Regulatory questions are routed to research.
- Drafted answers are passed to the critic.
- Outputs requiring approval enter the human review path.
- Unsupported requests enter the refusal path.

### 6.4 Critic and revision workflow

The critic is used as a quality gate.

A passing answer can proceed through the approval workflow.

A response requiring correction can be sent for revision, subject to the graph's configured revision handling.

### 6.5 Checkpoint persistence

SQLite-based checkpointing was implemented for LangGraph state persistence.

The checkpoint database used by the project is:

```text
state/checkpoints.sqlite
```

This enables workflow state to be persisted and resumed.

The checkpoint database was retained during the later Phase 7 evaluation corrections and should not be overwritten unnecessarily.

### 6.6 Phase 6 validation

The saved notebook outputs document workflow-level validation and a separate approved publishing run.

The workflow validation covered the five supported intents: `ANALYTICS`, `TRIAGE`, `REG_QA`, `BRIEF`, and `OUT_OF_SCOPE`. It exercised graph routing and the human interrupt/resume path. The five-intent validation run used an in-memory checkpointer and a mock publisher; it should not be confused with the subsequent live S3 publishing run.

A separate finalization run used the real S3 publisher after explicit human approval. The saved output records three uploaded reports in:

```text
s3://sagemaker-complaintiq-865928920861/complaintiq/reports/
```

The uploaded reports were `ANALYTICS`, `BRIEF`, and `REG_QA`. Their verified object sizes were 1,602, 3,344, and 5,776 bytes respectively, and three audit records were verified. The saved output explicitly states that the mock publisher was not used. The existing `TRIAGE` report was not republished.

This publishing evidence is limited to those three approved report objects. It does not establish persistent graph checkpoint writes or a production deployment.

The consolidated saved validation output also records 80/80 checks passed for its Phase 0–6 validation scope. The separate Phase 0–5 validation baseline recorded 156/156 checks passed (P0 19/19, P1 5/5, P2 14/14, P3 44/44, P4 16/16, P5 58/58). These are distinct validation summaries and should not be added together.

**Phase 6 status: Core graph workflow validation completed; human approval and live S3 publication demonstrated for the three reports listed above. Production deployment and persistent checkpoint verification are not claimed.**

---

## Phase 7 – Evaluation Framework and Quality Validation

### Objective

Phase 7 evaluates complaint triage, structured analytics, regulatory question answering, and safety controls. The evaluation evidence is consolidated, but the overall phase remains **partially complete** because some acceptance activities are incomplete or unavailable.

### 7.1 G1 – Complaint triage

- Gold dataset: 60 complaints.
- Final closure run: 60/60 cases completed successfully after recovery of the five initial failures.
- Product accuracy: **90.00%**.
- Normalized issue accuracy: **46.67%**.
- Normalized issue macro-F1: **0.3444**.
- Final closure latency: mean **4.566 s**, p50 **3.833 s**, p95 **9.086 s**.

The final closure metrics represent product and issue classification. The separate manual severity/vulnerability annotation worksheet remained unannotated (0/60 completed); severity and vulnerable-customer performance therefore have not been measured.

### 7.2 G2 – Structured analytics

- Gold dataset: 20 questions (18 answerable, 2 unanswerable).
- Agent outputs evaluated: 18 answerable questions.
- Strict result-set equality: **13/18 (72.22%)**.
- Five additional cases (G2-04, G2-05, G2-13, G2-15, G2-18) were manually accepted as semantically equivalent after review. Keep this separate from the strict equality score.
- G2 latency: mean **3.214 s**, p50 **2.937 s**, p95 **4.331 s**.

The two unanswerable questions concern population data and household income that are unavailable in the dataset. The available evidence does not establish that the system's refusal behavior was successfully validated for both questions.

### 7.3 G3 – Regulatory question answering

- Gold dataset: 20 questions (17 answerable, 3 intentionally unanswerable).
- All 17 answerable-question generations completed.
- Retrieval: mean Recall@5 **25.64%**, mean Recall@10 **39.30%**, hit rate@5 **94.12%**, and MRR **79.90%**.
- Citations: 167 total; 164 valid and 3 invalid; citation-ID validity **98.20%**.
- Critic: 17 executions; 13 successful critic decisions (2 PASS, 11 REVISE) and 4 critic failures.
- Independent Opus evaluation: **14 ACCEPT, 3 REVISE**. The REVISE cases are G3-04, G3-06, and G3-15.
- Manual review worksheet: 20 rows; 14 ACCEPT, 3 REVISE, and 3 unanswerable cases marked ACCEPT after review. The 17 answerable ratings were Opus-proxy assessments, not independent human compliance review.
- The three unanswerable cases (G3-18/19/20) had acceptable refusal wording on manual inspection, but the automated abstention detector passed 0/3. Preserve the detector result and the manual assessment as separate evidence.

The earlier G3 master validation recorded 70/70 structural/master checks passed. That result does not override the later citation counts, critic outcomes, semantic review, or the need for human regulatory review. A valid citation ID does not prove that the cited text supports the associated claim.

### 7.4 G4 – Safety and end-to-end scenarios

- Ten synthetic scenarios were prepared, including two prompt-injection cases and two vulnerable-customer cases.
- Offline guard validation: **10/10 injection checks passed**; both injection attempts were detected, with no false positives in the eight non-injection cases.
- Synthetic PII checks: **8/8 passed**, covering SSN, email, phone, and card-number redaction and long-input truncation.
- Human evaluation worksheet: 10 cases, still pending human rubric review.

G4 evidence is limited to offline guard/PII checks. It does not establish full agent execution, triage accuracy, final-response quality, or completion of the human 1–5 evaluation rubric.

### 7.5 Cross-track Phase 7 checkpoint

The consolidated offline audit found:

| Checkpoint item | Current evidence |
|---|---|
| G1 | PARTIAL |
| G2 | PARTIAL |
| G3 | PARTIAL |
| G4 | PARTIAL |
| B0 / B1 / B2 baselines | NOT FOUND |
| A1 / A2 ablations | NOT FOUND |
| Ten-case human judge calibration | NOT VERIFIED |
| Human Cohen's kappa | NOT AVAILABLE |
| Cost per request | NOT AVAILABLE |
| Comparable checkpoint latency table | INCOMPLETE |
| Failure analyses | 3 documented |

Three selected failure analyses were recorded: two G1 classification errors and one G3 unsupported-regulatory-claim case (G3-04). The audit covered 204 result files; duplicated failure-analysis files should not be counted as unique cases.

A 10-case calibration worksheet was prepared. An AI-assisted assessment was also created separately, but it is not human ground truth and must not be represented as human calibration or used to claim human Cohen's kappa.

**Phase 7 status: PARTIAL_EVIDENCE_CONSOLIDATED.** The available metrics and artifacts are useful evaluation evidence, but the baseline/ablation experiments, genuine human judge calibration, cost-per-request evidence, and remaining human review are not complete.

---

## Phase 8 – Offline Demonstration Notebook

An offline demonstration interface was implemented in `notebooks/07_demo.ipynb` (Option A).

- The notebook provides a local, notebook-based view of saved project and evaluation artifacts.
- The notebook contains 17 cells and passed notebook-format validation.
- The user executed Restart Kernel and Run All; the saved run completed all 17 cells without execution errors.
- The Phase 7 dashboard was corrected to use the consolidated checkpoint summary as the authoritative source. It displays G1–G4 as PARTIAL, B0/B1/B2/A1/A2 as NOT_FOUND, judge calibration as NOT_VERIFIED, cost per request as NOT_AVAILABLE, and checkpoint latency comparison as INCOMPLETE.
- The notebook includes local demonstration controls for previewing approve/edit/reject decisions. These controls represent a local UI demonstration; they are not evidence of a deployed application or a new LangGraph interrupt/resume test.

No online Streamlit application or production web deployment is included in the current scope.

**Phase 8 status: Offline notebook UI implemented and notebook execution validated.**

---

# 5. Current Phase and Consolidated Validation Status

## 5.1 Current project status

The core ComplaintIQ platform implementation and the selected offline demonstration scope are in place. Phase 7 evaluation evidence has been consolidated, but Phase 7 is not fully complete. The project should be described as a validated prototype with documented evaluation gaps, not as a production-ready banking complaints platform.

## 5.2 Consolidated evaluation status

| Track | Latest evidence | Remaining qualification |
|---|---|---|
| G1 – Triage | 60/60 final closure; product accuracy 90.00%; normalized issue accuracy 46.67%; issue macro-F1 0.3444 | Severity/vulnerability annotation remains 0/60 |
| G2 – Analytics | Strict equality 13/18 (72.22%); five additional semantic equivalences manually accepted | Two unanswerable refusal outcomes not proven |
| G3 – Regulatory QA | 17 answerable cases; Opus 14 ACCEPT / 3 REVISE; retrieval and citation metrics recorded | Three REVISE cases, human compliance review, and automated abstention validation remain open |
| G4 – Safety | Guard 10/10; synthetic PII checks 8/8 | Human rubric pending; no full agent end-to-end validation |
| Phase 8 – Demo | `07_demo.ipynb` executed successfully across 17 cells | Notebook-based demonstration only; no online deployment |

## 5.3 Important validation evidence

- Phase 0–5 unified validation: 156/156 checks passed.
- Phase 0–6 consolidated validation output: 80/80 checks passed.
- Phase 6 workflow validation exercised five intents and the human interrupt/resume path.
- A separate approved live S3 publishing run verified three report objects (ANALYTICS, BRIEF, REG_QA) and three audit records.
- G3 master validation recorded 70/70 checks passed; this is structural/master validation, not semantic or human regulatory approval.
- Phase 7 consolidated audit status: `PHASE7_PARTIAL_EVIDENCE_CONSOLIDATED`.

These counts belong to different validation scopes and must not be added together or interpreted as a single overall pass rate.

## 5.4 Scope decision for the demonstration

The selected demonstration deliverable is the offline Jupyter notebook UI in `notebooks/07_demo.ipynb`. An online Streamlit application is not part of the current implementation scope. The user has indicated that a demo video is not required for the current project deliverable.

---

# 6. Security, Reliability and Quality Controls

Several controls were implemented across the project.

## 6.1 PII protection

The guard and critic components include PII-related checks.

The objective is to detect potentially sensitive information and prevent unredacted personal information from appearing in generated responses.

## 6.2 Prompt-injection handling

The input guard includes prompt-injection detection and treats user-provided content as untrusted input.

## 6.3 SQL safety

The analytical workflow uses SQL validation and `guard_sql` to restrict unsafe SQL execution.

The reference SQL evaluation also used the SQL guard before executing queries.

## 6.4 Evidence-grounded generation

Regulatory answers are expected to use retrieved evidence.

Citation identifiers are included in generated answers to support source traceability.

## 6.5 Critic-based validation

The critic evaluates drafts before they can proceed through the workflow.

A valid citation ID is necessary but not sufficient. The cited source must support the associated claim.

## 6.6 Human oversight

The workflow includes a human interrupt and approval mechanism for outputs that require additional review.

## 6.7 State persistence

SQLite checkpointing is used to preserve graph execution state and support workflow resumption.

---

# 7. Repository Structure and Important Artifacts

The project uses the following main directories and files.

```text
complaintiq/
│
├── notebooks/
│   └── 06_eval.ipynb
│
├── src/
│   ├── indexing/
│   └── [additional project modules]
│
├── data/
│   └── [processed complaint data and related inputs]
│
├── eval/
│   ├── gold/
│   │   ├── G3_regulatory_gold.jsonl
│   │   └── G3_supervisory_candidates.jsonl
│   │
│   └── results/
│       ├── G3_retrieval_results.csv
│       ├── G3_retrieval_summary.json
│       ├── G3_generated_answers.jsonl
│       ├── G3_citation_results.csv
│       ├── G3_critic_summary.csv
│       ├── G3_critic_results.jsonl
│       ├── G3_generated_answers_validated.jsonl
│       ├── G3_failure_analysis.csv
│       ├── G3_repaired_answers.jsonl
│       ├── G3_repair_summary.csv
│       ├── G3_repair_errors.jsonl
│       └── correction_backups/
│
├── state/
│   └── checkpoints.sqlite
│
├── reports/
│   └── [generated evaluation and analysis reports]
│
└── README.md
```

**Note:** This is a documentation-oriented view of the known project artifacts, not a verified exhaustive listing of every file currently present in the repository. The exact repository tree should be checked before treating it as the final directory manifest.

---

# 8. Current Project Completion Summary

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Project foundation and initial setup | Foundation established; detailed historical setup record incomplete |
| Phase 2 | Data engineering and knowledge preparation | Completed |
| Phase 3 | RAG and vector retrieval | Core implementation completed; retrieval precision/source completeness limitations documented |
| Phase 4 | LLM integration and model wrapper | Core implementation completed |
| Phase 5 | Multi-agent implementation | Core implementation completed |
| Phase 6 | LangGraph orchestration | Core workflow validated; approved S3 publishing demonstrated for three reports |
| Phase 7 | Evaluation and quality validation | Partial evidence consolidated; outstanding human, baseline, ablation, abstention, and cost evidence |
| Phase 8 | Demonstration | Offline notebook UI implemented; no online deployment |

### Completed implementation and validation milestones

- Complaint dataset preparation and June holdout separation.
- Regulatory document processing, Titan embedding generation, and FAISS indexing.
- Complaint and regulatory retrieval components.
- Bedrock LLM integration and structured response handling.
- Agent-based workflow, SQL guard, PII and prompt-injection checks.
- LangGraph orchestration, human interrupt/resume workflow validation, and SQLite checkpointing implementation.
- Approved live S3 publication and verification for ANALYTICS, BRIEF, and REG_QA reports.
- G1 final closure metrics for 60 records.
- G2 strict result comparison and manual semantic-equivalence review.
- G3 retrieval, answer-generation, citation, critic, independent Opus, and manual-review artifacts.
- G4 offline prompt-injection and synthetic PII checks.
- Phase 7 consolidated checkpoint audit and three selected failure analyses.
- Phase 8 offline notebook demonstration, executed successfully across 17 cells.

---

# 9. Remaining Work and Recommended Next Steps

The remaining work below is presented as known evaluation and documentation gaps, not as a claim that all items must be implemented before demonstrating the current prototype.

## 9.1 G1 – Triage

1. Complete human annotation of the 60 records for severity and vulnerability-related fields if those metrics are required.
2. Calculate and report severity/vulnerability metrics only after annotation is completed.
3. Retain the final closure classification metrics and document the observed classification errors.

## 9.2 G2 – Analytics

1. Preserve the strict equality result of 13/18 separately from the five manually accepted semantic equivalents.
2. If required, validate the actual refusal outputs for G2-19 and G2-20.
3. Retain query-level discrepancies and avoid presenting semantic equivalence as strict equality.

## 9.3 G3 – Regulatory QA

1. Review G3-04, G3-06, and G3-15, which were marked REVISE by the independent Opus evaluation.
2. Complete genuine human regulatory/compliance review if required by the project acceptance criteria.
3. Investigate the automated abstention detector's 0/3 result separately from the manual review of the three refusal answers.
4. Keep citation-ID validity separate from semantic citation support.
5. Do not replace original evaluation artifacts or detector outputs with manually or AI-adjusted labels.

## 9.4 G4 – Safety

1. Complete the 10-case human evaluation worksheet if the human 1–5 rubric is required.
2. Treat current guard and PII results as offline component checks, not full end-to-end agent validation.

## 9.5 Cross-track evaluation gaps

1. Run and preserve B0/B1/B2 baseline experiments only if remaining budget and project scope permit.
2. Run and preserve A1/A2 ablation experiments only if required and feasible.
3. Complete the ten-case human judge calibration with genuine human labels before reporting human agreement or Cohen's kappa.
4. Capture validated cost-per-request data only if supported by reliable usage and pricing evidence.
5. Complete a comparable checkpoint latency table only when measurements use a consistent methodology.

## 9.6 Final project documentation

1. Update the report and README from the latest executed `06_eval.ipynb` and `07_demo.ipynb`.
2. Preserve actual notebook outputs and the original evaluation artifacts.
3. Clearly label implemented, executed, partially validated, and not completed items.
4. Document the offline notebook UI as the current demo scope; do not describe it as a deployed web application.

---

# 10. Environment Recovery Notes

The project was developed using AWS SageMaker Studio.

If the SageMaker Studio lab session expires, the repository and its Git-pushed contents should be treated separately from the temporary notebook execution environment.

To resume:

1. Reopen the SageMaker Studio environment.
2. Clone or pull the latest repository version.
3. Verify the Python environment and dependencies.
4. Confirm AWS credentials and Bedrock permissions.
5. Confirm access to the required S3 data and model resources.
6. Restore the notebook execution context.
7. Verify the processed data, vector indices, and evaluation artifacts.
8. Verify the checkpoint database before attempting to resume any graph workflow.

Example repository recovery commands:

```bash
git clone <YOUR_REPOSITORY_URL>
cd complaintiq

git status
git pull origin main
```

Check the configured AWS identity:

```bash
aws sts get-caller-identity
```

Check the configured region:

```bash
aws configure get region
```

Expected region:

```text
us-east-1
```

Do not assume that temporary notebook variables, in-memory FAISS objects, or runtime state will survive an expired SageMaker session. Reload them from their persisted artifacts.

Do not overwrite the existing checkpoint database or evaluation results without first backing them up.

---

# 11. Known Limitations

1. Regulatory retrieval does not consistently retrieve complete source text for every detailed legal statement.
2. Citation-ID validity does not establish semantic citation correctness.
3. G3 independent Opus evaluation marked three answers (G3-04, G3-06, G3-15) REVISE.
4. G3 automated abstention detection passed 0/3 intentionally unanswerable cases, although manual inspection considered the refusal wording acceptable; these are different forms of evidence.
5. G1 severity and vulnerability annotations remain incomplete (0/60).
6. G2 refusal behavior for the two unanswerable questions is not established by the available evidence.
7. G4 human rubric review remains pending; current checks cover offline guard and synthetic PII behavior only.
8. B0/B1/B2 baseline and A1/A2 ablation evidence was not found in the consolidated audit.
9. Genuine human judge calibration and human Cohen's kappa are not available. AI-assisted labels must not be represented as human labels.
10. Cost per request is not available from the consolidated checkpoint evidence.
11. The Phase 8 deliverable is a notebook-based offline UI, not an online Streamlit or production deployment.
12. The platform has not been established as production-ready or approved for regulated banking use.

These limitations should remain visible until the corresponding evidence is completed and verified.

---

# 12. Final Project Objective

The final goal of ComplaintIQ is to provide a reliable, traceable, and controlled banking complaints intelligence assistant that combines:

- Historical complaint intelligence.
- Structured analytics.
- Regulatory knowledge retrieval.
- LLM-powered reasoning.
- Multi-agent orchestration.
- Evidence-grounded response generation.
- Automated quality evaluation.
- Human approval and oversight.

The project has established its core data, retrieval, LLM, agent, and orchestration components, demonstrated approved report publication, consolidated evaluation evidence across G1–G4, and implemented an offline notebook demonstration.

**Overall project status: Core prototype implementation and offline demonstration are in place. Phase 7 has partial evaluation evidence with clearly documented outstanding validation gaps. The project is not represented as production-ready.**
