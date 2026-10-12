# Learn

LEARNING: L10 fatigue reliability and uncertainty in supplied parameters are different concepts; loads enter life with a strong power law.

EVIDENCE: Reference/scaling/dimensional tests, finite-difference elasticities and analytic-vs-MC quantiles.

IMPACT: Prevents reading a parameter interval as a certified bearing survival probability.

CONFIDENCE: High for explicitly executed fixture/reference checks; external validity is NOT_VERIFIED.

CARRY_FORWARD: Identify units, equivalent-load applicability and separate population reliability from input uncertainty.

UNRESOLVED: Manufacturer factors, real loads/bearings, complete ISO text, lubrication/contamination and engineering certification NOT_VERIFIED.

LEARNING: strictly positive inputs can still underflow in a power-law calculation.

EVIDENCE: preserved reviewer underflow fixture and test_numerical_limits. Initial test at 1e-100 was representable; its failed assumption is retained in validation history.

IMPACT: nonpositive/nonfinite nominal, sampled, analytic or sensitivity lives now reject before plotting.

CONFIDENCE: High for tested numerical boundaries.

CARRY_FORWARD: validate computed outputs as well as inputs.

UNRESOLVED: physical applicability outside hypothetical conventional conditions remains NOT_VERIFIED.
