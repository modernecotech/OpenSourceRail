# Selected vehicle residual mass completion

Candidate `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3` and selection `8e5905bc7c81d6177bbaafde81ab3a5f8cc54947c4923eb4493949566ac85cdc` retain the source ledger's accounted tare of **19,221.998 kg/car**. Candidate geometry represents **9,131.799 kg/car**. The existing positive accounting residual is **10,090.200 kg/car** across 10 accounts.

Each low/base/high case replaces that existing residual reserve with a declared 0.8×/1.0×/1.2× sensitivity. The reserve is not added again on top of the accounted tare.

| Case | Reserve sensitivity (kg/car) | Scenario tare (kg/car) | Six-car scenario tare (kg) | Change from existing tare (kg/car) |
|---|---:|---:|---:|---:|
| low (0.8×) | 8,072.160 | 17,203.958 | 103,223.749 | -2,018.040 |
| base (1.0×) | 10,090.200 | 19,221.998 | 115,331.989 | +0.000 |
| high (1.2×) | 12,108.240 | 21,240.038 | 127,440.228 | +2,018.040 |

## Account-level reserves

| Account | Existing residual (kg/car) | Low (kg/car) | Base (kg/car) | High (kg/car) |
|---|---:|---:|---:|---:|
| attachments | 180.000 | 144.000 | 180.000 | 216.000 |
| passive-bogie-pair | 1,764.182 | 1,411.345 | 1,764.182 | 2,117.018 |
| retained-comfort/HVAC | 960.000 | 768.000 | 960.000 | 1,152.000 |
| retained-comfort/body | 4,873.077 | 3,898.461 | 4,873.077 | 5,847.692 |
| retained-comfort/doors | 98.767 | 79.013 | 98.767 | 118.520 |
| retained-comfort/frame-joints | 202.739 | 162.191 | 202.739 | 243.287 |
| retained-comfort/glazing | 20.482 | 16.385 | 20.482 | 24.578 |
| retained-comfort/seating | 598.144 | 478.515 | 598.144 | 717.773 |
| roof-thermal | 47.809 | 38.247 | 47.809 | 57.371 |
| services | 1,345.000 | 1,076.000 | 1,345.000 | 1,614.000 |

## Provisional component completion

The completion routine partitions all 10 positive residual accounts into 28 source-linked or explicitly provisional component packages. The base case replaces each existing account balance exactly; no package is added on top. Candidate `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3` and selection `8e5905bc7c81d6177bbaafde81ab3a5f8cc54947c4923eb4493949566ac85cdc` bind the estimates.

The package-cost ranges are Class C factory-gate calculations from the dated Iraqi rate dataset plus declared process, burden, yield, QA, overhead and equipment proxies. They exclude delivery, final vehicle installation, commissioning and field civil works. Costs are reported per account because overlaps remain unresolved; they are not summed into a new train total or added to the 112-bundle corridor model. Use the account components only as a replacement for their matching aggregate account estimate.

Production uses 2 eight-hour shifts/day at 75% productive utilisation. The same cost basis retains two civil shifts/day and operating cases of 2, 2, 3 shifts/day, including the eventual three-shift operations case. Process hours are labour-hour estimates, not an elapsed production schedule; crew size, concurrent cells, precedence, tooling capacity and procurement lead times remain open.

| Residual account | Base mass (kg/car) | Packages | Base factory labour (h/car; six-car) | Class C factory-gate cost (IQD/car, low/base/high) | Six-car base cost (IQD) | Overlap review |
|---|---:|---:|---:|---:|---:|---|
| attachments | 180.000 | 1 | 14.4; 86.4 | 3,292,740 / 18,866,520 / 102,477,960 | 113,199,120 | unresolved |
| passive-bogie-pair | 1,764.182 | 1 | 141.1; 846.8 | 32,272,177 / 184,910,950 / 1,004,387,504 | 1,109,465,700 | unresolved |
| retained-comfort/HVAC | 960.000 | 1 | 76.8; 460.8 | 17,561,280 / 100,621,440 / 546,549,120 | 603,728,640 | unresolved |
| retained-comfort/body | 4,873.077 | 2 | 389.8; 2,339.1 | 89,143,192 / 510,766,662 / 2,774,349,776 | 3,064,599,970 | unresolved |
| retained-comfort/doors | 98.767 | 2 | 7.9; 47.4 | 1,806,740 / 10,352,136 / 56,230,071 | 62,112,815 | unresolved |
| retained-comfort/frame-joints | 202.739 | 8 | 231.1; 1,386.4 | 1,671,935 / 9,535,515 / 62,492,649 | 57,213,090 | unresolved |
| retained-comfort/glazing | 20.482 | 3 | 6.4; 38.3 | 109,474 / 727,959 / 5,493,624 | 4,367,755 | unresolved |
| retained-comfort/seating | 598.144 | 2 | 47.9; 287.1 | 10,941,853 / 62,693,892 / 340,536,684 | 376,163,352 | unresolved |
| roof-thermal | 47.809 | 1 | 14.4; 86.5 | 282,177 / 1,925,575 / 13,924,073 | 11,553,448 | unresolved |
| services | 1,345.000 | 7 | 107.6; 645.6 | 24,604,085 / 140,974,830 / 765,738,090 | 845,848,980 | unresolved |

### Component proposals

| Account | Component proposal | Base mass (kg/car) | Material family | Provisional process route | Base cost (IQD/car) |
|---|---|---:|---|---|---:|
| attachments | Body/bogie joints, fin-retention and thermal-joint reserve | 180.000 | finished-equipment | prepare joint, fin-retention and thermal-interface stock; cut, drill, form or mould metal/composite parts; fit isolation and fastener stacks to a reviewed joint detail; inspect torque, bond and maintenance access | 18,866,520 |
| passive-bogie-pair | Passive bogie frames, wheelsets, bearings, suspension and brakes reserve | 1,764.182 | finished-equipment | fabricate bogie frames and crossmembers; machine or procure wheelsets, axles and axleboxes; fit bearings, suspension and independent brakes; assemble, gauge, inspect and run-in the bogie pair | 184,910,950 |
| retained-comfort/HVAC | Supplier-reference HVAC package | 960.000 | finished-equipment | procure or obtain a bounded equipment estimate; receive and inspect; define mounting and service interfaces; bench or fit-check the package | 100,621,440 |
| retained-comfort/body | Inherited unlocated body, services, interior, cooling, electronics and contingency reserve | 4,778.254 | finished-equipment | separate the inherited reserve into equipment and fitout packages; procure catalogued equipment and locally fabricate supports or trim; assemble wiring, ducts, panels and interior fixtures at reviewed interfaces; inspect and record package mass and function | 500,827,890 |
| retained-comfort/body | Unmatched inherited body-account balance; disaggregation and overlap review required | 94.823 | finished-equipment | partition the account balance into non-overlapping parts; assign materials and make/buy routes; generate geometry and assembly interfaces; inspect and record component masses | 9,938,772 |
| retained-comfort/doors | Wabtec 1300 mm door-operator reference package | 82.000 | finished-equipment | procure or obtain a bounded equipment estimate; receive and inspect; define mounting and service interfaces; bench or fit-check the package | 8,594,748 |
| retained-comfort/doors | Door-leaf edges, seals, guides and fixings closure reserve | 16.767 | finished-equipment | trim and finish leaf edges; fit seals, guides and fixings; match the leaf to the operator envelope; cycle and inspect the assembled door | 1,757,388 |
| retained-comfort/frame-joints | GFRP hardpoint isolators | 6.019 | gfrp | cut GFRP sheet or laminate; finish edges and holes; bond or mechanically retain; inspect dimensions | 269,504 |
| retained-comfort/frame-joints | Roof-spreader plate stock | 102.643 | aluminium | cut or blank plate; form or machine interface; deburr and join; dimensional inspection | 3,863,249 |
| retained-comfort/frame-joints | GFRP joint-isolation pads | 5.928 | gfrp | cut GFRP sheet or laminate; finish edges and holes; bond or mechanically retain; inspect dimensions | 386,037 |
| retained-comfort/frame-joints | M8 head-and-nut stock envelopes | 7.541 | steel | purchase steel stock; cut or machine fastener envelope; apply corrosion protection; inspect thread and fit | 784,621 |
| retained-comfort/frame-joints | M8 bolt shanks | 12.311 | steel | purchase steel stock; cut or machine fastener envelope; apply corrosion protection; inspect thread and fit | 907,951 |
| retained-comfort/frame-joints | Joint bond film | 1.248 | adhesive | select compatible adhesive; meter and apply; cure under controlled conditions; inspect bond witness samples | 188,670 |
| retained-comfort/frame-joints | Crush sleeves | 22.121 | steel | purchase steel stock; cut or machine fastener envelope; apply corrosion protection; inspect thread and fit | 1,161,573 |
| retained-comfort/frame-joints | Frame-joint gusset plates | 44.928 | aluminium | cut or blank plate; form or machine interface; deburr and join; dimensional inspection | 1,973,912 |
| retained-comfort/glazing | EPDM glazing seal stock | 6.528 | elastomer | cut or mould seal stock; prepare retaining groove; fit and splice; inspect continuity | 216,901 |
| retained-comfort/glazing | Glazing bond allowance | 2.938 | adhesive | select compatible adhesive; meter and apply; cure under controlled conditions; inspect bond witness samples | 98,229 |
| retained-comfort/glazing | Aluminium glazing retention stock | 11.016 | aluminium | cut or blank plate; form or machine interface; deburr and join; dimensional inspection | 412,829 |
| retained-comfort/seating | Inherited unlocated interior and seating reserve | 541.706 | finished-equipment | separate the inherited reserve into equipment and fitout packages; procure catalogued equipment and locally fabricate supports or trim; assemble wiring, ducts, panels and interior fixtures at reviewed interfaces; inspect and record package mass and function | 56,778,384 |
| retained-comfort/seating | Seat supports, back supports, upholstery, bonds and fixings closure reserve | 56.438 | finished-equipment | fabricate or procure seat supports and back supports; fit upholstery, bonds and fasteners; assemble modules at saloon interfaces; proof-load and inspect fixtures | 5,915,508 |
| roof-thermal | White roof coating takeoff | 47.809 | coating | prepare roof surface; apply declared coating thickness; cure; inspect coverage and adhesion | 1,925,575 |
| services | Toshiba SCiB Type3-20 FM01202CCA04A | 1,050.000 | finished-equipment | procure or obtain a bounded equipment estimate; receive and inspect; define mounting and service interfaces; bench or fit-check the package | 110,054,700 |
| services | enclosure and module racks | 135.000 | finished-equipment | procure or obtain a bounded equipment estimate; receive and inspect; define mounting and service interfaces; bench or fit-check the package | 14,149,890 |
| services | DC protection, monitoring and busbars | 45.000 | finished-equipment | procure or obtain a bounded equipment estimate; receive and inspect; define mounting and service interfaces; bench or fit-check the package | 4,716,630 |
| services | cooled enclosure circuit and heat exchanger | 55.000 | finished-equipment | procure or obtain a bounded equipment estimate; receive and inspect; define mounting and service interfaces; bench or fit-check the package | 5,764,770 |
| services | isolated service DC/DC and low voltage supplies | 30.000 | finished-equipment | procure or obtain a bounded equipment estimate; receive and inspect; define mounting and service interfaces; bench or fit-check the package | 3,144,420 |
| services | station charge connector and isolation | 20.000 | finished-equipment | procure or obtain a bounded equipment estimate; receive and inspect; define mounting and service interfaces; bench or fit-check the package | 2,096,280 |
| services | isolation and retention mounts | 10.000 | finished-equipment | procure or obtain a bounded equipment estimate; receive and inspect; define mounting and service interfaces; bench or fit-check the package | 1,048,140 |

Dimensions and installed positions remain explicitly open. Known-density values produce only mass-equivalent material volume, never a geometric envelope. Equipment and inherited balances use Class C mass-based estimates. The body account includes inherited services/interior/cooling/electronics/contingency, so its cross-account overlap with separately named systems remains unresolved. The 180 kg attachment reserve can overlap frame joints, bogie interfaces and roof treatment. Component packages therefore replace only their own account and must not be summed across those overlaps as independent installed mass.

Not added to the 112-bundle city model. These selected-candidate component estimates are a decomposition/replacement view; integrating them requires suppressing the corresponding aggregate account cost lines and closing cross-account overlap first.

## Scope and evidence

This is a provisional sensitivity of the existing selected-candidate mass account. The low/base/high factors are declared scenarios, not probability bounds. Positive residuals are replaced within each scenario; they are not added twice. Equipment, joint, fastener, cooling, wiring, and installation identities/locations remain open where the source worksheet has no physical component evidence.

The two accounts with no accounting residual reconcile to represented geometry mass; this does not prove installation or reserve additional physical joints, fasteners and interfaces. The account totals therefore remain incomplete as an installed inventory.

The 0.8×/1.0×/1.2× factors are sensitivity assumptions only. They are not statistical confidence limits or supplier-confirmed ranges. Replace them with component-specific calculated mass or measured procurement/installation evidence when available.

The selected reference, CAD, and release states are unchanged. Centre of gravity, inertia, axle reactions, and complete installed mass remain unknown.

Reproduce with `python3 -m engineering.mass_reserve_sensitivity build` and `python3 -m engineering.mass_reserve_sensitivity verify`.

[Exact result](result.json) · [Manifest](manifest.json)
