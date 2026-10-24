# Israel Fractures Conference

**Reproducible statistical analysis of five Israeli Knesset elections (2019–2022) and social divides using official election and CBS locality data.**

## Publication status

The original V18 computational modules are now published under `src/`:
`pipeline_v16.py`, `heatmap_v15.py`, `socio_source.py`, and
`historical_audit.py`. The superseded simplified implementation has been
removed. Methodological comments, entry-point documentation and figure titles
are in English; original categorical labels and source column names remain
unchanged where translating them could affect reference outputs.

**Not all historical conference analyses are yet reproduced end to end.**
In particular, the original multi-election political clustering and Zehut
exception, complete coalition mapping, and exact V14 slide 19 ANOVA are not
part of the presently certified public workflow.

## Execute

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python run_analysis.py
```

The last command requires the official election and CBS inputs in `data/raw/`.
The public repository does not redistribute those datasets; use the separate
V18 local package supplied with this project or download from authorized
original sources and preserve the filenames.

When data are present, outputs are written to `outputs/tables/` and
`outputs/figures/`. The JSON report is
`outputs/tables/validation_v16.json`.

## GitHub Actions

Open **Actions → Scientific analysis verification → Run workflow**.
The first job runs Python tests against the published algorithms.
The second runs source-dependent computations **only when input files exist**
and uploads the tables and figures. It explicitly reports when data are
missing; a green code test does not certify the numerical slides.

[Detailed GitHub workflow instructions](docs/RUN_ON_GITHUB.md)

## Coverage

| Slides | Public V18 pipeline |
| --- | --- |
| 7 | Locality-level turnout grouped by CBS dominant religion |
| 8 | Election threshold and below-threshold vote share |
| 16 | Population-weighted locality religiosity indicators |
| 17 | CBS socioeconomic distribution |
| 20–21 | 2022 social clustering, demographics and nearest-neighbour diagnostic |
| 23 | 2022 family vote heatmap, exact values and controlled rounding |
| 13 (Netanyahu bloc) | Independent historical seats reference, 60 / 55 / 58 / 52 / 64 |
| 11–12, 13 (other coalitions), 19 (V14) | Not yet fully incorporated in reproducible public pipeline |

## Methodology

Analyses aggregate *localities*, not individual characteristics.
Cluster names and political-family interpretations are analytically
assigned; ecological associations are not causal effects. Social clustering
uses population-weighted K-means and fixed input columns. The 2022
political-family table explicitly includes Shas under Haredi.

The K21 Zehut reassignment is historically relevant but is not yet
implemented in the current public V18 pipeline. Accordingly, the
published workflow must not be presented as replicating slide 11.

## Source attribution and licensing

Election records are from Israel's Central Elections Committee; social and
economic measures are from Israel's Central Bureau of Statistics.
Users must check redistribution permissions before sharing raw datasets.
An open-source code license has not been selected yet.
