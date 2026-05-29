# FreeCAD Review Assemblies

This folder contains `.FCStd` review assemblies generated from the STEP
catalogue. The build123d source under `../../src/osr_mech/` remains the
authoritative geometry.

Regenerate the light-metro review assembly from `mechanical-py/` with:

```bash
scripts/freecad_trainset.sh --family light-metro-3car
```
