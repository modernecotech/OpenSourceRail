# Service-battery terminal recharge: known calculation issue

The current `state_of_charge` function applies the assumed charge-acceptance
fraction after capping the catalogue current limit by charger power. Its
per-leg `charge_leg` calculation applies that fraction to the catalogue limit
first. Consequently, the reported terminal replenishment time can be longer
than the time calculated with the per-leg assumption. The propagated leg
balances themselves use the per-leg limit. An empty terminal energy shortfall
can also be reported with an unknown time instead of zero.

For example, with a 75-module pack, 200 kW charger, 50% acceptance, 95%
efficiency and 50 kW hotel load, the per-leg assumption limits input to
108 kW. The current terminal calculation uses 100 kW. For ten 147.361774 s
legs under the stated defaults, the resulting 15.353 kWh shortfall gives
1,228.24 s using the current terminal calculation and 1,050.78 s using the
per-leg bound. These are conditional calculations, not validated charge power.

A corrected implementation and regression tests are prepared in isolated
commit `be03a8436a7b5b307840514e05146f98b3ee2574`. It is not part of the
current reference: changing the shared electrical source invalidates multiple
source-bound research publications. Those packets must be regenerated or
explicitly retained under their original source epochs before integration.
Battery temperature, state-of-charge acceptance and supplier qualification
remain unverified.
