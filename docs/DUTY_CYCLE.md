# Stepwise Bearing Duty-Cycle Calculator

**Status: synthetic local validation (13 October 2026); not production-validated.**

## Business problem and audience

Mechanical reliability and maintenance engineers need to compare *hypothetical*
rotating-equipment modes with different radial loads, speeds and operating
durations. A plain arithmetic average load is misleading for basic rolling-fatigue
life. This offline extension reports revolution-weighted equivalent load,
basic L10 hours, and each mode's fraction of **modeled** fatigue contribution.

## Requirements and use

Python 3.12+, standard library only for this extension. Run from repo root:

```sh
python3 src/duty_cycle.py examples/duty_cycle.json results/duty-cycle-report.json
python3 -m unittest discover -s tests -p 'test_duty_cycle*.py' -v
```

The original `src/bearing.py` and its tests require dependencies in
`requirements.lock`; install them to run the full suite. This extension
uses neither network services nor machine telemetry.

The example is **fictional**: C = 10 kN, mode A = 2 kN at 1000 rpm for 1 h;
mode B = 4 kN at 2000 rpm for 1 h. It gives mean speed = 1500 rpm,
equivalent radial load ≈ 3565.654 N, basic L10 ≈ **245.098039 h**.
Reproduce the exact JSON by running the command above. This is not an
individual bearing remaining-useful-life estimate.

## Formula

For each step i: N_i = 60 * rpm_i * hours_i;
u_i = N_i/sum(N_i). With p=3 (ball) or 10/3 (roller),
P_eq = (sum(u_i * P_i**p))**(1/p);
L10 = (C/P_eq)**p million revolutions;
L10h = 1e6*L10 / (60*mean_rpm), where mean_rpm =
sum(rpm_i*hours_i)/sum(hours_i).

## Scope, security and limitations

Synthetic-only input, at most 64 KiB and 100 positive-speed segments.
Only N/kN force units; only pure radial P=Fr; no axial or stop intervals.
Unknown fields, invalid numbers and unsupported bearing types reject.
No real equipment data, personal data, credentials, third-party network
access, or external writes. The CLI writes/overwrites only the chosen local
JSON output path: inspect it before sharing.

Not ISO-certified. No manufacturer X/Y factors, preload, minimum load,
static capacity, lubrication, contamination, field history or failure-time
distribution. An estimated **fatigue fraction is not failure probability**.
Do not use for safety, field maintenance or procurement decisions.

The repository's **MIT LICENSE** covers the original extension. See
`docs/DUTY_CYCLE_RESEARCH.md` for primary sources, alternatives and LEARN.
The numerical fixtures establish algebraic behavior, not physical accuracy.
