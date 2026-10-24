# Owner/builder planning and delivery platform

266 current city revisions,16 named GIS layers, alignment/station/service/OD edit proposals, immutable local revisions and a generic resource/procurement/monthly-cash adapter.

Missing source layers are disabled. Streets and soil display samples are labelled;1km population aggregation preserves source population totals. Radial circles are display aids, not a walking catchment calculation. Editing a station invalidates access, demand, engineering and delivery assumptions until those are rerun.

The generic compiler executes the retained ERP planning adapter. It generates draft quantities and constrained workfront tasks for any retained city. Registered missing rates stay unknown; neither a priced subtotal nor a schedule is a complete project or released design. Native records and independent physical field acceptance remain separate.

Open the [planning workspace](../../../workbench/planning/index.html). Export edits, then run `./osr plan compile edits.json --output build/my-plan`. A stale base revision or changed station order is refused. Local revision storage is append-only and recoverable.

Native owner, builder, operator, workforce and observation links use the isolated loopback stack and its existing authentication. The people link requires the relevant ERP module. This does not claim full OCC/HR federation or deployment permissions.

Primary geography and population sources remain in each city input receipt. All design, physical and procurement release flags remain false.
