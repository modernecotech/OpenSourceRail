# Technical Documentation

The primary v0.5 technical path is the [ferrite-PM maglev adapter](../engineering/ferrite_maglev/README.md). Wheel/rail reports remain configuration-specific reference evidence; their release status does not transfer to maglev.

The [root README](../README.md#find-your-way) is the only human-facing
navigation page. It provides direct routes by task and the authoritative
[source-of-truth table](../README.md#source-of-truth); this file deliberately
does not repeat either.

Technical material remains beside the source or discipline it explains:

- architecture decisions are in [ARCHITECTURE.md](ARCHITECTURE.md) and
  [RFCs](rfcs/README.md);
- planning and engineering guidance is linked directly from the root page;
- city and country pages contain only local evidence and link to the shared
  [deployment planning method](deployment-planning-reference.md);
- folder READMEs describe only their own code, models or evidence.

The generated [Markdown inventory](INDEX.md) lists tracked files for search and
CI diagnostics. It is not a reading path or a technical source of truth.

The published reader edition is available directly from the repository as the
[primary maglev PDF book](../OpenSourceRail-Book.pdf). It is generated from the
current adapter, native review and primary city directory; source
Markdown remains authoritative when a discrepancy is found.

Documentation ownership and generated-artifact rules are defined by the
[repository artifact policy](repository-artifact-policy.md).
