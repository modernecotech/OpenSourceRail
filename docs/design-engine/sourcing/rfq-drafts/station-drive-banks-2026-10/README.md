# Station-LIM bank RFQ scope drafts — October 2026

This unsent package contains five research-candidate bank scopes for candidate `9c7d0942c9de6056e6afd051549273d0f34a72edf301fdd680ba37d12da7879f` and evaluation `1491f90b02485e6ad9df63ac79b528e9c30e9e6d87041a3dc46b02efd364077b`. It retains 2,430 exact located primary-material occurrences and links 20 unresolved completion accounts without turning them into priced package members.

## Bank scopes

| Bank | Scope ID | Located occurrences | Primary gross stock (kg) | Source material lines | Open completion accounts | Order qty | Complete bank price |
|---|---|---:|---:|---:|---:|---:|---:|
| bank/0 | `4d332bd299be31a9c0b1b6c3fc96915c113031ff8ee8e205b981bb96b5d1a797` | 486 | 4563.712 | copper-conductor, linear-steel-hypothesis | 4 | unknown | unknown |
| bank/1 | `302a4a5ecdb7b0bbc536d027524a3b8fbca153ee6889f910fa32bb52d7aaf50d` | 486 | 4563.712 | copper-conductor, linear-steel-hypothesis | 4 | unknown | unknown |
| bank/2 | `61410bc993b249d289b62c73c74f38ae5deb62017375fcef7a42ea7655fca89d` | 486 | 4563.712 | copper-conductor, linear-steel-hypothesis | 4 | unknown | unknown |
| bank/3 | `c9c4af6a6c993d7d806145573a062fa4ca958805504021c4e6e503629fd27e81` | 486 | 4563.712 | copper-conductor, linear-steel-hypothesis | 4 | unknown | unknown |
| bank/4 | `d04c781e1f7d187451621b3f65a0a9c0e36aafb7ed32f39efc266089259c900f` | 486 | 4563.712 | copper-conductor, linear-steel-hypothesis | 4 | unknown | unknown |

Each bank scope requests a separate unit response and an optional five-bank total. Internal bank grouping is not a commercial order quantity. The included mass is located gross copper/steel primary stock only; windings, converter, feeders, supports, cooling, controls, protection, access, installation and maintenance do not become zero because they are not present in the stock subtotal.

## Existing domestic fabrication estimate

The candidate-level copper line already carries an indicative raw-material + assumed labour + 20% uplift screen for all five banks: 8 h/t: IQD 90,192,658.13; 16 h/t: IQD 91,034,539.73; 32 h/t: IQD 92,718,302.93. Material uses the 2025 Iraqi HS 74081100 national CIF import unit value and labour uses the September 2026 Baghdad skilled-worker base-wage proxy. These are not per-bank allocations, winding-grade prices, supplier quotations or complete drive costs. Insulation, winding/impregnation, tooling, yield, QA, equipment, employer burden, cooling, converter, protection, installation and renewals remain unpriced.

## Required duty and test response

Return separate performance for 8 common-service cases: 1.5 km, 2 km routes crossed with empty, normal, crowd-control and adverse-normal loads. The normal comparator uses 46 people/car (44 seats plus 2 wheelchair places); the 160 people/car case is a control, not planned standing service. The adverse-normal case uses the closure campaign's declared 1.0% grade, 10 m/s headwind and 0.025 rail-adhesion hypothesis; adhesion remains in the independent wheel/brake model and is not available LIM thrust.

The response asks for the current software map fields (position, speed, current and temperature axes; thrust, electrical input, loss, voltage and vertical force), plus explicit gap sensitivity and electrical frequency/phase data. The current map adapter does not consume air-gap as an axis or frequency as a field. Those adapter gaps are stated in the packet and must be resolved before a supplier map can support a physical journey.

## Quote structure and evidence

Quote imported-complete, imported-modules/local-assembly and local-fabrication/imported-modules alternatives separately. Break out imported and local content, raw material, labour, tooling, QA/testing, delivery, installation/commissioning, spares and renewals. Return dimensions, masses, bill of materials, material grades/certificates, exact operating limits, available-force map evidence, lead time, MOQ, currency, delivery terms, warranty and maintenance requirements. No local-content percentage is assumed.

The listed Iraqi and international sources are discovery/technical leads, not compatible products, supplier offers or endorsements. No RFQ was sent. The five-bank research candidate is separate from the selected reference's approximately 900 m shared winding allocation; prices, force maps, electrical duties or civil requirements do not transfer between them.

RFQ drafts remain disabled until an authorized operator selects a supplier, approves the technical package and sends the request. Candidate selection, engineering/procurement approval, physical acceptance, complete installed cost and whole-life cost remain open.

Machine-readable bank details, exact IDs, source hashes and response fields are in [station-drive-rfq-scope.json](station-drive-rfq-scope.json); the sealed source/output hashes are in [manifest.json](manifest.json).
