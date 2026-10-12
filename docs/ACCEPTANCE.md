# Acceptance criteria

1. Ball/roller known calculations, N/kN dimensional equivalence and power-law scaling match references.
2. Finite-difference sensitivities match analytic elasticities.
3. Unsupported units/axial load, nonfinite/zero inputs and oversized sampling reject.
4. Seeded samples reproduce; analytic lognormal quantiles agree with bounded MC to stated 5% tolerance; zero-CV boundary matches nominal.
5. Ten tests, dependency/lint checks, CLI reports and actual plots pass; limits and engineering assumptions disclosed.

All criteria must be executed locally or explicitly listed as unresolved. Reviewer acceptance is bounded by this profile.
