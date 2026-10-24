# Verification on GitHub Actions

Use **Actions → Scientific analysis verification → Run workflow**.

The **code-tests** job installs dependencies, compiles the published V18 modules,
and checks six stable computational invariants.

The **reproduce-slides** job executes `python run_analysis.py` only if all
required election/CBS input files exist in `data/raw/`. In the current public
repository these raw source files are excluded, so numerical reproduction is
not possible on GitHub Actions until an authorized way to supply them is added.
The job reports that limitation explicitly, and it does **not** claim success
for source-dependent calculations.

## Local complete execution

Use the separately delivered V18 local distribution containing authorized
inputs, or obtain the source files independently, preserving their filenames.

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python run_analysis.py
```

Outputs are written under `outputs/tables/` and `outputs/figures/`.

## Scientific coverage

The V18 core recalculates slides 7, 8, 16, 17, 20, 21, 23 and the separately
verified Netanyahu bloc. The historic K21–K25 political-family clustering,
the full slide 13 coalition configurations and the exact published V14 ANOVA
values are **not included** in its certified end-to-end pipeline. Describing
the repository as complete conference-wide numerical reproduction would be
inaccurate.

The K21 Zehut reclassification and Shas handling in the original historical
script remain to be ported without altering the clustering algorithm.
