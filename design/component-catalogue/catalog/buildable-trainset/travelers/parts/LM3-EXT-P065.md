# Shop traveler — LM3-EXT-P065 — CCTV camera, passenger intercom, PoE/data, and mounting kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.8 h |
| Route | `SOURCE` |
| Procurement BOM lines | `B19`, `E15` |

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


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-EXT-P065-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-EXT-P065-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-EXT-P065-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-EXT-P065`<br>`DOC-LM3-INT-SA330` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-EXT-P065`<br>`CERT-LM3-EXT-P065` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-EXT-P065-ENVELOPE`<br>`FIX-LM3-INT-SA330` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: fire/EMC/IP evidence | quality inspection | 0.25 | `QA-LM3-EXT-P065` | fire/EMC/IP evidence | quality inspector |
| 50 | verify acceptance gate: network enumeration | quality inspection | 0.25 | `QA-LM3-EXT-P065` | network enumeration | quality inspector |
| 60 | verify acceptance gate: camera coverage/privacy review | quality inspection | 0.25 | `QA-LM3-EXT-P065` | camera coverage/privacy review | quality inspector |
| 70 | verify acceptance gate: intercom call and service-removal trial | quality inspection | 0.25 | `QA-LM3-EXT-P065` | intercom call and service-removal trial | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-EXT-P065`<br>`KIT-LM3-INT-SA330` | item is released, tagged, and staged for parent assembly | cell lead |

## Operator / inspection signoff block

| Role | Name | Date | Signature | Status |
|---|---|---|---|---|
| operator |  |  |  | `blank` |
| cell lead |  |  |  | `blank` |
| quality inspector |  |  |  | `blank` |
| manufacturing engineer |  |  |  | `blank` |

## Nonconformance / deviation log

| NCR / deviation ID | Operation seq | Disposition | Approver | Closure date |
|---|---:|---|---|---|
|  |  |  |  |  |
