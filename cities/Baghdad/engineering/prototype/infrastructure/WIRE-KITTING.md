# Prepare a point-to-point wire kit

An electrical integrator can use one supplier wire list to produce cut labels and a blank inspection traveller. Each row is one wire in one named article, between two specified connector pins or terminals. Use one drawing revision and wire specification per kit. The [connector return](connector-return.csv) defines the enquiry scopes. The [traction and control schedule](ELECTRICAL-CONTROLS.md) describes the engineering reviews.

## Try the passive coupon

On a computer with Python 3, extract the whole procurement packet. Open a terminal in its `infrastructure` directory. The same command works from the repository's prototype infrastructure directory.

```sh
python3 wire_kit.py wire-practice.csv --revision COUPON-A --wire-spec PRACTICE-0.5MM2 --output coupon-a
```

Read `coupon-a/wire-cut-labels.csv`. The practice article represents two separate wires with four ends across terminal strips J1 and J2. C01 joins J1 pin 1 to J2 pin 2. Its 180 mm route, 20 mm service slack and 5 mm allowance at each end require **210 mm**. C02 joins J1 pin 2 to J2 pin 1 and uses a 220 mm route with the same allowances for **250 mm**. The two cut lengths total **460 mm**. These arbitrary identifiers and dimensions belong to the coupon. The actual vehicle, station and wayside pin assignments require supplier drawings.

For a paper inspection, cover the expected destinations and give a partner the two mock observations below. Use `continuity-traveller.csv` to record the independently checked drawing, expected and observed endpoints, instrument reference, approved limit reference, actual reading and unit, unintended-path check and disposition. For a paper exercise enter “simulated” for the instrument and reading. Leave any unavailable evidence open.

| Label | First observation | Disposition and repeat |
|---|---|---|
| C01 | J1 pin 1 reaches J2 pin 1 | Record the mismatch and hold the coupon. Reconcile both labels and the independent drawing. |
| C02 | J1 pin 2 reaches J2 pin 2 | Record the second mismatch. On a fresh practice sheet show C01 reaching J2 pin 2 and C02 reaching J2 pin 1. Retain both attempts. |

A physical practice coupon uses a passive, separated assembly and a permitted continuity method under the shop's approved procedure. Test limits, insulation tests, circuit function, protection behaviour and permission to energise require separate engineering information and authority.

## Import a supplier return

1. Copy [wire-practice.csv](wire-practice.csv) under a new name. Replace both practice rows with the supplier's complete list. Enter `supplier-proposal` in `data_class`. Copy the Airport candidate and drawing-packet evaluation from the issued packet, then give the actual supplier drawing revision and wire specification. Supply all fields including the article, wire ID, connector or terminal block and pin at each end. Copy the exact scope and interface text from the connector return. Store the signed drawing and cable specification alongside the input.
2. Enter measured or drawn route length, service slack, and each end's explicit termination allowance in whole millimetres. Use zero only when the supplier explicitly specifies zero. A missing allowance leaves the list incomplete. A strip length already included in the cut length must not be added again. Each end is unique within its article. Junctions, bus links, shared terminals, multiplexed connections, shields and multi-core assembly rules need their own approved schedule.
3. Run the command with the supplier's CSV, exact revision and specification and a fresh output directory. A different packet, unknown scope, missing field, repeated wire or occupied pin stops the import. The tool checks data identity and single-wire topology. Confirm the drawing and pin schedule independently, since incorrect but internally consistent assignments can pass these checks.
4. File `wire-kit.json` with the drawing, input CSV, cut labels and completed traveller. It records the candidate, packet, drawing revision, specification, file digests and total cut length. Ask the supplier for wire stock, terminal and connector price, preparation and testing hours, minimum purchase and measured scrap. Quote by the identified article and kit quantity. A proposed list supplies no installed quantity for other assemblies. Assign production release and installation acceptance to the nominated reviewers.
