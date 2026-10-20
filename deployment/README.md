# Development deployment configuration

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
