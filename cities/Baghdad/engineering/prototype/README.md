# Baghdad Airport prototype review

Open the [interactive prototype twin](review.html) in a browser. To review the earlier first-article drawings, download [airport-prototype.zip](airport-prototype.zip), extract it and open **START.html**. Both work offline. The archive includes IFC4, OBJ, drawings, quantities, electrical scenarios, cash flows and blank field-return forms.

This historical 12 km schematic combines the Airport line’s 15-minute timetable with a revised steel car. It preserves the published v0.7.2 opening as the price and engineering comparison. The offline twin reproduces its original fourteen-route appendix from the archived drawing issue. The current citywide clockface trial has its own publication and fleet assumptions. [Published opening](../../airport-integration.html) · [Original prototype issue](https://github.com/modernecotech/OpenSourceRail/blob/354522b7d7eabb57650f8d516eabf3b6df4916ba/cities/Baghdad/engineering/prototype/airport-prototype.zip) · [Retained appendix](retained-citywide-appendix.zip) · [Current citywide trial](../../CITYWIDE-SERVICE.md)

For new enquiries, start from the [corrected Airport design review](../simulation/ASSUMPTION-AUDIT.md) and issue only the scopes bound to the chosen revised layout. The drawings below refer to the earlier schematic. Fabrication and passenger service still require approved limits and site and first-article evidence.

## Production tasks and first-article records

The six [production packages and remaining tasks](PRODUCTION-READINESS.md) cover the car, bogie, viaduct, station, power and controls, and local workshops. The [historical offline buyer issue](airport-enquiries.zip) joins their price schedules to the same drawing and ERP estimate editions. Extract it and open **START.html**. For the proposed installed car, review the [dimensioned arrangement and fitout register](vehicle-factory/INSTALLED-GA.md). For civil and electrical work, start with the [infrastructure schedules and connector return](infrastructure/README.md).

### Size a factory and quote its work

The Airport factory specification lists the machines, jigs, moulds, inspection facilities and contract services needed for the 36-car opening. Read the daily load alongside each count. A 24-hour release cycle calls for eight beam mould positions, while a 48-hour cycle calls for sixteen at the same output. Use the equipment register to return measured cycles, shared facilities and installed or hire prices against the parent ERP lot. [Factory specification](FACTORY-SPECIFICATION.md) · [Equipment price return](factory-equipment.csv)

Use the [workshop price register](SHOP-COSTS.md) and [quotation procedure](PROCUREMENT-PLAN.md) to compare offers. Fabricators can start with the [plate and saw files](cam/CAM.md), [beam cutting instructions](infrastructure/YARD-CUTTING.md) and [wire kitting exercise](infrastructure/WIRE-KITTING.md). The [offline workshop](training/index.html) and [instructor guide](training/INSTRUCTOR.md) use the same candidate and factory edition.

## Review the earlier opening and first-article prices

The buyer register gives a quantity, price period and cost basis for each enquiry. It covers 54 lots, including the five first articles, independent surveys and trials, and two six-site electrical alternatives. The ERPNext buyer view compares competing offers against the same lot. The row for statutory taxes and duties awaits a determination for the buyer and import scope. [Procurement plan and portal instructions](PROCUREMENT-PLAN.md) · [Download the estimate for ERPNext](sourcing-estimate.json)

## Read the package by decision

| Reader | Start with | Decision the records support |
|---|---|---|
| Car builder and maintainer | Car mesh, portal drawing, revised cuts and workshop guide | Quote 144 pieces for a body and its two bogie frames. Check liner fit, leaf travel, removal access and individual axle loads. |
| Civil engineer and station operator | Beam, pier and platform IFCs with the mechanical record | Review the stock shapes and datums, support reactions, casting and lifting assumptions, boarding interface and site investigation. |
| Electrical and controls engineers | Feeder comparison, paired-path drawing, return forms and station-bench procedure | Test the voltage and protection envelope against utility and supplier data. Match the logged door, brake, drive and position signals to a particular vehicle, build and stop. |
| Operator and financier | Train replay, commercial guide, annual cash and citywide decision | Compare actual public cash obligations with allocations, including debt and renewals. Keep unknown demand, contracts and funding visible. |
| Manufacturer and buyer | Opening BOM and draft work orders | Follow a piece to its assembly, drawing and inspection point. The fleet totals cover 36 cars. The five first-article drafts each request one article. |

The bogie sheet locates the frame and axle datums and identifies each outstanding supplier fit. The paired and radial feeder bid guide explains how to compare two complete bids in the annual cash schedule. [Equipment interfaces](fitout-guide.md) · [Feeder bids and cash](feeder-cash-guide.md)

### What the numbers mean

The eight bare steel door openings on the test car are each 1,360 mm. Allowing 25 mm per side gives a proposed 1,310 mm fitted opening. The budget leaves 10 mm above the 1,300 mm requirement. The separate 1.3× vertical-load calculation examines jamb movement. The installer must measure the door with the real lining, seal, guides, bogies and payload. The revised 5.273 t/car figure is gross stock for the frame, bogie structures and liners. The 201.55 t gross train remains a planning load. [Mechanical drawings and inspection sequence](mechanical.md)

The 10 m beam enquiry includes 1,169 kg of scheduled bar and strand, the support footprints and lifting reactions. The station bay adds panel quantities, drainage rates and the straight-platform boarding gap. The supplier and site engineer still need to resolve the bar development, transfer strength, bearings, ground conditions and accessible egress. [Civil guide and drawing notes](civil-guide.md)

The revised train’s priced 30-site power system clears the published hot-circuit voltage floor by about 0.57 V. It falls below the floor when source voltage drops 1%, hot loop resistance rises another 5%, and load rises 5%. A separately identified six-station option with paired conductors clears that combined case. Losing a path pair and a site together still gives a voltage shortfall. The six-station cost awaits comparable installed offers. [Electrical cases, protection and witnessed trials](../commissioning/COMMISSIONING.md)

The revised 30-site layout prices about **$1.124bn** of opening construction. It retains the fleet price allowance pending a bid for the new car. The earlier **$813.7m** Airport budget assumed 21 trainsets and three supply sites. It uses a different timetable and power configuration. A funded opening date and all-in budget need the owner’s scope, site arrangements, finance and approvals. [Original Airport estimate](../../AIRPORT-OPENING.md)

## Reproduce the design

From the repository root, run the following commands. Normal verification reads the source-bound geometry package. Native mechanical recalculation uses the project Python environment.

```sh
./osr design railway prototype --check
./osr design railway prototype --packet build/airport-first-article.zip
.venv/bin/python cities/Baghdad/engineering/prototype/car_worker.py
python3 -m cities.Baghdad.citywide_service --check
```

In the archive, **manifest.json** identifies the physical opening, car frame and SHA-256 of every member. **decision-register.json** identifies the independent citywide selection, electrical and commercial evaluations. Identifiers change when their defined inputs change. Each IFC carries its article identity and local datum. The car is referenced to rail head, the track beam to its soffit, the pier to the underside of its footing and the platform bay to its top surface. Place these articles using the site survey before assembling a site model.

### Submit field results

The workshop guide traces the fleet takeoff to each pilot order. Weighing a complete train generates revised electrical and commercial forms for that case. [Manufacturing quantities](manufacturing-guide.md) · [Weighing and axle returns](weight-guide.md)

The buyer’s guide includes a worked example and the units, price scope and evidence needed for each field. [Commercial returns and annual cash](commercial-guide.md)

Keep field returns outside the checked-in publication. Preserve their original files, dates, issuer and article identity. Blank fields stay open. Use these commands from the repository root, replacing example paths with your working directory.

```sh
python3 -m cities.Baghdad.engineering.prototype.weights --help
./osr design railway prototype --financial-return build/returns/finance.json --packet build/quoted.zip
./osr design railway prototype --feeder-return build/returns/paired-feeder.json --packet build/electrical-review.zip
python3 -m cities.Baghdad.citywide_service --events M05 > build/M05.csv
```

A software replay can verify calculation inputs and identify a failed duty or mismatched article. Independent parties still need to authenticate the trial, approve limits, inspect the as-built installation and authorize service. [Field measurements and recorder procedures](../commissioning/COMMISSIONING.md)
