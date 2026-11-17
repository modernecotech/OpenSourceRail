# 20 m box-beam civil construction experiment

This is a bounded construction hypothesis for a separate physical candidate. The selected v0.6 reference, mandatory safety/access obligations and current line30 benchmark are unchanged. The 20 m whole-box source model was replayed from current source with the benchmark's +250 kg/car load reserve. Two 10 m match-cast pieces and 3 m square spread footings make the construction candidate physically different; the whole-beam structural screens do not qualify its joint or temporary stages.

## Exact replay

Run from `/home/hayder/Documents/.osr-v07-selected-20261116` into a **fresh private output directory**:

```bash
/usr/bin/time -v python3 build/v07-ethos/civil-20261117-box20-segmented-001/generate.py . build/v07-ethos/my-fresh-civil-run > build/v07-ethos/my-fresh-civil-run.log 2>&1
```

The original run command, stdout and resource figures are in `run.log`. `input.json` names every source SHA-256 and the fresh line30 packet. `result.json` includes the local whole-beam moving-load stress envelope, construction counts, necessary gravity/handling screens, cost coverage, holds and measurements. `manifest.json` seals the package files. No native solver was run.

## Interpretation

At 2 km the arithmetic gives 200 beam spans, 202 independent piers/footings, 400 ten-metre segment lifts and 800 bearing units. At 30 km it gives 3,000 spans, 3,002 independent supports, 6,000 lifts and 12,000 bearing units. A shared crosshead would have fewer bent positions but has no designed load path, foundation or quote here. The baseline whole-beam is too heavy for the declared 35 t transport payload and 60 t at 12 m crane hypothesis; half pieces pass those *provisional* mass thresholds. Actual charts, access, lifting fixtures and temporary stability remain open.

The fresh unsegmented Class C civil proxy is IQD 162.631 billion (USD 107.703 million). The 3 m footing adds a calculated material-only proxy of IQD 1.477 billion relative to gravity-minimum source footings. Segmentation and its new joint, towers, extra lifting and QA are unpriced, so this candidate has **no complete installed cost**. The 3 m footing meets the 200 kPa gravity-only hypothesis at 167.37 kPa; it fails the 100 kPa sensitivity. Soil, settlement and independent review are unresolved.
