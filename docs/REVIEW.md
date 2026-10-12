# Critical review — Bearing Life & Reliability Lab

Reviewer: separate same-model agent, not an independent model or external audit. Scope: hypothetical pure-radial basic fatigue-life algebra, dimensional checks, sensitivities, supplied-parameter uncertainty and local artifacts. No real bearing selection, certification or operational validation.

VERIFIED: **VALIDATED_LOCAL** for `docs/ACCEPTANCE.md` after numerical representability correction. Initial gate was PARTIALLY_VALIDATED; that critique is retained. No certification or real bearing reliability claim is accepted. Manual publication still requires final repository/privacy/artifact checks.

## Concrete finding and evidence

OBSERVED: allowed positive `dynamic_rating=1e-300` produced zero nominal life and nonfinite Monte Carlo relative errors; `analyze()` returned the invalid report with a warning. Finite positive input alone does not guarantee representable positive life. Correction required: reject nonfinite/nonpositive nominal, analytic, sample and sensitivity outputs before plotting/report return. VERIFIED correction: positive finite guards and floating-error handling reject the preserved underflow input. OBSERVED: both direct analyze and CLI reject; CLI exits 2 before creating an output directory. See `retest-observations.json`. The input and initial observation remain in `results/reviewer-fixtures/underflow-input.json` and `observations.json`.

OBSERVED: `OPENBLAS_NUM_THREADS=2 MPLBACKEND=Agg .venv/bin/python -m unittest discover -s tests -v` initially passed nine tests; corrected run passed ten including numerical-limit regression; `.venv/bin/pip check` passed. Initial reviewer `.venv/bin/ruff` invocation failed with exit 127 because that path is absent; this is retained as a reviewer-command failure, not silently converted to a lint success. The reviewer then resolved the actual tool path from `results/validation.json`: `../portfolio-delivery-20261012/.venv/bin/ruff`. OBSERVED: lint and format checks passed using that path, while the failed initial command remains disclosed.

VERIFIED: independently expressed nominal-hour calculation gives 1388.888888888889 h. Independent arithmetic-mean/CV lognormal algebra gives quantiles 728.1210204563715, 1404.784911216748 and 2710.2920961481736 h, matching the stored analytic quantiles. Observed fixture Monte Carlo relative quantile errors are approximately 0.23%, -0.50% and -0.31%, within the stated fixture 5% tolerance. See `reference-observations.json`. The tolerance is an executed fixed-fixture check, not guaranteed accuracy for every allowed CV/sample combination.

## Equations and interpretation

VERIFIED by inspection and tests: N/kN normalization, ball exponent 3, roller exponent 10/3, revolutions-to-hours conversion and analytic power-law elasticities. Unsupported axial load rejects rather than guessing catalog factors. Input CVs describe independent lognormal arithmetic means and coefficients of variation; zero CV gives the nominal boundary. Draws are seeded and repeatable.

The reviewer consulted [NSK primary fatigue-life methodology](https://www.nsk.com/tools-resources/abc-bearings/dynamic-load-ratings-and-fatigue-life/), which supports the power law and 90% basic fatigue rating interpretation. This model's parameter-induced L10 quantiles are distinct from bearing-population failure-time variability. The histogram is not a demonstrated lifetime/reliability distribution for real bearings. Pure-radial P=Fr, constant speed/load and conventional fatigue assumptions are documented restrictions.

Full paid ISO text was not obtained; failed large-catalog reads remain disclosed in the research record. No ISO certification, catalog X/Y factors, modified-life correction, static-capacity/minimum-load checks or nonfatigue failure modes are accepted. Sensitivity is local mathematical elasticity, not field reliability evidence.

## Value, security and remaining limits

INFERRED: transparent equations, dimensional/scaling tests and analytic uncertainty comparison offer credible engineering-teaching portfolio value alongside manufacturer tools. Hypothetical dynamic ratings, loads and CVs are supplied assumptions, not catalog data. Parameter independence, CV calibration and real bearing correspondence remain NOT_VERIFIED.

VERIFIED by inspection: strict synthetic input profile, 64 KiB config and 500–5000 sample bounds; no external computation or personal data. JSON embeds input/units/seed and numeric comparison evidence. MIT project license, runtime lockfiles, license metadata and advisory queries are present; vulnerability absence, exhaustive legal/supply-chain review and authorship beyond supplied provenance remain NOT_VERIFIED. Parent inspected the actual plot; reviewer did not independently inspect it. Hosted CI execution is NOT_VERIFIED.

Follow-up: retain representability tests and the separation of parameter uncertainty from fatigue reliability. Expanding to axial/general bearing selection needs manufacturer-specific inputs and a new applicability gate.
