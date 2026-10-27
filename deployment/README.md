# Development deployment configuration

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. Six 17 m comfort cars carry 44 seats plus two wheelchair places/car and no planned standing; the 120-second target gives 8,280 passengers/hour/direction. Passive steel-wheel bogies run on conventional rails carried by precast concrete. Station LIMs act on passive onboard secondaries; there are no traction motors, traction batteries or suspension magnets onboard. Service batteries, independent brakes and the existing station-led GoA4 architecture remain. The reference design is research only; city numerical regeneration, economics and physical release remain open. Historical studies retain their own recorded configurations and results.

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
