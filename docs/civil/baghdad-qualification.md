# Baghdad civil qualification inputs

The user-selected qualification target is Baghdad. The retained civil workbench
uses a 100 m double-track comparison segment, separate from the city's 54-line
planning inventory. This selection does not convert reference-software results
into qualification evidence.

The controlled sources are [`viaduct-load-model.toml`](viaduct-load-model.toml),
[`rolling-stock.toml`](../../lib/templates/rolling-stock.toml), and the
[Baghdad design](../../cities/catalogue/west-asia/Iraq/Baghdad/design.toml), soil
and survey readiness records. The selected profile has six cars, 24 axles and a
111 m planning length. Its retained mass envelopes are 204 t tare, 258 t AW2,
276 t AW3 and a separate 384 t infrastructure allowance. None specifies actual
loaded axle forces. LM3's three-car axle spacing must not be repeated.

The [readiness packet](../../engineering/civil_exploration/examples/baghdad-qualification/qualification.md)
records open inputs and accountable disciplines. Its JSON counterpart hashes
each controlled source. Supplier quotes, actual materials, support-zone ground
profiles, adopted project limits, surveyed alignment, physical testing and
independent authority acceptance remain open. The retained desktop soil summary
reports 30 missing profiles; stiffness hypotheses cannot supply those measurements.

Run `civil-study.py qualification` to generate a fresh readiness packet. Default
`run` and `programme` write the packet and return status 2 without invoking native
analysis when the supplier train pattern is missing. To replay the existing
software controls, select `--deployment reference` explicitly.

The first execution dependency is a supplier six-car drawing and case-specific
loaded axle schedule. A [strict supplier record](../../engineering/civil_exploration/schemas/supplier-train.json)
binds the original document by repository path and SHA-256. All 24 positions must
be unique, ordered and inside the stated train length; axle forces must sum to
the declared loaded mass under 9.81 m/s² gravity. A source-bound pattern enables
moving-force research, while every other qualification gate stays open. It
does not establish engineering acceptance of the supplier data or the structure.

The full coupled Baghdad programme additionally needs supplier suspension,
sprung/unsprung masses, bogie/articulation and contact data, and an adapter for
those relationships. The existing uniform LM3 coupled diagnostic is retained as
reference verification. Costs remain unknown until quotations and their scope
are supplied. Physical and operating release remain false.

Commands, resumption behaviour and model limits are documented in the
[workbench README](../../engineering/civil_exploration/README.md).
