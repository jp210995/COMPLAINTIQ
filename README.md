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

Evaluate the platform using structured test datasets, gold-standard questions, retrieval checks, answer generation, citation validation, critic evaluation, and human review.

Phase 7 is the evaluation and quality-validation phase.

It contains three major evaluation tracks:

- G1 – Complaint triage evaluation.
- G2 – Structured analytics evaluation.
- G3 – Regulatory question-answering evaluation.

**Important: Phase 7 implementation and evaluation activities have been performed, but the phase is not yet fully complete. Several empirical and manual validation tasks remain outstanding.**

---

### 7.1 G1 – Complaint Triage Evaluation

#### Objective

Evaluate whether the system can correctly identify complaint product, issue, sub-issue, severity, and vulnerability-related information.

#### Dataset preparation

A 60-record evaluation dataset was created.

The records contain:

```json
{
  "case_id": "...",
  "request": "...",
  "expected": {
    "product": "...",
    "issue": "...",
    "sub_issue": "..."
  },
  "manual_annotation": {
    "severity": null,
    "vulnerable_customer": null,
    "vulnerability_signals": null,
    "regulation_hints": null,
    "summary": null
  },
  "source": {},
  "annotation_status": "pending"
}
```

#### Manual annotation template

A separate CSV template was prepared with the following fields:

```text
case_id
severity
vulnerable_customer
vulnerability_signals
regulation_hints
summary
reviewer
review_notes
annotation_status
```

#### Dataset composition

| Product | Records |
|---|---:|
| Checking or savings | 32 |
| Credit card | 28 |
| Total | 60 |

#### Validation results

The following structural validation results were obtained:

| Validation | Result |
|---|---:|
| JSONL records | 60 |
| Unique case IDs | 60 |
| CSV rows | 60 |
| Schema errors | 0 |
| Complete manual annotation records | 0 |

The dataset was also checked for overlap with the June holdout.

#### Current G1 status

The G1 dataset and annotation template are structurally validated.

However, manual annotation remains pending.

Therefore, severity and vulnerability evaluation metrics should not be treated as completed or empirically validated.

**G1 status: Dataset preparation and structural validation completed; human annotation and final metric calculation pending.**

---

### 7.2 G2 – Structured Analytics Evaluation

#### Objective

Evaluate the analytical accuracy of the platform's SQL-based complaint analytics workflow.

#### Evaluation dataset

A set of 20 analytical questions was prepared.

The questions were classified as:

| Category | Count |
|---|---:|
| Answerable | 18 |
| Unanswerable | 2 |
| Total | 20 |

#### Reference SQL generation

Reference SQL queries were generated for the analytical questions.

The implementation used:

- DuckDB.
- SQL validation.
- `guard_sql`.
- Read-only query execution.
- Reference result generation.

The objective was to compare the agent's generated analytical results against independently executed reference queries.

#### Validation activities

The following were performed:

- Evaluation question preparation.
- Answerability classification.
- Reference SQL generation.
- SQL guard validation.
- Reference query execution.
- Gold and expected output preparation.
- Structural validation of evaluation artifacts.

#### Current G2 status

The evaluation dataset and reference artifacts were prepared and structurally validated.

However, the complete empirical comparison between actual agent outputs and reference results remains pending.

Consequently, no final analytical accuracy score should be reported yet.

**G2 status: Evaluation dataset and reference outputs prepared; agent-versus-reference empirical evaluation pending.**

---

### 7.3 G3 – Regulatory Question-Answering Evaluation

#### Objective

Evaluate whether the system can answer regulatory questions accurately using retrieved CFR, examination manual, and supervisory evidence.

This evaluation focuses on:

- Regulatory correctness.
- Evidence relevance.
- Citation validity.
- Grounded answer generation.
- Appropriate abstention.
- Critic-based quality assessment.

#### Evaluation dataset

A set of 20 regulatory questions was prepared.

| Category | Count |
|---|---:|
| Answerable questions | 17 |
| Intentionally unanswerable questions | 3 |
| Total | 20 |

The 17 answerable questions covered regulatory subjects such as:

- Regulation E.
- Regulation Z.
- Regulation V.
- Regulation F.
- Regulation DD.
- Supervisory Highlights.

Three questions were deliberately designed around proprietary Harbourline-specific information, which was not available in the knowledge corpus. These questions were intended to test whether the platform would abstain rather than fabricate information.

#### Gold-standard artifacts

The following files were prepared:

```text
eval/gold/G3_regulatory_gold.jsonl
eval/gold/G3_supervisory_candidates.jsonl
eval/results/G3_gold_resolution_summary.csv
```

One supervisory question, G3-17, was manually mapped to a specific source chunk:

```text
sh_issue22_2020-09_page_0011_chunk_0001
```

Source:

```text
sh_issue22_2020-09.pdf
```

Page:

```text
11
```

The chunk concerned a supervisory finding involving an advertised bonus offer and Regulation DD.

This mapping represents one verified finding and should not be interpreted as complete coverage of every deposit-account supervisory finding.

#### Retrieval evaluation

The G3 retrieval evaluation was executed.

Output artifacts:

```text
G3_retrieval_results.csv
G3_retrieval_summary.json
```

The retrieval evaluation examined whether relevant regulatory and supervisory chunks could be retrieved for the gold questions.

#### Answer generation

The answer-generation process was executed for all 17 answerable questions.

Generation output:

```text
G3_generated_answers.jsonl
```

All 17 answer-generation executions completed.

#### Citation validation

Citation validation was implemented to check the relationship between answer citation identifiers and the evidence supplied to the answer.

The citation parser was corrected to support multiple citation IDs within a single citation marker.

The validation process was also improved to distinguish:

- Valid citation IDs.
- Invalid citation IDs.
- Citation counts.
- Answers containing unsupported references.

#### Critic evaluation

The critic was executed against the 17 generated answers.

An initial correction run produced the following result:

| Result | Count |
|---|---:|
| PASS | 2 |
| REVISE | 11 |
| UNKNOWN | 4 |
| Total | 17 |

A subsequent validation and resolution run recovered all 17 drafts and corrected the citation parsing and critic result handling.

Run ID:

```text
20261106T142806Z
```

The corrected result was:

| Validation item | Result |
|---|---:|
| Total answers | 17 |
| Drafts recovered or generated | 17 |
| Unresolved drafts | 0 |
| Total citations | 80 |
| Valid citation IDs | 80 |
| Invalid citation IDs | 0 |
| Critic executions | 17 |
| Critic errors | 0 |
| PASS | 2 |
| REVISE | 15 |

This established that all 80 citation identifiers existed in the supplied evidence arrays.

It did **not** establish that all 80 citations semantically supported their associated statements.

#### G3 failure analysis

A detailed failure analysis was performed on the 15 answers marked REVISE.

The analysis identified several recurring issues:

1. Regulatory chunks were truncated before the full provision was available.
2. Some answers included claims that were not present in the cited evidence.
3. Some citations referenced the wrong chunk.
4. Some numerical claims were unsupported.
5. Some regulatory exceptions were extrapolated beyond the supplied text.
6. Some supervisory findings were not sufficiently qualified as examiner observations.
7. Some answers contained additional explanations that could not be substantiated using the available evidence.

The failure analysis was saved as:

```text
eval/results/G3_failure_analysis.csv
```

Examples of identified issues included:

- Regulation E provisional credit and error-resolution requirements.
- Regulation E consumer liability and negligence examples.
- Regulation Z billing-error procedures.
- Regulation V furnisher investigation and dispute obligations.
- Regulation F debt collection restrictions.
- Regulation DD disclosure requirements.
- Interest calculation and compounding provisions.

The key finding was that valid citation identifiers alone are insufficient. The cited source text must actually contain the regulatory statement being made.

#### Targeted repair attempt

A targeted repair attempt was executed.

Run ID:

```text
20261106T144421Z
```

The attempted process:

1. Loaded the 15 failed answers.
2. Loaded their critic feedback.
3. Retrieved fresh evidence through the research node.
4. Merged original and fresh evidence.
5. Passed the critic feedback through attempted revision fields.
6. Invoked the drafter.
7. Re-ran the critic.
8. Saved the repair outputs.

The repair artifacts included:

```text
G3_repaired_answers.jsonl
G3_repair_summary.csv
G3_repair_errors.jsonl
G3_targeted_repair_run_summary.json
```

However, the subsequent diagnostic established that the repair attempt had not changed the answer text.

#### Repair diagnostic findings

The diagnostic compared the original and repaired answers.

| Diagnostic | Result |
|---|---:|
| Failed answers processed | 15 |
| Identical drafts | 15 |
| Changed drafts | 0 |
| New evidence chunks | 0 |
| Critic PASS after repair | 0 |
| Critic REVISE after repair | 15 |

The drafts were byte-for-byte identical.

The original and repaired evidence IDs were also identical.

This indicated that the attempted repair did not successfully pass the critic's feedback into an effective revision process.

Further investigation identified that:

- `drafter_node` accepts a `CIQState` object.
- `CIQState` includes a `critique` field.
- The drafter references a variable named `critique`.
- The earlier repair attempt passed guessed feedback fields without verifying that the drafter consumed them.
- The research node uses the existing `REG_INDEX.search` method.
- Repeating the same search produced the same eight evidence chunks for the tested questions.

The next step is to inspect the exact drafter implementation and retrieval behavior before implementing another repair.

#### G3 artifacts

The following evaluation artifacts were created or updated:

```text
eval/results/G3_retrieval_results.csv
eval/results/G3_retrieval_summary.json
eval/results/G3_generated_answers.jsonl
eval/results/G3_citation_results.csv
eval/results/G3_critic_summary.csv
eval/results/G3_critic_results.jsonl
eval/results/G3_generated_answers_validated.jsonl
eval/results/phase7_validation_resolution_summary.json
eval/results/G3_failure_analysis.csv
eval/results/G3_repaired_answers.jsonl
eval/results/G3_repair_summary.csv
eval/results/G3_repair_errors.jsonl
eval/results/G3_targeted_repair_run_summary.json
```

Correction backups were retained under:

```text
eval/results/correction_backups/
```

#### Latest G3 independent Opus evaluation and Phase 7 master validation

A subsequent independent evaluation was completed for all 17 answerable G3 questions using Claude Opus 4.8. The saved evaluation output records:

| Result | Count |
|---|---:|
| Questions evaluated | 17 |
| ACCEPT | 14 |
| REVISE | 3 |

The three questions marked REVISE were G3-04, G3-06, and G3-15. This is the latest independent Opus evaluation result and supersedes the earlier 2 PASS / 15 REVISE critic-run summary as the current G3 evaluation snapshot. The earlier run remains part of the development history and failure-analysis record.

The saved `Validation(1).ipynb` also contains an executed Phase 7 G3 master validation cell (cell index 284; saved `execution_count` 1). Its recorded result is:

| Master validation item | Result |
|---|---:|
| Checks | 70 |
| Passed | 70 |
| Failed | 0 |
| Warnings | 0 |

The master validation output records all 17 G3 questions as evaluated and reports 17/17 structural checks passed. Its semantic review records four PASS and three REVIEW outcomes. The three REVIEW outcomes are not equivalent to failed structural checks; they indicate items that still require attention.

The Opus evaluation and the master validation are validation evidence for the G3 work performed. They do not constitute legal advice, regulatory approval, or sign-off by a human compliance reviewer.

#### Current G3 status

| Activity | Status |
|---|---|
| Gold question preparation | Completed |
| Retrieval evaluation | Executed |
| Answer generation | 17/17 executed |
| Citation ID validation | Completed |
| Earlier critic evaluation and failure analysis | Completed |
| Targeted repair attempt | Attempted; earlier repair was ineffective |
| Independent Opus evaluation | 17 evaluated; 14 ACCEPT / 3 REVISE |
| Phase 7 G3 master validation | 70/70 checks passed |
| Structural validation | 17/17 passed |
| Semantic review | 4 PASS / 3 REVIEW |
| Follow-up on G3-04, G3-06 and G3-15 | Pending |
| Manual regulatory/compliance review | Pending |
| Unanswerable-question abstention validation | Pending |

**G3 status: Independent evaluation and master validation executed successfully; three answers remain marked REVISE, and semantic/manual review and abstention validation remain open.**

---

# 5. Current Phase and Consolidated Validation Status

## 5.1 Current project phase

**Current phase: Phase 7 – Evaluation and Quality Validation.**

The project is currently in the G3 regulatory question-answering evaluation and refinement workstream. The latest saved G3 evaluation covers 17 answerable questions, with 14 ACCEPT and 3 REVISE from the independent Opus evaluation. The Phase 7 G3 master validation cell records 70/70 checks passed.

Phase 7 as a whole is **not complete**. G1 manual annotation and final metrics, G2 agent-versus-reference empirical comparison, remaining G3 review/follow-up, and the broader cross-track acceptance activities still need to be completed.

## 5.2 Consolidated validation status

| Evaluation track | Prepared dataset | Executed validation evidence | Remaining work |
|---|---|---|---|
| G1 – Triage | 60 records | Dataset/schema structure validated | Manual annotation and final triage metrics |
| G2 – Analytics | 20 questions | Reference SQL and expected outputs prepared | Agent-versus-reference empirical comparison and metrics |
| G3 – Regulatory QA | 20 questions (17 answerable, 3 intentionally unanswerable) | 17 answerable questions evaluated; Opus result 14 ACCEPT / 3 REVISE; G3 master validation 70/70 checks passed | Resolve/review the 3 REVISE answers; semantic and human review; validate abstention on 3 unanswerable questions |

## 5.3 Completed validation evidence

- Phase 0–5 unified validation: 156/156 checks passed (P0 19/19, P1 5/5, P2 14/14, P3 44/44, P4 16/16, P5 58/58).
- Phase 0–6 consolidated validation output: 80/80 checks passed.
- Phase 6 workflow test: all five intents exercised, including human interrupt/resume.
- Phase 6 approved live publishing run: three report objects (`ANALYTICS`, `BRIEF`, `REG_QA`) uploaded to the documented S3 prefix and verified; three audit records verified.
- Phase 7 G3 master validation: 70/70 checks passed, with 17/17 structural checks passed.
- Independent G3 Opus evaluation: 17 questions evaluated; 14 ACCEPT and 3 REVISE.

These validation counts belong to different scopes and runs; they are not additive. A passed structural/master validation does not imply that every answer is semantically correct or has received human regulatory approval.

## 5.4 Overall status

The core platform implementation and the Phase 6 workflow/publishing demonstrations are complete within the scope described above. Phase 7 remains in progress, and the project should continue to be described as a partially completed prototype rather than a production-ready banking complaints platform.

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
| Phase 1 | Project foundation and initial setup | Foundation established; historical detail incomplete |
| Phase 2 | Data engineering and knowledge preparation | Completed |
| Phase 3 | RAG and vector retrieval | Core implementation completed |
| Phase 4 | LLM integration and model wrapper | Completed |
| Phase 5 | Multi-agent implementation | Core implementation completed |
| Phase 6 | LangGraph orchestration | Core workflow validated; approved S3 publishing demonstrated for three reports |
| Phase 7 | Evaluation and quality validation | In progress; G3 master validation passed, 14 ACCEPT / 3 REVISE |

### Completed implementation milestones

- Complaint dataset preparation.
- June holdout separation.
- Regulatory document processing.
- Titan embedding generation.
- FAISS indexing.
- Complaint and regulatory retrieval.
- Bedrock LLM integration.
- Structured JSON generation.
- Usage and latency tracking.
- Agent-based workflow.
- SQL guard.
- PII and prompt-injection checks.
- Critic-based response evaluation.
- LangGraph orchestration.
- SQLite checkpointing.
- G1, G2, and G3 evaluation dataset preparation.
- G3 answer generation and citation validation.
- G3 failure analysis.
- Phase 6 five-intent workflow validation and human interrupt/resume test.
- Approved live S3 publication and verification for ANALYTICS, BRIEF, and REG_QA reports.
- Phase 7 G3 independent Opus evaluation (14 ACCEPT / 3 REVISE).
- Phase 7 G3 master validation (70/70 checks passed).

---

# 9. Pending Work and Recommended Next Steps

The following activities remain before the project can be considered fully validated.

## 9.1 Complete G1

1. Complete manual annotation of the 60 complaint records.
2. Review severity labels.
3. Review vulnerable-customer labels.
4. Review vulnerability signals.
5. Review regulatory hints.
6. Finalize human-reviewed summaries.
7. Execute the triage evaluation.
8. Calculate classification and assessment metrics.
9. Document error cases.

## 9.2 Complete G2

1. Restore the evaluation environment.
2. Load the 20 analytical questions.
3. Execute the analytics agent against the test questions.
4. Capture actual SQL and outputs.
5. Compare actual outputs with reference SQL results.
6. Evaluate answerability and abstention for the two unanswerable questions.
7. Calculate the final analytical evaluation metrics.
8. Document discrepancies and failure cases.

## 9.3 Complete G3

1. Resume from the saved repository and evaluation artifacts; do not assume the temporary SageMaker runtime is still available.
2. Review the three Opus REVISE cases: G3-04, G3-06, and G3-15.
3. Inspect the actual `drafter_node` implementation and confirm how it consumes the `critique` field.
4. Inspect the regulatory retrieval implementation and source completeness for the affected answers.
5. Improve or supplement retrieval where complete source text is available.
6. Revise unsupported or overextended claims and preserve appropriate qualifications.
7. Re-run the relevant G3 evaluation steps only when the environment and budget permit.
8. Complete manual regulatory/compliance review of all 17 answerable outputs.
9. Validate the three intentionally unanswerable Harbourline questions and confirm appropriate abstention.
10. Produce the final G3 evaluation report, clearly separating automated evaluation from human sign-off.

## 9.4 Final integration and project reporting

After the individual evaluation tracks are completed:

1. Execute an end-to-end workflow validation.
2. Validate all agent routing paths.
3. Verify human approval and refusal behavior.
4. Verify source citations and traceability.
5. Review security and PII handling.
6. Consolidate the G1, G2, and G3 evaluation results.
7. Prepare the final project report.
8. Document known limitations and future improvements.

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

The following limitations were identified during development and evaluation:

1. Regulatory retrieval does not consistently retrieve the complete text needed to support every detailed legal statement.
2. Some regulatory chunks are truncated, making them insufficient for detailed answer generation.
3. Citation ID validation does not establish semantic citation correctness.
4. Earlier G3 critic runs identified unsupported statements and incorrect citation mappings.
5. The first targeted G3 repair attempt did not change answer text; the latest independent Opus evaluation subsequently rated 14/17 ACCEPT and 3/17 REVISE.
6. G1 manual annotation has not been completed.
7. G2 agent-versus-reference empirical evaluation has not been completed.
8. The three G3 REVISE answers, manual review, and unanswerable-question abstention validation remain pending.
9. The 70/70 G3 master validation is not a substitute for semantic or human regulatory approval.
10. Model cost estimates require separate validation against actual usage and pricing.
11. Final end-to-end performance and quality metrics have not yet been consolidated.

These limitations should remain visible in the project documentation until they are addressed and verified.

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

The project has established the core data, retrieval, LLM, agent, and orchestration components.

The remaining focus is to complete G1 and G2 empirical evaluation, address the three G3 REVISE answers, complete human review and abstention testing, and consolidate cross-track performance results.

**Overall project status: Core platform implementation completed within the documented scope; Phase 7 evaluation and final validation remain in progress.**
