# Costed shift workplan and workload simulation

A planner can take a published railway, see which groups are needed on each
shift, price paid time and test how much work falls outside the planned
capacity. Run the workplan before asking an employer for wages or asking a
yard or installation contractor to commit to a calendar. The input and
results retain their railway and evaluation identities.

```sh
./osr workplan --network first --mode goa4 --availability-bps 9000 --output build/first-workplan
```

The example uses Baghdad's seven-corridor programme and shows a 10% capacity
loss with paid time held fixed. Run a second copy under a new output path to
compare scenarios. The battery, line power and Airport alignment studies have
their own engineering scopes. The seven-corridor programme budgets here use
the city network's existing quantity and service source.

| Select | Available cases |
|---|---|
| Railway | `first`, `metropolitan`, `metropolitan-mainlines`, or the location-neutral `core` comparator |
| Duty | `goa4`, `assisted` with a 25% onboard duty hypothesis, or `supervised` as an annual equivalent for commissioning |
| Capacity test | `10000` repeats the staffed capacity plan; `9000` tests 90% of that capacity; use the same payroll and prices for comparison |
| Your own inputs | Copy `plan.json`, update the changed field and its basis, and run `./osr workplan --plan edited.json --output build/revised-workplan`. Keep the study and source identities with the new proposal. |

The [example result](workplan/summary.md) prices 55 role and shift rows. Its
central operating payroll is **$12.27m per year** for a planning establishment
of 1,526 full-time equivalents. That sits alongside **$1.29m** for one priced
training intake, **$20.55m** for vehicle assembly and factory support across
the delivery window, and **$6.85m** for precast and erection labour in the
published civil scope. With planned capacity cut by 10%, the model shows
262,256 uncovered operating hours and 40,616 uncovered precast and erection
hours, before adding further shifts, relief or subcontract capacity. [Open the role and shift detail](workplan/workforce.csv) ·
[Read the machine-readable plan](workplan/plan.json) ·
[Download the Arrow-compatible Parquet table](workplan/workforce.parquet)

## Who works when and what the owner is buying

| Work and period | Workforce and timetable | Quantity, price or acceptance basis |
|---|---|---|
| Passenger operations, recurring | One station duty lead and two assistance posts per station, plus one security and one cleaning post. Three windows cover 06:00–14:00, 14:00–22:00 and 22:00–00:00. | The proposal derives recurring role-hours from service and station counts, and prices the pooled rosterable establishment. Confirm peaks, shift handover, breaks and passenger assistance requirements against station duty cards. |
| OCC, depot and infrastructure response, recurring | Continuous early, late and night rotation. The depot has eight posts per depot on each of the first two shifts and four per depot overnight. OCC desks and mobile civil, track and power teams cover all three shifts. | Compare desk and maintenance coverage by shift. The annual payroll includes declared relief. Price specialist overhaul, rescue, call-outs and cross-location relief against the actual operating rules. |
| Office and onboard roles | Schedule planning, payroll, stores and trainers on a weekday-equivalent office window. Under assisted or supervised service, allocate onboard duty by the available service profile. | Allow for timed turns, depot moves, sign-on, qualification and relief once actual duties are assigned. The GoA4 base has zero scheduled onboard posts. |
| Initial operator intake | 80 classroom or simulator hours and 80 mentored field hours per learner. The study allows up to 12 learners per instructor and four per mentor. | Learner, instructor and mentor time is priced only for the intake. Room, simulator, assessment costs and dates need a training provider. Credit any learner or mentor pay included elsewhere in the commissioning contract. |
| Vehicle works | Staff body, bogies, doors and interiors, HVAC, wiring, and marriage and test in one repeat daytime shift across the required lines. Also assign coordination, QA, stores and materials-handling posts. | Price scheduled posts including planned idle time and relief. Compare hours required per stage with capacity at 85% line availability and 80% direct-time share. The purchase allowance for productive assembly hours has a different boundary. |
| Precast yard | Plan 18 positions per yard with separate steel and strand, mould and stressing, batching, crane and yard transport, lab, foreperson and stores rows. | Derive labour from beam quantities, declared production rates and reserved workdays. Confirm shifts, curing, stock movement and inspection holds in the [yard and erection study](README.md#precast-yard-stock-and-erection). |
| Site erection | Staff supervision, crane, rigging, alignment and traffic access across the planned fronts. Book actual site possession hours before setting dates or shift premiums. | Compare the required and available labour in the window. Separate labour from operated cranes, subcontract crews, temporary works and road-control prices to avoid duplicate allowances. |
| Design, other works and handover | Secure surveys, rail and grid connections, station and depot works, emergency planning, independent review and integrated trials. | Each appears as an open work item with an owner and pricing route. Refer to the candidate's construction, equipment, testing and assurance accounts for the broader budgets. Price detailed hours and contracts against accepted quantities. [Programme decisions](../WORKPLAN.md) · [Capital and delivery ledger](../../../cities/Baghdad/COST-AND-DELIVERY.md) · [Standards evidence](../../certification/README.md) |

## Read the hours and costs

A row gives a role or workgroup, the period and start time, repeated workdays,
simultaneous posts where known, work required, paid time, available time,
shortfall and low/base/high cost. Annual operating payroll comes from a
pooled 2,080 paid hours and 1,720 rosterable hours per full-time position.
The staffing model spreads that payroll across shifts. The per-shift post
counts and the annual full-time establishment use different units.

Costs use the published October 2026 Baghdad wage proxies with the study's
employer loading, rail premium and exchange rate. The vehicle, yard and
erection rows value paid slots across the specified delivery window. They
provide a budget comparison with supplier wages and output, including idle
capacity. The prices are planning allowances inside the vehicle, civil,
training and operating accounts. Use contract exclusions and any labour
already embedded in a supplier's price to reconcile each account once.
The core comparator carries its hours with local wages open. [Wage basis and
existing payroll credits](README.md#baghdad-operating-pay-in-2026-prices)

A shortfall identifies work outside a shift's estimated capacity. Extra
capacity on another shift or in another trade remains visible in that row.
A shift marked unscheduled may have known labour hours and price with dates,
posts or facilities pending. Null values and the evidence gaps are retained
in the outputs.

## Outputs and repeatable checks

| File | Use |
|---|---|
| `summary.md` / `summary.json` | Compare known costs and base and stressed coverage by phase and account. Read the outstanding work and keep the account periods separate. |
| `workforce.csv` | Hand over detailed rows for a planner or buyer to review in a spreadsheet. |
| `workforce.parquet` | Read the same typed rows using an Apache Arrow reader. Currency is integer US cents and duration is integer minutes. Missing fields stay null. |
| `plan.json` / `run-receipt.json` | Retain the input, published source hashes, Rust binary hash, output hashes, and elapsed run time including the reservation. |

The Rust evaluator prices paid minutes and evaluates repeated shift patterns
in bounded batches. A three-year pattern occupies one row per role and
shift, so the calculation does not expand into one record per worker per day.
It measures the available labour against the requirement for each row and
keeps the schedule capacity and cost arithmetic in checked integers.
CSV supports review and Parquet supports projecting only the columns needed
by a reporting query. A named-person roster still requires qualifications,
breaks, shift and rest rules, route and depot turn assignments and site
possession times. The delivery scheduler handles dependencies and shared
resources separately. [Rust implementation and efficiency review](WORKFORCE-RUST.md)
