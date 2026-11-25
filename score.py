"""Compare human-reviewed observations with predefined case checks."""

import argparse
import json
from pathlib import Path
import sys


EXAMPLES = Path(__file__).resolve().parent / "examples"
CHECK_KINDS = {"required", "critical", "bonus"}


def read_object(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return data


def load_cases(path):
    rows = read_object(path).get("cases")
    if not isinstance(rows, list) or not rows:
        raise ValueError("cases must be a non-empty list")

    cases = {}
    for case in rows:
        if not isinstance(case, dict):
            raise ValueError("each case must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in cases:
            raise ValueError(f"invalid or duplicate case id: {case_id!r}")

        checks = case.get("checks")
        if not isinstance(checks, list) or not checks:
            raise ValueError(f"{case_id}: checks must be a non-empty list")

        check_ids = set()
        for check in checks:
            fields = ("id", "label", "expected", "kind")
            if not isinstance(check, dict) or any(
                not isinstance(check.get(field), str) or not check[field] for field in fields
            ):
                raise ValueError(f"{case_id}: checks require non-empty id, label, expected and kind")
            if check["kind"] not in CHECK_KINDS or check["id"] in check_ids:
                raise ValueError(f"{case_id}: invalid kind or duplicate check id: {check['id']!r}")
            check_ids.add(check["id"])

        if all(check["kind"] == "bonus" for check in checks):
            raise ValueError(f"{case_id}: add at least one required or critical check")
        cases[case_id] = checks
    return cases


def load_observations(path, cases):
    data = read_object(path)
    observations = data.get("observations")
    if not isinstance(observations, dict):
        raise ValueError("observations must be an object keyed by case id")

    values_by_case = {}
    for case_id, entry in observations.items():
        if case_id not in cases:
            raise ValueError(f"unknown case id: {case_id!r}")
        if not isinstance(entry, dict) or not isinstance(entry.get("values"), dict):
            raise ValueError(f"{case_id}: values must be an object")

        values = entry["values"]
        unknown_checks = values.keys() - {check["id"] for check in cases[case_id]}
        if unknown_checks:
            raise ValueError(f"{case_id}: unknown checks: {', '.join(sorted(unknown_checks))}")
        if any(value is not None and not isinstance(value, str) for value in values.values()):
            raise ValueError(f"{case_id}: observed values must be strings or null")
        values_by_case[case_id] = values
    return values_by_case


def score_case(checks, values):
    required_total = sum(check["kind"] != "bonus" for check in checks)
    bonus_total = len(checks) - required_total
    required_hits = bonus_hits = 0
    required_failed = required_pending = False
    details = []

    for check in checks:
        check_id = check["id"]
        kind = check["kind"]
        expected = check["expected"]
        prefix = f"{kind} / {check_id} / {check['label']}"
        if check_id not in values:
            required_pending |= kind != "bonus"
            details.append(f"{prefix}: unreviewed")
        elif values[check_id] != expected:
            required_failed |= kind != "bonus"
            actual = json.dumps(values[check_id], ensure_ascii=False)
            details.append(f"{prefix}: expected {expected!r}, observed {actual}")
        elif kind == "bonus":
            bonus_hits += 1
        else:
            required_hits += 1

    status = "PASS"
    if required_failed:
        status = "FAIL"
    elif required_pending:
        status = "INCOMPLETE"
    counts = f"required {required_hits}/{required_total}  bonus {bonus_hits}/{bonus_total}"
    return status, counts, details


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=EXAMPLES / "cases.json")
    parser.add_argument("--observations", type=Path, default=EXAMPLES / "observations.json")
    args = parser.parse_args(argv)

    try:
        cases = load_cases(args.cases)
        values_by_case = load_observations(args.observations, cases)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    counts = {"PASS": 0, "FAIL": 0, "INCOMPLETE": 0}
    details_by_case = {}
    width = max(map(len, cases))
    for case_id, checks in cases.items():
        status, score, details = score_case(checks, values_by_case.get(case_id, {}))
        counts[status] += 1
        print(f"{case_id:<{width}}  {status:<10}  {score}")
        if details:
            details_by_case[case_id] = details

    print(f"{counts['PASS']} passed, {counts['FAIL']} failed, {counts['INCOMPLETE']} incomplete")
    for case_id, details in details_by_case.items():
        for detail in details:
            print(f"  {case_id} / {detail}")
    return 0 if counts["PASS"] == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
