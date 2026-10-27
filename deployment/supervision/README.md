# Equipment supervision and lifecycle integration

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. Six 17 m comfort cars carry 44 seats plus two wheelchair places/car and no planned standing; the 120-second target gives 8,280 passengers/hour/direction. Passive steel-wheel bogies run on conventional rails carried by precast concrete. Station LIMs act on passive onboard secondaries; there are no traction motors, traction batteries or suspension magnets onboard. Service batteries, independent brakes and the existing station-led GoA4 architecture remain. The reference design is research only; city numerical regeneration, economics and physical release remain open. Historical studies retain their own recorded configurations and results.

[Project introduction](../../README.md) · [Engineering approach and current status](../../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

The generic gateway in [services/integration](../../services/integration/osr_integration/)
retains observation, historian, alarm, review and ERP identity functions. The
[current Workbench](../../docs/workbench/current/index.html) is a read-only v0.6
engineering viewer; the [maglev Workbench](../../docs/workbench/maglev/index.html)
is retained research. Neither is a commissioned operating control connection.

The [Docker composition](compose.yaml) describes the gateway and FUXA services.
Private credentials and existing local deployment records remain under
`var/supervision/`; this repository cleanup does not replace them. Live business
platform commissioning, authenticated device bindings, ERP permissions and
reviewed imports require a separately configured deployment. No automatic city
asset import or physical activation is provided by the current design runner.

Current [v0.6 research delivery packages](../../docs/design-engine/coupled-railway/delivery-index.json)
link stock, process/assembly records and disabled ERP drafts to their body and
railway identities. Historical city manufacturing plans retain their original
candidate scope. None supplies qualified production instructions or an accepted
MBOM. The planning adapter does not invent cycle times or release records.
Production method metadata requires explicit current-family qualification claims,
review references and exact source/product hashes. The gateway checks consistency;
external authentication and engineering adequacy remain separate requirements.

Run the offline boundary check with:

```bash
tools/automation/osr-python deployment/supervision/tests/verify-embedded.py
```

The retained native ERP/FUXA scripts require an independently configured live
instance and private credentials. Their presence does not establish current railway
commissioning or acceptance. Current verification results report only checks that
actually executed; physical and manufacturing release remain open.
