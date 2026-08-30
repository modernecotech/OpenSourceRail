# Fabrication and assembly digital twin

This source-linked planning twin follows four representative products from
material release through fabrication, assembly, quality hold points, and
handover: a 6 m track panel, a standard twin-platform station, an OSR-Pi25
twin-track viaduct bay, and a 49.5 m three-car LM3 trainset.

![Animated fabrication and assembly digital twin](fabrication-assembly-digital-twin.gif)

The animation normalizes the four production routes into 48 seconds so they
can be reviewed together. The JSON retains actual planning durations, 25 work
stages, predecessors, work centres, inputs, outputs, hold points, evidence,
cross-stream interfaces, and hashes of the controlled source documents.

The viaduct route now includes tested foundation construction, recorded pier
column delivery, erection and seat survey of the compact hollow cap, two
sub-75 t decked-beam lifts by portal/strand-jack launcher, an
actual-load-chart fallback gate, a maturity-controlled link-slab/diaphragm
connection stage, and separate walkway/containment cassettes.

| Artifact | Purpose |
|---|---|
| [`fabrication-assembly-digital-twin.json`](fabrication-assembly-digital-twin.json) | Machine-readable production route, live-state snapshots, relationships, source hashes, and validation checks |
| [`fabrication-assembly-digital-twin.blend`](fabrication-assembly-digital-twin.blend) | Native Blender scene with separately selectable staged components and animation |
| [`fabrication-assembly-digital-twin.mp4`](fabrication-assembly-digital-twin.mp4) | Detailed H.264 3D perspective animation |
| [`fabrication-assembly-digital-twin.gif`](fabrication-assembly-digital-twin.gif) | README-ready animation below the 20 MB repository limit |

Regenerate all outputs with:

```bash
design/component-catalogue/scripts/blender_fabrication_assembly_twin.sh
```

This is a fabrication-planning and first-article control twin, not released
shop drawings or an approved construction method. Numeric weld procedures,
fastener torques, lift studies, temporary works, supplier instructions, and
signed travelers remain mandatory release inputs.
