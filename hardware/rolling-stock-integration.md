# Rolling-stock hardware integration

This file is the hardware-side bridge to the `light-metro-3car`
trainset BOM and mechanical CAD. It keeps electronic host-class
documentation in `hardware/`, while the consist-level quantities and
physical envelopes remain owned by:

- [`docs/rolling-stock/light-metro-3car/bom-skeleton.md`](../docs/rolling-stock/light-metro-3car/bom-skeleton.md)
- [`docs/rolling-stock/light-metro-3car/README.md`](../docs/rolling-stock/light-metro-3car/README.md)
- [`mechanical-py/src/osr_mech/rolling_stock/systems.py`](../mechanical-py/src/osr_mech/rolling_stock/systems.py)

## Canonical light-metro-3car fit

| Hardware class | Consist quantity | Mechanical envelope | BOM lines | Notes |
|---|---:|---|---|---|
| T-ECU/S safety kernel | 2 | Per-end electronics cabinet | E1, E3-E6, E22 | One A-end unit and one B-end unit; active/hot-standby at train level |
| T-ECU/A application | 2 | Per-end electronics cabinet | E2, E7-E12, E22 | One A-end unit and one B-end unit; non-safety, single-redundant |
| T-OBS obstacle-detection ECU | 2 | Nose sensor pack | E18, E19 | One behind each cabless nose cowl |
| Trainset interior COTS modules | 3 car sets | Car systems + fit-out envelopes | B12-B20, A1-A5 | Quantities scale per self-contained car unless BOM says per consist |
| W-SBC wayside controller | route dependent | Wayside cabinet/pole, not trainset CAD | Wayside BOM | Not part of trainset material BOM |
| S-SBC station/depot host | station dependent | Station/depot cabinet, not trainset CAD | Station BOM | Not part of trainset material BOM |

## Ownership rule

- `hardware/` owns board architecture, DIY/COTS integration packs,
  schematics, custom-board gerbers, board-level BOMs, wiring maps,
  enclosure notes, and bring-up evidence.
- `mechanical-py/` owns physical CAD envelopes, FreeCAD review
  artifacts, and generated screenshots for train components.
- `docs/rolling-stock/light-metro-3car/bom-skeleton.md` owns
  procurement quantities per consist.

If a board changes size, connector side, heat dissipation, or service
clearance, update the matching mechanical envelope and drawing register.
If a consist quantity changes, update the rolling-stock BOM first, then
mirror that quantity here and in the host-class README.
