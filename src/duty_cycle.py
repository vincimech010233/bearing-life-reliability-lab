"""Offline, synthetic, stepwise pure-radial bearing duty-cycle L10 calculator.

Engineering teaching aid. The result is not an individual bearing RUL estimate.
"""

import argparse
import json
import math
import sys
from pathlib import Path

TOP_LEVEL = {"synthetic", "bearing_type", "dynamic_rating", "force_unit", "segments"}
SEGMENT_KEYS = {"radial_load", "speed_rpm", "duration_hours"}
MAX_BYTES = 65536
MAX_SEGMENTS = 100


def finite_number(value, label, *, minimum, maximum):
    """Reject booleans, nonfinite numbers, and physically unscoped extremes."""
    if (
        type(value) not in (int, float)
        or not math.isfinite(value)
        or not minimum <= value <= maximum
    ):
        raise ValueError(
            f"invalid {label}: expected a finite number in [{minimum}, {maximum}]"
        )
    return float(value)


def calculate(config):
    """Calculate a basic, repeated stepwise L10 estimate, without external I/O."""
    if (
        not isinstance(config, dict)
        or set(config) != TOP_LEVEL
        or config["synthetic"] is not True
    ):
        raise ValueError("synthetic profile with exact required fields only")
    kind = config["bearing_type"]
    if type(kind) is not str or kind not in ("ball", "roller"):
        raise ValueError("bearing_type must be 'ball' or 'roller'")
    unit = config["force_unit"]
    if type(unit) is not str or unit not in ("N", "kN"):
        raise ValueError("force_unit must be N or kN")
    factor = 1.0 if unit == "N" else 1000.0
    rating = finite_number(
        config["dynamic_rating"],
        "dynamic_rating",
        minimum=1e-3 / factor,
        maximum=1e9 / factor,
    ) * factor
    raw = config["segments"]
    if not isinstance(raw, list) or not 1 <= len(raw) <= MAX_SEGMENTS:
        raise ValueError("segments must be a list of 1-100 entries")

    p = 3.0 if kind == "ball" else 10.0 / 3.0
    segments = []
    for index, segment in enumerate(raw):
        if not isinstance(segment, dict) or set(segment) != SEGMENT_KEYS:
            raise ValueError(
                f"segment {index}: exactly radial_load, speed_rpm, duration_hours"
            )
        load = finite_number(
            segment["radial_load"],
            f"segment {index} radial_load",
            minimum=1e-3 / factor,
            maximum=1e9 / factor,
        ) * factor
        speed = finite_number(
            segment["speed_rpm"],
            f"segment {index} speed_rpm",
            minimum=0.01,
            maximum=100000,
        )
        duration = finite_number(
            segment["duration_hours"],
            f"segment {index} duration_hours",
            minimum=1e-6,
            maximum=1e6,
        )
        rev = 60 * speed * duration
        segments.append((load, speed, duration, rev))

    total_rev = math.fsum(row[3] for row in segments)
    total_hours = math.fsum(row[2] for row in segments)
    average_speed = total_rev / (60 * total_hours)
    cycle_fractions = [row[3] / total_rev for row in segments]
    # A revolution-weighted damage fraction is not a failure probability.
    relative_damage = [
        u * (row[0] / rating) ** p for u, row in zip(cycle_fractions, segments)
    ]
    rate = math.fsum(relative_damage)
    p_equivalent = rating * rate ** (1.0 / p)
    l10_million_rev = 1.0 / rate
    l10_hours = 1e6 * l10_million_rev / (60 * average_speed)
    duty_damage = total_rev * rate / 1e6
    repeats = 1.0 / duty_damage
    results = (
        total_rev,
        total_hours,
        average_speed,
        rate,
        p_equivalent,
        l10_million_rev,
        l10_hours,
        duty_damage,
        repeats,
    )
    if any(not math.isfinite(v) or v <= 0 for v in results):
        raise ValueError("input causes non-representable life or duty cycle")

    cases = []
    for (load, speed, duration, rev), u, damage in zip(
        segments, cycle_fractions, relative_damage
    ):
        cases.append(
            {
                "radial_load_N": load,
                "speed_rpm": speed,
                "duration_hours": duration,
                "revolutions": rev,
                "revolution_fraction": u,
                "fraction_of_modeled_fatigue_damage": damage / rate,
            }
        )

    return {
        "classification": "INFERRED",
        "synthetic": True,
        "profile": "pure-radial-stepwise-basic-l10-v1",
        "basis": (
            "Revolution-weighted equivalent radial load; repeated identical duty "
            "cycle; basic L10 is a 90%-survival population fatigue rating, not "
            "an individual lifetime prediction."
        ),
        "input": config,
        "normalized": {
            "dynamic_rating_N": rating,
            "bearing_type": kind,
            "basic_life_exponent": p,
            "segments": cases,
        },
        "duty_cycle_hours": total_hours,
        "duty_cycle_revolutions": total_rev,
        "average_speed_rpm": average_speed,
        "equivalent_radial_load_N": p_equivalent,
        "basic_L10_million_revolutions": l10_million_rev,
        "basic_L10_hours": l10_hours,
        "repeated_duty_cycles_at_basic_L10": repeats,
        "modeled_duty_cycle_fatigue_fraction": duty_damage,
        "limitations": (
            "Illustrative pure-radial P=Fr only. No axial loads, real load "
            "diagrams, catalog X/Y factors, static capacity, minimum-load or "
            "skidding checks, lubrication/contamination, shock transients, "
            "adjusted ISO rating life, field reliability or RUL validation. "
            "Segment fractions assume time at positive constant speeds; "
            "zero-rpm intervals are unsupported. Damage fraction is a model "
            "ratio, not an observed damage measurement or failure probability."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Synthetic JSON duty-cycle profile, <=64 KiB")
    parser.add_argument("output", type=Path, help="Output JSON file (created/overwritten)")
    args = parser.parse_args(argv)
    try:
        if args.input.stat().st_size > MAX_BYTES:
            raise ValueError("input exceeds 64 KiB")
        report = calculate(json.loads(args.input.read_text(encoding="utf-8")))
        encoded = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    except (ValueError, TypeError, OSError, OverflowError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
