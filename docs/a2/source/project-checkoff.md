# CSCI 4150 project checkoff: ECOllateral

Status against the supplied two-page course handout. Presentation: October 20 or 23,
2026; assigned day and Submitty deadline are unconfirmed. The prototype and experiments
cover cooling consumption; regional assessment remains planned.

## Project Scope & AI Integration

| Item | Status | Project response / evidence |
| --- | --- | --- |
| Clear goal, problem, and primary question | Documented | Assess development impacts on seasonal area reserves and watershed conditions; cooling is one pressure component |
| Achievable sub-goals and scope before mid-term | Documented | Working component prototype, five evidence investigations (E1-E5), explicit regional scope and remaining area-assessment work |
| Class AI tools/concepts mapped or exclusions justified | Partial | Explain rules, tree models, word/vector search, prediction ranges, and missing data; wait on neural/LLM work; confirm actual studio names/links |

## Data Acquisition & Governance

| Item | Status | Project response / evidence |
| --- | --- | --- |
| Identify public data, permitted scraping, or survey requirements | Documented for current scope | USGS/NOAA public APIs/files; no surveys or private scraping; check future permit sources |
| Exactly document where data come from and mark public datasets | Documented | `../../data-contracts.md`: exact download URLs, station IDs, dates, and evidence file fingerprints |
| Confirm instructor permissions for scraping / IRB before surveys | Pending if scope expands | No approval is claimed; Scott coordinates instructor clarification before new scraping or surveys |
| Clean flow into system components | Implemented / tested | Download -> monthly inputs -> fill gaps from training data -> predict -> check limits -> find permit quotes -> return JSON |

## System Architecture & Evaluation

| Item | Status | Project response / evidence |
| --- | --- | --- |
| Visual block diagram of component interactions | Prepared | Regional goal plus current number/permit components; editable diagram in slides; area balance remains planned |
| Evaluation metrics for individual components | Documented / tested | Units and bad-input checks; error/fit (MAE/RMSE/R2); range coverage; missing-data spread in MGD2; eligible/ineligible locations |
| Explicit success and failure criteria for outputs | Documented | Enforce limits/warnings; R2 > 0.80 and MAE < 0.05 MGD component goal; >=90% of missing-data changes within tolerance plus band checks; regional/facility criteria unverified |
| Component test plan | Implemented with limits | October 7 snapshot: 51 passing tests covering forced wrong values, saved-model reload, train-only gap filling, bad neighbors, permit locations, API errors; real-permit relevance testing remains planned |

## Team Organization & Workflow

| Item | Status | Project response / evidence |
| --- | --- | --- |
| Assign sub-goals and responsibilities to each member | Documented | Completed work: Shaun - system/model/API integration; Troy - environmental data, missingness, and permits; Scott - physical checks, uncertainty evaluation, and presentation evidence. Two slides per member. |
| Shared GitHub repository with instructor/TA access | Partial | Public GitHub repository; current base commit d6ef97b is pushed and CI passed (verified October 19). Instructor/TA access expectations remain unconfirmed; local A2 audit edits still need publishing |

## Presentation Preparation

| Item | Status | Project response / evidence |
| --- | --- | --- |
| Show architecture assessment if full system is incomplete | Prepared | Show the working prototype and what real-world tests remain; diagram explains number and permit paths |
| Draft mid-semester materials and slides | Prepared | Six slides, editable PPTX, PDF export, four-minute script |
| Explain the problem | Prepared | Slide 1 and dossier problem/user statement |
| Explain sub-goals, milestones, and teammate mapping | Prepared | Team snapshot and role-owned roadmap |
| Identify AI concepts/tools used | Prepared | Engineering rules; RF/XGBoost tree models; weighted word matching (TF-IDF); nearby-station/time gap filling; no generative LLM experiment claimed |
| Justify AI evaluation and feasibility takeaways | Prepared | Five investigations (E1-E5) with evidence; clear limits of made-up data and about 88% prediction-range coverage |
| Explain current state and remaining roadmap | Prepared | Component API/tests work; need regional supply/demand, returns, ecological baselines, checked boundaries/documents, measured targets, and independent range tests |
| Schedule instructor office hours before presentation | Pending | Scott coordinates a course-approved slot |

## Outstanding course items

- Assigned presentation day and Submitty deadline.
- Instructor/TA repository access and submitted commit.
- Exact class studio references.
- Office-hours appointment and rehearsal with all three members.
