# W-SBC v2 — block diagram

```
 ┌───────────────────────────────────────────────────────────┐
 │    24 V DC (cabinet) + 12 V backup (battery), diode-OR     │
 │    LTC7803 wide-input buck → 5 V → LDO chain              │
 │    5 V (CM5), 3.3 V, 1.8 V, 1.0 V, plus 24 V relay rail    │
 └───────────────────────────────────────────────────────────┘
                         │         │
                         ▼         ▼
                    ┌────────────────────┐
                    │  Radxa CM5 (RK3588S│   Industrial temp
                    │   industrial-temp) │   −40 °C .. +85 °C
                    │  SO-DIMM 260-pin   │
                    └────────────────────┘
                         │
     ┌───────────────────┼────────────────────────────┐
     │                   │                            │
     ▼                   ▼                            ▼
┌─────────┐        ┌─────────┐                 ┌─────────┐
│TSN A/B  │        │CAN-FD   │                 │Wayside  │
│backbone │        │switch   │                 │sensors: │
│ Eth     │        │drivers  │                 │  LIDAR  │
└─────────┘        └─────────┘                 │  radar  │
                        │                      │  CCTV   │
                        ▼                      │  balise │
                   ┌─────────┐                 │  HABD   │
                   │Isolated │                 └─────────┘
                   │DI × 8   │
                   │DO × 4   │
                   └─────────┘
                        │
    ┌───────────────────┼─────────────────────────┐
    │                   │                         │
    ▼                   ▼                         ▼
Fence-line        Switch-machine           Level-crossing
contact           motor (SIL-4 via         barriers
sensors           external 2oo2            (SIL-4 via
(intrusion)       AND-gate relay           external 2oo2
                  stage)                   AND-gate stage)

 ┌─────────────────────────────┐
 │  ATECC608B secure element   │  Signs SectionIntrusion +
 │  (I²C to CM5)               │  SwitchObservation entries
 │                             │  per RFC 0017.
 └─────────────────────────────┘
 ┌─────────────────────────────┐
 │  PTP1588 PHY                │  Sub-microsecond time sync
 │  (KSZ9031 + hw stamping)    │  across the consensus cluster
 └─────────────────────────────┘
 ┌─────────────────────────────┐
 │  M.2 NVMe 2280              │  Local consensus log shadow
 └─────────────────────────────┘
```

## Safety-critical actuator path

All SIL-4 actuator outputs (switch throw, LX barrier drop)
flow through the **same 2oo2 AND-gate relay pattern as
T-ECU/S**: the CM5 drives both channels via a pair of
independent GPIOs through optoisolators, and the relay stage is
passive-AND. Loss of either channel drops the actuator.

The CM5 is not itself 2oo2 in silicon. Safety redundancy at
the CPU level is provided by the **3-node consensus cluster** —
if this CM5 fails, the other two nodes continue, and the cluster
re-elects a leader within 1.5 s. Actuator state on this board
may freeze at the last-committed value but cannot enter an
unsafe state because the CM5 no longer drives the AND gate's
input (fail-restrictive).

## Non-safety accessory path

The non-safety crates (`osr-energy-site`, non-critical
`osr-balise` logging) share the same CM5 but do not drive any
actuator. Their faults are diagnostic, not safety-critical.

## Interfaces to sensor suite (RFC 0016)

The intrusion-detect sensor pack lives near the W-SBC on the
same pole or in the same cabinet:

- LIDAR connects via the 1000BASE-T Ethernet (using a separate
  PHY from the TSN backbone, so LIDAR traffic does not steal
  backbone bandwidth).
- Radar connects via CAN-FD.
- Stereo camera connects via MIPI-CSI-2 (optional — many
  junction boxes omit the camera to reduce cost).
- Fence-line contact sensors feed in via the 8 isolated
  digital inputs.

The CM5 runs `osr-intrusion-detect::evaluate` at 5 Hz and emits
one `SectionIntrusion` consensus entry per tick (signed by the
ATECC608B).
