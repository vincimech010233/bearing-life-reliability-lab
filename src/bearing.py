"""Basic L10 fatigue calculation for hypothetical pure-radial loads; not certification."""

import argparse
import html
import json
import math
import sys
from pathlib import Path
from statistics import NormalDist
import numpy as np

FIELDS = {
    "synthetic",
    "bearing_type",
    "dynamic_rating",
    "radial_load",
    "axial_load",
    "force_unit",
    "speed",
    "speed_unit",
    "cv",
    "samples",
    "seed",
}


def number(value, name, low=0, high=1e9, strict_positive=False):
    if (
        type(value) not in (int, float)
        or not math.isfinite(value)
        or value < low
        or value > high
        or strict_positive
        and value <= 0
    ):
        raise ValueError(f"invalid {name}")
    return float(value)


def validate(c):
    if not isinstance(c, dict) or set(c) != FIELDS or c["synthetic"] is not True:
        raise ValueError("restricted synthetic profile required")
    if (
        c["bearing_type"] not in {"ball", "roller"}
        or c["force_unit"] not in {"N", "kN"}
        or c["speed_unit"] != "rpm"
    ):
        raise ValueError("unsupported type/units")
    factor = 1 if c["force_unit"] == "N" else 1000
    C = number(c["dynamic_rating"], "rating", strict_positive=True) * factor
    P = number(c["radial_load"], "radial load", strict_positive=True) * factor
    axial = number(c["axial_load"], "axial load") * factor
    if axial != 0:
        raise ValueError("axial loads require catalog X/Y factors; unsupported")
    rpm = number(c["speed"], "speed", high=100000, strict_positive=True)
    if not isinstance(c["cv"], dict) or set(c["cv"]) != {"rating", "load", "speed"}:
        raise ValueError("three independent CVs required")
    cv = [number(c["cv"][k], "CV", high=0.3) for k in ["rating", "load", "speed"]]
    if (
        type(c["samples"]) is not int
        or not 500 <= c["samples"] <= 5000
        or type(c["seed"]) is not int
        or not 0 <= c["seed"] < 2**32
    ):
        raise ValueError("sample/seed bound")
    return C, P, rpm, 3.0 if c["bearing_type"] == "ball" else 10.0 / 3.0, cv


def positive_finite(values, name):
    values = np.asarray(values)
    if np.any(~np.isfinite(values)) or np.any(values <= 0):
        raise ValueError(f"{name}: numerical underflow/overflow or nonpositive result")


def life(C, P, rpm, p):
    for v, name in [(C, "rating"), (P, "load"), (rpm, "speed")]:
        number(v, name, high=1e15, strict_positive=True)
    if p not in (3.0, 10.0 / 3.0):
        raise ValueError("supported life exponent required")
    try:
        revolutions = 1e6 * (C / P) ** p
        hours = revolutions / (60 * rpm)
    except OverflowError as error:
        raise ValueError("nominal life exceeds numerical range") from error
    positive_finite([revolutions, hours], "nominal life")
    return revolutions, hours


def analytic_lognormal(C, P, rpm, p, cv):
    means = np.log([C, P, rpm])
    variance = np.log1p(np.square(cv))
    mu = means - 0.5 * variance
    mu_l = math.log(1e6 / 60) + p * mu[0] - p * mu[1] - mu[2]
    sigma_l = math.sqrt(p * p * (variance[0] + variance[1]) + variance[2])
    quantiles = [
        math.exp(mu_l + NormalDist().inv_cdf(q) * sigma_l) for q in [0.025, 0.5, 0.975]
    ]
    positive_finite(quantiles, "analytic quantiles")
    return quantiles


def analyze(c):
    C, P, rpm, p, cv = validate(c)
    rev, hours = life(C, P, rpm, p)
    rng = np.random.default_rng(c["seed"])
    variance = np.log1p(np.square(cv))
    mu = np.log([C, P, rpm]) - 0.5 * variance
    try:
        with np.errstate(over="raise", under="raise", invalid="raise", divide="raise"):
            draws = rng.lognormal(mu, np.sqrt(variance), (c["samples"], 3))
            positive_finite(draws, "parameter samples")
            sim = 1e6 / 60 * (draws[:, 0] / draws[:, 1]) ** p / draws[:, 2]
            positive_finite(sim, "sample lives")
            quantiles = np.quantile(sim, [0.025, 0.5, 0.975])
            exact = np.array(analytic_lognormal(C, P, rpm, p, cv))
            loads = np.linspace(0.5 * P, 1.5 * P, 61)
            curve = 1e6 / 60 * (C / loads) ** p / rpm
            positive_finite(curve, "sensitivity lives")
            positive_finite(quantiles, "sample quantiles")
    except (FloatingPointError, OverflowError) as error:
        raise ValueError("parameter range exceeds numerical model limits") from error
    report = {
        "classification": "INFERRED",
        "synthetic": True,
        "profile": "pure-radial-l10-v1",
        "input": c,
        "normalized": {"C_N": C, "P_N": P, "speed_rpm": rpm, "p": p},
        "basic_L10_revolutions": rev,
        "basic_L10_hours": hours,
        "reliability_basis": "Basic rating life associated with 90% survival against rolling-contact fatigue under conventional model conditions; not a guaranteed individual service life.",
        "elasticities_hours": {"rating": p, "load": -p, "speed": -1.0},
        "uncertainty": {
            "model": "independent lognormal inputs with supplied arithmetic means and CVs; parameter uncertainty, not bearing-to-bearing failure distribution",
            "samples": c["samples"],
            "seed": c["seed"],
            "parameter_life_quantiles_2_5_50_97_5_hours": quantiles.tolist(),
            "analytic_lognormal_quantiles_hours": exact.tolist(),
            "monte_carlo_relative_quantile_error": (
                (quantiles - exact) / exact
            ).tolist(),
        },
        "sensitivity": {"radial_load_N": loads.tolist(), "life_hours": curve.tolist()},
        "limitations": "Pure radial equivalent load P=Fr assumed. No catalog selection, axial factors, static capacity, minimum load, lubrication, contamination, reliability adjustment, wear, corrosion, electrical damage, mission certification or real bearing validation.",
    }
    return report, sim


def plot(r, samples, out):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4), layout="constrained")
    axes[0].plot(r["sensitivity"]["radial_load_N"], r["sensitivity"]["life_hours"])
    axes[0].set(
        xlabel="Hypothetical radial load (N)",
        ylabel="Basic L10 (h)",
        title="Pure-radial sensitivity",
    )
    axes[0].grid(alpha=0.25)
    axes[1].hist(samples, bins=40, density=True, color="#386ca0")
    axes[1].axvline(r["basic_L10_hours"], color="#a74335", label="Nominal L10")
    axes[1].set(
        xlabel="Parameter-induced L10 estimate (h)",
        ylabel="Density (1/h)",
        title="Independent lognormal input uncertainty",
    )
    axes[1].legend()
    fig.savefig(out, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output_dir")
    a = parser.parse_args()
    try:
        p = Path(a.input)
        if p.stat().st_size > 65536:
            raise ValueError("input exceeds 64 KiB")
        r, s = analyze(json.loads(p.read_text()))
        out = Path(a.output_dir)
        out.mkdir(exist_ok=True, parents=True)
        plot(r, s, out / "bearing.png")
        (out / "report.json").write_text(
            json.dumps(r, indent=2, allow_nan=False) + "\n"
        )
        (out / "report.md").write_text(
            "# Bearing Life & Reliability Lab\n\nINFERRED preliminary model; hypothetical pure-radial input.\n\nBasic L10: "
            + str(r["basic_L10_hours"])
            + " h ("
            + str(r["basic_L10_revolutions"])
            + " rev).\n\n"
            + r["reliability_basis"]
            + "\n\nParameter uncertainty: "
            + html.escape(str(r["uncertainty"]))
            + "\n\n"
            + r["limitations"]
            + "\n\n![Executed parameter study](bearing.png)\n"
        )
    except (ValueError, TypeError, KeyError, OSError, OverflowError) as e:
        print(e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
