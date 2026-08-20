# Behavior-Driven Product Analytics & Experimentation Platform

An end-to-end product analytics and experimentation platform for analyzing user behavior, measuring product performance, evaluating A/B experiments, generating decision-oriented insights, and persisting analytical artifacts to cloud storage.

The project combines **product analytics, experimentation, statistical inference, data validation, workflow orchestration, experiment tracking, API serving, dashboarding, containerization, CI/CD, and AWS integration** in a single reproducible analytics system.

---

## 1. Overview

Modern product teams continuously ship changes to recommendation systems, ranking algorithms, user interfaces, onboarding flows, pricing strategies, and other product experiences.

Shipping a change, however, does not answer the most important question:

> Did the change actually improve the product?

A metric can move for many reasons. Conversion may increase because of a successful product change, but it may also move because of traffic composition, assignment problems, random variation, or other behavioral effects.

This project builds a product analytics and experimentation platform that moves from raw behavioral events to validated product decisions.

The system:

- generates synthetic product-event data,
- validates event quality,
- computes product KPIs,
- analyzes funnels and user behavior,
- performs cohort and retention analysis,
- evaluates controlled experiments,
- checks experiment health and guardrails,
- tracks experiment results using MLflow,
- generates behavior-driven insights,
- exposes analytical outputs through FastAPI,
- provides an interactive Streamlit dashboard,
- orchestrates the analytics workflow using Apache Airflow,
- persists selected analytical artifacts to Amazon S3,
- and validates the pipeline through automated execution and CI checks.

---

## 2. Problem Statement

Product teams should not make launch decisions from a single metric in isolation.

Suppose a new recommendation experience increases conversion.

Before recommending a rollout, a Product Data Scientist should ask:

- Is the observed difference statistically significant?
- Is the experiment assignment valid?
- Is there evidence of sample-ratio mismatch?
- Did important guardrail metrics deteriorate?
- Does the confidence interval support the decision?
- Are behavioral changes consistent with the primary metric?
- Could the observed result be explained by data-quality problems?

The platform is designed around this decision-making process.

Instead of producing only dashboards, it creates a pipeline from:

**behavior → metrics → experiment evidence → validation → insight → decision support**

---

## 3. Project Objectives

The V1 platform was built to demonstrate the following capabilities:

- Product-event simulation
- Event-data validation
- KPI and product-metric computation
- Funnel analysis
- Cohort and retention analysis
- Controlled A/B experiment analysis
- Statistical significance testing
- Confidence-interval estimation
- Sample Ratio Mismatch (SRM) detection
- Experiment-assignment validation
- Guardrail evaluation
- Behavior-driven insight generation
- Automated validation gates
- MLflow experiment tracking
- Interactive analytics dashboarding
- REST API access to analytical outputs
- Dockerized application execution
- Apache Airflow workflow orchestration
- Amazon S3 artifact persistence using boto3
- GitHub Actions-based CI
- Reproducible end-to-end pipeline execution

---

## 4. System Architecture

```text
                    ┌──────────────────────────┐
                    │ Synthetic Product Events │
                    └─────────────┬────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │   Event Data Validation  │
                    └─────────────┬────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │ Product Metric Pipeline  │
                    └─────────────┬────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
                ▼                 ▼                 ▼
        ┌──────────────┐  ┌──────────────┐  ┌───────────────┐
        │    Funnel    │  │  Retention   │  │ Experimentation│
        │   Analysis   │  │   & Cohort   │  │    Analysis    │
        └──────┬───────┘  └──────┬───────┘  └───────┬───────┘
               │                 │                   │
               └─────────────────┼───────────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │   Validation Guardrails │
                    │ SRM / Assignment / Stats│
                    └─────────────┬────────────┘
                                  │
                   ┌──────────────┴──────────────┐
                   │                             │
                   ▼                             ▼
          ┌────────────────┐           ┌───────────────────┐
          │ MLflow Tracking│           │ EDA / Diagnostics │
          └────────────────┘           └─────────┬─────────┘
                                                │
                                                ▼
                                    ┌───────────────────────┐
                                    │ Behavior-Driven       │
                                    │ Insight Engine        │
                                    └───────────┬───────────┘
                                                │
                     ┌──────────────────────────┼────────────────────────┐
                     │                          │                        │
                     ▼                          ▼                        ▼
             ┌──────────────┐           ┌──────────────┐        ┌──────────────┐
             │  Streamlit   │           │   FastAPI    │        │  Amazon S3   │
             │  Dashboard   │           │  REST Layer  │        │  Artifacts   │
             └──────────────┘           └──────────────┘        └──────────────┘

                         Apache Airflow orchestrates
                         the analytical task workflow
```

---

## 5. End-to-End Pipeline

The local pipeline executes analytical modules sequentially and stops if a validation or execution step fails.

The high-level workflow is:

```text
Generate Events
      ↓
Validate Events
      ↓
Compute Product Metrics
      ↓
Validate Product Metrics
      ↓
Retention / Cohort Analysis
      ↓
Validate Retention Outputs
      ↓
Experiment Analysis
      ↓
Validate Experiment
      ↓
MLflow Experiment Tracking
      ↓
EDA Diagnostics
      ↓
Validate Diagnostics
      ↓
Behavior-Driven Insight Generation
      ↓
Validate Insights
      ↓
Upload Selected Artifacts to Amazon S3
```

The S3 upload occurs only after the analytical and validation stages complete successfully.

This prevents failed upstream processing from being treated as a successfully completed analytics workflow.

---

## 6. Synthetic Behavioral Event Generation

The project uses synthetic product-event data to create a controlled environment for developing and testing the analytics platform.

The generated event data represents user interactions with a digital product and provides the behavioral foundation for:

- product metrics,
- funnel analysis,
- retention analysis,
- experimentation,
- diagnostics,
- and insight generation.

A dedicated validation stage checks the generated event data before downstream analytics are allowed to execute.

This separation between **generation** and **validation** prevents downstream metrics from silently consuming malformed input data.

---

## 7. Product Metrics

The analytics layer computes core product metrics from behavioral event data.

The platform is designed around product questions rather than simply producing aggregations.

Analytical outputs are persisted under:

```text
data/processed/
```

and are consumed by downstream experimentation, diagnostics, APIs, dashboarding, MLflow, and cloud-storage components.

---

## 8. Funnel Analysis

The platform analyzes user progression through product journeys.

Funnel analysis helps answer questions such as:

- Where do users drop out?
- Which stage creates the largest conversion loss?
- How efficiently do users progress through the product journey?
- Where should a product team investigate friction?

Funnel outputs are persisted as processed analytical artifacts and are also exposed through the API/dashboard layer.

---

## 9. Cohort and Retention Analysis

The retention module groups users into cohorts and evaluates how user activity evolves after acquisition or initial activity.

The project produces retention-related outputs including:

```text
retention_metrics.csv
cohort_retention_matrix.csv
```

This enables analysis of:

- user retention,
- cohort behavior,
- changes in engagement over time,
- and differences between groups of users.

Retention analysis complements conversion metrics by showing whether product value persists beyond a single interaction.

---

## 10. Experimentation Framework

A core component of the project is the A/B experimentation framework.

The system evaluates control and treatment groups using statistical and experiment-health checks.

Experiment outputs include measures such as:

- Control conversion rate
- Treatment conversion rate
- Absolute lift
- Relative lift
- Z-statistic
- P-value
- Confidence interval
- SRM P-value
- Assignment validity
- Guardrail status

The experiment pipeline therefore goes beyond asking:

> Did treatment conversion increase?

It also asks:

> Is the experiment trustworthy enough for us to believe that increase?

---

## 11. Statistical Significance Testing

The experimentation module performs hypothesis testing on the difference between control and treatment outcomes.

A configurable significance threshold (`ALPHA`) is maintained in the project configuration rather than duplicated throughout analytical code.

This allows statistical decision thresholds to be modified centrally.

Experiment interpretation considers both the observed effect and statistical evidence rather than using raw conversion differences alone.

---

## 12. Confidence Intervals

Confidence intervals are calculated around experiment effects to communicate uncertainty.

This is important because a point estimate alone does not describe the plausible range of the true treatment effect.

Confidence intervals therefore provide additional evidence for product decision-making alongside hypothesis-test results.

---

## 13. Sample Ratio Mismatch Detection

The experimentation framework includes Sample Ratio Mismatch (SRM) detection.

SRM checks whether observed experiment-group allocation is consistent with the intended assignment proportions.

Unexpected allocation can indicate problems such as:

- broken randomization,
- instrumentation issues,
- eligibility differences,
- assignment bugs,
- or data loss.

An experiment with suspicious assignment should not be trusted simply because its primary metric appears statistically significant.

---

## 14. Experiment Assignment Validation

The project includes explicit validation of experiment assignment.

This separates:

```text
Treatment effect
```

from:

```text
Experiment validity
```

A statistically attractive treatment effect is insufficient if the underlying experiment was incorrectly assigned.

---

## 15. Guardrail Evaluation

Primary metrics do not capture every product consequence.

The experimentation framework therefore evaluates guardrail results alongside the primary treatment effect.

The decision layer considers:

- treatment effect,
- statistical significance,
- SRM,
- assignment validity,
- and guardrail failures.

This creates a more realistic product-experiment decision process than optimizing a single KPI.

---

## 16. Behavior-Driven Insight Engine

The project includes an insight-generation layer that transforms analytical outputs into prioritized product insights.

The goal is not merely to report metrics, but to help answer:

> What should the product team investigate or act on?

Generated insights are stored as analytical artifacts and surfaced through the application dashboard and API.

The project also supports ranked insight presentation so higher-priority findings can be surfaced first.

---

## 17. EDA and Diagnostics

A dedicated diagnostics module performs exploratory analysis on generated product data and analytical outputs.

EDA is separated from core metric computation so that exploratory diagnostics do not become mixed with production-style KPI definitions.

The diagnostics layer also has its own validation step before downstream insight generation.

---

## 18. MLflow Experiment Tracking

MLflow is used to track experimentation outputs.

Each experiment run can record:

### Parameters

- experiment name
- primary metric
- significance threshold
- experiment version

### Metrics

- control conversion rate
- treatment conversion rate
- absolute lift
- relative lift
- p-value
- confidence-interval bounds
- SRM p-value

### Tags

- SRM detected
- assignment valid
- guardrail failed

### Artifacts

Experiment output CSVs are stored as MLflow artifacts.

This creates a reproducible record of experiment evaluation rather than relying only on console output.

MLflow runs can be inspected through the local MLflow UI.

---

## 19. Streamlit Analytics Dashboard

The project includes a Streamlit dashboard for interactive exploration of analytical outputs.

The dashboard acts as the human-facing interface of the platform.

It surfaces product analytics, experimentation results, behavioral insights, and ranked findings in a form that can be consumed by product stakeholders.

Streamlit therefore serves a different responsibility from the REST API:

```text
Streamlit → Human-facing analytics interface
FastAPI   → Programmatic analytics interface
```

---

## 20. FastAPI Serving Layer

The platform exposes processed analytical outputs through a FastAPI REST layer.

V1 endpoints include:

```text
GET /
GET /health
GET /metrics
GET /funnel
GET /experiment
GET /retention
GET /insights
GET /segments/{segment_type}
```

The API reads validated analytical outputs rather than duplicating metric-calculation logic.

This keeps the serving layer thin and separates:

```text
Analytics computation
        ↓
Processed outputs
        ↓
API serving
```

Interactive API documentation is available through FastAPI's Swagger interface while the service is running.

---

## 21. Apache Airflow Orchestration

Apache Airflow is used to orchestrate the analytics workflow.

Instead of embedding analytics logic inside the DAG, Airflow executes the existing project modules as tasks.

This preserves separation of concerns:

```text
Airflow decides WHEN and IN WHAT ORDER work runs.

Project modules decide WHAT the analytical work does.
```

The DAG defines dependencies across stages such as:

```text
generate_events
      ↓
validate_events
      ↓
product_metrics
      ↓
validate_metrics
      ↓
retention_analysis
      ↓
validate_retention
      ↓
experiment_analysis
      ↓
validate_experiment
      ↓
mlflow_tracking
      ↓
eda_report
      ↓
validate_eda
      ↓
insight_engine
      ↓
validate_insights
      ↓
s3_upload
```

The Airflow integration was validated through an end-to-end DAG execution.

Task-level failures prevent downstream tasks from executing until the failure is resolved.

---

## 22. Failure Handling and Validation Gates

The platform follows a fail-fast pipeline design.

If a pipeline module exits unsuccessfully:

- the pipeline records the failure,
- downstream stages are not executed,
- and invalid analytical outputs are not treated as successful pipeline results.

Airflow provides additional task-level observability.

For example, if a task fails, dependent tasks are prevented from executing until the failed task is corrected or rerun.

This behavior was tested during development when an MLflow task encountered a container filesystem-permission issue. The failure was isolated at the MLflow task, downstream tasks were blocked, the environment issue was corrected, and the failed/downstream tasks were successfully rerun.

---

## 23. Docker

Docker is used to provide reproducible containerized execution.

The project uses containerization for application/runtime components and for the local Airflow environment.

Docker helps reduce environment-specific differences by defining application dependencies and runtime configuration explicitly.

---

## 24. Amazon S3 Integration

Amazon S3 is used as the cloud object-storage layer for selected analytical artifacts.

The project uses the AWS SDK for Python (`boto3`) to upload validated outputs programmatically.

Selected artifacts include:

```text
core_metrics.csv
funnel_metrics.csv
retention_metrics.csv
experiment_summary.csv
product_insights.csv
```

The resulting cloud-storage structure follows the pattern:

```text
s3://<project-bucket>/
└── processed/
    ├── core_metrics.csv
    ├── funnel_metrics.csv
    ├── retention_metrics.csv
    ├── experiment_summary.csv
    └── product_insights.csv
```

S3 integration was validated through:

1. AWS authentication
2. Bucket access
3. CLI upload/read verification
4. boto3-based programmatic upload
5. multi-artifact upload
6. end-to-end pipeline integration
7. Airflow orchestration integration

The S3 bucket is configured as private.

Public access is blocked, and S3-managed server-side encryption is used.

> **Important:** The project uses S3 for cloud artifact persistence. It does not claim that the complete application stack is permanently hosted or deployed on AWS.

---

## 25. CI/CD

GitHub Actions is used as the project's continuous-integration layer.

The CI workflow is designed to validate repository changes automatically and help detect failures before changes are treated as stable.

The project therefore combines:

```text
Local validation
      +
Pipeline validation
      +
Container validation
      +
CI validation
```

to improve reproducibility and reduce silent regressions.

---

## 26. Technology Stack

### Programming and Analytics

- Python
- Pandas
- NumPy
- SciPy

### Product Analytics

- KPI computation
- Funnel analysis
- Cohort analysis
- Retention analysis
- Behavioral segmentation
- Exploratory data analysis

### Experimentation

- A/B testing
- Hypothesis testing
- Z-tests
- Confidence intervals
- Sample Ratio Mismatch detection
- Assignment validation
- Guardrail analysis

### Application and Serving

- Streamlit
- FastAPI
- Uvicorn

### Experiment Tracking

- MLflow

### Workflow Orchestration

- Apache Airflow

### Cloud

- AWS
- Amazon S3
- boto3
- AWS CLI

### Engineering

- Docker
- Git
- GitHub
- GitHub Actions

---

## 27. Repository Structure

A simplified repository structure is shown below.

```text
.
├── airflow/
│   ├── dags/
│   │   └── product_analytics_dag.py
│   └── docker-compose.yaml
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── analytics/
│   │   ├── product_metrics.py
│   │   ├── retention_analysis.py
│   │   ├── validate_metrics.py
│   │   └── validate_retention.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── app.py
│   │
│   ├── config/
│   │   └── settings.py
│   │
│   ├── data_generation/
│   │   ├── generate_events.py
│   │   └── validate_events.py
│   │
│   ├── diagnostics/
│   │   ├── eda_report.py
│   │   └── validate_eda.py
│   │
│   ├── experimentation/
│   │   ├── experiment_analysis.py
│   │   └── validate_experiment.py
│   │
│   ├── insights/
│   │   ├── insight_engine.py
│   │   └── validate_insights.py
│   │
│   ├── pipeline/
│   │   └── run_pipeline.py
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   └── s3_storage.py
│   │
│   └── tracking/
│       └── mlflow_tracking.py
│
├── .github/
│   └── workflows/
│
├── app.py
├── Dockerfile
├── requirements.txt
└── README.md
```

The exact repository may contain additional generated artifacts, configuration files, tests, or supporting modules.

---

## 28. Running the Project Locally

### Prerequisites

Recommended environment:

```text
Python 3.11
Docker Desktop
Git
AWS CLI (only for AWS integration)
```

Create and activate a virtual environment before installing dependencies.

Install project dependencies:

```bash
python -m pip install -r requirements.txt
```

---

## 29. Run the End-to-End Analytics Pipeline

From the project root:

```bash
python src/pipeline/run_pipeline.py
```

A successful execution ends with a message similar to:

```text
PIPELINE COMPLETED SUCCESSFULLY
```

The pipeline is designed to stop if a required step or validation gate fails.

---

## 30. Run the Streamlit Dashboard

From the project root:

```bash
streamlit run app.py
```

The dashboard is then available through the local Streamlit URL displayed in the terminal.

---

## 31. Run the FastAPI Service

From the project root:

```bash
python -m uvicorn src.api.app:app --reload --port 8000
```

Open:

```text
http://127.0.0.1:8000/docs
```

to access the interactive Swagger API documentation.

---

## 32. Run MLflow

Experiment runs are stored using the configured local MLflow tracking directory.

On Windows, the V1 configuration uses a short local tracking path to avoid filesystem path-length issues.

Start the MLflow UI against the configured tracking location.

Example:

```bash
mlflow ui --backend-store-uri file:///C:/mlflow/productanalytics --port 5000
```

Then open:

```text
http://localhost:5000
```

and inspect:

```text
product-analytics-experimentation
```

---

## 33. Run Airflow Locally

Airflow runs through Docker.

From the Airflow directory:

```bash
cd airflow
docker compose up -d
```

Check container status:

```bash
docker compose ps
```

Then open the local Airflow UI:

```text
http://localhost:8080
```

The main DAG is:

```text
product_analytics_experimentation_pipeline
```

The DAG can then be triggered manually through the Airflow interface.

To stop the local Airflow environment:

```bash
docker compose down
```

---

## 34. AWS S3 Configuration

AWS integration requires locally configured AWS credentials with appropriate S3 permissions.

Verify authentication:

```bash
aws sts get-caller-identity
```

The project does **not** store AWS access keys or secret keys in source code.

The S3 integration uses the AWS credential chain available to boto3.

Run the S3 storage module directly with:

```bash
python src/storage/s3_storage.py
```

The end-to-end pipeline can also invoke the S3 upload stage automatically.

---

## 35. Security Considerations

The V1 project follows several basic security practices:

- AWS credentials are not hard-coded in project source.
- S3 public access is blocked.
- S3 artifacts use server-side encryption.
- Secrets should not be committed to Git.
- Generated local tracking artifacts should be excluded where appropriate.
- Cloud resources should be removed when no longer required.

This is a portfolio/learning system and should not be interpreted as a complete enterprise security architecture.

---

## 36. Key Engineering Decisions

### Separate analytics from serving

FastAPI and Streamlit consume processed analytical outputs instead of recomputing product metrics.

### Separate orchestration from business logic

Airflow coordinates existing Python modules rather than embedding analytics implementation inside the DAG.

### Validate before downstream consumption

Validation stages sit between major processing components.

### Persist only selected cloud artifacts

The project uploads selected decision-relevant outputs to S3 rather than blindly copying every local file.

### Centralize configurable statistical parameters

Experiment parameters such as the significance threshold are maintained in shared configuration.

### Fail fast

Pipeline execution stops when a required upstream stage fails.

---

## 37. Example Experiment Output

A validated experiment run produced results approximately corresponding to:

```text
Control conversion rate:   10.39%
Treatment conversion rate: 14.73%
Absolute lift:               4.35%
P-value:                     0.0383
```

These values are outputs from the project's synthetic experimentation environment and should not be interpreted as results from a real commercial product.

The platform additionally evaluates experiment validity, confidence intervals, SRM, assignment health, and guardrails before interpreting the treatment effect.

---

## 38. What This Project Demonstrates

This project is intended to demonstrate more than the ability to calculate metrics.

It demonstrates the ability to reason across the lifecycle of a product-data system:

```text
User behavior
     ↓
Data quality
     ↓
Metric definition
     ↓
Product analysis
     ↓
Experiment design
     ↓
Statistical inference
     ↓
Experiment validity
     ↓
Behavioral diagnosis
     ↓
Product insight
     ↓
Serving / communication
     ↓
Workflow orchestration
     ↓
Experiment tracking
     ↓
Cloud artifact persistence
```

The project therefore combines **Product Data Science** with practical **analytics engineering and production-oriented ML/data-system concepts**.

---

## 39. Current V1 Status

### Completed

- [x] Synthetic behavioral event generation
- [x] Event validation
- [x] Product KPI computation
- [x] Funnel analysis
- [x] Cohort analysis
- [x] Retention analysis
- [x] A/B experiment analysis
- [x] Statistical significance testing
- [x] Confidence intervals
- [x] SRM detection
- [x] Experiment-assignment validation
- [x] Guardrail evaluation
- [x] EDA and diagnostics
- [x] Behavior-driven insight generation
- [x] Validation gates
- [x] Streamlit dashboard
- [x] FastAPI serving layer
- [x] MLflow experiment tracking
- [x] Docker integration
- [x] Apache Airflow orchestration
- [x] Amazon S3 integration using boto3
- [x] GitHub Actions CI
- [x] End-to-end pipeline execution

**Project status: V1 complete.**

---

## 40. Known Limitations

The current V1 intentionally remains bounded in scope.

Key limitations include:

- Synthetic rather than real production-user data
- Batch-oriented rather than real-time event processing
- Local Airflow deployment through Docker
- Local MLflow tracking rather than a managed tracking service
- S3 artifact persistence rather than full AWS application hosting
- No production-scale distributed data warehouse
- No streaming infrastructure
- No enterprise authentication/authorization layer
- No production Kubernetes deployment

These are deliberate V1 boundaries rather than hidden claims.

---

## 41. Future Improvements

Possible future versions could extend the platform with:

- Real production event ingestion
- Kafka/Kinesis-based streaming
- Data warehouse integration
- Distributed analytical processing
- Automated experiment monitoring
- Advanced segmentation
- Sequential experimentation
- Multiple-testing corrections
- CUPED or variance-reduction techniques
- Automated anomaly detection
- Managed cloud orchestration
- Remote MLflow tracking
- Infrastructure as Code
- Full cloud deployment
- Production observability and alerting

These features are **not required for V1**.

---

## 42. Project Philosophy

The central principle behind this project is:

> A metric movement is not automatically a product conclusion.

Reliable product decisions require:

- trustworthy data,
- correctly defined metrics,
- valid experiments,
- statistical evidence,
- behavioral context,
- guardrail awareness,
- and reproducible analytical systems.

The platform was built around that principle.

---

## License

This repository is intended primarily for educational, portfolio, and interview-demonstration purposes.
