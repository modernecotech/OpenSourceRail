# T4 — Fare enforcement

**Scope:** on-board inspector work, non-payment handling, appeals.

**Cross-refs:** [`osr-afc`](../../../crates/osr-afc/),
RFC 0013 §4.3 T4.

## Rules

### T4.1 — Inspector identification

Fare inspectors wear a visible identity badge with photograph
and inspector number, and rotate routes daily so that the
same inspector does not work the same line consecutively.

**Why:** visible ID legitimises the stop for the passenger.
Daily rotation limits the opportunity for harassment (by
or of) any one inspector becoming personal.

### T4.2 — Fare check

On stopping a passenger, the inspector scans the passenger's
ticket (paper QR, mobile QR, or tap card) via the handheld
which verifies the HMAC-signed token against `osr-afc`'s
active-tokens list. Verification is online or cached
(cached ≤ 15 min old is accepted).

**Why:** the HMAC check catches forged tickets deterministic-
ally. The 15-minute cache keeps inspectors working through
short backhaul flaps without falsely accusing paying
passengers.

### T4.3 — Fare-evasion record

On a failed check, the inspector issues a supplement-fare
notice (printed on the handheld) stating the infringement,
date, and appeal route. The passenger's identifier (name +
document number per deployment law) is logged to the
infringement database. No physical detention occurs — the
passenger may leave the train at the next station.

**Why:** detention escalates the situation and puts both
parties at risk. The paper trail is sufficient legal basis
for the penalty; physical enforcement is a police function.

### T4.4 — Appeals

Supplement-fare appeals may be filed within 14 days of
issue, in writing or via the deployment's online portal.
The OCC reviews the appeal against the AFC record and
inspector log; outcome issued within 30 days.

**Why:** the 14-day window is long enough for a passenger
returning from travel and short enough to keep the AFC
record fresh in the database. The OCC-not-inspector review
keeps the decision independent of the person who issued.

### T4.5 — Inspector safety

Inspectors work in pairs during late-evening slots (after
21:00) and on routes flagged as elevated-risk by the OCC.
Lone working is permitted only during peak daytime hours on
mainline routes.

**Why:** lone inspectors on quiet late services are an
assault risk. Pair working is not about enforcement
productivity (which drops) but about the inspector going
home safely.
