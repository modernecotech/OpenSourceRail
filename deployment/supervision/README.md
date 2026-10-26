# Equipment supervision and lifecycle integration

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. Six 17 m comfort cars carry 44 seats plus two wheelchair places/car and no planned standing; the 120-second target gives 8,280 passengers/hour/direction. Passive steel-wheel bogies run on conventional rails carried by precast concrete. Station LIMs act on passive onboard secondaries; there are no traction motors, traction batteries or suspension magnets onboard. Service batteries, independent brakes and the existing station-led GoA4 architecture remain. The reference design is research only; city numerical regeneration, economics and physical release remain open. Maglev documents below are retained historical research, not the selected v0.6 physical design.

[Project introduction](../../README.md) · [Engineering approach and current status](../../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

The generic gateway in [services/integration](../../services/integration/osr_integration/)
retains observation, historian, alarm, review and ERP identity functions. The
[maglev Workbench](../../docs/workbench/maglev/index.html) is a read-only design
viewer. No maglev hardware adapter or operating control connection is commissioned.

The [Docker composition](compose.yaml) describes the gateway and FUXA services.
Private credentials and existing local deployment records remain under
`var/supervision/`; this repository cleanup does not replace them. Live business
platform commissioning, authenticated device bindings, ERP permissions and
reviewed imports require a separately configured deployment. No automatic city
asset import or physical activation is provided by the current design runner.

Current city [manufacturing plans](../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/maglev/manufacturing.json)
list operations, plant and outstanding acceptance work. They contain no qualified
production instructions or accepted MBOM. The planning adapter preserves that
boundary: it generates no factory methods, invented cycle times or release records.
Production method metadata requires explicit current-family qualification claims,
review references and exact source/product hashes. The gateway checks consistency;
external authentication and engineering adequacy remain separate requirements.

Run the offline boundary check with:

```bash
tools/automation/osr-python deployment/supervision/tests/verify-embedded.py
```

The retained native ERP/FUXA scripts require an independently configured live
instance and private credentials. Their presence does not establish current maglev
commissioning or acceptance. Current verification results report only checks that
actually executed; physical and manufacturing release remain open.
