# Integrated station, interlocking and recovery study

[Results](result.json.gz) · [Actual command/input/output records](executed.json.gz) · [Receipts](manifest.json)

Actual Rust resource ownership is bound to station control over an incoming six-car run, dwell, and a committed next departure. Full-tail evidence releases the old bundle only after the complete virtual consist clears its downstream overlap. Receiver, sensor, drive, resistor, stale observation and uncommitted departure counterexamples retain their failure scope. No physical command is enabled.

Equivalent SI motor constants enforce air-gap power conservation. Current, voltage and copper-loss limits remain scalar hypotheses rather than measured three-phase performance. The brake proposal includes delay, downgrade, friction, one failed unit, heat-energy capacity, clamp loads and explicit growth-reserve consumption. The independent winch proposal exposes energy, pull, anchorage, cable reach and unresolved access.

Historical [FTA emergency-preparedness guidance](https://www.transit.dot.gov/regulations-and-guidance/safety/recommended-emergency-preparedness-guidelines-rail-transit-systems) motivates independent braking and recovery; it is not a current Iraqi approval basis. [Twiflex industrial spring-applied brakes](https://www.twiflex.com/products/disc-braking-systems/spring-applied-calipers/vcs-series) and [ACE/Ashtead OEM capability](https://www.ashtead-technology.com/lifting-pulling-and-deployment/support-services/) are leads, with no selected railway-rated product or quote.

**Open:** measured friction/fade/heat transfer, passive capture and restraint, safe force modulation across loads, guideway local/global reactions, essential power, winch access and anchors, distributed authority, authenticated sensors, MCU timing and full physical acceptance.
