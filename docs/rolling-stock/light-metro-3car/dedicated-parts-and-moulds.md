# Dedicated body, chassis, fascia and interior parts

This page is the design-reference split of the LM3 body and fitout into parts
that a local factory can identify, fixture, inspect, replace and cost. It is not
a released drawing pack: material grades, laminate schedules, weld classes,
fastener values, structural calculations and supplier interfaces still pass
through their stated release gates.

## Chassis and body steel

| Product ID | Dedicated part family | Manufacturing boundary | Principal fixture/evidence |
|---|---|---|---|
| `LM3-BDY-P010` | left/right side sills | Longitudinal primary members | `LM3-TOOL-STEEL-FIXTURE`; heat and straightness trace |
| `LM3-BDY-P020` | centre spine and longitudinal load-path kit | Kept separate from transverse members until fixture load | Spine straightness and bogie-centre datum survey |
| `LM3-BDY-P021` | cross-bearers, door outriggers and equipment brackets | Nested and station-marked repeated transverse parts | Cross-bearer profile gauge, station map and tack survey |
| `LM3-BDY-P030` | bolster boxes, spring pads and pivot inserts | Machined datum set after qualified weld | Line-bore/NDT and spring-datum survey |
| `LM3-BDY-P060` | low-floor centre pan and service-floor supports | Low saloon floor and removable equipment access | PRM-height, aisle and pan-weld inspection |
| `LM3-BDY-P061` | raised bogie-end decks, transition ramps and hatch frames | Two removable end-zone sets per car | Deck/transition gauge and hatch-removal trial |
| `LM3-BDY-P070` | side posts, door portals, waist and cant rails | Two side frames per car | Door/window gauges and side-frame survey |
| `LM3-BDY-P080` | roof bows and equipment/cable rails | Structural roof datum below removable skins | HVAC/PV pitch and bracket proof evidence |

The steel frame remains the certified crash, buff, passenger, bogie, battery,
jacking and recovery load path. GFRP, liners, film and fairings never substitute
for these members.

## One-metre exterior part family

The 144-module trainset count is retained, but the engineering tree no longer
hides all four variants in one line.

| Product ID | Variant | Reference quantity/trainset | Controlled distinction |
|---|---|---:|---|
| `LM3-BDY-P130` | solid side | 48 | Unpierced side/weather panel; final mix follows the bay map |
| `LM3-BDY-P131` | window edge | 24 | Sealed reveal edge, window drain and cassette-removal clearance |
| `LM3-BDY-P132` | door edge | 24 | Door-pocket closeout, threshold drain and door-service sweep |
| `LM3-BDY-P133` | roof skin/fairing | 48 | HVAC, PV, antenna, access and drain trim variants |

All variants retain the 1,000 mm mould pitch, 994 mm finished width, clip datum,
independent anti-lift retainer, 6 mm dry EPDM joint and master-frame dry fit.
Production quantities are configuration-controlled by the final door/window bay
map; the four reference quantities sum to 144.

## Interior fitout split

| Product ID | Serviceable part family | Must remain accessible |
|---|---|---|
| `LM3-INT-P020` | main ceiling liners | Light, diffuser, detector and service apertures |
| `LM3-INT-P021` | light-trough bezels and diffuser carriers | Plug-in main and independent emergency lights |
| `LM3-INT-P022` | HVAC transitions, detector bezels and ceiling hatches | Air balance, detectors, cables and drain inspection |
| `LM3-INT-P030` | main sidewall liners | Side structure and window interface |
| `LM3-INT-P031` | four-piece window reveals | Glass edge, setting blocks and complete cassette removal |
| `LM3-INT-P032` | waist cable covers and LV/data access lids | Segregated harnesses and retained service loops |
| `LM3-INT-P040` | battery-strake covers | HV barrier labels and exterior-only pressure relief |
| `LM3-INT-P041` | seat-base fairings and equipment hatches | Structural seat saddles, isolation and cleaning access |
| `LM3-INT-P050` | vestibule kick and threshold closeouts | Door drains and threshold hardware |
| `LM3-INT-P051` | PRM transition/step covers, nosing and anti-slip pieces | Structural floor datum and trip-edge inspection |
| `LM3-INT-P052` | door-pocket liners and jamb covers | Certified door sweep, sensitive edge and emergency access |

Every interior moulding is non-structural. Seats and handrails connect through
calculated saddles and `OSR-RAIL-42`, never through the finish panel. All cabin
materials, films, adhesives and edge treatments require the project fire/smoke
evidence route.

## Fascia, panoramic glass and lamps

The six cowl casts remain `LM3-CWL-P011` through `P016`. Three dedicated fitout
kits now define what sits behind them:

| Product ID | Fitout | Design rule | Release check |
|---|---|---|---|
| `LM3-FAS-P010` | panoramic glass carrier, setting-block pockets and secondary retention | Transfers pane loads to the steel-backed ring; cowl skin is not structural | Carrier survey, edge-clearance gauge, retention proof and pane-removal trial |
| `LM3-FAS-P020` | reversible lamp cassette tray and aiming adjusters | Same physical end kit leads or trails; service hatch removal must not lose datum | Lamp gauge, aim/retention, harness clearance and removal trial |
| `LM3-FAS-P030` | EPDM seals, drain rail, washer sleeves and edge closeouts | Replaceable weather boundary with visible earths/connectors | Seal batch, compression map, drain flow and water test |

The panoramic glass supplier still owns glass construction, heater/busbar and
its adhesive or cassette process. The lamp supplier owns photometry, EMC/IP and
thermal evidence. The OSR parts own the repeatable mechanical datums and the
ability to remove either system without destroying the cowl.

## Dedicated mould and fixture set

| Tool ID | Purpose |
|---|---|
| `LM3-TOOL-SIDE-MOULD` | common 1 m side-module female surface |
| `LM3-TOOL-SIDE-VARIANT-NEST` | solid/window/door CNC trim and drill variants |
| `LM3-TOOL-ROOF-MOULD` | common 1 m roof skin surface |
| `LM3-TOOL-ROOF-FAIRING-MOULD` | HVAC curb, PV gland, antenna and hatch inserts |
| `LM3-TOOL-COWL-MOULD` | split brow, cheek, apron, hatch and backing-flange mould family |
| `LM3-TOOL-GLASS-CARRIER-NEST` | glass carrier, seal compression, sill drain and setting-block gauge |
| `LM3-TOOL-LAMP-AIM` | reversible cassette datum and photometric target carrier |
| `LM3-TOOL-INT-CEILING-MOULD` | ceiling, light and HVAC aperture family |
| `LM3-TOOL-INT-SIDE-MOULD` | sidewall, window reveal and waist-cover family |
| `LM3-TOOL-INT-STRAKE-MOULD` | battery strake, seat fairing and hatch family |
| `LM3-TOOL-INT-DOOR-PRM-MOULD` | vestibule, PRM/step and door-pocket family |

First-article MDF/epoxy or sealed machined-foam patterns are acceptable only
when the released resin/process permits them. Production visible surfaces use
female tools, removable inserts and CNC trim nests. A mould drawing must fix
draft, split lines, trim curves, flange returns, insert locations, vacuum/resin
ports, cure support and a dimensional inspection method.

## Assembly handoff

1. Release and survey the underframe, floor, side and roof structural datums.
2. Dry-build the four exterior variants on the master frame; prove clips,
   anti-lift devices, seals, drains and window/door service sweeps.
3. Build the six cowl casts, glass carrier and lamp tray on the end fixture;
   prove A/B interchange before fitting glass or lamps.
4. Pre-fit all interior panels on the bare service rails; demonstrate every
   window, light, HVAC, cable, seat-base and door service path.
5. Apply the controlled finish system, install bought-in equipment, complete
   water/rattle/functional tests, and attach signed evidence to the serialized
   car configuration.
