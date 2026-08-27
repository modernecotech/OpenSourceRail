#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
USER_DATA_ROOT="${OSR_ENGINEERING_DATA_ROOT:-${XDG_DATA_HOME:-$HOME/.local/share}/opensource-rail}"
LOCAL_BIN="${OSR_ENGINEERING_LOCAL_BIN:-$HOME/.local/bin}"
if [[ -n "${OSR_ENGINEERING_VENV:-}" ]]; then
    VENV_DIR="$OSR_ENGINEERING_VENV"
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
    VENV_DIR="$ROOT/.venv"
else
    VENV_DIR="$USER_DATA_ROOT/engineering-venv"
fi
NATIVE_ROOT="$USER_DATA_ROOT/native"
REQUIREMENTS="$ROOT/engineering/toolchain/python-requirements.txt"
REPORT_DIR="$ROOT/build/engineering/toolchain"
cd "$ROOT"

usage() {
    printf '%s\n' \
        'Usage: scripts/engineering-toolchain.sh --install-python | --check | --smoke | --benchmarks | --station-ifc | --cities [args] | --flesh-out' \
        '' \
        '  --install-python  Create/update the pinned user-local Python environment.' \
        '  --check           Capture installed versions and fail for missing baseline tools.' \
        '  --smoke           Run deterministic IFC/structure/grid/PV/battery smoke checks.' \
        '  --benchmarks      Run the JuPedSim corridor and Samawah SUMO timetable.' \
        '  --station-ifc     Export and validate station product-structure IFC files.' \
        '  --cities          Generate/run catalogue city packages; pass batch arguments.' \
        '  --flesh-out       Validate the register and run benchmarks plus station IFC.'
}

install_python() {
    if python3 -c 'import ensurepip' >/dev/null 2>&1; then
        python3 -m venv "$VENV_DIR"
    else
        python3 -m virtualenv "$VENV_DIR"
    fi
    "$VENV_DIR/bin/python" -m pip install --upgrade pip
    "$VENV_DIR/bin/python" -m pip install --requirement "$REQUIREMENTS"
    mkdir -p "$REPORT_DIR"
    "$VENV_DIR/bin/python" -m pip freeze --all > "$REPORT_DIR/pip-freeze.txt"
}

flatpak_field() {
    local app_id="$1"
    local field="$2"
    local scope="--system"
    if flatpak info --user "$app_id" >/dev/null 2>&1; then
        scope="--user"
    fi
    if [[ "$field" == "version" ]]; then
        flatpak info "$scope" "$app_id" \
            | sed -n 's/^[[:space:]]*Version:[[:space:]]*//p'
    else
        flatpak info "$scope" --show-"$field" "$app_id"
    fi
}

check_tools() {
    local report="$REPORT_DIR/installed-tools.txt"
    local failed=0
    mkdir -p "$REPORT_DIR"
    : > "$report"

    for app_id in org.freecad.FreeCAD org.qgis.qgis org.cloudcompare.CloudCompare org.eclipse.sumo; do
        if flatpak info --user "$app_id" >/dev/null 2>&1 \
            || flatpak info --system "$app_id" >/dev/null 2>&1; then
            printf '%s\tversion=%s\tcommit=%s\n' \
                "$app_id" \
                "$(flatpak_field "$app_id" version)" \
                "$(flatpak_field "$app_id" commit)" >> "$report"
        else
            printf '%s\tMISSING\n' "$app_id" >> "$report"
            failed=1
        fi
    done

    if flatpak info --user org.blender.Blender >/dev/null 2>&1 \
        || flatpak info --system org.blender.Blender >/dev/null 2>&1; then
        local bonsai_version
        bonsai_version="$(flatpak run org.blender.Blender -b --python-expr \
            'import importlib.metadata; print("Bonsai", importlib.metadata.version("bonsai"))' \
            2>&1 | sed -n 's/^Bonsai //p' | tail -n 1)"
        printf 'org.blender.Blender\tversion=%s\tcommit=%s\n' \
            "$(flatpak_field org.blender.Blender version)" \
            "$(flatpak_field org.blender.Blender commit)" >> "$report"
        if [[ -n "$bonsai_version" ]]; then
            printf 'blender:bonsai\tversion=%s\n' "$bonsai_version" >> "$report"
        else
            printf 'blender:bonsai\tMISSING\n' >> "$report"
            failed=1
        fi
    else
        printf 'org.blender.Blender\tMISSING\nblender:bonsai\tMISSING\n' >> "$report"
        failed=1
    fi

    if flatpak info --system org.freecad.FreeCAD >/dev/null 2>&1 \
        || flatpak info --user org.freecad.FreeCAD >/dev/null 2>&1; then
        flatpak run --command=sh org.freecad.FreeCAD -c \
            '/app/bin/ccx -v 2>&1 | head -n 2; /app/bin/gmsh --version' \
            | sed -n \
                -e 's/^This is Version /freecad:calculix\tversion=/p' \
                -e 's/^\([0-9][0-9.]*.*\)$/freecad:gmsh\tversion=\1/p' \
            >> "$report"
    fi

    if [[ -x "$LOCAL_BIN/rnx2rtkp" ]]; then
        printf 'native:rtklib\tversion=2.4.3.b34+dfsg-1build2\tsha256=%s\n' \
            "$(sha256sum "$LOCAL_BIN/rnx2rtkp" | cut -d' ' -f1)" >> "$report"
    else
        printf 'native:rtklib\tMISSING\n' >> "$report"
        failed=1
    fi

    local energy_binary="$NATIVE_ROOT/EnergyPlus-26.1.0-6f2e40d102-Linux-Ubuntu24.04-x86_64/energyplus-26.1.0"
    local fds_binary="$NATIVE_ROOT/FDS-6.11.1_SMV-6.11.2/bin/fds"
    if [[ -x "$energy_binary" ]]; then
        printf 'native:energyplus\tversion=26.1.0-6f2e40d102\tsha256=%s\n' \
            "$(sha256sum "$energy_binary" | cut -d' ' -f1)" >> "$report"
    else
        printf 'native:energyplus\tMISSING\n' >> "$report"
        failed=1
    fi
    if [[ -x "$fds_binary" && -x "$LOCAL_BIN/fds" ]]; then
        printf 'native:fds\tversion=6.11.1\tsha256=%s\n' \
            "$(sha256sum "$fds_binary" | cut -d' ' -f1)" >> "$report"
    else
        printf 'native:fds\tMISSING\n' >> "$report"
        failed=1
    fi

    if [[ -x "$VENV_DIR/bin/python" ]]; then
        "$VENV_DIR/bin/python" - <<'PY' >> "$report"
from importlib.metadata import version

for package in (
    "ifcopenshell",
    "jupedsim",
    "numba",
    "openseespy",
    "pandapower",
    "pvlib",
    "pybamm",
    "pyswmm",
    "swmm-toolkit",
):
    print(f"python:{package}\tversion={version(package)}")
PY
        "$VENV_DIR/bin/python" -m pip freeze --all > "$REPORT_DIR/pip-freeze.txt"
    else
        printf 'python-engineering-venv\tMISSING\n' >> "$report"
        failed=1
    fi

    cat "$report"
    return "$failed"
}

smoke_tools() {
    local energy_root="$NATIVE_ROOT/EnergyPlus-26.1.0-6f2e40d102-Linux-Ubuntu24.04-x86_64"
    local energy_out="$REPORT_DIR/energyplus"
    local fds_out="$REPORT_DIR/fds"

    "$VENV_DIR/bin/python" "$ROOT/engineering/toolchain/smoke_check.py"

    mkdir -p "$energy_out" "$fds_out"
    "$LOCAL_BIN/energyplus" \
        -D \
        -d "$energy_out" \
        "$energy_root/ExampleFiles/1ZoneUncontrolled.idf"
    grep -q 'EnergyPlus Completed Successfully' "$energy_out/eplusout.end"

    (
        cd "$fds_out"
        "$LOCAL_BIN/fds" \
            "$ROOT/engineering/benchmarks/fds/empty-box.fds"
    )
    grep -q 'FDS completed successfully' "$fds_out/osr_fds_empty_box.out"
    printf 'EnergyPlus and FDS smoke checks passed.\n'
}

validate_register() {
    python3 "$ROOT/engineering/toolchain/validate_analysis_register.py"
}

run_benchmarks() {
    "$VENV_DIR/bin/python" "$ROOT/engineering/benchmarks/jupedsim/station-corridor.py"
    "$VENV_DIR/bin/python" "$ROOT/engineering/benchmarks/sumo/city_timetable.py" \
        --design "$ROOT/designs/west-asia/Iraq/Samawah/design.toml"
}

run_station_ifc() {
    "$VENV_DIR/bin/python" "$ROOT/engineering/interchange/station_ifc.py"
}

case "${1:-}" in
    --install-python)
        install_python
        ;;
    --check)
        check_tools
        ;;
    --smoke)
        smoke_tools
        ;;
    --benchmarks)
        validate_register
        run_benchmarks
        ;;
    --station-ifc)
        validate_register
        run_station_ifc
        ;;
    --cities)
        shift
        validate_register
        "$VENV_DIR/bin/python" "$ROOT/scripts/generate-city-engineering.py" "$@"
        ;;
    --flesh-out)
        validate_register
        run_benchmarks
        run_station_ifc
        ;;
    -h|--help)
        usage
        ;;
    *)
        usage >&2
        exit 2
        ;;
esac
