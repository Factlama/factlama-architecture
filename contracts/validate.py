#!/usr/bin/env python3
"""Standalone JSON Schema / compatibility validator for FactLama's v0.1 canonical
fixtures.

This is the "standalone compatibility runner" referenced in EXECUTION_PLAN.md's
G0 exit evidence: it validates contracts/v0.1/examples/** against
contracts/v0.1/schemas/** without depending on factlama-reliability's or
factlama-observability's own test/CI foundation (that foundation is G1's job).
G2 additionally runs this same fixture set inside each implementation repo's
own test framework.

Usage:
    contracts/.venv/bin/python contracts/validate.py

Exit code 0 iff every examples/valid/** fixture validates cleanly against its
schema, and every examples/invalid/** fixture is rejected by its schema
(demonstrating unknown schema versions and missing required fields are
actually caught, not merely documented).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parent
SCHEMA_DIR = ROOT / "v0.1" / "schemas"
EXAMPLES_DIR = ROOT / "v0.1" / "examples"

# examples/valid/<type>/*.json directory name -> schema file. Also doubles as
# the recognized filename-prefix vocabulary for the flat examples/invalid/*.json
# fixtures (see _type_for_filename).
TYPES = {
    "verification_request": "verification_request.schema.json",
    "verification_result": "verification_result.schema.json",
    "judge_request": "judge_request.schema.json",
    "judge_result": "judge_result.schema.json",
    "reliability_event": "reliability_event.schema.json",
}


def _load_registry() -> Registry:
    """Register every schema file under its own declared $id, so relative
    $ref values (e.g. "common.schema.json#/$defs/Evidence") resolve against
    each schema's own $id as base URI, exactly as a spec-compliant consumer
    would resolve them."""
    resources = []
    for schema_path in SCHEMA_DIR.glob("*.schema.json"):
        contents = json.loads(schema_path.read_text())
        resource = Resource.from_contents(contents, default_specification=DRAFT202012)
        resources.append((resource.id(), resource))
    return Registry().with_resources(resources)


def _validator_for(type_name: str, registry: Registry) -> Draft202012Validator:
    schema_path = SCHEMA_DIR / TYPES[type_name]
    schema = json.loads(schema_path.read_text())
    return Draft202012Validator(schema, registry=registry)


def _type_for_filename(stem: str) -> Optional[str]:
    for type_name in sorted(TYPES, key=len, reverse=True):
        if stem == type_name or stem.startswith(type_name + "_"):
            return type_name
    return None


def _iter_examples(subdir: str):
    base = EXAMPLES_DIR / subdir
    if not base.exists():
        return
    for path in sorted(base.rglob("*.json")):
        rel = path.relative_to(base)
        if len(rel.parts) > 1:
            # examples/valid/<type>/<name>.json
            type_name = rel.parts[0]
        else:
            # examples/invalid/<type>_<descriptor>.json
            type_name = _type_for_filename(path.stem)
        yield path, type_name


def main() -> int:
    registry = _load_registry()
    validators = {name: _validator_for(name, registry) for name in TYPES}

    failures: list[str] = []
    checked = 0

    for path, type_name in _iter_examples("valid"):
        checked += 1
        if type_name not in validators:
            failures.append(f"{path}: cannot determine schema type from directory name")
            continue
        instance = json.loads(path.read_text())
        errors = sorted(validators[type_name].iter_errors(instance), key=lambda e: list(e.path))
        if errors:
            joined = "; ".join(f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in errors)
            failures.append(f"{path} [{type_name}] expected VALID but got errors: {joined}")
        else:
            print(f"OK    valid   {type_name:22s} {path.relative_to(EXAMPLES_DIR)}")

    for path, type_name in _iter_examples("invalid"):
        checked += 1
        if type_name is None or type_name not in validators:
            failures.append(f"{path}: cannot determine schema type from filename prefix")
            continue
        instance = json.loads(path.read_text())
        errors = list(validators[type_name].iter_errors(instance))
        if not errors:
            failures.append(f"{path} [{type_name}] expected INVALID but validated cleanly")
        else:
            print(f"OK    invalid {type_name:22s} {path.relative_to(EXAMPLES_DIR)}  (rejected: {errors[0].message})")

    print()
    if failures:
        print(f"FAILED: {len(failures)}/{checked} example(s) did not match expectation:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"PASSED: all {checked} example(s) matched expectation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
