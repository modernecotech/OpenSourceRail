# OpenSourceRail reference vehicle and track test assemblies

The first build can use interchangeable fixtures. Machine and identify the passive-car datum targets as one set. Issue the powered-car brake reaction fixture under the powered railway selection. The applied loads, control signals and vehicle equipment differ. The [generated schedules](reference-rigs.json) record each parent, the evaluation inputs and the producer hash.

## Passive bogie, body and platform mock-up

Use track centre as the lateral origin and running rail head as height zero. Set two rails to the reference 1,435 mm gauge on adjustable supports. Make wheel and body height independently adjustable. Locate four axle planes at −7.45, −5.35, +5.35 and +7.45 m relative to the car centre. Survey the two bogie pivots at ±6.40 m. Use the design's existing side-sill load spreaders as survey targets. Require the fabricator to establish lifting loads and qualified jacking points separately. The stock geometry and surfaces can be traced to the [vehicle generator](../station_rail/vehicle.py) and [brief](../station_rail/brief.toml).

Fit a removable platform edge beside the two 1.4 m clear door openings on the boarding side. Mark their centre lines at ±4.5 m on a single-car jig. The schedule also gives the twelve door positions from the midpoint of the coupled train. Use a straight reference beam for the platform edge, survey its top relative to both rail heads, then measure each threshold at both jambs. This measurement includes floor roll or twist that a single centre-line sensor misses. The fixture needs shims, a gauge rod, four independent wheel-pad readings per bogie, load cells or an equivalent weighing system, and position targets fixed to the body. The physical rig and instrument tolerances await quotations.

| Wheel and body setup | Axle centre above rail | Floor above rail | Passive fin bottom relative to rail head |
|---|---:|---:|---:|
| New 760 mm wheel at nominal ride height | 380 mm | 1,000 mm | +20 mm |
| Worn 680 mm wheel, suspension geometry held | 340 mm | 960 mm | −20 mm |
| Worn wheel, body lifted 40 mm from uncompensated position | 340 mm | 1,000 mm | +20 mm |

The second setup moves the fin bottom through the rail-head datum. Its lateral position between the rails determines possible contact with track equipment. The third setup recovers nominal floor and fin height but consumes suspension adjustment. Measure remaining bump and rebound travel, primary axle and brake clearance, fin-to-track hardware separation and the available range of the levelling mechanism at empty, normal and crowd control loads. Equal wheel wear and pure body heave are evaluation assumptions. Unequal wear, cant, twist and dynamic motion need their own tests. A comparison record should carry car and bogie serials, wheel diameters, individual pad loads, shims, surveyed edge position, raw displacement traces and calibration records.

### Bogie rotation against the carbody sill

The selected steel sideframe is 2.50 m long with its outer face 1.00 m from track centre. The carbody sill begins at 1.01 m. Their height ranges overlap. Rotate the bogie about its pivot with the body on the chord between its two pivots. For a circular curve of radius R, the bogie yaw magnitude is arcsin(6.40/R). Check both directions on both sides at each bogie. The calculation reads the actual box-stock coordinates and checks that all rotated corners remain within the opposing sill length.

| Trial alignment | Bogie yaw | Minimum face separation |
|---|---:|---:|
| Straight | 0° | +10.0 mm |
| 500 m radius | 0.733° | −5.9 mm |
| 250 m radius | 1.467° | −21.7 mm |
| 150 m radius | 2.445° | −42.4 mm |

Negative separation identifies overlap between the proposed sideframe envelope and the sill at nominal height, before sway or tolerances. One adjustable jig setting moves each sideframe 35 mm inward with the wheels and body sills fixed. This leaves 13.3 mm at the sill on the 250 m curve, but only 7.5 mm between the frame and hub. On the 150 m curve the revised setting still overlaps the sill by 7.5 mm. Measure the hub and axlebox envelopes with travel, wear and assembly tolerances before transferring the jig setting to a frame drawing. Moving the sill outboard changes floor ties, body width and load transfer. Narrowing or tapering the sideframe at its ends affects axlebox and primary-seat space. Compare those two physical revisions against partner drawings, wheelset removal, body bending and fatigue. With the spring travel set to its measured limits, turn an unloaded jig through the test angles in both directions and record the first contact angle before applying load. These radii are test conditions. Alignment-specific restrictions depend on actual curvature, suspensions, tolerances and verified clearance.

## Powered bogie, brake and viaduct reaction fixture

For the [30 km digital reference](../../docs/reference-v07/digital/selected.toml), instrument a bogie brake module, its body reaction link and the running-rail seat. Apply a longitudinal pull through the actual shoe contact plane and measure reaction at the mounting pins. Put independent displacement targets on the rail, fastening baseplate and beam. This separates pad slip, rail movement and beam displacement. Return measured contact height, pin spacing, play, bushing and bracket stiffness, load distribution and permanent set to the mount and fastener designers. A continuous rail can carry reactions across more than one span. A single module pull gives a fixture input, while global bearing and pier reactions require rail continuity, braking-train position, bearing restraints and longitudinal stiffness.

The calculation uses a 20 m/s approach, 2% downgrade, 0.6 m/s² net deceleration after application and eleven available modules. During an imposed delay the train accelerates freely downhill. Equal sharing between working modules and constant contact force after engagement are optimistic assumptions. The reference analytical normal train is 150.432 t. A separate 201.732 t structural crowd sensitivity gives a higher component test demand.

| Duty | Applied force per working module | Ideal contact energy at zero delay | Contact energy after 2 s delay |
|---|---:|---:|---:|
| Normal | 10.89 kN | 3.629 MJ | 3.773 MJ |
| Crowd sensitivity | 14.60 kN | 4.867 MJ | 5.059 MJ |

The calculated stop grows from 333.33 m to 386.93 m with the two-second delay in either load case because the model increases brake force with mass. The energy is shared by rail and shoe. Installed force, energy capacity, thermal recovery and load sharing still require evidence. At standstill on the same grade, the calculated total static holding demand follows weight and grade. Quote and test the parking hold independently of the moving brake. The assumed delays define test points. An acceptable delay must follow the route protection envelope.

For the electronic bench, record the time of protection demand, torque inhibition, motion of the module, first contact, force rise and independent standstill proof on one timebase. Wire separate channels for commanded state and measured reaction, and a latched fault input for lost proof or conflicting contacts. Repeat from a cold start, after hot stops and with one module isolated. Derive effective force delay from the traces and rerun the stopping calculation before allocating signalling margin. Protection and maintenance staff need the same raw event timeline and configuration identifier.

Run `python3 engineering/interface_studies/reference_rigs.py --check` from the repository root. The scripts and measurements described here are development work. The project has yet to establish permissible platform gaps, full installed masses, brake capacity and release limits for these fixtures.
