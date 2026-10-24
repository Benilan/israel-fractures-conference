# Israel Fractures Conference

Reproducible research project examining Israel's five Knesset elections (2019–2022), electoral geography, political clustering, and socioeconomic differences.

## Publication status

**Work in progress — public repository bootstrap.** This repository is not yet the complete V18 analysis package. In particular, the raw CBS and election datasets, full analysis modules and slide-level outputs have not been uploaded. Do not interpret a passing GitHub Actions run as independent verification of all conference figures.

## Intended verification

The analysis package includes Python processing of election and CBS inputs, turnout and threshold checks, socioeconomic indicators, social-profile clustering, a 2022 voting heatmap, and historical analyses. Some slide-level reconciliation work remains, especially political-family assignments and full coalition composition.

## Local package

The full V18 distribution was previously provided separately. Its main entry point is `python run_analysis.py`, with dependencies in `requirements.txt` and data under `data/raw/`. The public source repository is being populated.

## Automated checks

Go to **Actions → Repository checks → Run workflow**. The current workflow performs a repository-readiness check only; it will report clearly that the full analysis has not yet been installed.

## Data and attribution

Do not publish third-party files without checking redistribution permissions. Document CBS, Central Elections Committee, and other source URLs, access dates, and transformations before claiming end-to-end reproducibility.

## Research integrity

Statistical clusters, analytical reassignment choices (including Shas and Zehut), electoral seat counts, and interpretive conclusions must be documented separately. A functioning pipeline does not by itself validate political interpretations.
