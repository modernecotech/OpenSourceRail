#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MECH_ROOT="$REPO_ROOT/design/component-catalogue"

usage() {
    cat <<'EOF'
Usage: tools/automation/freecad-generate.sh [--all] [--models] [--single-car] [--platform-l-unit] [--catalogue] [--assemblies] [--civil-systems] [--fem] [--screenshots] [--station-scenes] [--digital-twin-animation] [--samawah-line-twin] [--fabrication-twin] [--mesh-exports] [--high-quality-renders] [--check]

Repository-level FreeCAD generator for OpenSourceRail mechanical artifacts.

Modes:
  --check           Report FreeCAD / Flatpak runtime availability and tracked artifact locations.
  --models          Build the light-metro trainset FreeCAD review model.
  --single-car      Build the corrected single-car assembly with aligned bogies.
  --platform-l-unit Build the standalone precast platform L-unit design.
  --catalogue       Build native FreeCAD parts catalogue and platform/station assemblies.
  --assemblies      Build assembled/exploded chassis-bogie and body review documents.
  --civil-systems   Build and validate the viaduct/station/junction integration test site.
  --fem             Run FreeCAD/CalculiX screening FEM models and result summaries.
  --screenshots     Capture FreeCAD GUI screenshots from generated review documents.
  --station-scenes  Build and capture station/track/train FreeCAD scene documents.
  --digital-twin-animation
                    Animate the civil/rolling-stock twin and encode the README GIF.
  --samawah-line-twin
                    Build and animate the complete source-linked Samawah Line 1 twin.
  --fabrication-twin
                    Build and animate the track/station/viaduct/train production twin.
  --mesh-exports    Export generated FreeCAD review documents to STL render meshes.
  --high-quality-renders
                    Export STL meshes and render README-grade PNGs with Blender/Cycles.
  --all             Run models, assemblies, civil systems, FEM, screenshots, station scenes, and the twin animation.

Examples:
  tools/automation/freecad-generate.sh --check
  tools/automation/freecad-generate.sh --models --assemblies
  tools/automation/freecad-generate.sh --fem
  tools/automation/freecad-generate.sh --all
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

    echo "review models: design/component-catalogue/models/cad/"
    echo "FEM outputs: design/component-catalogue/catalog/fea/"
    echo "screenshots: docs/screenshots/freecad/"
}

run_models=false
run_single_car=false
run_platform_l_unit=false
run_catalogue=false
run_assemblies=false
run_civil_systems=false
run_fem=false
run_screenshots=false
run_station_scenes=false
run_digital_twin_animation=false
run_samawah_line_twin=false
run_fabrication_twin=false
run_mesh_exports=false
run_high_quality_renders=false
run_check=false

if [ "$#" -eq 0 ]; then
    usage
    exit 2
fi

while [ "$#" -gt 0 ]; do
    case "$1" in
        --all)
            run_models=true
            run_single_car=true
            run_platform_l_unit=true
            run_catalogue=true
            run_assemblies=true
            run_civil_systems=true
            run_fem=true
            run_screenshots=true
            run_station_scenes=true
            run_digital_twin_animation=true
            run_high_quality_renders=true
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
        --civil-systems)
            run_civil_systems=true
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
        --digital-twin-animation)
            run_digital_twin_animation=true
            ;;
        --samawah-line-twin)
            run_samawah_line_twin=true
            ;;
        --fabrication-twin)
            run_fabrication_twin=true
            ;;
        --mesh-exports)
            run_mesh_exports=true
            ;;
        --high-quality-renders)
            run_high_quality_renders=true
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
fi

if [ "$run_single_car" = true ]; then
    scripts/freecad_trainset.sh --family urban-shuttle-1car --out models/cad/single-car-assembly.FCStd
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

if [ "$run_civil_systems" = true ]; then
    scripts/freecad_civil_systems_example.sh
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

if [ "$run_digital_twin_animation" = true ]; then
    scripts/freecad_digital_twin_animation.sh
fi

if [ "$run_samawah_line_twin" = true ]; then
    scripts/freecad_samawah_line_twin.sh
    scripts/blender_samawah_line_twin.sh
fi

if [ "$run_fabrication_twin" = true ]; then
    scripts/blender_fabrication_assembly_twin.sh
fi

if [ "$run_mesh_exports" = true ] || [ "$run_high_quality_renders" = true ]; then
    scripts/freecad_mesh_exports.sh
fi

if [ "$run_high_quality_renders" = true ]; then
    scripts/blender_freecad_renders.sh
fi
