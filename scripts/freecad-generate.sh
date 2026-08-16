#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MECH_ROOT="$REPO_ROOT/mechanical-py"

usage() {
    cat <<'EOF'
Usage: scripts/freecad-generate.sh [--all] [--models] [--single-car] [--platform-l-unit] [--catalogue] [--assemblies] [--fem] [--screenshots] [--station-scenes] [--check]

Repository-level FreeCAD generator for OpenSourceRail mechanical artifacts.

Modes:
  --check           Report FreeCAD / Flatpak runtime availability and tracked artifact locations.
  --models          Build the light-metro trainset FreeCAD review model.
  --single-car      Build the corrected single-car assembly with aligned bogies.
  --platform-l-unit Build the standalone precast platform L-unit design.
  --catalogue       Build native FreeCAD parts catalogue and platform/station assemblies.
  --assemblies      Build assembled/exploded chassis-bogie and body review documents.
  --fem             Run FreeCAD/CalculiX screening FEM models and result summaries.
  --screenshots     Capture FreeCAD GUI screenshots from generated review documents.
  --station-scenes  Build and capture station/track/train FreeCAD scene documents.
  --all             Run models, assemblies, FEM, screenshots, and station scenes.

Examples:
  scripts/freecad-generate.sh --check
  scripts/freecad-generate.sh --models --assemblies
  scripts/freecad-generate.sh --fem
  scripts/freecad-generate.sh --all
EOF
}

has_freecad_cmd() {
    command -v FreeCADCmd >/dev/null 2>&1 || command -v freecadcmd >/dev/null 2>&1
}

has_freecad_gui() {
    command -v FreeCAD >/dev/null 2>&1 || command -v freecad >/dev/null 2>&1
}

has_freecad_flatpak() {
    command -v flatpak >/dev/null 2>&1 && flatpak info org.freecad.FreeCAD >/dev/null 2>&1
}

check_environment() {
    echo "OpenSourceRail FreeCAD integration"
    echo "repo: $REPO_ROOT"
    echo "mechanical package: $MECH_ROOT"
    if has_freecad_cmd; then
        echo "FreeCADCmd: available"
    elif has_freecad_flatpak; then
        echo "FreeCADCmd: available through org.freecad.FreeCAD Flatpak"
    else
        echo "FreeCADCmd: not found"
    fi

    if has_freecad_gui; then
        echo "FreeCAD GUI: available"
    elif has_freecad_flatpak; then
        echo "FreeCAD GUI: available through org.freecad.FreeCAD Flatpak"
    else
        echo "FreeCAD GUI: not found"
    fi

    echo "review models: mechanical-py/catalog/freecad/"
    echo "FEM outputs: mechanical-py/catalog/fea/"
    echo "screenshots: docs/screenshots/freecad/"
}

run_models=false
run_single_car=false
run_platform_l_unit=false
run_catalogue=false
run_assemblies=false
run_fem=false
run_screenshots=false
run_station_scenes=false
run_check=false

if [ "$#" -eq 0 ]; then
    usage
    exit 2
fi

while [ "$#" -gt 0 ]; do
    case "$1" in
        --all)
            run_models=true
            run_assemblies=true
            run_fem=true
            run_screenshots=true
            run_station_scenes=true
            ;;
        --models)
            run_models=true
            ;;
        --single-car)
            run_single_car=true
            ;;
        --platform-l-unit)
            run_platform_l_unit=true
            ;;
        --catalogue)
            run_catalogue=true
            ;;
        --assemblies)
            run_assemblies=true
            ;;
        --fem)
            run_fem=true
            ;;
        --screenshots)
            run_screenshots=true
            ;;
        --station-scenes)
            run_station_scenes=true
            ;;
        --check)
            run_check=true
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
    shift
done

if [ "$run_check" = true ]; then
    check_environment
fi

cd "$MECH_ROOT"

if [ "$run_models" = true ]; then
    scripts/freecad_trainset.sh --family light-metro-3car
    scripts/freecad_trainset.sh --family light-metro-3car-fullset-3train
fi

if [ "$run_single_car" = true ]; then
    scripts/freecad_trainset.sh --family urban-shuttle-1car --out catalog/freecad/single-car-assembly.FCStd
fi

if [ "$run_platform_l_unit" = true ]; then
    scripts/freecad_platform_l_unit.sh
fi

if [ "$run_catalogue" = true ]; then
    scripts/freecad_catalog.sh
fi

if [ "$run_assemblies" = true ]; then
    scripts/freecad_assembly_review.sh
fi

if [ "$run_fem" = true ]; then
    scripts/freecad_fea.sh
fi

if [ "$run_screenshots" = true ]; then
    scripts/freecad_screenshots.sh
fi

if [ "$run_station_scenes" = true ]; then
    scripts/freecad_station_scenes.sh
fi
