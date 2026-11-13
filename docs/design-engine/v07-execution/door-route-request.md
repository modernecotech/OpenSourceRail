# One-opening guide and belt route request

The [route request](door-route-request.json) carries the selected manufacturing
child, analytical installed child, evaluation, opening, all 74 component
definitions and 694 counted pieces from the retained
[door interface handoff](door-interface-handoff.json). It does not change that
handoff or its original installation result. The request is a controlled input
for designing `car-0/door-0`, not an installed door model.

The source definition has one 2.9 m cut guide and one 5.8 m cut belt per
opening. The installed-layout illustration draws each cut-length item as a
2 m straight zone. That drawing is useful for locating an unresolved item,
but it cannot show the full guide, the belt loop, its mount or its removal.
The proposed 1.4 m opening and two 0.72 m leaf travels add to 2.84 m. The
60 mm difference from guide stock is arithmetic only. It makes the missing
end stops, attachments and clearances more urgent; it is not a fit allowance.

| Needed next | Controlled input and check |
|---|---|
| Header to body | Car-local datum frame, hole pattern, joint, load path, adjacent structure and access hatch |
| Guide and carriages | Full guide endpoints and section, mounting datums, bearing fits, retention, stops and swept/removal envelope |
| Belt and drive | Identified pulley axes, closed pitch path, tensioner range, shaft/coupling interface and thermal duty |
| Leaves and protection | Leaf positions and motion sweep, seals, crush gaps, obstruction/lock sensing, wiring and manual release |
| Production and service | Controlled dimensions/tolerances, inspection limits, replacement procedure and evidence of clearances |

The intake checker rejects the 2 m guide proxy as full geometry, a 5.8 m
straight belt, a nonclosed belt path, short guide endpoints, mixed candidate
identities and claimed acceptance. It can return missing inputs for a partial
proposal. Even a syntactically complete proposal still needs independent
motion, clearance, electrical and physical review before native assembly or
manufacturing release. Unknown datums and acceptance limits remain `null`.

Generate/check the current request and assess a proposed route with:

```sh
python -m tools.automation.v07_door_route
python -m tools.automation.v07_door_route --check
python -m tools.automation.v07_door_route --proposal /external/door-route-proposal.json
```

The current generator pins the exact retained handoff bytes. A physical
change to guide stock, belt or installation requires a new candidate and a
new reviewed handoff before the pin is advanced. The original source-bound
installation receipt remains historical evidence. This slice ran no native
CAD, FEA or ERP jobs and did not establish installed mass or a qualified door.
