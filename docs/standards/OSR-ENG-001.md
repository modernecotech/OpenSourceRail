# OpenSourceRail engineering standard OSR-ENG-001

Version **1.0.0**, effective **2026-10-10**. This is an active OpenSourceRail
internal process standard for shared engineering definitions, numerical
verification, manufacturing evidence and physical correlation. The
[machine-readable policy](../../engineering/assurance/standards/osr-eng-001.toml)
owns its version, reference editions and numerical thresholds.

This standard applies to OpenSourceRail research and engineering workflows. It
does not declare ISO certification, railway approval or production release.
Applicable law and authority requirements take precedence, followed by the
accepted project design basis, applicable adopted ISO methods, and these internal
rules. An approved project may impose stricter limits.

## Applicable ISO references

The references below were checked against ISO's official catalogue on the
effective date. Select the applicable material, process, product and test scope.
Before claiming conformity, retain the controlled edition/amendments, applicable
clauses, test procedure and completed conformity review. Catalogue descriptions
identify scope; they do not substitute for normative method requirements.

| Domain | Reference and intended use |
|---|---|
| Railway quality | [ISO 22163:2023](https://www.iso.org/standard/79427.html): railway quality management; bind customer, statutory and regulatory requirements to evidence. |
| Measurements | [ISO/IEC 17025:2017](https://www.iso.org/standard/66912.html): competent testing/calibration and retained measurement evidence. |
| Structural design basis | [ISO 2394:2015](https://www.iso.org/standard/58036.html): reliability and risk principles; project limit states and resistance factors remain required. |
| Ride evaluation | [ISO 2631-4:2001](https://www.iso.org/standard/32178.html): fixed-guideway relative comfort guidance; select the applicable ISO 2631-1 weighting and evaluation method. |
| Datums and tolerances | [ISO 1101:2017](https://www.iso.org/standard/66777.html): geometrical specification; [ISO 286-1:2010](https://www.iso.org/standard/45975.html): applicable fits and size-tolerance system. |
| Fasteners | [ISO 898-1:2013](https://www.iso.org/standard/60610.html): applicable steel fastener mechanical properties; [ISO 16047:2005](https://www.iso.org/standard/27788.html): applicable torque/clamp-force tests. |
| Welds | [ISO 5817:2023](https://www.iso.org/standard/80209.html): applicable fusion-weld workmanship; [ISO 15614-1:2017](https://www.iso.org/standard/51792.html): applicable welding-procedure qualification. |
| NDT personnel | [ISO 9712:2021](https://www.iso.org/standard/75614.html): relevant industrial NDT qualification/certification. |
| Concrete coupons | [ISO 1920-4:2020](https://www.iso.org/standard/72260.html): hardened-concrete strength test procedures. |
| Composite coupons | [ISO 14125:1998](https://www.iso.org/standard/23637.html): composite flexural properties; additional tests must establish the actual layup and interface laws. |
| Metallic fatigue | [ISO 12107:2012](https://www.iso.org/standard/50242.html): fatigue experiment planning/statistical analysis. |
| Pile tests | [ISO 22477-1:2018](https://www.iso.org/standard/70807.html): maintained axial static compression tests; lateral and cyclic behaviour require separate procedures. |

ISO 2631-4 addresses relative comfort rather than supplying a universal absolute
comfort threshold. Raw peak carbody acceleration from a short startup simulation
shall not be labelled an ISO ride result. A workmanship quality level, fastener
property class or coupon result shall not substitute for assembled strength,
fatigue resistance, actual preload or joint capacity.

## Mandatory OpenSourceRail rules

1. **Configuration:** retain existing product/joint identities, exact revisions,
   datums, material batches, serials, geometry sources, selected property sources
   and file hashes. Freeze as-designed, as-built and as-maintained configurations.
   Changed inputs shall invalidate dependent calculations and inspection evidence.
2. **Model scope:** declare idealisations, unresolved properties, validity ranges,
   initial conditions and intended load cases. Missing data shall remain open.
   Envelope volume shall not establish material mass. Synthetic data shall never
   establish supplier release, measured properties or physical validation.
3. **Numerical verification:** use independent analytical/native benchmarks,
   force/moment/work checks and separate temporal/spatial refinement. Retain
   unsuccessful cases. A converged nonlinear solve alone shall not establish
   discretisation accuracy or physical validity.
4. **Material and connection resistance:** identify all material regions,
   reinforcement, tendons, interfaces, fasteners, welds, bearings and soil laws in
   the load path. Evaluate applicable ultimate, service, fatigue, long-term,
   temperature and construction conditions. Unknown resistance or an uncovered
   failure mode shall block an engineering acceptance claim.
5. **Normal service:** normal wheel contact shall remain strictly positive for
   the accepted service envelope. Use geometry/friction-specific railway force
   limits, actual ride evaluation methods and approved project deformation limits.
   Distress/defect tests shall retain contact loss and stop conditions separately.
6. **Coverage:** include complete passages, operating/resonance speeds, empty,
   nominal, crush and uneven loading, braking, rescue/maintenance, degraded
   conditions, both tracks and arrival offsets. Short startup comparisons shall
   remain screening evidence.
7. **Calibration:** retain timestamps, SI units, instrument calibration, specimen
   and configuration identity, positive measurement uncertainty and bounded
   parameters. Holdout specimens shall be separate from calibration specimens.
   Report sensitivity rank, parameter covariance, residual bias/RMSE, uncertainty,
   correlation and extrapolation limits. Physical acceptance requires actual tests
   and independent review.
8. **Manufacturing:** drawings shall specify functional datums, tolerances, fits,
   processes, connection definitions and inspection characteristics before issue.
   Bind work orders, calibrations, batches, serials and nonconformances to the exact
   revision. Successful CAD generation shall not issue a drawing or clear a defect.
9. **Search and cost:** compare equal service/route scope and trial budgets; retain
   failures and identical uncertainty cases across methods. Confirm selected
   designs with finer coupled/local models. Include foundations, track, transport,
   temporary works, inspection, maintenance and replacement; missing prices shall
   remain null.
10. **Release:** numerical verification, ISO method conformity, physical validation,
    drawing issue and authority acceptance shall remain separate decisions. Only
    the existing controlled release process may authorise production or operation.

## Internal numerical and calibration thresholds

These are **OpenSourceRail rules**, chosen as reproducible screening criteria.
They are not ISO-prescribed tolerances or manufacturing specifications.

| Check | Internal criterion | Reason and scope |
|---|---|---|
| Independent refinement | Each declared observable changes by at most 5% between final levels | Makes resolution effects visible before comparing candidates; refine time and mesh separately. |
| Native load equilibrium | Relative force and moment error at most 0.1% | Detects allocation/postprocessing errors; moment uses a force-times-length scale for near-zero applied moments. |
| Contact work mapping | Absolute residual at most 10⁻⁶ W in the retained benchmark | Checks the opposing work maps in this benchmark; choose documented scaling for materially different solver units/scales. |
| Analytical/native benchmark | Relative error at most 10⁻⁶ | Checks implementations against independent equations, without claiming physical accuracy. |
| Section equilibrium | Relative error at most 10⁻⁵ | Checks fiber resultants; it does not establish uncovered limit states. |
| Native datum solve | Position residual at most 10⁻⁵ mm; orientation residual at most 10⁻⁸ rad | Numerical assembly closure only; these values are not production tolerances. |
| Holdout residual | Uncertainty-normalised RMSE at most 2; absolute normalised bias at most 1 | Candidate calibration screen; actual model discrepancy, correlated samples and operational prediction intervals require independent assessment. |

Acceptance limits for wheel force ratios, weighted ride, fatigue, clearance,
deflection, settlement, bearing pressure, material resistance and proof loads
shall be linked to their applicable method, geometry and project requirement.
This internal process standard does not invent universal values for those limits.

## Execute and review

```sh
tools/automation/osr-python tools/automation/check-shared-engineering-standard.py \
  --review engineering/civil_exploration/examples/shared-spatial-engineering-review.json \
  --protocols build/engineering/spatial-campaign-converged/protocols.json \
  --output build/engineering/osr-standard-assessment
```

The assessment binds the standard version, review, protocol and implementation
hashes. It produces governed protocols and separate numerical pass/fail and open
physical/ISO gates. The published synthetic review remains unqualified even when
its numerical rules pass. Revisions to this standard shall identify changed rules
and their affected evidence; a new standard version shall not silently reaccept
old inspections or physical tests.
