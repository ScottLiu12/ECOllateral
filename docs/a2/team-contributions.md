# ECOllateral: A2 team contributions

CSCI 4150 | Mid-Semester System & Evidence Review | Shaun, Troy, Scott

We divided the project into three complementary areas: system development,
environmental data and retrieval, and evaluation and communication. Each member's
contribution connects to the prototype and evidence presented in our A2 review.

## Shaun: system development and integration

Shaun developed the system architecture and connected the environmental inputs,
prediction models, physical checks, and permit results through the API. He handled
model training and the RandomForest/XGBoost comparison, documenting why XGBoost
was selected for the prototype. His work established the path from a facility
request to a daily cooling-water estimate, prediction range, and warnings.

Evidence: system map, API and model implementation, and E1 model-comparison results.

## Troy: environmental data and permit retrieval

Troy worked on environmental data acquisition and preparation, including station
and climate-division checks and drought and groundwater interpretation. He analyzed
missing-data handling and the biased-station failure in E2. He also worked on permit
retrieval and geographic filtering, connecting exact quotations to the requested
location and documenting the fictional location tests in E4.

Evidence: data contracts, E2 missingness results and donor diagnostic, and E4 retrieval cases.

## Scott: evaluation and evidence presentation

Scott evaluated the physical-rule checks in E3 and prediction-range coverage in E5.
He analyzed what the failures mean for the design, including the need for separate
calibration data and further testing with measured consumption. He organized the
evidence, slides, and presentation materials to explain the results, design
decisions, and limits of the current prototype.

Evidence: E3 constraint cases, E5 coverage results, evidence summary, dossier, and slides.
