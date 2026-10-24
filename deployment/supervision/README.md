# Equipment supervision and lifecycle integration

<!-- osr-system-context:start -->
OpenSourceRail develops an open, locally buildable urban railway with fixed linear motors at stations and, where needed, located boosters. Trains coast between powered zones while onboard ferrite support, guidance and passenger services remain independently powered; passengers transfer between fixed lines at junctions. Simple vehicles, repeated civil works and repairable local production aim for high useful passenger throughput and affordable construction, operation and debt repayment. Current studies and digital workflows support development; an accepted physical railway has not been established.

[Project introduction](../../README.md) · [Engineering approach and current status](../../engineering/ferrite_maglev/README.md)
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
