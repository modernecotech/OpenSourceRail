# Standards and evidence for railway decisions

Use this register to see how OpenSourceRail's design, software, procurement and asset
records support recognised railway and management-system practices. For each mapped
control, the crosswalk gives the standard and edition, whose design the evidence describes,
the risk, the available evidence and the open decision. It can support a funding review,
supplier enquiry or assessment plan. Project applicability and acceptance remain open in
the published register.

- [Read the standards and evidence crosswalk](compliance-matrix.md).
- [Download the machine-readable evidence graph and SHA-256 hashes](digital-assurance-report.json).
- [Review or amend the source register](standards.toml).

## What operators and funders can check

| Decision | Where to look |
|---|---|
| Can the proposed service handle degraded conditions? | **RAMS-01** and **SIG-01** connect the lifecycle and signalling evidence to the operating study, station cycle and fault tests. Obtain project acceptance criteria and hardware and site demonstration records before accepting the associated risks. |
| Will passengers be protected during boarding and evacuation? | **ACCESS-01** and **POWER-01** identify the door and platform studies, supply and return-path assumptions, and the open clearance, earthing and isolation work. |
| Can a supplier price and deliver an identifiable item? | **CIV-01**, **QMS-01** and **LAB-01** show the construction basis, candidate revision, inspection steps and required first-article test evidence. |
| Can the operator take over and maintain the railway? | **ASSET-01** and **BIM-01** show the serial history, priced renewals and IFC export identities. Agree the maintenance and as-built information requirements with the recipient. |

The references are a starting point for adoption. ISO 22163:2023 still references
ISO 9001:2015 in its published railway QMS basis. Record how the buyer or certification body
applies that dated reference alongside the newer general quality standard. Similarly,
the IFC4 sample files demonstrate exchange within the ISO 16739 family. Check the file
schema and delivery requirements before accepting an exchange to ISO 16739-1:2024.
[ISO 22163 and its amendment](https://www.iso.org/standard/79427.html) ·
[ISO 9001 edition history](https://www.iso.org/standard/9001) ·
[IFC schema record](https://www.iso.org/standard/84123.html)

## Use on a specific railway

1. Identify the corridor, candidate and evaluation revision, software build, interfaces,
   operating conditions, owner and decision sought. The Airport enquiry receipts and twin
   model register show how to retain those identities.
2. Agree jurisdiction, governing law, contract and funder requirements, applicable editions
   and any national adoptions or annexes. Name the duty holder and assessment route. Record
   the basis for each applicability decision.
3. With access to the applicable standard, record the clause identifier and a locally
   authored obligation summary. Assign it to an OSR control, hazard or requirement and
   record the verification method, acceptance limit and competent reviewer.
4. Attach exact raw results, test article identity, instruments, calibration records and
   signed reviews. Use the repository evidence to plan what can be compared and what
   needs inspection, a physical test or an organisational audit.
5. Record who accepted which decision, against which evidence and with what conditions
   of use. A budgetary quotation, fabrication release and operating authorisation each
   require the evidence appropriate to that decision. When evidence changes, revisit
   the affected requirements and decisions.

Use one line per applicable obligation in the deployment register. For example,
an operator considering **POWER-01** can enter the adopted IEC 62128-1 reference,
the traction section and drawing revision, the earthing or isolation obligation,
the verification procedure and approved limits, and the person responsible for
the signed results. Keep the disposition open while the utility and site data are
pending. The working register should also record the decision requested, the
responsible reviewer and any use restrictions.

An evidence graph hash identifies the file bytes reviewed. Test source, recorded
digital results, manufacturer data and physical measurements have different authority.
The checker verifies mapping and file integrity. The responsible organisations
own applicability, conformity and release decisions.

## Reproduce and review changes

Run from the repository root with Python 3.11 or later.

```sh
python3 -m engineering.assurance.standards --check
python3 -m engineering.assurance.standards --impact
python3 -m engineering.assurance.standards --write
```

Use **--impact** before refreshing the outputs. It identifies controls whose evidence
bytes, mapping or publisher reference changed since the published report. Missing
evidence stops compilation. If the publisher review is due, verify the editions and
adoptions before updating the source dates. CI checks that the published Markdown and
JSON match the current source. Check the status of the underlying evaluation or test
separately before relying on its result.

## Earlier editions and restored functions

The earlier compiler mapped standards to the former component inventory, preliminary
failure-mode screens and component release gates. Its report and evidence are bound to
that edition. This register restores evidence mapping and change impact for current
sources. The old item-by-item screens remain available for reproducing the earlier
study. [Former digital standards workflow](https://github.com/modernecotech/OpenSourceRail/blob/298d4e15fbcbcd923d7fcf7e519ebc4915ef7e1b/docs/certification/digital-standards-adherence.md) ·
[Former component assurance register](https://github.com/modernecotech/OpenSourceRail/blob/298d4e15fbcbcd923d7fcf7e519ebc4915ef7e1b/docs/certification/component-assurance-register.md)
