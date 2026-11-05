# Equipment supervision and lifecycle integration

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. The reference vehicle has six 17 m comfort cars, each with 44 seats and two wheelchair places, no planned standing, and passive steel-wheel bogies on conventional rails carried by concrete. Its passive LIM interface is available for comparison; no installed propulsion architecture or powered length is selected. Acceleration, braking, speed and headway are candidate-specific design variables. The retained 120-second service control gives 8,280 nominal places/hour/direction. The reference vehicle has service batteries and independent brakes, without onboard traction motors, traction batteries or suspension magnets; alternatives must account for their complete system effects. Calculated, priced corridor and city outlines support comparison with explicit assumptions. Engineering verification, prototype validation and manufacturing or operating release remain separate gates.

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
