# T-ECU/A v2 — block diagram

```
 ┌───────────────────────────────────────────────────────────┐
 │          24 V DC input (redundant, diode-OR)               │
 │   LM5164 buck → 5 V → LDO chain → per-rail                  │
 │   5 V (CM5), 3.3 V (PHY + CAN + SE), 1.8 V, 1.0 V           │
 └───────────────────────────────────────────────────────────┘
                    │         │         │
                    ▼         ▼         ▼
              ┌────────────────────────────────┐
              │   RPi CM5 / Radxa CM5 drop-in   │
              │   (SO-DIMM 260-pin)             │
              │   BCM2712 / RK3588S — 4-core A76│
              │   4–16 GB LPDDR4X, eMMC on-mod  │
              └────────────────────────────────┘
                    │         │         │
           ┌────────┤         │         ├────────────┐
           │        │         │         │            │
           ▼        ▼         ▼         ▼            ▼
      ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
      │TSN Eth │ │CAN-FD  │ │MIPI-CSI│ │USB-C x2│ │M.2 NVMe│
      │ A + B  │ │ HVAC   │ │CCTV cam│ │console │ │ + M.2  │
      │(redun) │ │ LIGHT  │ │ input  │ │+ diag  │ │  5G    │
      └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
           │
           ▼
      ┌────────┐
      │88E6321 │  TSN Ethernet switch — 6 ports
      │switch  │  TCN-E A + B to T-ECU/S + T-OBS,
      └────────┘  plus 4 passenger-facing for PIS displays
           │
     ┌─────┴─────┐
     ▼           ▼
  to T-ECU/S   to T-OBS
  safety       obstacle
  kernel       detector

 ┌─────────────────────────────┐
 │  ATECC608B secure element   │  1 per board
 │  (I²C to CM5)               │
 └─────────────────────────────┘
 ┌─────────────────────────────┐
 │  SX1276 LoRa radio (SPI)    │  TRG-2 backup
 │  868/915 MHz per region     │
 └─────────────────────────────┘
```

## Block inventory

| Block | Ref | Purpose |
|---|---|---|
| Power input A | `J1` | 24 V DC primary |
| Power input B | `J2` | 24 V DC redundant |
| Main buck | `U1` | LM5164 24→5 V, 4 A |
| LDO 3.3 V | `U2` | TPS7A52 5→3.3 V for PHY/CAN/SE |
| LDO 1.8 V | `U3` | For MIPI + TSN PHY |
| CM5 module | `U4` | RPi CM5 on SO-DIMM (Radxa CM5 pin-compatible) |
| TSN switch | `U5` | Marvell 88E6321 — 6-port TSN-capable |
| Ethernet PHY ×2 | `U6`, `U7` | 88E1512 on TSN A/B uplink to T-ECU/S |
| CAN transceiver A | `U8` | TCAN1462 — HVAC bus |
| CAN transceiver B | `U9` | TCAN1462 — lighting bus |
| USB hub | `U10` | USB 3.1 Gen 1 — depot console + diag loader |
| M.2 slot (NVMe) | `M1` | 2280 — event recorder ring buffer |
| M.2 slot (5G) | `M2` | 2230/3042 Cat.22 modem |
| LoRa radio | `U11` | SX1276 on SPI from CM5 |
| ATECC608B | `U12` | Trust anchor, I²C |
| HDMI header | `J3` | Commissioning display output |
| TSN connector A | `J4` | M12 X-code — TCN-E A |
| TSN connector B | `J5` | M12 X-code — TCN-E B |
| USB-C | `J6`, `J7` | Depot console + diagnostics |
| M.2 antenna ports | `J8`, `J9` | 5G (4 × 4 MIMO) |
| LoRa antenna | `J10` | 868/915 MHz |

## Non-safety architecture

T-ECU/A is **single-redundant**, not 2oo2. A failure degrades
comfort and diagnostics but not safety:

- TCMS stops publishing rollup state → OCC supervisor sees "trainset silent" and
  dispatches recovery per RFC 0013 C1.3.
- HVAC fails → passenger discomfort, not a safety event.
- Event recorder fails → forensic gap, recoverable from the
  T-ECU/S black-box mirror.
- TRG silent → `osr-atp` continues on the last-known MA until
  the validity window expires, then trips EB.

The safety chain (T-ECU/S + T-OBS + W-SBC interlocking) does
not depend on T-ECU/A being healthy.
