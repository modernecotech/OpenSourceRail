# Rubavu operations cross-check

- Status: **running-time-screen-passed-awaiting-junction-evidence**
- Automatic running-time cross-check: **passed**
- Retained full-service replay matches current inputs/tools: **yes**
- Service execution basis: **source-bound-CI-executable**
- Junction occupancy evidence: **pending**
- Authority accepted: **no**

| Line | OSR reference | SUMO mean | Difference | Tolerance | Result |
|---|---:|---:|---:|---:|---|
| line-1 | 1001.8 s | 1012.5 s | 10.7 s | 150.3 s | pass |
| line-2 | 1212.5 s | 1228.5 s | 16.0 s | 181.9 s | pass |
| line-3 | 1178.6 s | 1190.5 s | 11.9 s | 176.8 s | pass |

> The automatic result is a deterministic planning-model timing comparison, not proof of safe headways, signalling performance or junction capacity.

> Junction occupancy must be checked in an independently reviewed conflict-capable model and the operator or authority must sign the bound evidence before operational release.

## Remaining junction gate

- independently reviewed junction-occupancy evidence not received

## Remaining acceptance gate

- signed operational acceptance record not received
