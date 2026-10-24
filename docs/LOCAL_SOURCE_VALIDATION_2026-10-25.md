# Local source validation — 25 October 2026

The nine newly provided source files were compared byte-for-byte (SHA-256)
against the corresponding files in the V18 local distribution. **All nine
matched**. Filenames in the uploaded attachments differ only by download
suffixes; the V18 file names remain the canonical input paths.

Local validation was executed on the original `Israel_Fractures_V18_PUBLICATION`
code with those identical files:

- `python -m pytest -q`: **7 passed**
- `python run_analysis.py`: **exit status 0; 11/11 pipeline checks passed**
- Social-profile localities: **1,040**
- CBS socioeconomic localities: **1,174**
- Nearest-neighbour agreement: **57.3076923077%**
- Votes in the profile heatmap: **3,804,996**
- All below-threshold lists (2022): **8.760180509%**

## Status of GitHub Actions

Raw source files were **not** committed to this public repository. The GitHub
Actions workflow therefore does not run data-dependent numerical analyses
until a legally authorized source-data distribution mechanism is configured.

The local run verifies the existing V18 scope, **not** the entire conference:
the historic K21–K25 political-family assignment / Zehut treatment,
alternative coalition scenarios, and published V14 weighted ANOVA have not
all been integrated into this public execution path.

For a complete scientific claim, source availability and those historical
calculations must both be resolved.
