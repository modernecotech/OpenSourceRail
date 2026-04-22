# D5 — Terminal turnback

**Scope:** at an end-of-line `terminal` or `depot-terminal`
station: stop, cab transfer, blade observation at the turnback
switch, new outbound authority.

**Cross-refs:** RFC 0010 §1 (terminal archetype), RFC 0012 §4.3
(switch facing / trailing), RFC 0013 §4.1 D5.

## Rules

### D5.1 — Full stop at the terminal platform

The trainset stops at the terminal platform per D4.1
(± 0.5 m of reference mark). The driver verifies the DMI
shows `Terminal` before beginning passenger alight.

**Why:** terminal-specific procedures (cab transfer, pantograph
raise to the dock) are gated by the `Terminal` banner. A non-
terminal stop doesn't give access to them.

### D5.2 — Passenger alight

The driver commands `Door open` and makes the "end of the
line, all change" PA. Doors remain open until the DMI shows
`All clear` — platform staff confirm, or (at unstaffed
terminals) the driver visually sweeps each car from the cab
camera feed.

**Why:** a passenger asleep on a terminal arrival wakes up at
the depot or on the back run. The "all clear" confirmation
lands the liability with station staff or the driver's cam
review, not ambiguity.

### D5.3 — Pantograph raise (at docks)

If the terminal has a 1 500 V DC charging dock (per the
`terminal` / `depot-terminal` archetypes), the driver commands
`Panto up` on the DMI after the doors close. The pantograph
rises, the dock arms, charging begins.

**Why:** raising the panto before door close is a personnel-
hazard question — any crew on the roof is in the way. Doors-
closed is the signal that the consist is clear-to-panto.

### D5.4 — Cab transfer

The driver powers down the active cab per D8.1–D8.5, walks the
length of the train to the opposite cab, powers up per
D1.1–D1.2 (the pre-service brake test is skipped — already
done). The DMI shows the opposite cab as `armed`; the previous
cab shows `disarmed`.

**Why:** dual-cab arming is a D1.6 violation that the DMI
flags; a proper cab transfer is the only non-violating path.

### D5.5 — Turnback-switch observation

If the turnback involves a facing-point switch, the driver
observes the blade position via the cab camera (or directly,
at a terminal with visible tracks) before commanding
departure. The DMI also shows the FPS position (green +
locked in commanded direction); both indicators must agree.

**Why:** FPS is a SIL-4 asset. The DMI reflects
`osr-wayside-points`'s fused observation; adding a visual
check is a belt-and-braces that catches a rare DMI-vs-reality
disagreement from an unreported local sensor fault.

### D5.6 — Outbound MA

The driver waits for the outbound MA on the DMI, acknowledges
per D2.1, and proceeds per the full D2 sequence.

**Why:** every departure — including post-turnback — is an
independent D2. No shortcut across the boundary.
