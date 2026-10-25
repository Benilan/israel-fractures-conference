# Israel Fractures Conference

**Reproducible statistical analysis of five Israeli Knesset elections (2019–2022) and social divides using official election and CBS locality data.**

## Publication status

The complete election/CBS pipeline is implemented in Python and runs
through a single entry point, `python run_analysis.py`. GitHub Actions was
reported passing after the Ward/V14 scientific corrections. The October 2026
finalization updates visualizations so slides 11 and 19 consume the
independently recalculated data, not values embedded in PowerPoint.
This latest revision requires its own CI confirmation.

**Scope limitation:** slides 13's historical bloc labels are political
interpretations. Netanyahu bloc totals are checked against the reference
seat table, but the other displayed parliamentary segments are not a complete
official 120-seat-per-election reconstruction.

## Execute

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python run_analysis.py
```

The last command requires the official election and CBS inputs in `data/raw/`.
The workflow copies available files from `data/manual/` into `data/raw/`.
Use the named official-source election and CBS files, and verify redistribution
permissions before distributing any third-party data.

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

| Slides | Reproducible pipeline |
| --- | --- |
| 7–8 | Turnout by dominant locality religion; full national electoral threshold |
| 11 | Ward family evolution across K21–K25, including Shas and Zehut corrections |
| 12 | Locality-centroid map of dominant 2022 political family |
| 13 | Visual bloc composition; Netanyahu totals independently cross-checked |
| 16–17 | CBS religiosity profile and socioeconomic distribution |
| 19 | Population-weighted descriptive eta squared using historical Ward partition |
| 20–21 | Weighted social K-means, neighbour analysis and locality-centroid map |
| 23 | Social-profile by political-family vote share heatmap |

## Methodology

Analyses aggregate *localities*, not individual characteristics.
Cluster names and political-family interpretations are analytically
assigned; ecological associations are not causal effects. Social clustering
uses population-weighted K-means and fixed input columns. The 2022
political-family table explicitly includes Shas under Haredi.

The K21 Zehut and Shas corrections are explicitly implemented and audited
in the historical reconstruction module.

## Source attribution and licensing

Election records are from Israel's Central Elections Committee; social and
economic measures are from Israel's Central Bureau of Statistics.
Users must check redistribution permissions before sharing raw datasets.
An open-source code license has not been selected yet.

## Map outputs

The single command `python run_analysis.py` now also generates:

- `outputs/figures/slide_12_political_family_map.png`
- `outputs/figures/slide_21_social_profiles_map.png`
- `outputs/tables/slide_12_dominant_family_assignments.csv`

These are **locality-centroid dot maps**, following the plotting approach found
in the original historical analysis. They are not municipality-boundary
choropleths. The 2022 classification is used for the slide 12 map; the
2019–2022 stability calculation remains separate and needs its historical
family mapping. All outputs are included in the GitHub Actions artifact when
the data-dependent job succeeds.

## October 2026 scientific audit

The published `run_analysis.py` now also calls
`src/historical_reproduction.py` to independently reconstruct the Ward
electoral family groups, document the Shas/Zehut reassignment, and compute
the historical population-weighted eta-squared indicators (V14 methodology).
New CSVs and a diagnostics JSON are written to `outputs/tables/`.

See [scientific verification and limitations](docs/HISTORICAL_SCIENTIFIC_VERIFICATION.md).
The opposition/coalition segments of slide 13 are **not yet fully certified**
against a complete 120-seat-per-election official table. Slides 11 and 19 now use computed CSVs; the coalition composition chart
still carries an explicit PowerPoint-reference interpretation. Confirm the
latest workflow after any code change.
