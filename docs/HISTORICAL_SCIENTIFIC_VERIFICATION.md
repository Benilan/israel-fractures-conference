# Scientific verification: slides 11, 13 and 19

## Slide 11 — Seven electoral families

The original historical Ward clustering has been independently recalculated
locally from the five official locality vote files. The procedure centres
each eligible ballot list's locality vote-share vector, normalizes it to unit
Euclidean length and applies Ward linkage (seven statistical clusters).
Two explicit political-interpretation exceptions are necessary:

- Shas (`שס`) is placed with the Haredi family.
- Zehut (`ז`) in April 2019 (K21) is reassigned from the Ward religious
  Zionism cluster to the secular national right.

The vote share of Zehut in K21 is **2.739002 percentage points**. The
recalculated national figures are:

| Family | April 2019 | November 2022 | Change |
|---|---:|---:|---:|
| Secular center-left | 35.9208% | 33.7207% | -2.2001 pp |
| Popular right | 30.0080% | 23.4081% | -6.5999 pp |
| Religious Zionism | 6.9169% | 12.0310% | +5.1141 pp |
| Haredim | 11.7729% | 14.1279% | +2.3550 pp |
| Arab parties | 7.8229% | 10.7330% | +2.9101 pp |
| Secular national right | 6.7537% | 4.4848% | -2.2689 pp |
| Other lists | 0.8049% | 1.4946% | +0.6897 pp |

The published slide reports rounded changes, and is consistent with these
figures. **Importantly, code must not use the PowerPoint chart values as the
source for the scientific result.**

The module `src/historical_reproduction.py` is now invoked by
`run_analysis.py`; it exports a party/election assignment table and
unrounded vote shares.

## Slide 19 — Population-weighted descriptive eta squared

Using the historical 2022 locality dominant-family assignment and CBS
socio-demographics, independent local calculations obtained:

| Variable | Recalculated eta² × 1,000 | Published integer |
|---|---:|---:|
| Higher education | 714.4714 | 714 |
| Religiosity | 694.1175 | 694 |
| Computer equipment | 671.3360 | 671 |
| Median age | 660.8686 | 661 |
| Median employee wages | 657.6000 | 658 |
| Average number of children | 623.4327 | 624 |

Five of six are within ordinary integer rounding; the last differs by
approximately 0.57 on the plotted 0–1,000 scale, and warrants review of
the exact handling of missing population and weighting before declaring
perfect numerical identity. The published ordering is reproduced.

Eta squared is descriptive association of *localities*, not a causal
explanation of individual voters. Ordinal religiosity coding should be
handled carefully. A V15 alternative party-family mapping produces different
estimates and must not be represented as the V14 result.

## Slide 13 — Electoral coalitions

The independent historical seats reference table sums to the Netanyahu bloc
totals (K21–K25): **60, 55, 58, 52, 64**.

The PowerPoint contains further opposition and scenario segments, but those
were reconstructed from the slide rather than independently joined to an
exhaustive source table of the 120 official seats at every election.
Accordingly **slide 13 is only partly independently verified**.

A complete scientific validation requires a party-level 120-seat table for
each election, with explicit bloc / swing-party definitions, and assertions
that each election sums to exactly 120 seats. This is not something that can
be inferred from the existing five locality vote CSVs without the official
seat-allocation rules and coalition metadata.

## GitHub workflow

The latest public pipeline invokes `src/historical_reproduction.py` and
will fail if the Ward family evolution or weighted eta calculations differ
materially from the independent references. The final scientific GitHub
Actions run on this commit has **not yet been confirmed** at the time of
writing. Once run, check `outputs/tables/historical_recalculation_report.json`
and the two new CSVs.

Note: do not interpret passing image-rendering tests as scientific
verification; reference graphics on slides 11, 13 and 19 currently use
the editable PowerPoint values rather than the newly recomputed CSVs.
These charts should ultimately consume the recomputed tables directly.

## Correction after GitHub execution — V14 grouping

The 25 October GitHub diagnostics identified that the first implementation
merged the two Ward center-left clusters **before** computing weighted eta
squared. This is appropriate for the seven-family national comparison on
slide 11 but changes the grouping in the V14 ANOVA. The code now retains an
unmerged `WardGroupV14` column (seven Ward groups plus Other, with Shas
reassigned to Haredim) for slide 19; `Family` continues to hold the seven
presentation-family labels for slide 11.

Previously failing values (education 674.54476 versus 714; computer
equipment 643.81062 versus 671) were obtained with the improperly merged
groups, **not** evidence that the historical slide values were falsified.
The new GitHub Actions execution must still be checked. The audit continues
to fail if the recalculated values differ materially.
