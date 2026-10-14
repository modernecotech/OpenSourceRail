"""Read-only work projections; record owners and handback histories stay separate."""

from .contracts import fingerprint

OWNERS = {
    "business": "ERPNext/Frappe purchasing, stock, manufacturing, HR and accounting",
    "railway-assurance": "OSR inspection/NCR/independent handback and appointed authority",
    "telemetry": "integration gateway observations, alarms and scoped supervision",
    "design-experiments": "immutable local problem/candidate/job/attempt store",
    "acceptance": "named scope-qualified independent decision; never search or task completion",
}


def projection(
    city,
    environment,
    *,
    jobs=(),
    twin_jobs=(),
    railway_records=(),
    erp_routes=None,
    telemetry=None
):
    entries = []
    if environment == "simulation":
        for row in twin_jobs:
            if row["city"] == city:
                entries.append(
                    dict(
                        id="city-twin:" + row["id"],
                        owner="design-experiments",
                        native_id=row["id"],
                        state=row["status"],
                        title="City delivery twin",
                        railway_handback=False,
                    )
                )
    for row in jobs:
        if row["city"] != city or row["environment"] != environment:
            continue
        entries.append(
            dict(
                id="design:" + row["id"],
                owner="design-experiments",
                native_id=row["id"],
                state=row["status"],
                title=row["request"]["problem"]["id"],
                railway_handback=False,
            )
        )
    for collection in ("workOrders", "inspections", "defects", "approvals"):
        for row in (railway_records or {}).get(collection, []):
            if row.get("environment") and row["environment"] != environment:
                continue
            entries.append(
                dict(
                    id="assurance:" + collection + ":" + str(row.get("id")),
                    owner="railway-assurance",
                    native_id=row.get("id"),
                    state=row.get("status", "unknown"),
                    title=row.get("title", collection),
                    source_record=row,
                    railway_handback=False,
                )
            )
    for name, route in sorted((erp_routes or {}).items()):
        entries.append(
            dict(
                id="business-route:" + name,
                owner="business",
                native_id=None,
                state="native-owner",
                title=name,
                route=route,
                completion_copied_to_assurance=False,
                railway_handback=False,
            )
        )
    return dict(
        schema="osr-shared-work-projection/1",
        city=city,
        environment=environment,
        entries=entries,
        owners=OWNERS,
        telemetry=telemetry or {"state": "unavailable"},
        projection_sha256=fingerprint(entries),
        business_revision_is_not_assurance_revision=True,
        physical_release=False,
        railway_handback=False,
    )
