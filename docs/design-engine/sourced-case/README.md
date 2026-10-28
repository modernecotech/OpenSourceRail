# Published specifications applied to the reference-cell research

The project has executable generators and validators; it does **not** yet have a
qualified railway or a complete, quoted production design. This package records
actual hardware substitutions, their resulting numerical studies and the tests
needed to resolve the remaining engineering decisions.

[Executed results and scope](validation.md) · [closure and required tests](closure-summary.json)

The selected six-car wheel/LIM configuration remains unchanged. These alternatives
study compact wayside roller accelerators, exact motor/inverter/gear variants,
equipped vehicle revisions and distributed power where station-only coasting
cannot satisfy a route's energy balance. All use separate candidate identities.

## Usable primary sources

| Item or experiment | What it supplies | Boundary retained in the model |
|---|---|---|
| [Gurit Kerdyn PET core](https://www.gurit.com/wp-content/uploads/bsk-pdf-manager/2024/06/PDS-Kerdyn-14-0524.pdf) | Grade-specific density, shear and through-thickness compression properties | Typical published properties are not laminate/joint design allowables; transverse compression modulus is not longitudinal bending modulus |
| [Hexcel sandwich design handbook](https://www.hexcel.com/wp-content/uploads/2026/01/Honeycomb_Sandwich_Design_Technology-1.pdf) | Independent sandwich bending/shear method cases | Its particular materials and bonded specimens do not qualify the proposed body |
| [EMRAX downloads](https://emrax.com/downloads/) and [Parker GVM catalogue](https://www.parker.com/content/dam/Parker-com/Literature/Electromechanical-Europe/Literature/192_300108_GVM_catalogue.pdf) | Exact motor variants, continuous ratings and cooling conditions | Different revisions, voltage windings, ambient and coolant conditions are not interchangeable; missing Parker electrical parameters remain missing |
| [Spheros REVO-E bus HVAC](https://www.spheros.com/media/Document/5039/PDS_Spheros_REVO-E_Global_DataSheet__EN_2024-07_DOK15232-001.pdf) | Purchased envelope, mass and electrical connection requirements | Family cooling ranges and tropical application statements do not establish the particular unit's capacity at 55 °C |
| [EpicPower EPC 5k5 648i](https://epicpower.es/product/epc-5k5-648i/) | 600 V/48 V bidirectional power conversion and current limits | Maximum efficiency is not a guaranteed minimum; current website and older PDF mass differ; conditioned enclosure and rail integration remain required |
| [Victron Lithium NG documentation](https://www.victronenergy.com/batteries/lithium-ng-batteries) | Battery variants, topology and operating limits | Public manufacturer list prices are Class B comparisons, with no installed quotation or life-cycle guarantee |
| [Published railway disc/pad experiment](https://pmc.ncbi.nlm.nih.gov/articles/PMC4534372/) | Speed/temperature-dependent friction method comparison | Disc contact speed differs from train speed; this experiment is not a friction map for the proposed purchased caliper/pad |

Exact retrieval hashes, source versions, interpretations and unresolved fields are
retained in the [source registries](../../../engineering/sourced_case/data/).
The published sources are applied to the components they actually describe.
They are not substituted for measurements of an assembled OpenSourceRail train.

## Reproduce and inspect

See the [executable package and commands](../../../engineering/sourced_case/README.md).
The [run manifest](manifest.json), [case index](summary.json),
[structural experiments](structural-methods.json) and
[reopened occurrence geometry](revised-vehicles-ifc.json) bind their payloads to
source and candidate identities. Raw failed executions remain in the structural
archive. The local explorer displays exact revisions, mass and scoped price
coverage, trajectories, open tests and production records.

A [separate V4 bolster experiment](../sourced-bolster/README.md) tests a physical
revision diagnosed from the saved structural response. It has its own body,
evaluation, source and mass identities; it is a next experiment rather than an
automatically preferred railway.

The large cell archive is stored as authenticated bounded chunks described by
[storage.json](storage.json). `./osr design sourced verify-publication` and
`verify-geometry` reconstruct its ignored local cache, then check the original
archive hash and replay the original numerical/geometry verifier. Chunk storage
does not replace source or candidate checks.

The wider platform remains connected through the existing candidate registry,
CAD/IFC, occurrence-linked EBOM/MBOM and disabled ERPNext delivery drafts. A revised
part invalidates the affected mass, analyses, civil quantities, manufacturing,
cost, protection and city-service results. It cannot silently revise a released
manufacturing order.

## Completion boundaries

Catalogue and numerical evidence advances design definition and screening. The
following still require their own records: manufactured laminate and joint tests;
motor/inverter/gear cooling and repeated duty; wet/contaminated contact grip;
actual brake pressure, response, temperature and stopping correlation; hot cabin
cooling; shore connection/interlocks and charge cycling; wheel–rail dynamics;
survey, geotechnics and civil verification; complete supplier/process prices;
HIL fault tests; independent assessment; prototype and pilot-line operation.

No complete installed mass, whole-life-cost winner, operating motor map or physical
acceptance is inferred from a clean software test, a consistent IFC or a numerical
arrival. The generated closure dashboard provides the exact evidence requests.
