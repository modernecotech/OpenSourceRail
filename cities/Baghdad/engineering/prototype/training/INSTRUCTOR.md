# Run the Airport factory workshop

Open [the workshop](index.html) in a browser after extracting the complete procurement packet. It runs offline. For a paper class, print this guide and cover the answer key. Allow 15 minutes for one role and 15 minutes for a handover with a second person. A buyer and a fabricator can share one copy. Use a calculator, paper and the [factory specification](../FACTORY-SPECIFICATION.md). No ERP account or machine access is needed for the paper exercises.

The exercises follow the Airport opening with six six-car powered-wheel sets, 36 cars and 72 powered bogies. The project also maintains a six-car passive-wheel reference. Use the Airport identifiers on every exercise sheet. The training numbers below include invented bids, faults and readings. The resulting records have training status throughout.

## Brief each role

Give the learner one row. Ask for a quantity with units, the reason a proposed action fails, a corrected disposition and the record the receiving role needs.

| Role | Inputs and problem to hand out | Handover the learner produces |
|---|---|---|
| Buyer | The fleet allowance is USD 50.88m for six sets. A offers six at USD 9m/set. B offers only three at USD 8m/set. Calculate A's increase in direct cost. | Fill a bid register for both offers. Show lot, edition, supplier alias, round, scope, quantity, unit rate, extended amount, validity and exception. Request a complete B return in a new round. |
| CAD/CAM technician | The cut register contains 5,184 pieces, of which 3,168 use the section/liner saw. An old frame drawing is attached to a nest of 5,184 plates. Calculate the plate scope. | Identify the mismatched source, separate plate and saw jobs and review one preview against the current issue. Give the fabricator the stock, units, orientation, drawing revision, preview reference, operation, open checks and review disposition. [CAM handoff](../cam/CAM.md) |
| Vehicle fabricator | One build bed is offered for 36 bodies. Allow 60 occupied hours/body, 48 h of one-time setup and 250 eight-hour days at 80% availability. Size the bed count. | Draw a loading sheet. Give quality the jig identifiers and the three datum wear pads on each jig. Ask for the survey after the frame is unclamped and record the owner of the check. |
| Precast yard planner | Eight beams must leave the moulds each day. The bid changes occupancy from 24 h to 48 h while offering eight positions. Size the revised provision. | Draw two days of occupancy and identify when each position returns to use. Give quality the mock beam ID, pre-pour inspection, batch, cure, transfer strength and survey references. Keep transfer and lifting on hold pending signed evidence. |
| Electrical integrator | There are 30 grid gateways, 116 section gateways and six dispatch controllers. Calculate the control device allocation. Give two mock points the same address and query a return for 152 rectifier cabinets. | Record as-expected and as-found point addresses, affected serials, corrected map revision and repeat result on an isolated paper bench sheet. Ask the supplier for a separate cabinet schedule. |
| Quality inspector and maintainer | The rough opening is 1,360 mm with 25 mm reserved per side. The minimum clear opening is 1,300 mm. An invented loaded reading after a liner exchange is 1,298 mm. Calculate the signed margin. | Keep the failed reading. Record outgoing and incoming serials, instrument and method, approved limit reference, signed margin, corrective action, reinspection and the independent handback owner. Then assess a synthetic 1,304 mm recheck. |
| Instructor and shift planner | Of four attendees, two have current fixture-specific authorisation, one has expired authorisation and one has only the course score. Count those eligible on the stated criterion. | Describe who can be assigned, who needs reassessment, and who needs supervised practice. Use the observation sheet below for one learner teach-back. |

For a CAD/CAM teach-back, use the CAM manifest and locate `parts/gusset.dxf` within the CAM directory. Find the blank quantity for the gusset, identify its sheet pattern, and give its drawing and preview revisions to a second learner. The issued manifest allocates 1,440 of the 2,016 plate blanks to gussets. Count the remaining 576 seats by their three part families. The practice coupon follows a separate drawing and machine setup.

## Answer key and correction prompts

| Role | Expected result and disposition | Ask the learner |
|---|---|---|
| Buyer | A extends to USD 54m. Credit the USD 50.88m allowance once. The direct increase is **USD 3.12m** before project allowances. B extends to USD 24m for half the scope and stays outside like-for-like ranking. | What changes in a second round? Keep B's original receipt, return revised terms under their own identity and check life-cycle terms separately. |
| CAD/CAM | **2,016 plate pieces** belong to the plate route. Reject the old revision and bind the preview to the corrected cut list. | Which shop inputs control a usable program? Identify machine limits, postprocessor/controller, stock, fixture, tool, process allowances and first-off inspection. A preview establishes the scope of the digital exercise. |
| Vehicle | 2,208 occupied hours divided by 1,600 usable hours/bed gives 1.38, rounded up to **two beds**. At three pads/bed, issue six pad positions. | Can the crew and shared survey equipment serve the proposed sequence? Ask for the scheduled trial and recorded post-unclamp geometry. |
| Precast | Eight beams/day × 48/24 = **16 positions**. Eight positions support four beams/day under the proposed cycle. | Which evidence releases a specific cast? Give the batch-linked approved transfer strength and the separate lifting checks. |
| Electrical | **152 allocated control devices**. Record the duplicate point, hold the affected serials, correct the controlled mapping and repeat the affected checks against the independent list. Cabinet count stays open. | Who supplies the missing cabinet quantity? Obtain panel and circuit schedules from the power supplier and retain the open count in the enquiry. |
| Quality and maintenance | Nominal clear width is 1,310 mm. The first signed margin is **−2 mm** and the recheck is **+4 mm**. Retain the failed inspection and both serials. Refer the corrected result to the authorised reviewer. | Which operating state and wear condition were observed? Record these, calibration and measurement uncertainty before proposing handback. |
| Instructor | **Two** have stated in-scope authority. Check validity and restrictions against the actual shift. Retain separate attendance, result and task authorisation. | Can the learner explain the failure and identify the person who reviews its correction? Record each observed skill separately. |

## Practise the software handover

1. **Buyer and supplier.** In the authorised ERPNext training project, open `/airport-sourcing`, select the Airport estimate edition and fleet lot, and prepare a draft Request for Quotation for two supplier aliases. Each supplier uses its own test identity. Compare the two returns under **Project competitions**. On paper, use the same columns as the buyer's bid register. For the tooling lot, consult the [shop cost ranges](../SHOP-COSTS.md) and identify the scope a new return would replace.
2. **Factory and quality.** Map a body bed to an ERPNext Workstation, the joining operation to a Routing, and the reviewed BOM to a draft Work Order. Capture setup and first-off references on the Job Card. For the failed aperture check, enter a mock Quality Inspection with the serial, limit, observed result and hold. Link the Issue, Asset Repair and reinspection to the exchange serials. Retain the original failure.
3. **Training lead.** In a permitted Frappe HR training environment, map the lesson to a Training Program, schedule a Training Event, and record assessment in a Training Result. The competence owner reviews observed work, scope, restrictions and validity before Shift Assignment. Follow local access controls for personnel records. The offline exercise exports only case answers and edition identifiers.
4. **Handover.** The receiving role repeats one calculation from the source and explains one remaining engineering or buying decision. For a handover in another working language, ask both roles to repeat the units, issue, failed check and disposition in that language. Budget controlled translations and instructor review before local use.

## Price a trial class

For one trial, put two learners through each of the seven roles. At 30 minutes per pair, one instructor delivers 3.5 contact hours. Add two hours of preparation. If a separate assessor observes each learner individually for a further 15 minutes, allow 3.5 assessor hours and 10.5 learner-hours in total, including assessment. In a paper pricing exercise, USD 25 per instructor-hour, USD 30 per assessor-hour and USD 10 per learner-hour give **USD 347.50** for this class. These invented rates let buyers check the extension and replace each input with a local offer.

Ask training providers to return trainer, assessor and paid learner time separately, plus translation, supervised machine time, materials, travel and repeat assessments. Identify which hours and first articles a machine supplier already includes in commissioning. In ERPNext, reference the training scope and supplier quotation before assigning any added cost to a purchase or service lot. The factory equipment subtotal excludes the class.

## Observe the teach-back

Use an anonymous exercise reference such as `PRACTICE-01`. Copy the following fields onto each sheet. Store real competence authorisations separately in the controlled personnel system.

| Field | What to record |
|---|---|
| Identity | Workshop edition, candidate, frame and applicable evaluations from the [blank digital record](evidence-template.json), role, source document and source item |
| Calculation | Inputs with units, expression, result, source quantity and any open scope |
| Discrepancy | Expected versus observed result, affected mock item or serial, containment decision and first attempt |
| Correction | Corrected issue or reading, who rechecks it, repeat result, remaining hold and next recipient |
| Observation | Mark each criterion below **demonstrated** or **repeat**. Give a concrete correction for each repeat. |

A learner demonstrates the exercise when they can **(1)** identify the matching issue, **(2)** derive the quantity with units, **(3)** catch the injected mismatch, **(4)** preserve it and describe the correction, and **(5)** tell the receiving role what evidence and review remain. Repeat only the missed criteria and preserve both attempts. The browser scores the quantity and chosen disposition. The instructor observes the other work. A training result can support a later competence review. Machine operation, fabrication release and physical acceptance require separate authority and evidence.

## Save or replay a session

Choose **Save attempts as JSON** before closing the tab. Open the same workshop edition and use **Replay a saved attempt file** to recalculate the record. Each attempt carries a case ID, numeric answer, zero-based action index and the two calculated checks. The file contains no names or accounts. Replaying a file appends its attempts in order, so begin in a fresh tab for an independent replay. The loader checks the candidate, frame and evaluation identities. A saved exercise is editable and provides no signature or proof of attendance.
