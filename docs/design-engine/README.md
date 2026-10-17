# Design, Jobs And Evidence Workflows

The [17 October architecture feedback](architecture-feedback-2026-10-17.md) adds
[12 coupled provisional cases](architecture-feedback/index.html), a lighter-frame
branch, full-module platforms and published British stressing/lifting equipment
checks. Its 2,316 beam response records retain the open acceptance gates.

The [queued-systems results](queued-systems-results-2026-10-16.md) add
[63 executed preliminary package studies](queued-systems/index.html), provisional
six-car load and platform alternatives, mechanical interface repairs, factory
utilities and itemised production/inspection evidence registers. Six native CAD
checks passed; full engineering qualification and manufacturing release remain open.

The [multi-agent design scenario](multi-agent-design-scenario-2026-10-16.md)
allocates all current vehicle/station/civil inventories to 63 work packages.
The [campaign runner](../../engineering/generative_design/README.md) generates
beam and tooling alternatives, propagates bed demands and executes existing
native part searches while retaining every manufacturing closure gap.
The [executed results and variations](multi-agent-design-results-2026-10-16.md)
include a [native review](generative-campaign/index.html) and the remaining agent
work queue.

The [Pi-beam railway and handling continuation](factory-beam-demands-2026-10-16.md)
adds a [native review and load diagrams](factory-beam-demands/index.html), six
Pi20/Pi25 diagnostic comparisons and a British-manufactured spreader enquiry.
The retained three-car reference produces adverse tension screens; current
six-car loading, material limits and lifting capacity remain unknown.

The [factory development handover](factory-buildout/index.html) maps completed
plan stages 1–5 to both factory examples, British supplier cases and the
[376-object whole-bed review](factory-whole-bed/index.html). The
[delivery record](factory-completion-2026-10-16.md) distinguishes review-package
completion from remaining engineering design and stage 6 qualification.

The [mechanical/civil factory buildout plan](mechanical-civil-factory-plan-2026-10-16.md)
now has [Baghdad example models and supplier equipment](../../engineering/factory_examples/README.md):
fixture tooling, Pi20/Pi25 manufacturing screens, vehicle hall and pilot precast yard,
with actual native CAD exports and explicit qualification gaps.

The [support and finite-resource continuation](factory-support-notes-2026-10-16.md)
adds a [93-object native review](factory-support/index.html), anchor/grout/pad
demands and five shared crane/crew/bed scenarios through common factory jobs.
The [staged-load continuation](factory-stages-notes-2026-10-16.md) adds
[individual-strand histories and ideal end-pin demands](factory-stages/index.html),
with British test/calibration equipment enquiries and four sequence comparisons.

Open the Workbench **Design → Auto-design** flow or use the
[common CLI](../../engineering/design_engine/README.md). All existing native
ERP/FUXA functions remain available through their task-area secondary routes.

| Role | Editable input | Command / interface | Output and unresolved gate |
|---|---|---|---|
| Planner | `cities/workspaces/samawah/project.osr.toml`, controlled city definition and service inputs | Plan → City Studio; `./osr catalogue plan --city samawah`, then selected local generation | Current city artifacts and project twin; survey, demand, utilities and railway acceptance remain external |
| Engineer | Versioned problem, coupled material grade, supports and assembly parameters | Design → Auto-design; `./osr design search --problem clipped-side-bay --city samawah --refine --evaluations 512` | Source-bound candidates, detailed/fault/holdout comparisons, quantities and draft review package; real strength/fire/fatigue/calibration stay visible |
| Maintainer | Native asset, defect/work order and scoped evidence | Maintain → Connected assets / Railway works; Assure → People and evidence | Existing owner records plus durable drafts; case completion or verified document metadata grants no handback |
| Reviewer | Private appointment/measurement/quote/site document, exact record revision and scope | Named account sign-in, separate record author and reviewer, then Verify record | Integrity/completeness verification; technical applicability and independent acceptance remain separate |

**Source:** editable configurations and domain implementation own the design.
**Current:** a completed attempt verified against the current source/toolchain.
**Historical:** retained earlier attempts and studies; their bytes stay verifiable
even when the current source or physical baseline differs.

The inspector distinguishes public potential components from project-qualified
materials and parts. Manufacturer dates, limits and source links remain visible.
The Liebherr MACS 8.0 sheet specifies 400 V three-phase AC power and 110 V DC
controls; the OSR DC-bus study does not establish that conversion or compatibility.
See the [manufacturer sheet](https://www.liebherr.com/shared/media/aerospace-and-transportation/transportation/downloads/products/liebherr-modular-air-conditioning-system.pdf).

Fill appointments when people are known; no invented staff are pre-assigned.
Upload retained evidence with an inspector/document-controller account, then
use a different account with the existing Ops Core `approver` or `admin` role to verify its exact bytes and revision. Start
Workbench with `--users <private-user-store>` configured through the existing
Ops Core user administration. [Ownership and handoffs](record-ownership.md).

Run `./osr doctor --profile minimal`, or select `panel`, `civil`, `cad-bim`,
`browser`, `formal` or `stack`. Toolchain receipts and Python locks are local,
immutable outputs; missing native tools are reported, never replaced by passes.
Use `./osr check --scope impact --changed <files> --plan` for scoped local checks,
and `./osr check --scope all` for the complete local profile. GitHub stores source
and reviewed artifacts; Actions remains disabled.

Inspect attempt logs and solver artifacts in Jobs, including cancelled or failed work. Export creates an offline source-bound package and hashed download chunks; concatenate them in numbered order, verify the displayed archive SHA256 and inspect its manifest. Native CAD/STEP/unissued drawings are available with CLI `export --native`.

The evidence area exposes scoped quotation completeness. The design area accepts sourced finite-resource planning inputs, procurement release hours and closure/availability windows. Missing costs, people and installed quantities remain unresolved. [All 36 packages and remaining engineering work](plan-status.md).

Inspect a current physical candidate, then open **Engineering input draft**. Enter sourced SI manufacturing rules or, for civil candidates, survey/ground/prestress inputs in the supplied template. Drafts survive reload in their exact city/environment/revision/candidate scope. **Retain and check numerical draft** preserves the original candidate and reports missing fields and adverse checks; it changes no adopted baseline or acceptance. Source hashes here identify inputs; upload and independently review retained documents in People and evidence to verify their bytes.

Manufacturing sweeps use conservative bounding boxes; declared clearances do not qualify a workshop. The [ABB converter sheet](https://library.e.abb.com/public/3ade265d028245cb91b97353a515581c/NEW%20PDS%20BORDLINE_M40_DC_750V_U_.pdf) and [exact Renogy G1 sheet](https://www.renogy.com/content/RSP200DB-72-US/RSP200DB-72-G1%20Datasheet.pdf) supply potential part facts. They earn no installed mass or vehicle energy credit. Civil transfer equations are checked against the [independent FHWA example](https://www.fhwa.dot.gov/bridge/lrfd/pscus054.cfm); its material data are not project properties.

Seeded searches also retain `sensitivity.json`: bounded one-variable re-execution using the same charter, scope and common budget. Unknown costs/carbon stay unknown. Full-train cases start the entire assembly before the approach and calculate exit time under the prescribed motion. Solver timeouts retain converged checkpoints and incomplete joint-resultant cycles, without inventing fatigue life or a full passage.

Run the worker-connected independent passage campaign with:

```bash
./osr design refine --problem full-train --city samawah --evaluations 64 --wall-seconds 3600
```

`vehicle-assembly` uses the same campaign. Each of four scenarios declares a
baseline plus independent time-step, deck-mesh, rail-spacing and body-mode cases
before execution. This is 20 native cases plus charged compilation, screening
and two assembly diagnostics. A one-hour budget is an execution allowance, not
a completion guarantee. Per-case timeouts share the remaining job budget.

Jobs retain `passage-progress.json`, each scenario's `refinement-plan.json` and
`comparison.json`, and each native case's input/result/history/log manifest.
The comparison and inspector distinguish cases planned, cases executed and axis
comparisons passed. An unchanged, identical source/toolchain epoch, verified
retained artifacts, complete passage and all seven monitored metrics are required
before the provisional 5% numerical screen can pass. Missing cases remain
unknown; failed contact and numerical screens remain adverse. Neither paired
historical runs nor a completed solver job establish independent convergence or
physical acceptance.

Review and use a revised input without altering its parent:

1. Start a job with the exact project, configuration revision and known baseline.
2. Select a physical candidate. Use the guided SI fields and source selectors to
   retain/check manufacturing, site, prestress or foundation drafts. Blank fields
   remain unknown; expanding the raw JSON editor is optional.
3. Retain applicable source documents in People and evidence, with the candidate,
   physical-definition hash and any part/batch scope. A separate authenticated
   approver verifies the exact record revision and source bytes.
4. Select the checked drafts and verified records, supply a new configuration
   revision and rationale, and propose an input revision. An independent reviewer
   reviews that exact proposal. This is permission for research use only.
5. Run the reviewed revision. The server creates a new immutable child job and
   reruns compilation, mandatory checks and any requested optimisation. Export
   includes all reviewed ancestors and retained documents for private review.

Screening, optimisation, native confirmation and CAD export report their own
setup requirements. The assembly inspector links installed parts, joints, mass
and unresolved allocations to failed/unknown checks. Both English and Arabic
guided journeys are tested; human accessibility acceptance remains open.

The common engine has fifteen fixed-function problems, including native
`mechanical-cleat` and `civil-steel-beam` generation. Select **Recursive native
iteration** to generate, solve and compare subsequent designs using native
feedback. [Commands, determinism and bounded optimum scope](../../engineering/design_engine/README.md).
Use
`civil-system-alternatives` for the existing deck/pier/foundation/material families
on a fixed 100 m, two-track reference function, and `vehicle-assembly` for actual
equipment arrangements and declared connection hypotheses within the six-car
reference family. These choices do not qualify a new material or joint.

An explicit `--interactions build/factors.json` file adds two to six declared
variables, each with two supplied levels, and an `evaluations` limit. Every actual
corner is charged to the common job budget. Reports retain engineering failures,
unknown objectives and missing corners; they infer no probability distribution.
[Review scope and remaining engineering work](review-follow-up.md).
