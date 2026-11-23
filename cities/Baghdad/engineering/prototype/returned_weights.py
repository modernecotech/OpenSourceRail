"""Recalculate an Airport first article and issue returns for its revised opening."""

from pathlib import Path

from cities.Baghdad import airport_integration, airport_opening
from cities.Baghdad.engineering.commissioning import feeder, measurements
from cities.Baghdad.engineering.prototype import car, commercial, weights


def assess(
    article,
    submission,
    *,
    directory=None,
    service=None,
    financial_return=None,
    financial_directory=None,
    feeder_return=None,
):
    """Assess the published weight form or a labelled envelope containing that form."""
    kind = "unclassified"
    if isinstance(submission, dict) and "record_kind" in submission:
        if submission.keys() != {"record_kind", "weights"} or submission["record_kind"] not in (
            "synthetic-fixture",
            "supplier-declaration",
            "physical-measurement",
        ):
            raise ValueError("Identify the origin and include the complete weight form")
        kind = submission["record_kind"]
        submission = submission["weights"]

    service = airport_integration.build()["service"] if service is None else service
    inputs = airport_opening.opening_inputs()
    mass = weights.assess(article, submission, directory=directory, inputs=inputs, service=service)
    sources = (
        Path(__file__),
        Path(weights.__file__),
        Path(feeder.__file__),
        Path(measurements.__file__),
        Path(commercial.__file__),
    )
    result = {
        "schema": "baghdad-prototype-weight-review/1",
        "parent_candidate_id": article["candidate_id"],
        "parent_evaluation_id": article["evaluation_id"],
        "frame_revision": article["frame_revision"],
        "record_kind": kind,
        "source_sha256": {p.relative_to(car.ROOT).as_posix(): car.sha(p.read_bytes()) for p in sources},
        "weights": mass,
        "dependent_input_ids": {
            "financial": car.identity(financial_return) if financial_return is not None else None,
            "feeder": car.identity(feeder_return) if feeder_return is not None else None,
        },
        "candidate_id": None,
        "opening_evaluation_id": None,
        "electrical": None,
        "commercial": None,
        "templates": None,
        "result": mass["result"],
        "physical_accepted": False,
        "authorised_for_purchase": False,
        "energisation_authorised": False,
    }
    child = mass["opening"]
    if child is not None:
        if child["bundle"]["vehicle_revision"] != article["frame_revision"]:
            raise ValueError("The returned mass belongs to a different frame")
        power = feeder.evaluate(child, feeder_return, service=service)
        accounts = commercial.assess(child, service, inputs[0], financial_return, financial_directory)
        result.update(
            candidate_id=child["candidate_id"],
            opening_evaluation_id=child["evaluation_id"],
            electrical=power,
            commercial=accounts,
            templates={
                "finance": commercial.form(child),
                "feeder": {opt: feeder.return_form(child, opt) for opt in feeder.OPTIONS},
                "hot_test": {opt: measurements.template(child, opt) for opt in feeder.OPTIONS},
            },
        )
    result["evaluation_id"] = car.identity(result)
    return result
