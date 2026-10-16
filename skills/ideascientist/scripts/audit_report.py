#!/usr/bin/env python3
"""Check proposal structure and evidence records; never judge scientific truth."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    print("Missing dependency: jsonschema>=4.18,<5. No audit performed.", file=sys.stderr)
    raise SystemExit(2)


NONEMPTY = {"type": "string", "minLength": 1, "pattern": r"\S"}
SOURCE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["id", "title", "location", "version_date", "read_status", "digest", "evidence"],
        "properties": {
            "id": {"type": "string", "pattern": r"^P[0-9]{3,}$"},
            "title": NONEMPTY,
            "location": NONEMPTY,
            "version_date": {"anyOf": [{"type": "string", "format": "date"}, {"type": "null"}]},
            "read_status": {"enum": ["body_read", "abstract_only", "unavailable"]},
            "digest": NONEMPTY,
            "evidence": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["claim", "locator"],
                    "properties": {"claim": NONEMPTY, "locator": NONEMPTY},
                    "additionalProperties": False,
                },
            },
        },
        "additionalProperties": False,
    },
}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def string_values(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from string_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from string_values(item)


def schema_errors(schema, value, name):
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{name}/{ '/'.join(map(str, error.absolute_path)) }: {error.message}"
        for error in validator.iter_errors(value)
    ]


def audit(run_dir: Path, cutoff: date | None = None) -> dict:
    run_dir = run_dir.resolve()
    try:
        report = read_json(run_dir / "report.json")
        sources = read_json(run_dir / "sources.json")
        schema = read_json(Path(__file__).resolve().parents[1] / "assets/report.schema.json")
    except (OSError, ValueError) as exc:
        return {"ok": False, "errors": [str(exc)], "warnings": []}
    errors = schema_errors(schema, report, "report") + schema_errors(SOURCE_SCHEMA, sources, "sources")
    if errors:
        return {"ok": False, "errors": errors, "warnings": []}

    by_id = {}
    for source in sources:
        if source["id"] in by_id:
            errors.append(f"Duplicate source id: {source['id']}")
        by_id[source["id"]] = source

    cited = {m for text in string_values(report) for m in re.findall(r"\[([Pp]\d+)\]", text)}
    for entry in report["related_work"]:
        cited.update(entry["citations"])
    warnings = []
    for identifier in sorted(cited):
        source = by_id.get(identifier)
        if source is None:
            errors.append(f"{identifier}: citation has no source record")
            continue
        if source["read_status"] != "body_read":
            errors.append(f"{identifier}: cited source has no body_read record")
        if not source["evidence"]:
            errors.append(f"{identifier}: missing claim and locator evidence")
        raw_digest = Path(source["digest"])
        digest = (run_dir / raw_digest).resolve()
        if raw_digest.is_absolute() or not digest.is_relative_to(run_dir):
            errors.append(f"{identifier}: digest must be a relative file inside the run directory")
        else:
            try:
                if not digest.is_file() or not digest.read_text(encoding="utf-8").strip():
                    errors.append(f"{identifier}: reading digest is missing or empty")
            except (OSError, UnicodeError):
                errors.append(f"{identifier}: reading digest cannot be read as UTF-8")
        location = source["location"]
        parsed = urlparse(location)
        if parsed.scheme in {"http", "https"}:
            if not parsed.netloc or parsed.username or parsed.password:
                errors.append(f"{identifier}: invalid public source URL")
        elif not Path(location).is_absolute() or not Path(location).is_file():
            errors.append(f"{identifier}: location must be HTTP(S) or an existing absolute file path")
        version_date = source["version_date"]
        if cutoff is not None:
            if version_date is None:
                errors.append(f"{identifier}: unknown version date in temporal mode")
            elif date.fromisoformat(version_date) >= cutoff:
                errors.append(f"{identifier}: source version is on or after cutoff {cutoff.isoformat()}")
        elif version_date is None:
            warnings.append(f"{identifier}: source version date is unknown")
    return {
        "ok": not errors,
        "cited_sources": len(cited),
        "errors": errors,
        "warnings": warnings,
        "scope": "Structure and evidence records only. No verification of truth, entailment, novelty, or scientific validity.",
    }


def parse_date(value: str) -> date:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise argparse.ArgumentTypeError("Use YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--cutoff", type=parse_date, help="Exclusive upper bound for cited source version dates")
    args = parser.parse_args()
    result = audit(args.run_dir, args.cutoff)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
