# Door module delivery preflight

The [current preflight](door-pack-preflight.json) inventories what the actual
one-opening door still needs before a controlled delivery review pack can be
compiled. It binds the retained [door handoff](door-interface-handoff.json) and
[route request](door-route-request.json) to the same manufacturing child and
analytical installed child. The source counts are **74 part types and 694 pieces
per opening**, including **597 purchased pieces across 35 types**.

No same-child railway delivery proposal was supplied in this run. The report
therefore marks the closure study, installed/civil bundle, nominal service and
fleet, core and full-scope cost, and sealed delivery proposal as unprovided.
The existing analytical body is not a mated installed door. Reference city
service and cost packets belong to another physical candidate and cannot fill
these inputs.

The preflight also lists 74 part types without supplied drawing, inspection and
routing mappings, three assembly document sets not supplied, and 74 unprovided
conversion decisions. **Unprovided** means no controlled index was given to
this check; it does not assert that a drawing cannot exist elsewhere. The
source catalogue's stock sketches, process proposals and general tolerances
are not automatically released mating drawings or approved inspection limits.

When a same-child proposal and controlled documents are available, run:

```sh
python -m tools.automation.v07_door_pack_preflight \
  --proposal /external/proposal.json \
  --documents /external/documents.json \
  --conversions /external/conversions.json
```

This preflight rejects the reference body identity, changed door component
identities, quantities or make/buy routes, foreign document mappings and
acceptance claims. It inventories supplied paths and IDs; it does **not** read
or authenticate drawing payloads, prove the complete railway study, price
conversions or authorise ERP work. The existing `review.compile_review_pack`
must then verify exact source files, sidecar content, estimates and candidate
bindings. Native receipt, Incoming QA, consumption, replacement and handback
need a later disposable ERPNext run with admitted disk resources.

Rebuild/check the committed no-input inventory with:

```sh
python -m tools.automation.v07_door_pack_preflight
python -m tools.automation.v07_door_pack_preflight --check
```

This slice ran no native CAD, FEA or ERP operation and created no purchase,
inspection or installation record. Engineering, manufacturing and physical
acceptance remain open.
