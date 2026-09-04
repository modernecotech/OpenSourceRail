"""Practical reference defaults for bought-in LM3 product families.

The defaults join the controlled product tree, design-reference geometry and
manufacturer candidate register.  They make concept layouts and RFQs concrete
without silently selecting a supplier or claiming engineering release.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from osr_mech.rolling_stock.product_geometry import geometry_specs
from osr_mech.trainset_cots_candidates import load_and_validate


@dataclass(frozen=True)
class DefaultProductSpecification:
    product_id: str
    default_name: str
    use_class: str
    candidate_ids: tuple[str, ...]
    design_reference_envelope_mm: tuple[float, float, float]
    public_parameters: tuple[str, ...]
    affordability_basis: str
    must_close_before_freeze: tuple[str, ...]
    must_override_when: tuple[str, ...]


# These two SOURCE rows are material/interface kits rather than external-component
# geometry, so the candidate register does not map them automatically.
SUPPLEMENTAL_CANDIDATES = {
    "LM3-CWL-P010": ("OSR-COTS-COMPOSITE-GURIT-130FR",),
    "LM3-FAS-P030": ("OSR-COTS-GLASS-AGC", "OSR-COTS-GLAZING-SIKA268"),
}

# Prefer the complete system over a complementary adhesive, connector, sensor or
# application computer where more than one useful candidate covers the same row.
PREFERRED_CANDIDATE = {
    "LM3-EXT-P020": "OSR-COTS-GLASS-AGC",
    "LM3-EXT-P030": "OSR-COTS-GLASS-AGC",
    "LM3-TRC-P070": "OSR-COTS-HV-SCHALTBAU-C360",
    "LM3-SAF-P010": "OSR-COTS-FIRE-LIIONTAMER-3",
    "LM3-CTRL-P010": "OSR-COTS-CONTROL-DUAGON-MH50C",
    "LM3-CTRL-P020": "OSR-COTS-ROUTER-WESTERMO-630-5G",
    "LM3-ART-P030": "OSR-COTS-TRAINLINE-IGUS-HARTING",
    "LM3-FAS-P030": "OSR-COTS-GLASS-AGC",
}

SAFE_DEFAULT_OVERRIDES = {
    "LM3-FIN-P020": {
        "default_name": (
            "qualified light-colour base roof finish; CaCO3 coating restricted "
            "to coupon and one-car trial"
        ),
        "use_class": "trial-only-reference-not-an-orderable-fleet-product",
    },
    "LM3-TRC-P060": {
        "default_name": (
            "supplier-neutral 650-700 VDC side-contact RFQ; automated collector "
            "retained only as a concept alternative"
        ),
        "use_class": "interface-rfq-default-not-selected",
    },
}


def _row_value(row: object, name: str) -> object:
    value = getattr(row, name, None)
    if value is None:
        raise ValueError(f"product row has no {name}: {row!r}")
    return value.value if hasattr(value, "value") else value


def default_product_specifications(
    product_rows: Iterable[object],
) -> tuple[DefaultProductSpecification, ...]:
    """Return one controlled reference default for every non-MAKE LM3 row."""

    candidate_data = load_and_validate()
    candidates = {str(row["id"]): row for row in candidate_data["candidate"]}
    product_to_candidates = {
        str(product_id): tuple(str(value) for value in values)
        for product_id, values in candidate_data["product_to_candidates"].items()
    }
    product_to_candidates.update(SUPPLEMENTAL_CANDIDATES)
    geometry = geometry_specs()
    rows: list[DefaultProductSpecification] = []
    expected_ids: set[str] = set()
    for product in product_rows:
        route = str(_row_value(product, "route"))
        if route == "MAKE":
            continue
        product_id = str(_row_value(product, "id"))
        expected_ids.add(product_id)
        candidate_ids = product_to_candidates.get(product_id, ())
        if not candidate_ids:
            raise ValueError(f"{product_id} has no reference-default candidate")
        missing = sorted(set(candidate_ids) - set(candidates))
        if missing:
            raise ValueError(f"{product_id} references unknown candidates {missing}")
        preferred_id = PREFERRED_CANDIDATE.get(product_id, candidate_ids[0])
        if preferred_id not in candidate_ids:
            raise ValueError(f"preferred candidate {preferred_id} does not cover {product_id}")
        preferred = candidates[preferred_id]
        spec = geometry[product_id]
        override = SAFE_DEFAULT_OVERRIDES.get(product_id, {})
        default_name = str(
            override.get(
                "default_name",
                f"{preferred['manufacturer']} — {preferred['model']}",
            )
        )
        use_class = str(
            override.get(
                "use_class",
                f"{preferred['selection_state']}-reference-default-not-selected",
            )
        )
        rows.append(
            DefaultProductSpecification(
                product_id=product_id,
                default_name=default_name,
                use_class=use_class,
                candidate_ids=candidate_ids,
                design_reference_envelope_mm=tuple(float(value) for value in spec.envelope_mm),
                public_parameters=tuple(str(value) for value in preferred["public_spec"]),
                affordability_basis=str(preferred["localisation"]),
                must_close_before_freeze=tuple(str(value) for value in preferred["fit_required"]),
                must_override_when=(
                    "the selected order code exceeds the controlled design-reference envelope",
                    "vehicle load, duty, thermal, EMC, fire, accessibility or RAM calculations require another rating",
                    "the quoted configuration lacks the required rail evidence or lifecycle support",
                    "a qualified local equivalent has lower whole-life cost after interface and regression testing",
                ),
            )
        )
    actual_ids = {row.product_id for row in rows}
    if actual_ids != expected_ids:
        raise ValueError(
            "reference-default coverage mismatch: "
            f"missing={sorted(expected_ids - actual_ids)}, "
            f"unexpected={sorted(actual_ids - expected_ids)}"
        )
    return tuple(rows)


def default_specification_payload(product_rows: Iterable[object]) -> dict[str, Any]:
    """Return the complete serialisable register and its source subset."""

    product_rows = tuple(product_rows)
    rows = default_product_specifications(product_rows)
    candidate_data = load_and_validate()
    referenced_ids = {candidate_id for row in rows for candidate_id in row.candidate_ids}
    sources = [
        {
            "id": row["id"],
            "manufacturer": row["manufacturer"],
            "model": row["model"],
            "manufacturer_url": row["manufacturer_url"],
            "source_class": row["source_class"],
            "selection_state": row["selection_state"],
        }
        for row in candidate_data["candidate"]
        if row["id"] in referenced_ids
    ]
    bid_count = sum(str(_row_value(row, "route")) == "BID" for row in product_rows)
    source_count = sum(str(_row_value(row, "route")) == "SOURCE" for row in product_rows)
    return {
        "schema": "org.opensourcerail.lm3-reference-defaults.v1",
        "status": "concept-and-rfq-defaults-not-procurement-or-engineering-release",
        "purpose": (
            "Provide a concrete, affordable starting configuration for every bought-in "
            "LM3 product row while preserving supplier competition and override gates."
        ),
        "checked_on": candidate_data["checked_on"],
        "candidate_source": candidate_data["source_file"],
        "candidate_source_sha256": candidate_data["source_sha256"],
        "default_count": len(rows),
        "route_counts": {"BID": bid_count, "SOURCE": source_count},
        "source_count": len(sources),
        "defaults": [
            {
                "product_id": row.product_id,
                "default_name": row.default_name,
                "use_class": row.use_class,
                "candidate_ids": list(row.candidate_ids),
                "design_reference_envelope_mm": list(row.design_reference_envelope_mm),
                "public_parameters": list(row.public_parameters),
                "affordability_basis": row.affordability_basis,
                "must_close_before_freeze": list(row.must_close_before_freeze),
                "must_override_when": list(row.must_override_when),
            }
            for row in rows
        ],
        "sources": sources,
        "validation": {
            "all_bought_in_rows_covered_once": len(rows) == bid_count + source_count,
            "all_defaults_have_public_parameters": all(row.public_parameters for row in rows),
            "all_defaults_have_override_triggers": all(row.must_override_when for row in rows),
            "all_candidate_ids_resolve": referenced_ids == {str(row["id"]) for row in sources},
            "experimental_finish_has_safe_fallback": (
                next(row for row in rows if row.product_id == "LM3-FIN-P020").use_class
                == "trial-only-reference-not-an-orderable-fleet-product"
            ),
        },
    }


def render_default_specifications(payload: dict[str, Any], titles: dict[str, str]) -> str:
    """Render the reference register for design and procurement review."""

    lines = [
        "# LM3 bought-in product reference defaults",
        "",
        "<!-- Generated by tools/automation/buildable-trainset.sh; do not hand-edit. -->",
        "",
        str(payload["purpose"]),
        "",
        f"- Status: `{payload['status']}`",
        f"- Defaults: **{payload['default_count']}** "
        f"(`BID` {payload['route_counts']['BID']}; `SOURCE` {payload['route_counts']['SOURCE']})",
        f"- Manufacturer/reference sources: **{payload['source_count']}**",
        f"- Candidate sources checked: **{payload['checked_on']}**",
        "",
        "A default is the affordable first configuration to draw, cost and request in an RFQ.",
        "It is not a nominated supplier, order code, quotation, safety approval or permission",
        "to manufacture. CAD envelopes are fit constraints, not claimed supplier dimensions.",
        "",
        "## Default index",
        "",
        "| Product | Reference default | Use class | CAD envelope X × Y × Z (mm) | Sources |",
        "|---|---|---|---:|---|",
    ]
    for row in payload["defaults"]:
        envelope = " × ".join(f"{float(value):g}" for value in row["design_reference_envelope_mm"])
        sources = "<br>".join(f"[`{value}`](#{str(value).lower()})" for value in row["candidate_ids"])
        lines.append(
            f"| `{row['product_id']}` {titles[row['product_id']]} | {row['default_name']} | "
            f"`{row['use_class']}` | {envelope} | {sources} |"
        )
    lines.extend(["", "## Product requirements and override gates", ""])
    for row in payload["defaults"]:
        lines.extend(
            [
                f"### `{row['product_id']}` — {titles[row['product_id']]}",
                "",
                f"Default: **{row['default_name']}**.",
                "",
                "Published reference facts:",
                "",
                *[f"- {value}" for value in row["public_parameters"]],
                "",
                f"Affordability/localisation basis: {row['affordability_basis']}",
                "",
                "Close before supplier freeze:",
                "",
                *[f"- {value}" for value in row["must_close_before_freeze"]],
                "",
                "Override the default when:",
                "",
                *[f"- {value}" for value in row["must_override_when"]],
                "",
            ]
        )
    lines.extend(["## Controlled manufacturer/reference sources", ""])
    for source in payload["sources"]:
        lines.append(
            f"### `{source['id']}` — [{source['manufacturer']} {source['model']}]"
            f"({source['manufacturer_url']})"
        )
        lines.extend(
            [
                "",
                f"- Source class: `{source['source_class']}`",
                f"- Selection state: `{source['selection_state']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Controlled source",
            "",
            f"- Candidate register: `{payload['candidate_source']}` "
            f"(`{payload['candidate_source_sha256']}`)",
            "",
        ]
    )
    return "\n".join(lines)


__all__ = [
    "DefaultProductSpecification",
    "default_product_specifications",
    "default_specification_payload",
    "render_default_specifications",
]
