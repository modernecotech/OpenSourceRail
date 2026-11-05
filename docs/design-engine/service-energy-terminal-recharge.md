# Service-battery terminal recharge: consistent charging limits

The active `state_of_charge` and per-leg `charge_leg` calculations now both
apply the assumed charge-acceptance fraction to the catalogue current limit
before capping it by charger power. Terminal replenishment therefore uses the
same input-power bound as the route legs. An empty terminal energy shortfall
reports zero additional charging time, including when the available net charge
rate is nonpositive. A positive shortfall with no positive net charge rate
continues to report an unknown replenishment time.

For example, with a 75-module pack, 200 kW charger, 50% acceptance, 95%
efficiency and 50 kW hotel load, the per-leg assumption limits input to
108 kW. The former terminal calculation used 100 kW. For ten 147.361774 s
legs under the stated defaults, the resulting 15.353 kWh shortfall gives
1,228.24 s using the former calculation and 1,050.78 s using the consistent
bound. These are conditional calculations, not validated charge power.

The implementation and regression tests originate in commit
`be03a8436a7b5b307840514e05146f98b3ee2574`, now integrated into the active code.
Affected current reports are regenerated from that implementation; retained
research packets keep their original source epochs and calculations.
Battery temperature, state-of-charge acceptance and supplier qualification
remain unverified.

A [retained source-epoch archive](retained-battery-source-epoch/README.md)
preserves source bytes for 15 of the affected publications. It requires their
original packet trees; it does not retrospectively correct their calculations.
An [additional archive](retained-service-energy-extra/README.md) preserves
source bytes and packet inventories for 14 further manifests, including the
separately recorded physical-followup producer epoch.
