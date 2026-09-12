# Engineering Integration and Assurance

This domain combines reusable design sources with city alignment and accepted
engineering inputs. It owns analysis and exchange evidence, not the canonical
component geometry.

| Area | Contents |
|---|---|
| [`analysis/analysis-register.toml`](analysis/analysis-register.toml) | Machine-readable source of truth for current analysis status and remaining evidence |
| [`analysis/`](analysis/) | Field-to-drainage/ground deployment gates, station evidence and solver inputs |
| [`interchange/`](interchange/) | Deterministic IFC4.3 and station-interchange generators; [`ifc_mesh.py`](interchange/ifc_mesh.py) converts indexed native solids into bounded, source-bound browser geometry |
| [`models/bim/reference/`](models/bim/reference/) | Public IFC, IDS, BCF, validation and coordination review set |
| [`models/digital-twins/`](models/digital-twins/) | Source-linked fabrication and construction review scenes |
| [`assurance/`](assurance/) | Formal specifications and simulation-component coverage evidence |
| [`toolchain/`](toolchain/README.md) | Pinned external engineering applications and validation commands |

Structural release calculations, surveys, ground data, supplier drawings and
jurisdictional approvals remain deployment-specific gates.

City `engineering/depot-scope/` reports reconcile the operating depot inventory
with the station BOM, reference canopy, cost allowances and initial dispatch
requirements. See the [Samawah reconciliation](../cities/catalogue/west-asia/Iraq/Samawah/engineering/depot-scope/README.md).
These reports quantify outstanding work; they do not establish equipment
placement, an installed budget or overnight stabling feasibility.
