# Connected OpenSourceRail lifecycle

The integrated view connects **plan → design → procure → manufacture → construct
→ commission → operate → maintain → renew** through stable equipment identities,
versioned engineering evidence and native ERP transactions.

[Open the local lifecycle view](http://127.0.0.1:8090/docs/lifecycle/).
[Deployment and recovery](../../deployment/supervision/README.md).

## Implemented connections

| Owning system | Integration |
| --- | --- |
| OSR city generator | Uses existing station/depot IDs and engineering revision; shared templates with 266 city profiles |
| Embedded Rust | `osr-energy-site` example runs the existing evaluator; gateway converts its watts and state of charge into the common telemetry contract |
| Station software | `StationScadaOutput` / `LightingZoneStatus` adapter preserves native lighting semantics |
| FreeCAD | Versioned FCStd object metadata; selected charger object opens the city asset view |
| Bonsai / IFC | Existing IFC GlobalIds retained; checksum-bound sidecar maps the reference model to city positions |
| QGIS | Existing GeoPackage/layer evidence and original station feature IDs map to the same position |
| Other engineering tools | Versioned evidence manifests for SUMO, OSR analysis, OpenSees, EnergyPlus, FDS, SWMM, JuPedSim, CloudCompare, Blender and verification outputs |
| ERPNext | Reviewed Item/BOM mapping, partial delivery/outstanding quantities, currency-separated commitments/invoices, native manufacturing actuals and condition-driven Issues |
| FUXA | Generated station screens for charger, battery, PV and facilities, including quality, timestamp and native gateway status |
| OSR assurance | Existing works/inspection/handback/defect records shown alongside the asset; independent authority retained |

Samawah and Mosul have operating **simulation** pilots. Their reference station
geometry is not a site-approved cabinet manufacturing design. Supplier drawings,
manufacturing recipes, commissioned device maps and operational acceptance remain
real engineering inputs, not automatically generated approvals.

## Engineering packages and desktop tools

```sh
./osr supervision engineering cities/catalogue/west-asia/Iraq/Samawah/operations/engineering-integration.json --output build/supervision/samawah/engineering.json
python3 tools/automation/desktop-links.py samawah
```

An engineering manifest records city, asset, input revision, assumptions, owning
tools/versions and actual file checksums. IFC objects, FCStd object names, QGIS
layers and GIS feature IDs are extracted from existing artifacts. A tool's absent
version remains explicitly unknown; it must be established during review.

`build/supervision/<city>/desktop-links.json` connects the existing reference
charger `STN-CHG-P010` to the pilot station position. Shared library models are
qualified by city and artifact; they are not mistaken for unique installed assets.
For a multi-station model, provide reviewed object-to-position bindings; ambiguous
selection is rejected.

In FreeCAD, select a charger part and run
[`opensource_rail.FCMacro`](../../tools/integration/opensource_rail.FCMacro).
Choose the generated city link file. The macro opens Workbench without editing CAD.

For Bonsai's Python console:

```python
import sys
sys.path.insert(0, '/path/to/OpenSourceRail/tools/integration')
import desktop_bridge
# Select the charger IFC object before running:
desktop_bridge.bonsai('/path/to/OpenSourceRail/build/supervision/samawah/desktop-links.json')
```

For QGIS's Python console, after selecting the existing station feature:

```python
import sys
sys.path.insert(0, '/path/to/OpenSourceRail/tools/integration')
import desktop_bridge
desktop_bridge.qgis('/path/to/OpenSourceRail/build/supervision/samawah/desktop-links.json', iface)
```

These bridges carry stable references. CAD changes return to FreeCAD; coordination
changes return through Bonsai/BCF to the design owner. Live telemetry and ERP
transactions stay outside IFC. Desktop selection resolution is tested with the
actual reference object identities; graphical interaction inside each desktop
application still requires a user session.

## Engineering-to-execution boundary

An execution proposal must explicitly map component type/revision to ERP Item,
stock unit, production BOM, drawing, inspection requirement and reviewed conversion
rule. The conversion rule describes production allowances and process inputs; a
CAD parts list alone does not satisfy it.

```sh
./osr supervision execution-proposal build/supervision/samawah/engineering.json reviewed-item-mapping.json --output build/supervision/samawah/execution.json
```

`osr_erpnext.integration.preview_execution` verifies the native Item and submitted
active BOM and returns a fingerprint. `apply_execution` records an immutable
`OSR Execution Mapping` after review. Neither submits orders. Use the existing
manufacturing component to create draft Work Orders from the reviewed BOM.
Native ERP procurement, quality, stock and accounting workflows remain in force.

The native acceptance test purchases ten units, receives four, reports six
outstanding, manufactures one assembly from its reviewed BOM and checks actual
production. Its temporary transactions are rolled back. No test production or
purchase is presented as real city progress.

## Maintenance and configuration feedback

The simulation demonstrates fault → FUXA alarm → one ERP Issue → case status in
OSR. The Issue links back to evidence/trends, and its native project is retained.
Inspections, restrictions and handback continue in OSR. A closing Issue does not
clear a controller alarm or grant operational release.

Installation/serial/batch records and replacement history support affected-assets
queries. Simulation evidence can rehearse as-designed, released-for-execution,
as-built, as-commissioned and as-maintained transitions. A physical installation
must instead obtain its release from the existing OSR assurance workflow.

Delivery, invoicing, production, installation and engineering acceptance remain
separate measures. The feedback does not invent accepted quantities, domestic
value added or manufacturing origin when source evidence is absent.

## Extension points and remaining deployment work

The generated [operating-readiness audit](../operating/readiness.md) compiles
real-asset simulation packages for all 266 city profiles rather than validating
them against a placeholder station. It also compiles every ERP/component profile
and records which full task payloads are locally materialised. This closes the
repository configuration/asset-coverage ambiguity; it does not turn simulation
templates into commissioned physical mappings.

The contract and evidence adapters are reusable; the currently running equipment
binding is the Rust simulation gateway. Physical Modbus/OPC UA/MQTT/NATS adapters
need the actual supplier interfaces and deployed broker configuration. No new
broker or Node-RED installation is needed for this HTTP pilot.

The later commercial, fare settlement, land agreements, supplier localisation,
repair-pool and contractor valuation proposals require their own reviewed rules
and real master data. This implementation establishes their stable identities and
execution evidence; it does not claim those domain workflows are complete.

## Evidence and traceability in the Workbench

**Connected assets → Record lifecycle evidence** supports design review,
execution release, installation/replacement, commissioning tests, simulation
commissioning release, maintenance, renewal review, analysis and change proposals.
The shared [evidence catalogue](evidence-types.json) builds the form for every city.
Review shows the exact asset, environment, engineering revision, immutable record
ID and versioned references before submission. A scoped evidence credential is
required; the gateway enforces roles and prerequisites. A failed reply can be
retried with the same reviewed ID. Changing the target discards that review and
clears the evidence credential. Successful recording also clears the credential.

Evidence is not a file-upload or electronic-signature service. References identify
existing versioned sources. Inspector and reviewer must be different identities
for simulation commissioning release; physical release still belongs to OSR
assurance. ERP case closure remains separate.

**Trace serial or batch** searches current and removed installations within the
selected city and environment. Results show revision and replacement history,
and can open a matching connected asset. A search on both fields requires both
to match; it does not search other cities or bypass credential scopes.
