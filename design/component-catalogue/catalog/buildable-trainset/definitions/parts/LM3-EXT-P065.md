# LM3-EXT-P065 — CCTV camera, passenger intercom, PoE/data, and mounting kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-INT-SA330` |
| Procurement BOM lines | `B19`, `E15` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Replaceable cameras and intercoms use keyed connectors and common adapters while preserving coverage, privacy and accessible call locations.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-PASSENGER-LUMINATOR` — [Luminator Technology Group rail passenger information, video and communication systems](https://luminator.com/rail/railkom)
- Procurement state: `rfq-required`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Use open Ethernet/IP interfaces and OSR mounting adapters so displays, cameras, audio and intercoms can be substituted individually after EMC, cybersecurity, accessibility and system regression tests.
- Known fit gaps: Exact display, camera, amplifier, intercom, recorder and software licences remain to be selected.
- Mandatory equivalence:
  - same or better released fit, mounting datums, connector keying and service envelope
  - same or better mass, load, duty-cycle, thermal, electrical and environmental ratings
  - same or better functional safety, fire, EMC, cybersecurity and applicable rail evidence
  - documented failure modes, maintenance intervals, spares and obsolescence route
  - first-article inspection plus component, subassembly and vehicle regression tests
  - signed design-authority substitution record preserving the original anchor and evidence hashes

## Material specification

| Field | Value |
|---|---|
| Material family | rail-rated CCTV/passenger-intercom equipment kit |
| Grade / part class | serialised display/camera/intercom/audio modules, keyed power/data connectors, fire-rated harness tails, common-rail adapters and captive service fasteners |
| Governing standard | supplier rail electronics specification plus project fire/smoke, EMC, IP, cybersecurity/configuration, accessibility and lifecycle evidence |
| Form factor | plug-in line-replaceable modules with labelled connectors, strain relief, bend-radius/service loops and no hidden joints behind fixed trim |
| Nominal section | field of view/visibility/reach, mounting envelope, connector keying, heat rejection and service clearance fixed by LM3-INT-230 interface drawings |
| Finish / protection | cleanable tamper-resistant passenger finish, sealed penetrations, galvanic/electrical isolation and protected labels |
| Traceability | equipment serial, hardware/firmware/configuration revision, harness batch, adapter position, network address and functional-test record |

Evidence required:

- certificate of conformity
- incoming inspection record
- fire/EMC/IP evidence
- network enumeration
- coverage/intelligibility test
- timed module replacement

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, fire/EMC/IP evidence, network enumeration, camera coverage/privacy review, intercom call and service-removal trial
- Tooling basis: RFQ-LM3-EXT-P065, CERT-LM3-EXT-P065, GAUGE-LM3-EXT-P065-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- fire/EMC/IP evidence
- network enumeration
- camera coverage/privacy review
- intercom call and service-removal trial

## Source references

- `cots_equipment.py`
- `bom-skeleton.md B19`
- `LM3-INT-230`
