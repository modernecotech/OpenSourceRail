# Equipment supervision and lifecycle integration

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. Six 17 m comfort cars carry 44 seats plus two wheelchair places/car and no planned standing; the 120-second target gives 8,280 passengers/hour/direction. Passive steel-wheel bogies run on conventional rails carried by precast concrete. Station LIMs act on passive onboard secondaries; there are no traction motors, traction batteries or suspension magnets onboard. Service batteries, independent brakes and the existing station-led GoA4 architecture remain. The reference design is research only; city numerical regeneration, economics and physical release remain open.

[Project introduction](../../README.md) · [Engineering approach and current status](../../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

The generic gateway in
[`services/integration/osr_integration/`](../../services/integration/osr_integration/)
supports observation, historian, alarm, review and ERP identity workflows. The
[Docker composition](compose.yaml) describes the gateway and FUXA services.
These services support integration development and review; they are not a
commissioned railway-control connection.

Current research delivery packages link manufacturing and control records to
the selected vehicle and railway identities in the
[candidate delivery index](../../docs/design-engine/coupled-railway/delivery-index.json).
They do not provide qualified production instructions, accepted equipment
configurations or movement authority. The v0.6 planning handoff contains route,
stop, service and OD proposals only; it does not import assets into the live
gateway or create operational controls.

Private credentials and deployment records belong under `var/supervision/`.
Site deployment requires authenticated device bindings, reviewed imports,
accountable permissions, independently validated protection and a configured
business platform. The design runner does not activate physical outputs or
commission devices.

Run the offline boundary check with:

```bash
tools/automation/osr-python deployment/supervision/tests/verify-embedded.py
```

Native FUXA and ERP integration scripts require independently configured live
services and private credentials. Their presence does not establish current
railway commissioning or acceptance.
