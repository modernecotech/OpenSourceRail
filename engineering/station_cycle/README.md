# Station energy capture and controlled relaunch

This adapter extends the parts-linked station-pair experiment with two local
energy stores and repeated, explicitly scheduled point-train movements. Rust
integrates actual capture and launch work; Python propagates the exact physical
candidate into mass reserves, manufacturing accounts and fourteen cost scopes.

[Generated comparison and evidence](../../docs/design-engine/station-cycle/README.md)
contains the reproducible commands, assumptions, negative results and disabled
manufacturing drafts. [Prior feedback evidence](../../docs/archives/station-pair-feedback-20261107/README.md)
is retained at its original Git/source epoch.

Use `./osr design station-cycle plan` before a bounded private `run`, then
`publish` to a fresh directory and `verify --replay` with a private state path.
Both stores start empty in nominal cases. Explicit initially-full sensitivity
cases carry their initial-energy debit. Actual reverse stopping coordinates are
retained. No energy travels backward in time or between station stores.

This is serial storage-cycle research, not proof of the requested concurrent
passenger service, actual spring/hydraulic force laws, complete installed CAD or
physical qualification. Regeneration does not increase independent brake
capability. Physical, manufacturing and operating release remain separate gates.
