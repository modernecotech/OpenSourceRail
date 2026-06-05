# RFC 0027 — Brownfield Pilot: Existing-Asset Recovery & Workshop Integration

**Status:** Draft — proposed
**Date:** 2026-04-26
**Depends on:** [RFC 0003 Samawah Reference Deployment](0003-samawah-reference-deployment.md), [RFC 0008 Rolling-Stock Reference Design](0008-rolling-stock-reference-design.md), [RFC 0014 Depot Design Standard](0014-depot-design-standard.md), [RFC 0022 Bogie + Traction Drive](0022-bogie-traction-drive.md), [RFC 0025 DIY Switch and Point-Machine](0025-diy-switch-and-point-machine.md)

## 1. Summary

Most OSR target countries — Iraq, Sudan, Pakistan, Mozambique, Angola,
Venezuela, several CIS states — already own large quantities of
**dormant Soviet-era / British-era / American-aid-era rolling stock
and rail workshops**, mostly stored or partially functional. RFC 0003
(Samawah reference deployment) is the worked example: satellite
imagery identifies **300–800 wagons stored in the rail yards adjacent
to Samawah Train Station**, plus a rolling-stock workshop building
(historically the target of a 2011 Iranian Waxon Park rehabilitation
deal whose outcome is unclear).

Stored fleet + dormant workshop + active mainline through the city
makes Samawah a **brownfield pilot** rather than a greenfield one. This
RFC commits a systematic doctrine for converting brownfield assets
into OSR-compatible production capacity, and is intended to apply to
every deployment that begins with an existing asset stockpile.

The doctrine has three phases:

| Phase | Scope | Duration |
|---|---|---|
| **P1 — Asset assessment** | Site visit, fleet inventory, workshop tooling audit, bogie/wheelset NDT sample, IRR/national-rail-authority disposition negotiation | 3–6 months |
| **P2 — Component recovery** | Strip 50–100 wagons for bogies, wheelsets, brake hardware, fasteners, couplers; sell scrap steel; train workforce on the strip operation | 6–12 months |
| **P3 — First-article OSR trainset** | Build OSR bogie frame (RFC 0022 §2.2) + wheelset recovered in P2, OSR car body (RFC 0008 Track A or B), commission at the rehabilitated workshop. Workshop becomes the regional rolling-stock factory. | 12–24 months |

**This RFC does NOT replace any greenfield-spec RFC.** It runs in
parallel to RFC 0008 / RFC 0014 / RFC 0022. Where a deployment has no
brownfield assets, the greenfield path remains the default. Where it
has them, this RFC is the contract for converting them.

## 2. Non-goals

- **Not a wagon-acquisition policy.** The legal framework for buying,
  leasing, or jointly operating recovered wagons is per-deployment
  and lives in RFC 0029 (operator-financial model, separate).
- **Not a replacement for RFC 0008.** OSR rolling stock is still the
  light-metro / metro families per RFC 0008 §1. Recovered wagons are
  **donor stock** — the OSR trainset is built fresh, using recovered
  components.
- **Not a heritage-preservation effort.** Wagons that are
  historically significant should be retained for museum/preservation
  use; this RFC's scope is the operationally serviceable bulk
  remainder.

## 3. Why brownfield pilots beat greenfield where assets exist

| Asset class | Greenfield CAPEX | Brownfield CAPEX | Saved |
|---|---|---|---|
| **Wheelsets** (760 mm forged, refurbished) | $2 800–4 200 / pair (RFC 0022 §10 tier-2 sourcing) | $300–800 / pair (NDT + reprofile) | ~$2 500 / pair × 4 pairs / consist = **~$10 k / consist** |
| **Bogie machine tools** (CNC mill 4 m, jig table, MAG welder bay, plasma cutter) | $400 k–700 k for greenfield switch shop (RFC 0025 §3.1) | $50–200 k for tool refurbishment + commissioning at existing workshop | **~$250–500 k per shop** |
| **Workshop building** (10 000 m² portal-frame industrial shed, pit tracks, traverser foundations, crane gantries) | $5–8 M for greenfield depot (RFC 0014) | $0.5–2 M for rehabilitation of dormant workshop | **~$3–6 M per workshop** |
| **Rail-grade structural steel** (recoverable from non-restorable wagon bodies) | $1 100–1 400 / t (RFC 0009 sourcing) | $150–250 / t scrap-recovery cost | **~$900 / t × ~5 t / wagon × 200 wagons = ~$900 k** |
| **Coupler / brake hardware** (SA-3, vacuum / air-brake fittings) | $5 k–12 k / unit | $200–500 / unit (refurbish or scrap) | Highly site-specific |
| **Trained workforce** (rail mechanical fitters, welders, machine operators) | 18–24 months training pipeline (RFC 0027 — workforce plan, planned) | Existing workforce continues + cross-trains on OSR-specific kit | **Salary-savings + early-deployment time-savings of 1–2 years** |

For a Samawah-scale pilot (16 trainsets, single light-metro line, one
main depot), brownfield asset recovery saves on the order of
**$8–15 M in mechanical/civil capital** plus **18–24 months of
schedule** — a meaningful fraction of the RFC 0021 §6 €435 M total
CAPEX, and an even larger fraction of the *time* budget which is
usually the binding constraint.

## 4. Phase 1 — Asset assessment (3–6 months)

### 4.1 Required deliverables

| Artefact | Owner | Scope |
|---|---|---|
| **Fleet inventory** | OSR design team + national rail authority | Wagon-by-wagon list with VIN, year, type (covered / hopper / flatbed / passenger coach), recorded last service date, structural condition (1–5 scale), owning entity, legal disposition status |
| **Workshop tooling audit** | Mechanical engineering team (local + visiting) | Per-tool register: machine type, capacity envelope, last calibration / operation date, replacement/repair cost, missing components |
| **Bogie / wheelset NDT campaign** | Independent NDT contractor | Magnetic-particle inspection on a representative ~5 % sample of stored wheelsets; ultrasonic testing on a ~2 % sample of axles. Report flaw severity per [EN 13262](https://standards.iteh.ai/catalog/standards/cen/...) class. |
| **Civil survey of workshop site** | Local civil engineering firm | Foundation condition, water/sewer connections, electrical-supply capacity, road/rail access, contamination assessment |
| **Disposition framework** | Government-relations lead | Memorandum-of-understanding draft with national rail authority covering ownership, lease terms, joint-venture options, indemnity for legacy environmental liabilities |

### 4.2 Sample budget

Phase 1 typically runs $200 k–500 k depending on stockpile size.
Major line items:

| Line item | Sample cost |
|---|---|
| Fleet-inventory team (4 engineers × 4 months on-site) | $80–120 k |
| NDT contractor (sample wheelsets / axles) | $40–80 k |
| Workshop tooling audit + civil survey | $30–60 k |
| MoU legal / negotiation support | $20–60 k |
| Per-diem, travel, equipment hire | $30–80 k |
| Contingency 20 % | $40–80 k |

This is a small fraction of the total project CAPEX and the
findings feed directly into Phase 2 / Phase 3 sizing.

## 5. Phase 2 — Component recovery (6–12 months)

### 5.1 Recovery operation

The recovery operation runs at the existing workshop, **using the
existing workforce**. Wagons are pulled into the workshop one at a
time, stripped to component level, and the components are sorted
into:

- **OSR-reusable components** (wheelsets, axleboxes, bearings, brake
  cylinders, coupler bodies, structural-steel sections, hand brakes,
  electrical contactors, lighting fixtures).
- **Resale components** (couplers + drawgear in working order go to
  freight operators in the region; HVAC and water systems if any).
- **Scrap stream** (steel body sheets, broken castings, weather-
  damaged wood).

### 5.2 Wheelset recovery — the highest-value stream

Per RFC 0022 §3, OSR uses **760 mm new / 680 mm worn** wheelsets.
Iraqi Republic Railways (IRR) and most former-Soviet-aligned
networks use **920 mm / 1050 mm** wheelsets — these are NOT
directly OSR-compatible. However, the **axleboxes, bearings,
springs, and brake gear** are reusable, and **the axles themselves
can be re-machined to OSR diameter** if their rough-bar diameter is
above the 130 mm minimum.

So the recovery yield is:
- **Wheelsets directly usable**: ~5–10 % (where rolling stock was
  already 760 mm, e.g. some passenger-coach trucks)
- **Axles re-machinable**: ~50–60 % of stored stock
- **Axleboxes / bearings / spring sets**: ~70–80 % (subject to NDT)
- **Brake hardware** (cylinders, slack adjusters): ~60–70 %
- **Couplers** (SA-3 + drawgear): ~70 % directly resaleable to legacy
  freight operators in the region

Strip rate at a properly tooled workshop is ~1 wagon per crew per
shift. With two crews and a single shift, ~10 wagons / week → 250 /
year. This is sufficient to support a 16-trainset OSR fleet at
4 wheelsets / car × 3 cars / consist × 16 = 192 wheelsets, with the
wheelset balance going to the spares pipeline and to subsequent
deployments.

### 5.3 Coupler retrofit — the catch

**OSR commits to Scharfenberg Type 10 automatic couplers** per
[RFC 0008 §3.1](0008-rolling-stock-reference-design.md). Recovered
wagons use SA-3 (former-Soviet automatic) plus screw/buffer. These
are **incompatible**, so the brownfield path **does NOT involve
re-coupling recovered wagons into the OSR consist directly**. Every
OSR car ships with new Scharfenberg couplers; the recovered SA-3
couplers go to the resale stream.

This is correct: a brownfield recovery should NOT compromise the
single-coupler-standard discipline that lets any OSR consist rescue
any other OSR consist on the network.

## 6. Phase 3 — First-article OSR trainset (12–24 months)

The recovered components feed forward into the standard OSR build
process:

| OSR component | Source from recovery |
|---|---|
| Bogie frame (RFC 0022 §2.2) | New, fabricated in the rehabilitated workshop using its CNC + welding capability |
| Wheelset (RFC 0022 §3) | Recovered axle + new (or refurbished 760 mm) wheel forging press-fit at the workshop |
| Axlebox + bearing | Recovered, NDT-passed, with new gaskets / seals |
| Primary suspension (chevron rubber) | New (RFC 0022 §5.1) — recovered rubber elements are usually weathered |
| Secondary suspension (air-spring) | New (RFC 0022 §5.2) — recovered air-spring assemblies are usually leak-prone after >5 y storage |
| Traction motor (PMSM) | New (RFC 0022 §4.1, sourced from RFC 0022 §10 tier-2 supplier) |
| Inverter (SiC) | New (RFC 0008 §3.2 DIY path or RFC 0022 §4 sourced) |
| Brake disc + caliper | New (per RFC 0022 §6) — recovered cast-iron discs are usually unsuitable for the regenerative-friction blend RFC 0021 expects |
| Body shell (alu-extrusion or steel space-frame) | New (RFC 0008 §3.1 Track A or RFC 0023 §1.1 Track B) — built in the workshop |
| Battery (Na-ion) | New per RFC 0021 |
| Electronics (DIY safety stack) | New per RFC 0019 |
| Coupler | New Scharfenberg (RFC 0008 §3.1) |
| Lighting / interior | Mix — recovered wiring harness + COTS interior per RFC 0008 §3.3 |

In other words: the brownfield component recovery yields **~30–40 %
of the per-consist mechanical mass and ~$30–60 k per consist in
saved component cost**, but the OSR architecture is preserved
verbatim. No SA-3 couplers, no 920 mm wheelsets, no Soviet-era
electrical systems on the OSR consist itself.

## 7. Workshop conversion — what stays, what goes

The Samawah workshop is presumed to have:

| Existing capability | OSR fit | Action |
|---|---|---|
| Wheelset turning / re-profiling | ✓ Direct fit | Keep + commission to RFC 0022 NDT spec |
| Bogie pit tracks | ✓ Direct fit | Keep + extend to OSR bogie wheelbase (2 100 mm — RFC 0022 §3) |
| Overhead bridge crane | △ Useful but RFC 0014 prefers stinger track | Keep where existing; RFC 0014 stinger-track is a greenfield-only choice |
| Steam + diesel locomotive shed equipment | ✗ Not applicable to OSR (battery-electric, RFC 0021) | Decommission or convert to general-purpose mechanical workshop |
| SA-3 coupler tooling | ✗ Not applicable | Decommission or repurpose for resale-stream operations |
| Air-brake testing rig | △ Compatible if convertible to electric brake | Repurpose for OSR EP-brake commissioning (RFC 0008 §3.2) |
| Wagon-frame welding line | ✓ Direct fit | Keep + commission to EN 15085 CP-C2 (the lowest rail welding class — fits the existing workforce) |
| Painting + livery shop | ✓ Direct fit | Keep + retrain on RFC 0008 §3.5 livery scheme |

The conversion isn't free — typically $0.5–2 M for the rehabilitation
itself plus $1–3 M for net-new tooling required for OSR-specific
operations (PMSM motor commissioning, SiC inverter test rigs, Na-ion
battery pack assembly). But that's an order of magnitude less than
greenfield `main-heavy` depot CAPEX of $12.0 M (RFC 0014).

## 8. Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| **Phase 1 inventory reveals stored fleet is too degraded to recover** | Medium | Phase 1 cost is bounded ($200–500 k); decision-gate at end of Phase 1 — abandon brownfield if NDT pass-rate < 30 % |
| **National rail authority refuses to negotiate disposition** | Low–medium | Pre-screen via diplomatic + technical-community channels before committing to Phase 1 |
| **Workshop legacy environmental liability** (asbestos, lead paint, fuel-tank contamination) | Medium | Civil survey in Phase 1 explicitly includes environmental scoping; remediation cost goes into the disposition negotiation, not the project budget |
| **Workforce knowledge gap on OSR-specific equipment** (SiC inverters, PMSM motors, DIY safety electronics) | High | Cross-training in Phase 2, with project-funded secondment of OSR-experienced engineers from earlier deployments. RFC 0027 (workforce plan, planned) will own this. |
| **SA-3 coupler resale market dries up** before recovery completes | Low | Resale stream is a bonus, not a critical path. Scrap value remains. |
| **Recovered axles fail post-machining NDT** | Medium | Build Phase 3 demand schedule against the **post-NDT survival rate**, not raw recovery numbers. Carry a 30 % buffer. |
| **Mid-project change of national-rail-authority leadership** delays disposition | Medium–high | MoU should commit ownership at Phase 1 close, before Phase 2 capital is exposed |

## 9. Applicability beyond Samawah

This RFC's Samawah example is illustrative. The same doctrine
applies wherever a country has:

- An active mainline running through (or near) a candidate OSR
  deployment city.
- A dormant rolling-stock stockpile of standard-gauge (1 435 mm)
  freight / passenger stock — even if the stock is otherwise
  incompatible with OSR.
- A rail workshop / depot building, even partially functional.
- A national rail authority capable of negotiating disposition.

Cities with documented brownfield potential (preliminary, not
verified):

| City | Country | Stockpile rumour / status |
|---|---|---|
| Samawah | Iraq | **Confirmed by 2026-04-26 satellite review** — 300–800 wagons, workshop building |
| Khartoum | Sudan | Sudan Railways stored fleet at Atbara workshop (Sudan Railways / Sudan Railway Workshops) |
| Karachi | Pakistan | Pakistan Railways Karachi Cantonment yard — large freight stockpile |
| Maputo | Mozambique | CFM stored fleet at Machava |
| Luanda | Angola | CFL stockpile (Caminho de Ferro de Luanda) |
| Tashkent | Uzbekistan | UTY workshops at Tashkent + significant Soviet-era stockpile |

Each of these warrants a **city-specific Phase 1 assessment** before
greenfield-vs-brownfield decision. The decision should default to
**brownfield where assets are real and recoverable**.

## 10. Open questions

1. **IRR (Iraqi Republic Railways) disposition framework** —
   ownership of stored stock, lease terms, joint-venture options for
   the Samawah workshop. Requires direct contact with the Iraqi
   Ministry of Transport (وزارة النقل) and IRR / السكك الحديد
   العراقية.
2. **Waxon Park 2011 deal outcome** — did the Iranian rehabilitation
   agreement complete? What was delivered? Is the equipment intact?
3. **Wagon-by-wagon census** — currently we have a satellite-image
   estimate of 300–800 wagons. A real census on the ground is the
   single highest-value Phase 1 deliverable.
4. **Environmental liability assessment** at the workshop — historical
   diesel + steam-loco operations may have left contamination that
   needs remediation before OSR commissioning.
5. **Legal pathway** for Iraqi (or other national) rolling-stock
   transfer to a project-controlled vehicle — sovereign-immunity,
   competition law, public-procurement compliance.

## 11. Revision history

| Date | Version | Change |
|---|---|---|
| 2026-04-26 | v0 | Stub. Three-phase doctrine (assess / recover / build), Samawah worked example, applicability matrix. Triggered by 2026-04-26 operator review identifying the Samawah rail-yard stockpile + workshop from satellite imagery. |
