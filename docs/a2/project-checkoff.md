# CSCI 4150 project checkoff: ECOllateral

The evidence and slides are prepared for the mid-semester review. The assigned
October 20/23 presentation day and exact submission time still need confirmation.
Each status describes that checklist item; it does not mean the whole project has
been validated for regional ecosystem impacts. This follows the supplied two-page course handout.
Terms and the short project explanation are in `explain-it-simply.md`.

## Project Scope & AI Integration

| Item | Status | Project response / evidence |
| --- | --- | --- |
| Clear goal, problem, and primary question | Documented | Assess development impacts on seasonal area reserves and watershed conditions; cooling is one pressure component |
| Achievable sub-goals and scope before mid-term | Documented | Working component prototype, four approach investigations, explicit regional scope and remaining area-assessment work |
| Class AI tools/concepts mapped or exclusions justified | Partial | Explain rules, tree models, word/vector search, prediction ranges, and missing data; wait on neural/LLM work; confirm actual studio names/links |

## Data Acquisition & Governance

| Item | Status | Project response / evidence |
| --- | --- | --- |
| Identify public data, permitted scraping, or survey requirements | Documented for current scope | USGS/NOAA public APIs/files; no surveys or private scraping; check future permit sources |
| Exactly document where data come from and mark public datasets | Documented | `data-governance.md`: exact download URLs, station IDs, dates, and evidence file fingerprints |
| Confirm instructor permissions for scraping / IRB before surveys | Pending if scope expands | No approval is claimed; Scott coordinates instructor clarification before new scraping or surveys |
| Clean flow into system components | Implemented / tested | Download -> monthly inputs -> fill gaps from training data -> predict -> check limits -> find permit quotes -> return JSON |

## System Architecture & Evaluation

| Item | Status | Project response / evidence |
| --- | --- | --- |
| Visual block diagram of component interactions | Prepared | Regional goal plus current number/permit components; editable diagram in slides; area balance remains planned |
| Evaluation metrics for individual components | Documented / tested | Units and bad-input checks; error/fit (MAE/RMSE/R2); range coverage; missing-data spread in MGD2; eligible/ineligible locations |
| Explicit success and failure criteria for outputs | Documented | Always enforce limits/warnings; R2 > 0.80 and MAE < 0.05 MGD benchmark goal; >=90% of missing-data changes within tolerance plus band checks; real-facility criteria unverified |
| Component test plan | Implemented with limits | 51 local tests: forced wrong values, saved-model reload, train-only gap filling, bad neighbors, permit locations, API errors; real-permit relevance testing remains planned |

## Team Organization & Workflow

| Item | Status | Project response / evidence |
| --- | --- | --- |
| Assign sub-goals and responsibilities to each member | Assigned | Shaun: code and connected components; Troy: environmental data and tests; Scott: permits, evidence, and slides |
| Shared GitHub repository with instructor/TA access | Partial | Configured remote: `https://github.com/ScottLiu12/ECOllateral`; actual collaborators, instructor/TA access, and pushed snapshot are unverified |

## Presentation Preparation

| Item | Status | Project response / evidence |
| --- | --- | --- |
| Show architecture assessment if full system is incomplete | Prepared | Show the working prototype and what real-world tests remain; diagram explains number and permit paths |
| Draft mid-semester materials and slides | Prepared | Six slides, editable PPTX, PDF export, four-minute script |
| Explain the problem | Prepared | Slide 1 and dossier problem/user statement |
| Explain sub-goals, milestones, and teammate mapping | Prepared | Team snapshot and role-owned roadmap |
| Identify AI concepts/tools used | Prepared | Engineering rules; RF/XGBoost tree models; TF-IDF/FAISS word search; nearby-station/time gap filling; no generative LLM experiment claimed |
| Justify AI evaluation and feasibility takeaways | Prepared | Four approach investigations with evidence; clear limits of made-up data and about 88% prediction-range coverage |
| Explain current state and remaining roadmap | Prepared | Local API and experiments work; need measured water use, checked station matches, real permits, and separate prediction-range tests |
| Schedule instructor office hours before presentation | Pending human action | Scott coordinates a course-approved slot; no booking or message has been sent |

## Final readiness checks

- [x] System map explains how numbers, rules, text, and locations represent information.
- [x] Four meaningful approach investigations have evidence that can be inspected.
- [x] Important failures/limits and the changes they call for are explained.
- [x] Adopt / Modify / Reject / Defer decisions link to evidence IDs.
- [x] Next technical question and team responsibilities are stated.
- [ ] Confirm the assigned day and Submitty deadline.
- [ ] Verify instructor/TA GitHub access and the desired pushed snapshot.
- [ ] Confirm exact class studio references and actual completed team contributions.
- [ ] Schedule office hours and rehearse with all three members.

Source instructions are requirements for course readiness. They are not permission to
submit, message others, alter repository access, or claim that pending actions occurred.
