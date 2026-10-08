# CSCI 4150 project checkoff: ECOllateral

Status: evidence and presentation package prepared for the mid-semester review.
The assigned October 20/23 presentation day and exact submission time remain pending.
Use the completion column for the stated item, rather than treating the whole project
as field-validated. The checkoff source is the user's two-page course handout.

## Project Scope & AI Integration

| Item | Status | Project response / evidence |
| --- | --- | --- |
| Clear goal, problem, and primary question | Documented | Dossier: estimate physically plausible on-site cooling consumption and locate regulatory excerpts for review |
| Achievable sub-goals and scope before mid-term | Documented | Runnable scenario prototype, four evidence investigations, separate field-validation backlog |
| Class AI tools/concepts mapped or exclusions justified | Partial | Symbolic rules, tabular ML, vector retrieval, uncertainty and missingness are mapped; neural/LLM work is deferred; actual studio names/links still need team confirmation |

## Data Acquisition & Governance

| Item | Status | Project response / evidence |
| --- | --- | --- |
| Identify public data, permitted scraping, or survey requirements | Documented for current scope | USGS/NOAA public APIs and bulk files; no current surveys or private scraping; future permit sources need review |
| Exactly document where data come from and mark public datasets | Documented | `data-governance.md`, endpoint names, station IDs, source periods, evidence manifest |
| Confirm instructor permissions for scraping / IRB before surveys | Pending if scope expands | No approval is claimed; Scott coordinates instructor clarification before new scraping or surveys |
| Clean flow into system components | Implemented / tested | Ingestion, monthly features, train-only imputation, regression, physical clipping, retrieval, extractive text, JSON |

## System Architecture & Evaluation

| Item | Status | Project response / evidence |
| --- | --- | --- |
| Visual block diagram of component interactions | Prepared | Semantic/system SVG and PNG; native editable map in presentation |
| Evaluation metrics for individual components | Documented / tested | Unit conversions, invalid-input tests, MAE/RMSE/R2, coverage, MGD2 sensitivity variance, geographic inclusion/exclusion |
| Explicit success and failure criteria for outputs | Documented | Bounds and warning invariants; R2 > 0.80 and MAE < 0.05 MGD benchmark target; >=90% sensitivity tolerance criterion; field criteria remain unverified |
| Component test plan | Implemented with limits | 51 local tests; fault-injected bounds, model reload, imputation isolation, donor failures, geographic retrieval, API errors; real-corpus relevance evaluation remains planned |

## Team Organization & Workflow

| Item | Status | Project response / evidence |
| --- | --- | --- |
| Assign sub-goals and responsibilities to each member | Assigned | Shaun: coding/integration; Troy: environmental data and validation; Scott: permit/evidence review and presentation |
| Shared GitHub repository with instructor/TA access | Partial | Configured remote: `https://github.com/ScottLiu12/ECOllateral`; actual collaborators, instructor/TA access, and pushed snapshot are unverified |

## Presentation Preparation

| Item | Status | Project response / evidence |
| --- | --- | --- |
| Show architecture assessment if full system is incomplete | Prepared | Distinguish working prototype from unvalidated field forecasting; semantic map shows both numeric and document paths |
| Draft mid-semester materials and slides | Prepared | Six slides, editable PPTX, PDF export, four-minute script |
| Explain the problem | Prepared | Slide 1 and dossier problem/user statement |
| Explain sub-goals, milestones, and teammate mapping | Prepared | Team snapshot and role-owned roadmap |
| Identify AI concepts/tools used | Prepared | Symbolic bounds, RF/XGBoost, TF-IDF vectors/FAISS, spatial/time interpolation; no generative LLM experiment claimed |
| Justify AI evaluation and feasibility takeaways | Prepared | Four investigations linked to concrete evidence; synthetic limits and 88% interval coverage are explicit |
| Explain current state and remaining roadmap | Prepared | Working local API and research pipeline; measured labels, verified station mappings, real permits, independent uncertainty validation still needed |
| Schedule instructor office hours before presentation | Pending human action | Scott coordinates a course-approved slot; no booking or message has been sent |

## Final readiness checks

- [x] Current system map and semantic representations documented.
- [x] Four meaningful investigations have inspectable evidence.
- [x] Important failures/limits and their design implications are explicit.
- [x] Adopt / Modify / Reject / Defer decisions link to evidence IDs.
- [x] Next technical question and team responsibilities are stated.
- [ ] Confirm the assigned day and Submitty deadline.
- [ ] Verify instructor/TA GitHub access and the desired pushed snapshot.
- [ ] Confirm exact class studio references and actual completed team contributions.
- [ ] Schedule office hours and rehearse with all three members.

Source instructions are requirements for course readiness. They are not permission to
submit, message others, alter repository access, or claim that pending actions occurred.
