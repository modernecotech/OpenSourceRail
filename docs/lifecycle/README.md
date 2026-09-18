# Connected OpenSourceRail lifecycle

The integrated view connects **plan → design → procure → manufacture → construct
→ commission → operate → maintain → renew** through stable equipment identities,
versioned engineering evidence and native ERP transactions.

[Open the local lifecycle view](http://127.0.0.1:8090/docs/lifecycle/).
[Deployment and recovery](../../deployment/supervision/README.md).

## Read performance and history

FUXA polls only its active device's current measurements and alarms. It does not
load whole-city evidence or command history. Lifecycle snapshots retrieve latest
measurements in one indexed query and include at most 20 recent evidence records
per asset. **Load older evidence** retrieves earlier records with a stable cursor.

The delivery panel requests the selected asset's city/environment queue, displays
its total and pending counts, and provides **Pending only** and **Load older
deliveries** controls. Other-city traffic cannot evict a pending event from this
view. Authenticated `/outbox` and `/evidence` GET endpoints accept `limit` (1–100)
and `before` cursors; the gateway still enforces the caller's city/environment scope.

See the [load and recovery review](../operating/scaling-and-recovery-review.md)
for measured results and the remaining two-second capacity finding.

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
| ERPNext | Reviewed Item/BOM mapping, partial delivery/outstanding quantities, currency-separated commitments/invoices, native manufacturing actuals, condition-driven Issues and reviewed native Asset Repairs |
| FUXA | Generated station screens for charger, battery, PV and facilities, including quality, timestamp and native gateway status |
| Factory methods | Nine read-only views generated from the 120-product LM3 method coverage and attached to each real `depots-production` identity; reviewed ERP mappings correlate native Work Orders |
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

## Manufacturing-method supervision

A production-plant asset in a `light-metro-3car` city receives one view for each of the nine validated
LM3 methods. This reuses the generated 120-product coverage, 30 tooling families,
work centres, crew/cycle planning, steps, hold points and release gates; it does
not copy recipes into a second configuration. FUXA and Workbench show simulated
cycle progress, cell unavailability and quality hold with timestamp/quality.
The Workbench filters native Work Orders through immutable `OSR Execution Mapping`
rows for the selected method or its product IDs and current engineering revision,
requiring the exact Item **and** BOM pair from the same mapping. A matching Item
with a different BOM revision is excluded.
When no reviewed mapping exists, it explicitly reports zero matching work orders
instead of treating every project production record as affected.

The quality-hold fixture rehearses a method excursion and creates a deduplicated
ERP Issue after persistence. It deliberately does not invent a process temperature,
create/complete a Quality Inspection, change Work Order state, accept or reject
product, or satisfy the method release gate. Actual travelers, observations,
NCR/rework disposition, inspection evidence and accountable manufacturing release
remain native ERP/QMS and OSR evidence work.

Before a prepared supervisory revision replaces a live simulation baseline,
`review-package` now traces exact changed values through existing component,
parent/source-asset, IFC, Rust-crate and ERP identities. It includes installed
serials, append-only lifecycle evidence, open alarm/maintenance cases and pending
commands. The Workbench presents the same review beside matching ERP purchase,
receipt and production feedback. Evidence is marked for reassessment rather than
edited or invalidated, and no order is automatically cancelled or changed.

Apply is bound to the accepted baseline hash and the complete review hash; new
evidence or other in-scope lifecycle state makes an older review stale. Unrelated
city/environment baselines remain outside the transaction. Automatic apply is
blocked for component substitution, an installed-position retirement, a pending
command-contract change and physical remapping. Native BOM exposure is now
available alongside this supervisory slice; full CAD/solver dependency graphs
remain open. The bounded native checks below now cover every disposition action
in the ERP catalogue; they do not constitute manufacturing or railway release.

### Engineering revision exposure

**Engineering & delivery → Engineering revision exposure** follows the selected
equipment's component or factory product/tooling IDs into its reviewed execution
mappings. It includes the current engineering revision and, when a prepared
change exists, the old and proposed revisions. City, company and project must
match. Missing mappings do not fall back to every transaction in the project.

The reusable ERP reader follows explicit nested `BOM Item.bom_no` references,
never the Item's current default BOM. It reports:

- Draft and submitted project purchase lines for the mapped Item and its BOM
  materials. These are potential shared-item exposures, not proven revision
  allocations; closed orders remain labelled historical.
- Draft, unfinished and completed Work Orders matching an exact Item/BOM pair.
  Planned, produced, remaining and native material quantities stay separate.
- Submitted Stock Entries linked to those Work Orders, retaining warehouses,
  stock units, serial/batch bundle and quality-inspection references. Movements
  do not establish current available inventory, accepted WIP or railway release.

The export preserves native read permissions and shows unreadable/missing BOMs,
cyclic references and traversal limits as coverage warnings. All records are
limited to the selected project and company. Other projects and unlinked stock
need separate review. The snapshot observation time is visible, and **Download
revision exposure** exports the same checksummed observations for review.

Refresh with `./osr erp snapshot`, or the existing five-minute feedback timer.
These snapshots cannot put work on hold, cancel procurement or supersede
engineering evidence. The native workflow below records a proposed disposition
and its independent review.
The supervisory apply checksum does not cover these separately timed ERP exports.

### Reviewed disposition plans

Inside Workbench's native ERP city project, choose **OpenSourceRail → Revision
dispositions**. Pick a reviewed engineering mapping and a purchase line, exact
Item/BOM Work Order or linked Stock Entry from its visible exposure. A proposal
requires a responsible ERP user with project access, due date, rationale and
versioned evidence references. Its preview shows the affected native record;
recording creates one immutable **OSR Revision Disposition** and a native ToDo.
Repeating the same request returns the existing record; changed content with
the same identity is rejected.

The record-specific choices are requests to retain/review, amend or cancel a
purchase, stop or rework production, or inspect/trace material movements. These
are plans, not native transaction commands. A second user, different from both
proposer and responsible person, can preview and record **Endorse plan** or
**Reject plan** with review evidence. Endorsement requires the same current ERP
exposure checksum and no coverage warnings. A stale proposal can be rejected;
it needs a new proposal identity for a revised plan. Each proposal has at most
one immutable decision, preserved in **OSR Disposition Decision**.

Manufacturing Manager, Projects Manager and System Manager roles can create/read
these records. Existing project and exposure permissions still govern the
workflow. Server endpoints derive actor identities; generic document insertion,
editing and deletion cannot bypass the reviewed workflow. Workbench displays
the decision separately from whether its exposure is still current. Native
ToDo completion does not verify execution of the requested business action.
Reviewers also need the native source-document read roles: for example,
Manufacturing User grants Work Order access, while Manufacturing Manager alone
does not. Partial exposure remains explicit and cannot receive an endorsement.

Upgrade after a backup: `./osr erp build`, `./osr erp up`, `./osr erp bench migrate`,
then `./osr erp snapshot`. Migration installs all three disposition record types. The same workflow
uses each city's existing project, company, mappings and permissions without
city-specific code or invented organisation/approval identities.

The workflow rechecks visible ERP data during preview and recording; it does not
freeze native orders or stock against concurrent or later changes. Such changes
make the recorded plan stale in refreshed feedback. An endorsed plan alone does
not verify its execution.

### Independent native outcome verification

For an endorsed plan, perform business work through the native ERPNext workflow,
then choose **Verify native outcome** in Revision dispositions. The action registry
supplies the appropriate native document fields. Enter rationale and versioned
evidence references, inspect the displayed record details and readings, then
record the independent verification. **Open verification evidence** exposes the
immutable observation and its underlying native document identities.

| Requested action | Native evidence and verification boundary |
|---|---|
| Retain for review | Unchanged full exposure and unchanged native target; records a retention review without imposing a hold or release |
| Cancellation | Cancelled Purchase Order, with original reviewed quantities and received quantities preserved |
| Amendment | Submitted direct `amended_from` successor of the cancelled order, all lines in the same project, same Items/units, no receiving yet; the reviewer sees replacement quantities, prices, dates and totals |
| Production stop | Submitted Work Order with native status `Stopped`, unchanged quantities, BOM and materials |
| Rework | Completed native corrective Job Card linked to the original submitted Job Card, exact project/Work Order/BOM/Item, performed time logs and quantity, zero process loss, and its linked submitted accepted Quality Inspection |
| Inspection | Submitted Quality Inspection for every reviewed Stock Entry line, exact Item/row references, sample sizes, inspectors and performed readings; accepted and rejected results remain distinct |
| Material trace | Submitted Stock Entry reconciled to permission-visible Stock Ledger Entries and referenced serial/batch bundles; identifies this movement, not current inventory or installed configuration |

The verifier must differ from the proposer, responsible person, native record's
last updater and recorded evidence updaters/inspectors. Existing project and
source-document permissions apply. In the pinned ERP version, Work Order access
requires Manufacturing User, Quality Inspection access requires Quality Manager,
and Stock Ledger Entry access requires Stock User (or another native role granting
that access). Disposition roles alone do not grant access to source evidence.

Checks compare the complete saved, checksummed exposure with current visible
exposure. Only the selected outcome's allowed differences are excluded: cancelled
or directly amended purchase orders, a stop status, inspection links, and the Work
Order timestamp updated by corrective costing. Other BOM, order, quantity or
material changes require a fresh disposition review. Amended orders, corrective
cards, inspections and traced stock entries must be submitted. Cancellation, stop,
amendment, inspection and corrective evidence must
be updated after endorsement. Retention and trace intentionally read existing
records. Item substitution needs a new engineering review and mapping.

Recording adds an immutable **OSR Disposition Execution**, bound to the observed
native data, evidence selection and verifier. Identical retries return the existing
record; changed observations invalidate a preview. Refreshed feedback reports the
action-specific outcome, **Verification stale**, or **Verification unavailable**,
retaining the verifier and history. Resuming work, cancelling an inspection or
changing evidence invalidates the earlier observation. A verified rejected
inspection means the requested inspection was performed: it never means accepted
material. The original exposure may correctly show changed while the expected
native outcome is verified. Refresh `./osr erp snapshot` after business changes.

Proposals created before full exposure capture need a new reviewed proposal;
they cannot be retroactively verified from a checksum alone. Preview and record
recheck observations but do not freeze concurrent native transactions. Native
inspection and corrective evidence cover only the displayed quantities and
samples, not all WIP, all defects or engineering conformity. The workflow does not
execute business actions, complete ToDos or authorise manufacturing/railway release.

The native acceptance test purchases ten units, receives four, reports six
outstanding, manufactures one assembly from its reviewed BOM and checks actual
production. It also tests draft and partially completed production, mixed-project
purchase lines, linked stock movements, a restricted ERP reader, independent
all catalogue outcomes, native corrective work, rejected inspections, batch
movement traces and stale feedback after source changes. Its temporary
transactions are rolled back. No test production or
purchase is presented as real city progress.

## Maintenance and configuration feedback

The simulation demonstrates fault → FUXA alarm → one ERP Issue → reviewed native
Asset Repair → part consumption, actual downtime and repair feedback. The Issue
links back to evidence/trends, and its native project is retained. From the Issue,
**Prepare repair** previews the commissioned Asset, technician, expected downtime,
part warehouse availability and optional serial/batch bundle. Applying the review
creates a draft Asset Repair plus native assignment, without submitting it or
closing the case. The repair preserves a checksum-bound request, condition-event
history and references to the existing OSR configuration/serial evidence.

The native acceptance test closes the Issue while its Asset remains out of order,
then completes the repair, consumes a stocked part through ERPNext and confirms
feedback still reports `required-in-osr`. The supervision rehearsal replaces
`SIM-CHARGER-001` with `SIM-CHARGER-002`, retains the removed serial in affected-
asset search, and requires a fresh independent commissioning test/release before
maintenance evidence. Inspections, restrictions and handback continue in OSR: an
Issue closure, alarm clearance or completed Asset Repair grants no operational
release.

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

Those packages now reuse all 9,097 catalogue switch identities for read-only
points condition views and derive one explicitly aggregate AFC view from each
station. Native level-crossing evaluation and templates are present, but no city
currently declares a crossing asset, so the audit creates none. FUXA/ERP expose
no point or barrier command, route state, protection reset or movement authority.
Samawah also reuses its production-plant identity for nine LM3 method views;
Mosul's `metro-4car` family receives none until applicable methods or a reviewed
module-reuse mapping exist. These views are provided
without claiming that a planned method, simulated hold or ERP Work Order is a
performed traveler, accepted product or released first article.

The contract and evidence adapters are reusable; the currently running equipment
binding is the Rust simulation gateway. Physical Modbus/OPC UA/MQTT/NATS adapters
need the actual supplier interfaces and deployed broker configuration. No new
broker or Node-RED installation is needed for this HTTP pilot.

FUXA full-project replacement is now guarded by a deterministic deployment
manifest and a live-versus-desired review. The review exposes every device/view
addition, replacement and removal and becomes stale if either side changes. The
previous project and applied review are backed up before import. Reviewed custom
display inputs are not yet a separate configuration type, so the manifest records
an empty set and treats live-only edits as explicit removals rather than silently
claiming they are preserved.

The later commercial, fare settlement, land agreements, supplier localisation,
multi-location repair-pool and contractor valuation proposals require their own reviewed rules
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

**Engineering & delivery → Prepared change impact** is a read-only usability
surface. It shows the proposal-wide summary and then narrows to the selected
equipment position, including exact changed paths, affected records, embedded
source crates and required human review activities. “Preview only” and any apply
blockers remain visible; the view cannot approve or apply a package.

Evidence is not a file-upload or electronic-signature service. References identify
existing versioned sources. Inspector and reviewer must be different identities
for simulation commissioning release; physical release still belongs to OSR
assurance. ERP case closure remains separate.

**Trace serial or batch** searches current and removed installations within the
selected city and environment. Results show revision and replacement history,
and can open a matching connected asset. A search on both fields requires both
to match; it does not search other cities or bypass credential scopes.

## Cross-domain change context

Prepared change impact also checks the proposed revision against ERP observations
scoped to city, company and project, with a five-minute freshness limit, and verifies
linked engineering artifact hashes. Missing or changed inputs are listed explicitly.
The context checksum binds these observations; it does not extend the supervisory
apply transaction to ERP. Native business actions still revalidate their current
exposure, and CAD/solver, rework acceptance and formal supersession remain open. See
the [review follow-through](../operating/review-follow-through.md).
