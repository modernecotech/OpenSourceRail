# Equipment supervision and lifecycle integration

<!-- osr-system-context:start -->
OpenSourceRail develops affordable rail that local companies can build, maintain and improve. The published digital release joins a costed vehicle, civil works, controls, production plan and Workbench journey; Baghdad has separate elevated city planning alternatives. The earlier v0.6 passive-wheel, station-launch design remains research, not the installed drive selection for the v0.7 reference or Baghdad. Each candidate retains its own geometry, mass, service, power, cost and evidence. Safety and accessibility remain requirements. Digital results do not grant fabrication or passenger-operation approval.

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
