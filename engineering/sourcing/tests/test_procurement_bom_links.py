from engineering.sourcing.model import identity
from engineering.sourcing.procurement_bom import _link_unlocated_obligations


def _package(family, key):
    return {"package_family": family, "package_key": key,
            "package_id": identity({"family": family, "key": key})}


def test_unlocated_obligations_link_to_related_scopes_without_becoming_package_content():
    packages = [
        _package("vehicle-body-stock-kit", "car/0"),
        _package("vehicle-bogie-stock-package", "car/0/bogie/0"),
        _package("vehicle-bogie-stock-package", "car/0/bogie/1"),
        _package("vehicle-secondary-stock-kit", "car/0/station-secondary"),
        _package("civil-rail-stock-pair", "span/0"),
        _package("civil-concrete-stock-package", "span/0"),
        _package("wayside-lim-primary-material-set", "bank/0"),
    ]
    obligations = [
        "car/0/weld-interface/abc123",
        "car/0/passive-bogie-pair/residual",
        "car/0/passive-secondary/residual",
        "car/0/retained-comfort/HVAC/residual",
        "span/0/direct_fastener_kg",
        "span/0/reinforcement_kg",
        "bank/0/cooling-and-services",
        "infrastructure/foundations-ground-site",
    ]

    result = _link_unlocated_obligations(obligations, packages)
    links = {row["scope_key"]: row for row in result["links"]}

    assert result["source_obligation_count"] == 8
    assert result["linked_unique_obligation_count"] == 7
    assert result["unlinked_obligation_count"] == 1
    assert result["unlinked_obligation_ids"] == ["infrastructure/foundations-ground-site"]
    assert links["car/0/passive-bogie-pair"]["related_package_ids"] == sorted(
        row["package_id"] for row in packages
        if row["package_family"] == "vehicle-bogie-stock-package")
    assert links["span/0/track-fastening"]["related_package_ids"] == [
        next(row["package_id"] for row in packages if row["package_family"] == "civil-rail-stock-pair")]
    assert links["span/0/precast-reinforcement-and-prestress"]["related_package_ids"] == [
        next(row["package_id"] for row in packages if row["package_family"] == "civil-concrete-stock-package")]
    assert links["bank/0/cooling-and-services"]["related_package_ids"] == [
        next(row["package_id"] for row in packages if row["package_family"] == "wayside-lim-primary-material-set")]
    assert all(row["association_is_package_membership"] is False for row in links.values())
    assert all(row["allocated_to_package_mass_or_quantity"] is False for row in links.values())
    assert result["links_are_non_additive"] is True
