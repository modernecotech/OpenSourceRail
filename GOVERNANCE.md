# OpenSourceRail Governance

OpenSourceRail is currently a founder-led pre-1.0 project. This
governance file makes the operating model explicit while the contributor
base, maintainers, and deployment partners are still forming.

## Project Principles

- Safety claims are evidence-led and conservative.
- Deployment responsibility is explicit: the repository is not the
  operator, assessor, insurer, or regulator.
- City-specific work stays parameterized through the unified deployment
  model rather than becoming one-off forks.
- Vendor neutrality matters. Open standards, reproducible artifacts, and
  local manufacture are preferred where they are technically credible.
- The first adoptable product is the non-safety owner-operator stack:
  simulator, Ops Core, asset register, QA, maintenance, and evidence
  portal.

## Roles

| Role | Responsibility |
|---|---|
| Maintainer | Reviews and merges changes, keeps releases coherent, protects scope. |
| Domain reviewer | Reviews a specific area such as operations, civil, rolling stock, hardware, formal methods, or safety evidence. |
| Contributor | Proposes issues, docs, tests, data, or implementation changes. |
| Release manager | Freezes a milestone, runs checks, assembles release notes and assets, and publishes tags/releases. |
| Deployment partner | Supplies local evidence, operator review, site data, field tests, and authority engagement for a real deployment. |

Until named maintainers are listed in a separate `MAINTAINERS.md`, the
repository owner acts as maintainer and release manager.

## Decision Process

Small fixes can be merged by maintainer review:

- typos, stale links, formatting, and screenshots;
- generated documentation drift with reproducible commands;
- tests that do not change public behavior;
- small implementation fixes within an existing RFC.

Larger changes need an issue or RFC before merge:

- public architecture or safety claims;
- new crates or subsystem boundaries;
- changes to generated city cost, finance, fleet, energy, or capacity
  assumptions;
- hardware host-class changes;
- rolling-stock structure, battery, braking, door, or train-control
  changes;
- governance, license, release, and contribution policy changes.

The default rule is rough consensus plus maintainer acceptance. Safety
and certification changes require explicit evidence review, not only
code review.

## Releases

Milestones use tags such as `v0.2.0`. A release should include:

- release notes and known limitations;
- the reader PDF;
- Samawah case-study links;
- simulator and operations-portal instructions;
- evidence matrix and release-gap links;
- verification commands and results.

The current release checklist is
[`docs/releases/next.md`](docs/releases/next.md).

## Conduct

This project does not yet have a separate code-of-conduct file. Until it
does, contributors are expected to be precise, civil, safety-conscious,
and willing to separate technical disagreement from personal criticism.
Maintainers may close or moderate issues that are abusive, off-topic,
spam, or unsafe.

## Conflicts Of Interest

Contributors connected to vendors, operators, contractors, funders, or
public authorities should disclose that context when it materially
affects a recommendation, benchmark, cost claim, or deployment proposal.

## Changing Governance

Governance changes should be proposed as pull requests against this file
with a short rationale. Once there are multiple active maintainers, this
file should be updated to list maintainer nomination, removal, and
tie-break rules.
