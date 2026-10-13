# Duty-cycle engineering research and comparative review — 2026-10-13

**OBSERVED (official SKF):** A variable-load bearing history can be reduced
to constant-load intervals. SKF expresses basic rating life as the reciprocal
of the sum of revolution fractions divided by each interval's basic life.
Peak loads must be represented. See SKF *Super-precision bearings*, p. 35:
https://cdn.skfmediahub.skf.com/api/public/0901d19680495562/pdf_preview_medium/0901d19680495562_pdf_preview_medium.pdf

**OBSERVED (Schaeffler):** The technical pocket guide describes equivalent
operating speed and revolution-weighted load for stepwise duties. We omit
manufacturer life-adjustment factors entirely:
https://www.schaeffler.com/remotemedien/media/_shared_media/08_media_library/01_publications/schaeffler_2/catalogue_1/downloads_6/stt_de_en.pdf

**Alternatives inspected:** https://github.com/frasere/ISO-281 implements
application-specific bearing-life analyses for oscillatory pitch systems;
https://github.com/boschresearch/pylife is a broader mechanical fatigue
library. Manufacturer methods and software offer wider validity.
This narrow standalone algebra checker does not replace these and makes
no claim of novelty or market superiority. No third-party code copied.

**LOCAL EVIDENCE:** On 2026-10-13, eight independent synthetic unit tests
in the development workspace passed (8/8); the demo CLI was executed.
Example result: 1500 rpm mean speed, 3565.654160826243 N equivalent
radial load and 245.09803921568624 basic L10 hours. The locally committed
smoke/equation/validation tests and hosted CI must be checked at the PR
SHA before claiming remote verification. No material/field validation.

**LEARN**
- LEARNING: Revolution fractions, rather than time fractions, govern the
  equivalent fatigue load when speed changes.
- EVIDENCE: Independent two-mode inverse-life reference, algebraic tests,
  and the synthetic rare-peak-load check.
- IMPACT: An occasional heavy hypothetical load can dominate modeled
  fatigue contribution.
- CONFIDENCE: High for the given algebra/fixtures; real bearings NOT_VERIFIED.
- CARRY_FORWARD: Reject unsupported conditions explicitly; retain units.
- UNRESOLVED: Actual load histories, bearing catalog factors, validation,
  maintenance utility and professional adoption.

**Publication gate:** Project MIT license present. Original synthetic
fixtures, no credentials, no private systems, no imported vendor code.
Local tests passed. Hosted CI, branch review and full supply-chain scan
remain unverified pending the GitHub PR checks.
