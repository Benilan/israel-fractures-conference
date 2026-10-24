# GitHub Actions and reproducibility

Select **Actions → Python verification → Run workflow**.

The workflow compiles the committed Python source and tests important invariants,
including mutually exclusive 2022 voting families, Shas in the Haredi family,
and controlled percentage rounding.

**Important:** raw source files are not included in this public repository.
Thus passing actions tests are not evidence that all conference numbers were
recalculated. To run 2022 electoral / social analysis, provide the five official
election CSV files and the CBS census file under `data/raw/`, retaining
the input names in `src/analysis.py`, then run:

```bash
pip install -r requirements.txt
python run_analysis.py
pytest -q
```

The current public source computes the turnout-by-dominant-religion output
(slide 7), social profiles (slides 20–21) and 2022 heatmap (slide 23).
It does **not** yet reproduce every election-history and socioeconomic
calculation. The historically reported results for slides 11–13 and 19 require
reconciliation of the historic electoral family classification, including the
Zehut list in K21, and the source-specific weighted ANOVA procedure.

For a truly automated full run on Actions, publish redistribution-cleared source
data or configure a reliable, documented, legally permitted data download.
