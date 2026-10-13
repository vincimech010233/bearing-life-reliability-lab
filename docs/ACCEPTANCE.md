# Acceptance criteria

1. Ball/roller known calculations, N/kN dimensional equivalence and power-law scaling match references.
2. Finite-difference sensitivities match analytic elasticities.
3. Unsupported units/axial load, nonfinite/zero inputs and oversized sampling reject.
4. Seeded samples reproduce; analytic lognormal quantiles agree with MC within 5% for the fixed example fixture (not a guarantee for arbitrary inputs); zero-CV boundary matches nominal and renders as a constant estimate.
5. The full committed suite, dependency/lint checks, both CLI reports and actual plots pass; limits and engineering assumptions are disclosed. Current dated evidence is in `results/review-20261013/`.
6. Actual input reads are limited to 64 KiB. Duplicate JSON fields, deep nesting, invalid UTF-8 and unsupported schemas reject before output creation.
7. Stepwise duties match an independent Decimal inverse-life reference, dimensional/scaling invariants and supported numerical endpoints for ball and roller exponents.

All criteria must be executed locally or explicitly listed as unresolved. Reviewer acceptance is bounded by this profile.
