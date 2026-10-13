"""Bounded, unambiguous JSON input for the offline calculators."""

import json
from pathlib import Path

MAX_BYTES = 65536


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def read_config(path):
    # Bound the actual read, including streams and files that change after stat.
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("input exceeds 64 KiB")
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=unique_object)
    except RecursionError as error:
        raise ValueError("JSON input is nested too deeply") from error
