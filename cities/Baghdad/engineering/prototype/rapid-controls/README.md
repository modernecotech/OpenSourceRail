# From a CAM revision to a reviewed manufacturing record

Use this disconnected exercise to rehearse a rapid-production workcell before procuring a controller, gateway or machine. The flow matches a scanned work order, drawing and fixture revision to a specific CAM job, then records completion and inspection evidence against the same part serial. A failure holds the review record and names the field to investigate. The exercise uses the existing FreeCAD practice NC and native replay receipt for a wax coupon. The source vehicle remains at fitout and quotation maturity. [CAD/CAM package](../cam/CAM.md) · [Vehicle factory routing](../vehicle-factory/factory-routing.md)

```bash
python3 cities/Baghdad/engineering/prototype/rapid-controls/replay.py --check
python3 cities/Baghdad/engineering/prototype/rapid-controls/replay.py --case wrong-fixture
python3 cities/Baghdad/engineering/prototype/rapid-controls/test_replay.py
```

[Example review receipt and source digests](example-review.json)

## What the shop can rehearse

| Stage and role | Review evidence |
|---|---|
| Planner issues a job card | Work order and operation, part serial, material batch, physical candidate, drawing and route revisions. Freeze these on the card before sending the schedule to the cell. |
| Manufacturing engineer prepares a programme | Match the FreeCAD CAM evaluation to the native replay receipt, the post digest and exact NC bytes. Use the vehicle's nominal plate DXFs and blank frames for quotation. Establish workholding, collision clearance, tooling and machine-specific post verification for the actual steel programme. |
| Cell technician prepares the setup | Scan the fixture ID and revision, program ID and machine ID. Verify the physical references, clamps and tooling at the machine. The exercise holds a mismatched programme or fixture and flags lost, stale or reordered samples. |
| Inspection technician checks the part | Match the part serial, job, inspector and gauge calibration identifier. The example uses synthetic width and depth measurements with declared uncertainty in integer micrometres. A band inside the limits can enter training review, a band beyond the limits goes to rework review, and an overlap holds the record. |
| Quality lead reviews the record | Follow the job, source hashes and inspection from an ERPNext draft Job Card to Quality Inspection and the engineering disposition. Keep rework and reinspection attached to the same part identity. |

The built-in replay covers nine cases. Choose `--case nominal` to get a complete job, trace and result bundle. To test an edited trace, save its `trace` object as a separate JSON file and pass `--trace FILE`. Timestamps in the exercise are relative monotonic milliseconds. Sample sequences begin at one, the synthetic freshness window is 2,000 ms and every sample repeats the binding for training. A production gateway must establish authentic source identity, clock and observation semantics before using an analogous rule. The inspection limits and calibration identities in the exercise are invented. Actual drawing tolerances, gauge studies and signed dispositions belong in the supplier's first-article record.

## Allocate the controller interfaces

| Interface | Proposed production responsibility |
|---|---|
| CNC or robot controller | Own the installed programme, coordinated motion, tool offsets and machine vendor diagnostics. Expose machine identification, state and execution observations through a read-only review account. Map supplier signals to this job contract after proving identifier availability on the actual controller. |
| Safety PLC and local permits | Enforce guards, interlocks, enabling and authorised reset under the integrator's validated safety design. The exercise exports an evidence disposition and holds both equipment permission and fabrication release false in every case. |
| Scan and metrology station | Read the workpiece, material batch, fixture revision and gauge. Store calibrated results and the operator evidence required to trace the accepted joint, dimension or interface. |
| Gateway and review service | Timestamp and retain observations with source quality. Isolate acquisition from equipment command authority and carry inspection and mismatch evidence into a draft workflow for accountable review. |
| ERPNext and Frappe HR | Use the existing Work Order, Job Card, Quality Inspection and Employee Skill Map workflow. Record operation qualification separately from authority to sign production release. Test import and permissions in a buyer-approved sandbox. |

OPC UA for Machine Tools provides a standard model for machine identification, monitoring and job management. Read access to selected observations supports this design; assigning job orders and motion remains outside this replay. The Robotics companion specification provides asset and condition observations for robot cells. Obtain the exact profiles, tags, role permissions and evidence samples in the supplier return. [OPC UA Machine Tools](https://reference.opcfoundation.org/specs/OPC-40501-1/6) · [OPC UA Robotics](https://reference.opcfoundation.org/specs/OPC-40010-1/4.1) · [Existing supervision gateway](../../../../../deployment/supervision/README.md) · [ERPNext and HR](../../../../../deployment/erpnext/README.md)

A first shift can rehearse the nominal trace, wrong fixture, data loss and a marginal reading using one planner, one cell technician and one independent quality reviewer. The supplier should demonstrate fixture exchange, machine-side correction and first-article remeasurement before quoting repeat cycle times. Include the training hours, inspection load, downtime and rework handling in the rapid-production estimate.
