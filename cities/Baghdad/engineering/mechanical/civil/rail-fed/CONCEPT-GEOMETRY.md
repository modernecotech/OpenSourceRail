# Rail-fed erection concept geometry

[Two terminal precast yards and inward gantries](two-fronts.png) · [View along and across the deck](launch-section.png) · [3D concept mesh](rail-fed-launch.obj) · [2D DXF](rail-fed-launch.dxf)

The [dimensioned yard plan](terminal-yard.png) and [editable DXF](terminal-yard.dxf)
use the same metre-based footprint, zones, mould cells and released beam positions.

Each terminal yard feeds a launching gantry from behind. Two starter bays at
each end provide a launch and transfer zone. The flatbed travels on a
temporary construction rail path supported by released deck units. At the
front, the gantry places girders for both tracks onto the shared supports.
Traffic around starter bays, the closure bay and exceptional obstructions
still depends on approved access and exclusion plans.

| Geometry or equipment | Basis |
|---|---|
| Standard bay | 20 m span based on the shared-pier U-girder study |
| One U-girder envelope | 4.00 m wide and 1.55 m deep, with nominal 0.20 m webs and 0.24 m floor. End thickenings, ducts, bearing seats and stressing interfaces remain with the candidate design. |
| Paired running decks | 4.50 m centre-to-centre pitch on a shared crosshead |
| Illustrative gantry and feed | An indicative overhead gantry spanning the launch bay and support envelopes, one 22 m flatbed envelope and one carried girder. Temporary rail spacing is an illustrative interface. |
| Common ground works | The view includes indicative pier, crosshead and foundation envelopes. Verify survey, support geometry and construction-stage load paths for a specific site. |

The [high-load girder study](../../../simulation/AUDIT-RESULTS.md#what-changes-the-vehicle-and-civil-enquiry)
supplies the trial section description. The [span family model](../family_comparison.py)
supplies the width, web, floor and track-pitch basis. The drawings show a straight
repeat bay and deliberately separate the gantry and transporter envelopes from
the girder geometry. The equipment supplier and temporary-works designer still
need to establish the transfer and transverse placement geometry, clearances,
reaction loads, rail support and safe working envelopes.

The mesh uses metres with X along the route, Y transverse and Z upwards.
Groups identify supports, released decks, temporary rail, flatbed, carried
girder, gantry and the next bay edges. When importing into a millimetre-based
CAD project, apply a 1,000× coordinate scale to the OBJ mesh. The 2D DXF uses
metre drawing units and puts the two views side by side in model space.
The geometry supports option review and quotation scope.

Regenerate using Python with Matplotlib. To compare independently, pass a
different output directory and compare the files.

```sh
.venv/bin/python cities/Baghdad/engineering/mechanical/civil/rail-fed/render.py --output build/rail-fed-geometry
```
