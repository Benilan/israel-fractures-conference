# Israel Fractures Conference — reproducible analysis

Python code for an empirical exploration of five Israeli parliamentary elections (2019–2022), local voting patterns and CBS social characteristics.

## What's in this repository

- `src/analysis.py`: executable 2022 social-profile clustering and vote-by-profile heatmap, plus turnout by each locality’s dominant religion.
- `run_analysis.py`: local entry point.
- `tests/test_repository.py`: checks analytical invariants.
- `.github/workflows/verify.yml`: manually runnable GitHub Actions test workflow.
- `docs/RUN_ON_GITHUB.md`: precise instructions and remaining prerequisites.

## Run

```bash
pip install -r requirements.txt
python -m pytest -q
python run_analysis.py
```

**Data dependency:** the full computation expects the five official Knesset election CSVs and CBS 2022 census file in `data/raw/`, with filenames listed in `src/analysis.py`. These files are not published here. Without those files, the tests can run but the complete calculations cannot.

## Verification scope

This public code currently recalculates turnout by locality dominant religion (slide 7), the five 2022 social profiles (slides 20–21), and the 2022 voting heatmap (slide 23). It is **not yet** a full numerical reproduction of the conference; other analyses from the prior local V18 package have not all been transferred. In particular, the historic K21–K25 clustering, K21 Zehut reassignment, full coalition mappings and the weighted ANOVA on slide 19 remain outside the published executable pipeline.

## GitHub Actions

Go to **Actions → Python verification → Run workflow**. The workflow runs source compilation and unit tests. It performs raw-data calculations only if those inputs are available. A green test badge alone does not certify the presentation.

## Methodological cautions

- Locality level associations are not individual voting behavior or causal claims.
- Social K-means cluster labeling is an empirical interpretive procedure tied to the CBS 2022 data.
- The 2022 party families are explicitly defined in `FAMILIES_2022`, and Shas is included under Haredi.
- Historical K21 Zehut attribution requires its own explicit documented mapping; it should not be conflated with the 2022 mapping.

## Data attribution and licensing

The census and election data should be sourced from Israel's Central Bureau of Statistics (CBS) and Central Elections Committee respectively. Verify each dataset's redistribution terms before publishing raw files. No license for the project's original code has yet been selected.
