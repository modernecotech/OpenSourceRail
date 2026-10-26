# Development deployment configuration

<!-- osr-system-context:start -->
OpenSourceRail develops simple, affordable, locally maintainable urban transport. The development default is six 17 m comfort cars, each with 44 seats plus two wheelchair places and no planned standing; the 120-second service target gives 8,280 normal passengers/hour/direction. All permanent magnets and suspension controls remain onboard; concrete beams carry passive steel facings, while station windings provide launch and receiving power. Lightweight assemblies, repeated civil works and repairable local production support the low-cost ethos. Stable physical operation and manufacturing release remain open.

[Project introduction](../README.md) · [Engineering approach and current status](../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

The [host inventory](hosts.toml) contains one offline maglev research host.
Its [runtime profile](maglev.toml) runs the Rust `osr-maglev-control` examples
on an off-the-shelf SBC or development computer. No hardware addresses or
physical output adapters are configured.

The [component policy](components.toml) explicitly assigns this research core
and classifies all other Cargo workspace members as unqualified research
software. Library membership is not a deployment or safety acceptance claim.

Verify the profiles with:

```bash
tools/automation/osr-python tools/automation/validate-host-manifests.py
```

Target SBC selection, isolated sensing, current-drive interfaces, independent
protection, measured timing, power-loss response and physical commissioning
remain open. Design and manufacturing release flags remain false.
