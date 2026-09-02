# Depot thermal and fire mitigation work packages

Generated from [`mitigation-work-packages.toml`](mitigation-work-packages.toml),
which is the canonical owner/evidence/closure register.

**Design response:** Keep charger power stages and stationary storage in a physically separated outdoor/open-sided energy compound; keep controls and switchgear in a separate room with 2 x 30 kW packaged DX cooling (one duty, one standby).

> The deterministic comparison supports layout development only. No package closes without project inputs, signed supplier evidence and competent local approval.

| ID | Package | Owner role | Related products | State |
|---|---|---|---|---|
| `STN-MIT-001` | Charger and battery supplier evidence freeze | depot electrical lead | `STN-DEP-P040`, `STN-DEP-P050` | `open-deployment` |
| `STN-MIT-002` | Energy-compound site and fire-strategy release | architect/engineer of record and fire engineer | `STN-DEP-P010`, `STN-DEP-P040`, `STN-DEP-P050` | `open-deployment` |
| `STN-MIT-003` | Controls-room cooling detailed design | mechanical services lead | `STN-DEP-P070` | `open-deployment` |
| `STN-MIT-004` | Energy-compound detection and protection integration | electrical and fire systems leads | `STN-DEP-P040`, `STN-DEP-P050`, `STN-DEP-P070` | `open-deployment` |
| `STN-MIT-005` | Factory and site acceptance evidence | depot commissioning manager | `STN-DEP-P040`, `STN-DEP-P050`, `STN-DEP-P070` | `open-deployment` |
| `STN-MIT-006` | Independent review and operating handover | operator design authority | `STN-DEP-SA850` | `open-deployment` |

## Evidence required

### `STN-MIT-001` — Charger and battery supplier evidence freeze

- selected manufacturer/model and controlled datasheets
- maximum-ambient derating and charger loss/duty map
- cell-to-pack propagation and credible heat-release data
- fault response, remote isolation and maintenance clearances

### `STN-MIT-002` — Energy-compound site and fire-strategy release

- surveyed compound location and code-compliant separation distances
- wind-sensitive fire/smoke cases and occupied-building exposure assessment
- outward access, fencing, emergency response and firefighting provisions
- spill/firewater drainage, containment and environmental approval

### `STN-MIT-003` — Controls-room cooling detailed design

- project weather and envelope model
- selected 2 x 30 kW units with site-ambient derating
- duty/standby controls, high-temperature alarm and loss-of-cooling response
- refrigerant, condensate, maintainability and power-failure design

### `STN-MIT-004` — Energy-compound detection and protection integration

- detection technology and coverage drawings
- cause-and-effect matrix including alarm, charger abort and remote isolation
- protection coordination, earthing and emergency-stop design
- interface test procedure with OCC and depot maintenance systems

### `STN-MIT-005` — Factory and site acceptance evidence

- charger, battery and cooling FAT records
- installed thermal-load and duty/standby changeover test
- alarm, abort, isolation and loss-of-comms test
- fire-system integrated test witnessed by the approving parties

### `STN-MIT-006` — Independent review and operating handover

- closed design comments and statutory approvals
- approved emergency and degraded-operation procedures
- as-built model, asset register, spares and maintenance plan
- training, drill and operator acceptance records
