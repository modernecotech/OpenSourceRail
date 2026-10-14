# Design, Jobs And Evidence Workflows

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
