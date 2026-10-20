# Engineering Integration and Assurance

v0.5 primary physical development: [ferrite-maglev adapter](ferrite_maglev/README.md), [Rust control package](../crates/osr-maglev-control/README.md) and [architecture transition](../docs/rfcs/0035-v05-primary-ferrite-maglev.md). Older physical studies remain explicit wheel/rail comparators.

This domain owns the primary maglev geometry, calculations, control coupling and city-planning adapter under `ferrite_maglev/`. Other analysis and exchange packages below retain their own configurations; the old component catalogue does not supply accepted maglev geometry.

| Area | Contents |
|---|---|
| [`ferrite_maglev/`](ferrite_maglev/README.md) | Primary magnetic/mechanical/civil studies, city planning, source-bound publication and open acceptance programme |
| [`analysis/analysis-register.toml`](analysis/analysis-register.toml) | Machine-readable source of truth for current analysis status and remaining evidence |
| [`analysis/`](analysis/) | Field-to-drainage/ground deployment gates, station evidence and solver inputs |
| [`interchange/`](interchange/) | Deterministic IFC4.3 and station-interchange generators; [`ifc_mesh.py`](interchange/ifc_mesh.py) converts indexed native solids into bounded, source-bound browser geometry |
| [`models/bim/reference/`](models/bim/reference/) | Public IFC, IDS, BCF, validation and coordination review set |
| [`models/digital-twins/`](models/digital-twins/) | Source-linked fabrication and construction review scenes |
| [`assurance/`](assurance/) | Formal specifications and simulation-component coverage evidence |
| [`baghdad_detail.py`](baghdad_detail.py) | Source-bound six-car Baghdad parts, software/ERP allocation and electronics sizing register; [design and Iraqi slab manufacture](../cities/catalogue/west-asia/Iraq/Baghdad/DETAILED-ENGINEERING.md) |
| [`assembly_design/`](assembly_design/README.md) | Source-linked Baghdad requirements, generated assembly alternatives, native correspondence and isolated capability development with independent research review; [first retained campaign](../docs/design-engine/assembly-design/index.html) |
| [`toolchain/`](toolchain/README.md) | Pinned external engineering applications and validation commands |

Structural release calculations, surveys, ground data, supplier drawings and
jurisdictional approvals remain deployment-specific gates.

City `engineering/depot-scope/` reports reconcile the operating depot inventory
with the station BOM, reference canopy, cost allowances and initial dispatch
requirements. See the [Samawah reconciliation](../cities/catalogue/west-asia/Iraq/Samawah/engineering/depot-scope/README.md).
These reports quantify outstanding work; they do not establish equipment
placement, an installed budget or overnight stabling feasibility.
