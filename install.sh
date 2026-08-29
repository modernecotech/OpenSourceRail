#!/usr/bin/env bash
# One Linux bootstrap for the OpenSourceRail platform.
set -euo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly RUST_VERSION="1.88.0"
readonly NODE_VERSION="22.23.2"
readonly UV_VERSION="0.11.20"
readonly PYTHON_VERSION="3.11.13"
readonly TRUNK_VERSION="0.21.8"
readonly FLATHUB_URL="https://dl.flathub.org/repo/flathub.flatpakrepo"

OSR_TOOL_ROOT="${OSR_INSTALL_TOOL_ROOT:-${XDG_DATA_HOME:-${HOME}/.local/share}/opensource-rail/toolchains}"
OSR_TOOL_BIN="$OSR_TOOL_ROOT/bin"
OSR_NODE_ROOT="$OSR_TOOL_ROOT/node-v$NODE_VERSION"

PROFILE="core"
ACTION="install"
DRY_RUN=0
BUILD=1
RUN_AFTER=0
INSTALL_TEMP=""
DISTRO_FAMILY=""
PACKAGE_MANAGER=""

usage() {
    cat <<'EOF'
Usage: ./install.sh [options]

Install and optionally run OpenSourceRail on Debian- or Red Hat-family Linux.

  (no option)       Install the Workbench, simulator, design tools, and tests
  --engineering     Also install CAD, BIM, GIS, SUMO, and analysis tools
  --run             Start the integrated Workbench after installation
  --check           Check an existing installation without changing it
  --no-build        Install dependencies without compiling the applications
  --dry-run         Print the selected package and toolchain actions only
  -h, --help        Show this help

Supported package managers: apt-get, dnf, and yum.
Supported CPU architectures: x86_64 and aarch64.

The installer uses user-local, pinned Rust, Node.js, Python, uv, and Trunk
toolchains. System package managers supply only common native libraries and,
for --engineering, Flatpak. It does not alter shell startup files.
EOF
}

fail() {
    printf 'install error: %s\n' "$*" >&2
    exit 1
}

note() {
    printf '\n==> %s\n' "$*"
}

print_command() {
    printf '  +'
    printf ' %q' "$@"
    printf '\n'
}

run() {
    print_command "$@"
    if (( ! DRY_RUN )); then
        "$@"
    fi
}

run_root() {
    if (( EUID == 0 )); then
        run "$@"
    elif (( DRY_RUN )); then
        run sudo "$@"
    else
        command -v sudo >/dev/null 2>&1 || fail "sudo is required to install native packages"
        run sudo "$@"
    fi
}

cleanup() {
    if [[ -n "$INSTALL_TEMP" && -d "$INSTALL_TEMP" ]]; then
        rm -rf -- "$INSTALL_TEMP"
    fi
}
trap cleanup EXIT

temporary_directory() {
    if [[ -z "$INSTALL_TEMP" ]]; then
        INSTALL_TEMP="$(mktemp -d -t osr-install.XXXXXXXX)"
    fi
}

download_checked() {
    local url="$1"
    local expected_sha="$2"
    local output="$3"
    run curl --proto '=https' --tlsv1.2 --fail --location --retry 3 --output "$output" "$url"
    if (( DRY_RUN )); then
        printf '  + verify sha256 %s\n' "$expected_sha"
    else
        printf '%s  %s\n' "$expected_sha" "$output" | sha256sum --check --status \
            || fail "checksum mismatch for $url"
    fi
}

parse_arguments() {
    while (( $# )); do
        case "$1" in
            --engineering)
                PROFILE="engineering"
                ;;
            --run)
                RUN_AFTER=1
                ;;
            --check)
                ACTION="check"
                ;;
            --no-build)
                BUILD=0
                ;;
            --dry-run)
                DRY_RUN=1
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                fail "unknown option: $1"
                ;;
        esac
        shift
    done
    if [[ "$ACTION" == "check" && "$DRY_RUN" == "1" ]]; then
        fail "--check and --dry-run are separate non-mutating modes"
    fi
}

detect_distribution() {
    local requested="${OSR_INSTALL_FAMILY:-}"
    local distro_id=""
    local distro_like=""
    if [[ -n "$requested" ]]; then
        case "$requested" in
            debian|redhat) DISTRO_FAMILY="$requested" ;;
            *) fail "OSR_INSTALL_FAMILY must be debian or redhat" ;;
        esac
    elif [[ -r /etc/os-release ]]; then
        # shellcheck disable=SC1091
        source /etc/os-release
        distro_id="${ID:-}"
        distro_like="${ID_LIKE:-}"
        case " $distro_id $distro_like " in
            *" debian "*|*" ubuntu "*) DISTRO_FAMILY="debian" ;;
            *" rhel "*|*" fedora "*|*" centos "*) DISTRO_FAMILY="redhat" ;;
        esac
    fi

    [[ -n "$DISTRO_FAMILY" ]] || fail \
        "unsupported Linux family; this installer supports Debian and Red Hat derivatives"

    if [[ "$DISTRO_FAMILY" == "debian" ]]; then
        PACKAGE_MANAGER="apt-get"
    elif command -v dnf >/dev/null 2>&1 || (( DRY_RUN )); then
        PACKAGE_MANAGER="dnf"
    else
        PACKAGE_MANAGER="yum"
    fi

    if (( ! DRY_RUN )); then
        command -v "$PACKAGE_MANAGER" >/dev/null 2>&1 \
            || fail "$PACKAGE_MANAGER was not found for the detected $DISTRO_FAMILY family"
    fi
}

detect_architecture() {
    local machine="${OSR_INSTALL_ARCH:-$(uname -m)}"
    case "$machine" in
        x86_64|amd64)
            ARCH="x86_64"
            NODE_ARCH="x64"
            UV_TARGET="x86_64-unknown-linux-gnu"
            NODE_SHA="d60acfe00a2932254bb0ad20e01b0d74397a0875595de719654b214f4b03f307"
            UV_SHA="5de211d9278af365497d387e25316907b3b4a9f25b4476dd6dbf238d6f85cff3"
            TRUNK_SHA="cd9fb2822c9f0ae111737500c179226cb080241ac55002c1db7344aa51a97fec"
            ;;
        aarch64|arm64)
            ARCH="aarch64"
            NODE_ARCH="arm64"
            UV_TARGET="aarch64-unknown-linux-gnu"
            NODE_SHA="fff4078c5def658577f92c88db7db3bc0072924bfb93fe52c1e744a54e94abb8"
            UV_SHA="c8b5b7f9c804b640da0bb66cddddf0a00ce971f64d8076622d70bd141bc80857"
            TRUNK_SHA="1d78218d20a9eff834136c406c9e7612a644c4bec47d85fda9d1c31f7bc8331f"
            ;;
        *)
            fail "unsupported CPU architecture: $machine (expected x86_64 or aarch64)"
            ;;
    esac
}

activate_toolchain() {
    export PATH="$ROOT/.venv/bin:$OSR_TOOL_BIN:$OSR_NODE_ROOT/bin:${HOME}/.cargo/bin:$PATH"
    export PLAYWRIGHT_BROWSERS_PATH="${OSR_PLAYWRIGHT_BROWSERS_PATH:-$OSR_TOOL_ROOT/playwright}"
}

install_native_packages() {
    note "Installing common native packages with $PACKAGE_MANAGER"
    if [[ "$DISTRO_FAMILY" == "debian" ]]; then
        run_root apt-get update
        local packages=(ca-certificates curl git build-essential pkg-config libssl-dev tar xz-utils)
        [[ "$PROFILE" == "engineering" ]] && packages+=(flatpak)
        run_root env DEBIAN_FRONTEND=noninteractive apt-get install -y "${packages[@]}"
    else
        local packages=(ca-certificates curl git gcc gcc-c++ make pkgconf-pkg-config openssl-devel tar xz)
        [[ "$PROFILE" == "engineering" ]] && packages+=(flatpak)
        run_root "$PACKAGE_MANAGER" install -y "${packages[@]}"
    fi
}

install_uv() {
    note "Installing uv $UV_VERSION"
    if (( DRY_RUN )); then
        download_checked \
            "https://github.com/astral-sh/uv/releases/download/$UV_VERSION/uv-$UV_TARGET.tar.gz" \
            "$UV_SHA" "/tmp/uv-$UV_TARGET.tar.gz"
        print_command install -m 0755 uv uvx "$OSR_TOOL_BIN/"
        return
    fi
    mkdir -p "$OSR_TOOL_BIN"
    if [[ -x "$OSR_TOOL_BIN/uv" ]] \
        && [[ "$($OSR_TOOL_BIN/uv --version | awk '{print $2}')" == "$UV_VERSION" ]]; then
        printf '  uv %s already installed\n' "$UV_VERSION"
        return
    fi
    temporary_directory
    local archive="$INSTALL_TEMP/uv.tar.gz"
    download_checked \
        "https://github.com/astral-sh/uv/releases/download/$UV_VERSION/uv-$UV_TARGET.tar.gz" \
        "$UV_SHA" "$archive"
    tar -xzf "$archive" -C "$INSTALL_TEMP"
    install -m 0755 "$INSTALL_TEMP/uv-$UV_TARGET/uv" "$OSR_TOOL_BIN/uv"
    install -m 0755 "$INSTALL_TEMP/uv-$UV_TARGET/uvx" "$OSR_TOOL_BIN/uvx"
}

install_node() {
    note "Installing Node.js $NODE_VERSION"
    local archive_name="node-v$NODE_VERSION-linux-$NODE_ARCH.tar.xz"
    if (( DRY_RUN )); then
        download_checked "https://nodejs.org/dist/v$NODE_VERSION/$archive_name" \
            "$NODE_SHA" "/tmp/$archive_name"
        print_command install "$OSR_NODE_ROOT/bin/node"
        return
    fi
    if [[ -x "$OSR_NODE_ROOT/bin/node" ]] \
        && [[ "$($OSR_NODE_ROOT/bin/node --version)" == "v$NODE_VERSION" ]]; then
        printf '  Node.js %s already installed\n' "$NODE_VERSION"
        return
    fi
    temporary_directory
    local archive="$INSTALL_TEMP/$archive_name"
    download_checked "https://nodejs.org/dist/v$NODE_VERSION/$archive_name" "$NODE_SHA" "$archive"
    tar -xJf "$archive" -C "$INSTALL_TEMP"
    mkdir -p "$OSR_TOOL_ROOT"
    [[ ! -e "$OSR_NODE_ROOT" ]] \
        || fail "$OSR_NODE_ROOT exists but is not a valid Node.js $NODE_VERSION installation"
    cp -a "$INSTALL_TEMP/node-v$NODE_VERSION-linux-$NODE_ARCH" "$OSR_NODE_ROOT"
}

install_rust() {
    note "Installing Rust $RUST_VERSION and the WebAssembly target"
    if (( DRY_RUN )); then
        print_command curl --proto '=https' --tlsv1.2 --fail --location --output /tmp/rustup-init.sh https://sh.rustup.rs
        print_command sh /tmp/rustup-init.sh --default-toolchain none -y
        print_command rustup toolchain install "$RUST_VERSION" --profile minimal \
            --component clippy --component rustfmt --target wasm32-unknown-unknown
        return
    fi
    if ! command -v rustup >/dev/null 2>&1; then
        temporary_directory
        curl --proto '=https' --tlsv1.2 --fail --location --retry 3 \
            --output "$INSTALL_TEMP/rustup-init.sh" https://sh.rustup.rs
        sh "$INSTALL_TEMP/rustup-init.sh" --default-toolchain none -y
        export PATH="${HOME}/.cargo/bin:$PATH"
    fi
    rustup toolchain install "$RUST_VERSION" --profile minimal \
        --component clippy --component rustfmt --target wasm32-unknown-unknown
}

install_trunk() {
    note "Installing Trunk $TRUNK_VERSION"
    local archive_name="trunk-$UV_TARGET.tar.gz"
    if (( DRY_RUN )); then
        download_checked \
            "https://github.com/trunk-rs/trunk/releases/download/v$TRUNK_VERSION/$archive_name" \
            "$TRUNK_SHA" "/tmp/$archive_name"
        print_command install -m 0755 trunk "$OSR_TOOL_BIN/trunk"
        return
    fi
    mkdir -p "$OSR_TOOL_BIN"
    if [[ -x "$OSR_TOOL_BIN/trunk" ]] \
        && [[ "$($OSR_TOOL_BIN/trunk --version | awk '{print $2}')" == "$TRUNK_VERSION" ]]; then
        printf '  Trunk %s already installed\n' "$TRUNK_VERSION"
        return
    fi
    temporary_directory
    local archive="$INSTALL_TEMP/$archive_name"
    download_checked \
        "https://github.com/trunk-rs/trunk/releases/download/v$TRUNK_VERSION/$archive_name" \
        "$TRUNK_SHA" "$archive"
    tar -xzf "$archive" -C "$INSTALL_TEMP"
    install -m 0755 "$INSTALL_TEMP/trunk" "$OSR_TOOL_BIN/trunk"
}

install_python_environment() {
    note "Creating the Python design environment"
    if (( DRY_RUN )); then
        print_command uv python install "$PYTHON_VERSION"
        print_command uv venv --python "$PYTHON_VERSION" --seed "$ROOT/.venv"
        print_command uv pip install --python "$ROOT/.venv/bin/python" pytest \
            --editable "$ROOT/design-py[geotiff,batch]" \
            --editable "$ROOT/mechanical-py[test]" \
            --editable "$ROOT/tools/osr-aln-convert[test]" \
            --editable "$ROOT/tools/reference-ma"
        return
    fi
    uv python install "$PYTHON_VERSION"
    if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
        uv venv --python "$PYTHON_VERSION" --seed "$ROOT/.venv"
    elif ! "$ROOT/.venv/bin/python" -c \
        'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)'; then
        fail "$ROOT/.venv uses Python older than 3.11; move it aside and rerun the installer"
    fi
    uv pip install --python "$ROOT/.venv/bin/python" pytest \
        --editable "$ROOT/design-py[geotiff,batch]" \
        --editable "$ROOT/mechanical-py[test]" \
        --editable "$ROOT/tools/osr-aln-convert[test]" \
        --editable "$ROOT/tools/reference-ma"
}

install_node_environment() {
    note "Installing pinned browser-test packages"
    if (( DRY_RUN )); then
        print_command npm ci
        if [[ "$DISTRO_FAMILY" == "debian" ]]; then
            print_command npx playwright install --with-deps chromium
        else
            print_command npx playwright install chromium
        fi
    else
        (cd "$ROOT" && npm ci)
        if [[ "$DISTRO_FAMILY" == "debian" ]]; then
            (cd "$ROOT" && npx playwright install --with-deps chromium)
        else
            # Playwright's dependency helper is apt-specific. Red Hat desktop
            # installations normally carry Chromium's libraries already; the
            # browser itself is still pinned by package-lock.json.
            (cd "$ROOT" && npx playwright install chromium)
        fi
    fi
}

install_engineering_environment() {
    note "Installing the optional engineering desktop and solver environment"
    local applications=(
        org.freecad.FreeCAD
        org.blender.Blender
        org.qgis.qgis
        org.cloudcompare.CloudCompare
        org.eclipse.sumo
    )
    run flatpak remote-add --user --if-not-exists flathub "$FLATHUB_URL"
    run flatpak install --user --noninteractive -y flathub "${applications[@]}"
    if (( DRY_RUN )); then
        print_command flatpak run org.blender.Blender --command extension install --sync --enable bonsai
    elif flatpak run org.blender.Blender -b --python-expr \
        'import importlib.metadata; print(importlib.metadata.version("bonsai"))' \
        >/dev/null 2>&1; then
        printf '  Blender Bonsai extension already installed\n'
    else
        run flatpak run org.blender.Blender --command extension install --sync --enable bonsai
    fi
    if (( DRY_RUN )); then
        print_command uv pip install --python "$ROOT/.venv/bin/python" \
            --requirement "$ROOT/engineering/toolchain/python-requirements.txt"
    else
        uv pip install --python "$ROOT/.venv/bin/python" \
            --requirement "$ROOT/engineering/toolchain/python-requirements.txt"
        mkdir -p "$ROOT/build/engineering/toolchain"
        uv pip freeze --python "$ROOT/.venv/bin/python" \
            > "$ROOT/build/engineering/toolchain/pip-freeze.txt"
    fi
}

build_platform() {
    if (( ! BUILD )); then
        return 0
    fi
    note "Building the Workbench and command-line applications"
    if (( DRY_RUN )); then
        print_command npm run frontend:build
        print_command cargo build --release --bin osr-sim --bin osr-design
    else
        (cd "$ROOT" && npm run frontend:build)
        (cd "$ROOT" && cargo build --release --bin osr-sim --bin osr-design)
    fi
}

check_command() {
    local command_name="$1"
    if command -v "$command_name" >/dev/null 2>&1; then
        printf '  ok       %s\n' "$command_name"
    else
        printf '  missing  %s\n' "$command_name"
        CHECK_FAILED=1
    fi
}

check_installation() {
    activate_toolchain
    note "Checking the $PROFILE installation"
    CHECK_FAILED=0
    for command_name in git curl rustup cargo rustc node npm uv trunk python3; do
        check_command "$command_name"
    done
    if [[ -x "$ROOT/.venv/bin/python" ]]; then
        "$ROOT/.venv/bin/python" -c 'import numpy, requests, osr_planner, osr_mech, osr_aln, reference_ma'
        printf '  ok       Python project packages\n'
    else
        printf '  missing  %s\n' "$ROOT/.venv/bin/python"
        CHECK_FAILED=1
    fi
    rustup target list --installed --toolchain "$RUST_VERSION" \
        | grep -qx wasm32-unknown-unknown \
        || { printf '  missing  wasm32-unknown-unknown for Rust %s\n' "$RUST_VERSION"; CHECK_FAILED=1; }
    [[ "$(node --version 2>/dev/null)" == "v$NODE_VERSION" ]] \
        || { printf '  wrong    Node.js (expected v%s)\n' "$NODE_VERSION"; CHECK_FAILED=1; }
    [[ "$(trunk --version 2>/dev/null | awk '{print $2}')" == "$TRUNK_VERSION" ]] \
        || { printf '  wrong    Trunk (expected %s)\n' "$TRUNK_VERSION"; CHECK_FAILED=1; }
    if npx playwright install --list 2>/dev/null | grep -q 'chromium'; then
        printf '  ok       Playwright Chromium\n'
    else
        printf '  missing  Playwright Chromium\n'
        CHECK_FAILED=1
    fi

    if [[ "$PROFILE" == "engineering" ]]; then
        for app_id in org.freecad.FreeCAD org.blender.Blender org.qgis.qgis \
            org.cloudcompare.CloudCompare org.eclipse.sumo; do
            if flatpak info --user "$app_id" >/dev/null 2>&1 \
                || flatpak info --system "$app_id" >/dev/null 2>&1; then
                printf '  ok       %s\n' "$app_id"
            else
                printf '  missing  %s\n' "$app_id"
                CHECK_FAILED=1
            fi
        done
        "$ROOT/.venv/bin/python" -c \
            'import ifcopenshell, jupedsim, openseespy, pandapower, pvlib, pybamm, pyswmm' \
            || { printf '  missing  engineering Python package(s)\n'; CHECK_FAILED=1; }
        flatpak run org.blender.Blender -b --python-expr \
            'import importlib.metadata; print(importlib.metadata.version("bonsai"))' \
            >/dev/null 2>&1 \
            || { printf '  missing  Blender Bonsai extension\n'; CHECK_FAILED=1; }
    fi

    (( CHECK_FAILED == 0 )) || fail "installation check failed"
    printf '\nOpenSourceRail installation check passed.\n'
}

main() {
    parse_arguments "$@"
    detect_distribution
    detect_architecture
    activate_toolchain

    if [[ "$ACTION" == "check" ]]; then
        check_installation
        return
    fi

    printf 'OpenSourceRail Linux installer\n'
    printf '  profile:       %s\n' "$PROFILE"
    printf '  distribution:  %s (%s)\n' "$DISTRO_FAMILY" "$PACKAGE_MANAGER"
    printf '  architecture:  %s\n' "$ARCH"
    printf '  tool root:     %s\n' "$OSR_TOOL_ROOT"

    install_native_packages
    install_uv
    install_node
    install_rust
    install_trunk
    activate_toolchain
    install_python_environment
    install_node_environment
    if [[ "$PROFILE" == "engineering" ]]; then
        install_engineering_environment
    fi
    build_platform

    if (( DRY_RUN )); then
        printf '\nDry run complete; no changes were made.\n'
        return
    fi

    check_installation
    printf '\nInstalled. Start the integrated GUI with:\n  ./scripts/osr workbench\n'
    if (( RUN_AFTER )); then
        exec "$ROOT/scripts/osr" workbench
    fi
}

main "$@"
