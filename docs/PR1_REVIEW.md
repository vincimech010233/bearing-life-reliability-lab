# PR #1 critical review — 2026-10-13

Scope: the complete bearing-life repository, all four existing commits, PR #1
at `920ef21bfce174d7bc8d8add7e968b35994c70f0`, historical results and GitHub CI.
Security checks are explicitly authorized for this repository only. Application
reproductions use local synthetic fixtures; no external systems were probed.
Public source/advisory queries are read-only. A separate same-model agent used
an adversarial reviewer perspective. This is an internal second review, not an
external audit or proof of engineering validity.

## Findings and disposition

| Finding | Evidence and correction | Public duplicate classification |
| --- | --- | --- |
| R1: ineffective 64 KiB input limit | VERIFIED: a FIFO with reported size zero supplied 70,219 bytes; baseline duty CLI wrote a report. Both CLIs now read at most 65,537 bytes and reject before parsing if the actual limit is exceeded. Regression also tests exactly 65,536 bytes. | NO_PUBLIC_DUPLICATE_FOUND in the target repository/history searched. This does not establish novelty. |
| R2: deeply nested JSON escapes error handling | VERIFIED: 32,001 bytes with 16,000 nested arrays made both baseline CLIs exit 1 with `RecursionError`. The shared loader translates that error into `ValueError`; CLI regression requires exit 2, no traceback and existing output preservation. | KNOWN_PUBLIC: [CPython #135835](https://github.com/python/cpython/issues/135835) documents the same decoder behavior. The application must handle it. |
| R3: degenerate histogram cannot represent finite large lives | VERIFIED: zero-CV inputs with L10 around `1.67e244` hours failed plotting with unrepresentable bins. Constant samples now render as a labeled vertical marker without assigning a density to a point mass. Regression executes the PNG render. | POSSIBLE_DUPLICATE: [NumPy #27142](https://github.com/numpy/numpy/issues/27142) covers the related histogram precision problem, with different data conditions. |
| R4: malformed direct inputs raise incidental exceptions | VERIFIED by regression: huge integers must reject without conversion overflow; non-string bearing/unit fields must reject without set-membership `TypeError`. Range checks precede float conversion and enum fields require strings. Duplicate JSON fields now reject rather than silently choosing the last value. | NO_PUBLIC_DUPLICATE_FOUND in the target repository/history searched; duplicate-key decoder behavior itself is documented in [Python JSON documentation](https://docs.python.org/3/library/json.html#repeated-names-within-an-object). |
| R5: advisory audit exits successfully without verified coverage | VERIFIED by synthetic response/network fixtures: the original developer tool returned exit 0 on service failure or listed advisories. It now returns 1 for advisories and 2 for unavailable/incomplete evidence, requires one result per query and supports a separate evidence output. CI runs this check. | NO_PUBLIC_DUPLICATE_FOUND in the target repository/history searched. |
| R6: unsupported test-count/acceptance wording | OBSERVED: submitted suite contains six extension methods, 16 total; the prior eight-test claim cannot be corroborated by committed tests. Historical claims are retained and explicitly qualified. Acceptance now states the 5% Monte Carlo tolerance applies to the fixed fixture. README exposes both calculators; provenance distinguishes declared authorship from independent proof. | NO_PUBLIC_DUPLICATE_FOUND in the target repository/history searched. |
| R7: duplicated CI work and deprecated action runtime | OBSERVED: repeated install/lint steps; old job warns of Node 20 deprecation. CI now performs each check once, exercises both examples, uses a 10-minute timeout and read-only contents permissions, disables persisted checkout credentials and pins official v7 action commits. | Historical formatting failure is KNOWN_PUBLIC in the [failed PR run](https://github.com/vincimech010233/bearing-life-reliability-lab/actions/runs/38345000152), already fixed by commit `920ef21`; it remains historical failure evidence. No public duplicate of the new CI cleanup finding was found. |

Baseline reproductions, including the initial inconclusive shallower nesting
attempt, are retained in `results/review-20261013/adversarial-baseline.json`.
No mathematical correction to the duty formula was warranted.

## Numerical and executable verification

VERIFIED within stated criteria: the full suite passes 33 methods. A separate
`python -S` run passes the 11 duty-cycle methods without site packages, retaining
the standard-library-only extension. The committed Decimal regression checks
40 seeded profiles; scaling, units, segment permutation/splitting, repeat duration,
speed changes, contribution normalization and 32 single-mode endpoint combinations
cover both exponents. The independent adversarial reviewer additionally checked
200 profiles spanning the allowed ranges with 60-digit Decimal inverse-life
arithmetic: maximum relative difference `4.367946866409983e-15`, zero failures
against a `1e-12` criterion. This measures arithmetic agreement, not field accuracy.

OBSERVED: the constant example produces 1388.888888888889 hours; the fictional
two-mode example produces 245.09803921568624 hours and 3565.654160826243 N
equivalent radial load. Both examples were executed into a dated directory,
leaving historical example artifacts unchanged. The generated ordinary plot was
visually inspected for legible axes, units and distinction between parameter
uncertainty and fatigue reliability. No performance benchmark was claimed.
Actual commands, exits and source hashes are in `results/review-20261013/validation.json`.

The [SKF super-precision catalog](https://cdn.skfmediahub.skf.com/api/public/0901d19680495562/pdf_preview_medium/0901d19680495562_pdf_preview_medium.pdf),
printed page 35, supports revolution fractions and inverse-life combination for
variable duties. Reading that primary source confirms the algebra under the
restricted conditions. The Schaeffler link in the earlier research record failed
in this web reader; that attempt remains inconclusive.

## Dependencies, history and release checks

OBSERVED: the dated OSV response contains 12 results for the 12 pinned runtime/dev
versions, with zero listed advisories. The first sandbox network attempt failed
and is preserved separately as NOT_VERIFIED. `pip check` passes; installed runtime
versions match `requirements.lock`. Runtime, Ruff and official CI-action license
metadata is in `results/review-20261013/licenses.json`. Project MIT licensing does
not relicense third-party wheels. OSV, metadata and regex checks do not prove
absence of vulnerabilities, package authenticity or exhaustive legal compatibility.

OBSERVED: the GitHub API lists only PR #1 and no separate target issues, releases,
repository advisories, inline review threads or reviews requiring resolution.
The repository allows squash merges; `main` had no rulesets or branch protection
at inspection. Open secret-scanning alerts were empty. No security setting or
protection was weakened. A conservative scan of all 51 reachable historical blobs
and the changed working source/docs/evidence found no matching credential or
private-host-path patterns. See `results/review-20261013/privacy-scan.json`.

Official action revisions were resolved through GitHub tag refs and reviewed
against release notes: checkout v7.0.1 at
`3d3c42e5aac5ba805825da76410c181273ba90b1`, setup-python v7.0.0 at
`5fda3b95a4ea91299a34e894583c3862153e4b97`. They use Node 24; the hosted
Ubuntu runner satisfies their documented minimum runner version. Final hosted
success must be verified at the pushed PR head and squash commit; this local
record does not predict or fabricate it. See the repository PR and Actions pages
for the permanent publication evidence.

OBSERVED unrelated workspace limitation: the separately required workspace
infrastructure validator fails because an existing canonical event at row 337
lacks `event_id`. That failure predates this review and was previously recorded.
It is outside this repository, outside its CI and not a repository release rule.
The validator was run, its failure retained locally, and unrelated log history
was not rewritten. Repository publication depends on the project checks above
and the actual GitHub checks, not a claim that global workspace health passed.

## LEARN and remaining uncertainty

VERIFIED: speed changes require revolution weighting; time-only load averaging
is mathematically wrong except under special conditions. A finite positive
result can still be impossible to histogram as a density when samples collapse
to a point. Checking a file's metadata does not bound the bytes actually read.
External security evidence must fail closed when coverage or availability is missing.

Confidence is high for the executed algebraic fixtures and corrected error paths.
INFERRED: the calculators can support transparent teaching comparisons.
NOT_VERIFIED: physical accuracy, catalog applicability, parameter independence/CV
calibration, modified ISO life, axial/stop/shock behavior, static capacity, minimum
load, lubrication/contamination and actual bearing reliability or maintenance use.
Fatigue contribution is a model ratio, not failure probability. L10 is a population
fatigue rating, not individual remaining useful life. Full ISO conformity, market
novelty and exhaustive supply-chain/legal/security assurance are not claimed.
