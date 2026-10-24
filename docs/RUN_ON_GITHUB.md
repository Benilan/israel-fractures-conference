# Running the project using GitHub Actions

Go to **Actions → Python verification → Run workflow**.

The public job checks Python syntax and a minimal smoke-test suite. It **does
not** establish that conference figures were reproduced.

For full reproducibility, the research pipeline (`src/pipeline_v16.py`,
`src/heatmap_v15.py`, `src/socio_source.py`, `src/historical_audit.py`)
and nine original election/CBS files must be made available to the runner.
The public GitHub repository does not currently include those files.

The local V18 package can be run where those source files are held:

```bash
python -m pip install -r requirements.txt
python run_analysis.py
python -m pytest tests -q
```

The historical grouping corrections for Shas and Zehut should be encoded
in a single auditable mapping before claiming that the slide 11 series are
reproduced. Validation of slide 13 alternative blocs must likewise be
clearly distinguished from the verified Netanyahu-bloc seat totals.
