import copy

from engineering.toolchain import baseline_assurance


def test_all_analytical_benchmarks_pass_independent_formulations() -> None:
    cases = baseline_assurance.analytical_cases()
    assert len(cases) == 7
    assert all(case["passed"] for case in cases)
    assert {case["id"].split("-")[1] for case in cases} == {
        "STRUCT",
        "THERM",
        "DRAIN",
        "ENERGY",
        "ELEC",
        "EGRESS",
        "TIME",
    }


def test_interchange_contracts_pass_and_keep_planning_boundary() -> None:
    checks = baseline_assurance.interchange_checks()
    assert all(check["passed"] for check in checks)
    duty = next(check for check in checks if check["id"] == "XCHG-DUTY-001")
    assert duty["source_kind"] == "planning"
    assert not duty["acceptance_eligible"]


def test_report_result_is_conjunction() -> None:
    report = baseline_assurance.build_report()
    assert report["passed"]
    changed = copy.deepcopy(report)
    changed["benchmarks"][0]["passed"] = False
    assert not all(row["passed"] for row in changed["benchmarks"] + changed["interchange"])
