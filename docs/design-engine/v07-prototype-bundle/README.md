# v0.7 powered prototype research bundle

This packet joins the powered six-car vehicle, a rigid overhead 1.5 kV DC supply
concept, and the equal-service calculation under **one research candidate**. It
does not change the selected v0.6 passive-wheel reference. The immutable
[result](packet/result.json) records the physical candidate ID, a separate
engineering revision, evaluation ID, provisional next-experiment selection ID,
the exact eight source hashes, and the native IFC file hash.

## Engineering content and limit

- Six 17 m cars, 276 normal places, 72 km/h cap, 0.4 m/s² command and 120 s
  control case. The vehicle child provides 24 driven axles; the overhead child
  provides the electrical supply hypothesis. The 82.8 kWh/car retained battery
  remains for service loads only.
- Conditional motor/brake/collector equipment allocation adds 1,070–2,395
  kg/car after a counted passive part is retired. The independent +2,400 kg/car
  service sensitivity bounds that allocation. It yields **25.072 t/car** normal
  and **33.622 t/car** at the 160-person crowd control, both accounted upper
  analytical loads, not measured installed weights. The equal-load static means
  are about 61.49 and 82.46 kN/axle. Actual maxima, CG, dynamics, fasteners,
  wiring, cooling and complete installed mass remain open.
- On the 2.727 km, +2% comparison leg the model requests 102.23 kN and 2.045 MW
  mechanical peak, 33.79 kWh mechanical energy, and at least 0.0693 optimistic
  traction adhesion across 24 driven axles. With the declared 25% peak rating
  margin, 85% drive efficiency and 30 kW auxiliaries, procurement must seek at
  least **3.037 MW train DC input / 506 kW per six 1C4M groups**. Six 460 kW
  lower catalogue entries do not satisfy this hypothesised rating floor.
- The independent brake calculation demands about 119.8 kN train rail-direction
  force at the normal upper load on a 2% downgrade, with wheel brakes unavailable.
  One of twelve bogie modules out demands about 10.89 kN and 218 kW peak heat per
  remaining module. Coil power, protected stopping energy after overhead loss,
  actuator behavior, parking, longitudinal force and hot duty are **unknown**.
  The service battery is not credited as certified brake supply.
- The native [IFC4](packet/nominal-prototype-interface.ifc) is exported through
  IfcOpenShell 0.9.0.post1, reopened, and checked for 54 candidate-bound motor,
  brake and collector **interface boxes**. Each box has a distinct digital
  occurrence ID; no physical serial or lot is asserted. These nominal volumes
  are not detailed native CAD, installed mass, approved clearance or civil
  structure. STEP export awaits approved supplier geometry and a complete CAD
  assembly. The manufacturing BOM, route, draft procurement and construction
  records are explicitly unreleased.
- All 14 candidate installed capital scopes and whole-life price remain
  **unknown**. The labelled synthetic line-30 cost numbers in the packet are
  another-candidate proxies and cannot price this powered configuration.

The source-bound generator rejects changed child outputs and mixed identities.
It keeps the inherited support geometry identifiable while withholding approval
of axle loads, overhead mounts, foundations, erection and civil cost. Physical,
manufacturing and operating acceptance all remain false pending drawings,
measurements, quotations, site data and independent review.

## Reproduction

In an environment with the repository requirements, including IfcOpenShell 0.9:

```sh
python -m engineering.design_search.v07_prototype_bundle check \
  --output docs/design-engine/v07-prototype-bundle/packet
pytest -q engineering/design_search/tests/test_v07_prototype_bundle.py
```

For a changed source packet, run `write` with a **fresh private output
directory** and review the generated identities before replacing this packet.
The prior source-bound outputs must be regenerated when their own producers or
current selected packet changes. This packet is a controlled research handoff,
not an approved railway or v0.7 release acceptance record.
