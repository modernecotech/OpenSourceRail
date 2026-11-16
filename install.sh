#!/usr/bin/env bash
# Check, install, and run OpenSourceRail with one command.
set -euo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly TOOL_ROOT="${HOME}/.local/share/opensource-rail/toolchains"
readonly TOOL_BIN="$TOOL_ROOT/bin"
readonly RUST_CHANNEL="stable"
readonly PYTHON_VERSION="3.11"
readonly PLAYWRIGHT_ROOT="$TOOL_ROOT/playwright"
readonly FLATHUB_URL="https://dl.flathub.org/repo/flathub.flatpakrepo"

INSTALL_TEMP=""
INSTALL_STAGE=""
NODE_VERSION=""
UV_VERSION=""
# Bootstrap resolution uses only Bash, curl and the official release checksum files.
# shellcheck source=tools/automation/toolchain-release.sh
source "$ROOT/tools/automation/toolchain-release.sh"
DISTRO_FAMILY=""
PACKAGE_MANAGER=""

fail() {
    printf 'Setup error: %s\n' "$*" >&2
    exit 1
}

section() {
    printf '\n==> %s\n' "$*"
}

cleanup() {
    if [[ -n "$INSTALL_TEMP" && -d "$INSTALL_TEMP" ]]; then
        rm -rf -- "$INSTALL_TEMP"
    fi
    if [[ -n "$INSTALL_STAGE" && -d "$INSTALL_STAGE" ]]; then
        rm -rf -- "$INSTALL_STAGE"
    fi
}
trap cleanup EXIT

temporary_directory() {
    if [[ -z "$INSTALL_TEMP" ]]; then
        INSTALL_TEMP="$(mktemp -d -t osr-install.XXXXXXXX)"
    fi
}

confirm() {
    local prompt="$1"
    local interactive_default="$2"
    local unattended_default="$3"
    local reply=""
    local suffix="[y/N]"
    [[ "$interactive_default" == "yes" ]] && suffix="[Y/n]"

    if [[ -t 0 ]]; then
        read -r -p "$prompt $suffix " reply
        [[ -n "$reply" ]] || reply="$interactive_default"
    elif IFS= read -r reply; then
        [[ -n "$reply" ]] || reply="$unattended_default"
    else
        reply="$unattended_default"
    fi
    [[ "$reply" =~ ^([Yy]|[Yy][Ee][Ss])$ ]]
}

detect_host() {
    [[ "$(uname -s)" == "Linux" ]] || fail "this installer supports Linux"
    [[ -r /etc/os-release ]] || fail "/etc/os-release is missing"
    # shellcheck disable=SC1091
    source /etc/os-release
    case " ${ID:-} ${ID_LIKE:-} " in
        *" debian "*|*" ubuntu "*)
            DISTRO_FAMILY="debian"
            PACKAGE_MANAGER="apt-get"
            ;;
        *" rhel "*|*" fedora "*|*" centos "*)
            DISTRO_FAMILY="redhat"
            if command -v dnf >/dev/null 2>&1; then
                PACKAGE_MANAGER="dnf"
            else
                PACKAGE_MANAGER="yum"
            fi
            ;;
        *" suse "*|*" opensuse "*)
            DISTRO_FAMILY="suse"
            PACKAGE_MANAGER="zypper"
            ;;
        *" arch "*)
            DISTRO_FAMILY="arch"
            PACKAGE_MANAGER="pacman"
            ;;
        *)
            fail "supported Linux families use apt-get, dnf, yum, zypper, or pacman"
            ;;
    esac
    command -v "$PACKAGE_MANAGER" >/dev/null 2>&1 \
        || fail "$PACKAGE_MANAGER is missing"

    case "$(uname -m)" in
        x86_64|amd64)
            ARCH="x86_64"
            NODE_ARCH="x64"
            UV_TARGET="x86_64-unknown-linux-gnu"
            ;;
        aarch64|arm64)
            ARCH="aarch64"
            NODE_ARCH="arm64"
            UV_TARGET="aarch64-unknown-linux-gnu"
            ;;
        *)
            fail "supported CPU architectures are x86_64 and aarch64"
            ;;
    esac
}

activate_toolchain() {
    local node_path="" uv_path="" tool_path
    tool_path="$ROOT/.venv/bin:$TOOL_BIN:${HOME}/.cargo/bin:$PATH"
    node_path="$(osr_receipt_binary "$TOOL_ROOT" node)" || true
    uv_path="$(osr_receipt_binary "$TOOL_ROOT" uv)" || true
    [[ -z "$node_path" ]] || tool_path="$(dirname "$node_path"):$tool_path"
    [[ -z "$uv_path" ]] || tool_path="$(dirname "$uv_path"):$tool_path"
    export PATH="$tool_path"
    export PLAYWRIGHT_BROWSERS_PATH="$PLAYWRIGHT_ROOT"
}

installed_tool_ready() {
    local tool="$1" path version arch archive_sha binary_sha
    path="$(osr_verify_receipt_binary "$TOOL_ROOT" "$tool")" || return 1
    IFS=$'\t' read -r version arch archive_sha binary_sha < "$TOOL_ROOT/$tool-current.receipt"
    [[ "$tool" != uv || -x "$(dirname "$path")/uvx" ]] || return 1
    command_version_is "$path" "$version"
}

existing_release_ready() {
    local tool="$1" version="$2" arch="$3" sha="$4" path recorded_version recorded_arch recorded_sha binary_sha
    path="$(osr_verify_receipt_binary "$TOOL_ROOT" "$tool")" || return 1
    IFS=$'\t' read -r recorded_version recorded_arch recorded_sha binary_sha < "$TOOL_ROOT/$tool-current.receipt"
    [[ "$recorded_version" == "$version" && "$recorded_arch" == "$arch" && "$recorded_sha" == "$sha" ]] || return 1
    command_version_is "$path" "$version"
}

write_tool_receipt() {
    local tool="$1" version="$2" arch="$3" archive_sha="$4" binary_sha="$5" temporary
    temporary="$(mktemp "$TOOL_ROOT/.$tool-receipt.XXXXXXXX")"
    printf '%s\t%s\t%s\t%s\n' "$version" "$arch" "$archive_sha" "$binary_sha" > "$temporary"
    chmod 0600 "$temporary"
    mv -f -- "$temporary" "$TOOL_ROOT/$tool-current.receipt"
}

status_line() {
    local label="$1"
    local available="$2"
    if [[ "$available" == "yes" ]]; then
        printf '  ready    %s\n' "$label"
    else
        printf '  missing  %s\n' "$label"
    fi
}

command_version_is() {
    local command_name="$1"
    local expected="$2"
    command -v "$command_name" >/dev/null 2>&1 \
        && "$command_name" --version 2>/dev/null | head -n 1 | awk -v expected="$expected" \
            '{ for (i = 1; i <= NF; i++) if ($i == expected) found = 1 } END { exit !found }'
}

native_ready() {
    local command_name
    for command_name in curl git tar xz sha256sum cc c++ make pkg-config ffmpeg pdftotext fc-match; do
        command -v "$command_name" >/dev/null 2>&1 || return 1
    done
    fc-match DejaVuSans >/dev/null 2>&1 || return 1
    pkg-config --exists cairo || return 1
}

python_ready() {
    [[ -x "$ROOT/.venv/bin/python" ]] || return 1
    "$ROOT/.venv/bin/python" - "$ROOT/engineering/requirements.txt" <<'PY' >/dev/null 2>&1
import importlib
from importlib import metadata
from pathlib import Path
import sys

from packaging.requirements import Requirement

for line in Path(sys.argv[1]).read_text().splitlines():
    line = line.split('#', 1)[0].strip()
    if not line:
        continue
    requirement = Requirement(line)
    if metadata.version(requirement.name) not in requirement.specifier:
        raise SystemExit(1)

for module in ('cairosvg', 'mistune', 'numpy', 'scipy', 'matplotlib',
               'PIL', 'reportlab', 'pytest', 'ifcopenshell', 'ifctester', 'gmsh'):
    importlib.import_module(module)
PY
}

rust_ready() {
    command -v rustup >/dev/null 2>&1 \
        && rustup run "$RUST_CHANNEL" rustc --version >/dev/null 2>&1 \
        && rustup run "$RUST_CHANNEL" cargo --version >/dev/null 2>&1
}

node_packages_ready() {
    local stamp="$ROOT/node_modules/.osr-package-lock.sha256"
    [[ -f "$stamp" && -f "$ROOT/package-lock.json" ]] || return 1
    [[ "$(<"$stamp")" == "$(node --version) $(sha256sum "$ROOT/package-lock.json" | cut -d' ' -f1)" ]]
}

playwright_ready() {
    command -v npx >/dev/null 2>&1 \
        && npx playwright install --list 2>/dev/null | grep -q chromium
}

build_ready() {
    [[ -x "$ROOT/target/release/examples/wheel_station_contract" \
        && -f "$ROOT/docs/workbench/current/index.html" ]]
}

show_core_status() {
    section "Current installation"
    native_ready && status_line "Linux build libraries" yes \
        || status_line "Linux build libraries" no
    installed_tool_ready node && status_line "Node.js (receipt)" yes \
        || status_line "Node.js (receipt)" no
    installed_tool_ready uv && status_line "uv (receipt)" yes \
        || status_line "uv (receipt)" no
    rust_ready && status_line "Rust stable ($(rustup run "$RUST_CHANNEL" rustc --version))" yes \
        || status_line "Rust stable" no
    python_ready && status_line "Python design packages" yes \
        || status_line "Python design packages" no
    node_packages_ready && status_line "JavaScript packages" yes \
        || status_line "JavaScript packages" no
    playwright_ready && status_line "Playwright Chromium" yes \
        || status_line "Playwright Chromium" no
    build_ready && status_line "Current wheel/LIM design and Workbench" yes \
        || status_line "Current wheel/LIM design and Workbench" no
}

run_root() {
    if (( EUID == 0 )); then
        "$@"
    else
        command -v sudo >/dev/null 2>&1 || fail "sudo is needed for missing Linux libraries"
        sudo "$@"
    fi
}

install_native_packages() {
    native_ready && return
    section "Installing missing Linux libraries"
    case "$DISTRO_FAMILY" in
        debian)
            run_root apt-get update
            run_root env DEBIAN_FRONTEND=noninteractive apt-get install -y \
                ca-certificates curl git build-essential pkg-config libcairo2-dev libssl-dev tar xz-utils ffmpeg poppler-utils fonts-dejavu-core fontconfig
            ;;
        redhat)
            run_root "$PACKAGE_MANAGER" install -y \
                ca-certificates cairo-devel curl git gcc gcc-c++ make pkgconf-pkg-config openssl-devel tar xz ffmpeg poppler-utils dejavu-sans-fonts fontconfig
            ;;
        suse)
            run_root zypper --non-interactive install \
                ca-certificates cairo-devel curl git gcc gcc-c++ make pkg-config libopenssl-devel tar xz ffmpeg poppler-tools dejavu-fonts fontconfig
            ;;
        arch)
            run_root pacman --sync --refresh --needed --noconfirm \
                ca-certificates cairo curl git base-devel pkgconf openssl tar xz ffmpeg poppler ttf-dejavu fontconfig
            ;;
    esac
}

download_checked() {
    local url="$1"
    local expected_sha="$2"
    local output="$3"
    curl --proto '=https' --tlsv1.2 --fail --location --retry 3 \
        --max-time 600 --max-filesize 314572800 \
        --output "$output" "$url"
    printf '%s  %s\n' "$expected_sha" "$output" | sha256sum --check --status \
        || fail "checksum mismatch for $url"
}

install_uv() {
    local version sha url target_root archive binary_sha release
    release="$(osr_resolve_uv "$UV_TARGET")" || fail "cannot resolve the latest stable uv release"
    IFS=$'\t' read -r version sha url <<< "$release"
    [[ -n "$version" && -n "$sha" && -n "$url" ]] || fail "incomplete uv release receipt"
    UV_VERSION="$version"
    target_root="$TOOL_ROOT/uv-$version"
    section "Installing current uv $version in your home folder"
    mkdir -p "$TOOL_ROOT"
    if [[ -d "$target_root" ]]; then
        existing_release_ready uv "$version" "$UV_TARGET" "$sha" \
            || fail "existing uv directory lacks a matching verified release receipt"
        command_version_is "$target_root/bin/uvx" "$version" || fail "existing uvx differs"
    else
        temporary_directory
        archive="$INSTALL_TEMP/uv-$version.tar.gz"
        download_checked "$url" "$sha" "$archive"
        INSTALL_STAGE="$(mktemp -d "$TOOL_ROOT/.uv-stage.XXXXXXXX")"
        tar -xzf "$archive" -C "$INSTALL_STAGE" --no-same-owner \
            "uv-$UV_TARGET/uv" "uv-$UV_TARGET/uvx"
        mkdir -p "$INSTALL_STAGE/bin"
        install -m 0755 "$INSTALL_STAGE/uv-$UV_TARGET/uv" "$INSTALL_STAGE/bin/uv"
        install -m 0755 "$INSTALL_STAGE/uv-$UV_TARGET/uvx" "$INSTALL_STAGE/bin/uvx"
        rm -rf -- "$INSTALL_STAGE/uv-$UV_TARGET"
        command_version_is "$INSTALL_STAGE/bin/uv" "$version" || fail "uv archive version differs"
        mv -- "$INSTALL_STAGE" "$target_root"
        INSTALL_STAGE=""
    fi
    binary_sha="$(sha256sum "$target_root/bin/uv" | cut -d' ' -f1)"
    write_tool_receipt uv "$version" "$UV_TARGET" "$sha" "$binary_sha"
    activate_toolchain
}

install_node() {
    local version sha url archive_name target_root archive binary_sha release
    release="$(osr_resolve_node "$NODE_ARCH")" || fail "cannot resolve the latest Node.js LTS release"
    IFS=$'\t' read -r version sha url <<< "$release"
    [[ -n "$version" && -n "$sha" && -n "$url" ]] || fail "incomplete Node.js release receipt"
    NODE_VERSION="$version"
    target_root="$TOOL_ROOT/node-$version"
    section "Installing current Node.js LTS $version in your home folder"
    mkdir -p "$TOOL_ROOT"
    if [[ -d "$target_root" ]]; then
        existing_release_ready node "$version" "$NODE_ARCH" "$sha" \
            || fail "existing Node.js directory lacks a matching verified release receipt"
    else
        temporary_directory
        archive_name="node-$version-linux-$NODE_ARCH.tar.xz"
        archive="$INSTALL_TEMP/$archive_name"
        download_checked "$url" "$sha" "$archive"
        INSTALL_STAGE="$(mktemp -d "$TOOL_ROOT/.node-stage.XXXXXXXX")"
        tar -xJf "$archive" -C "$INSTALL_STAGE" --no-same-owner
        command_version_is "$INSTALL_STAGE/node-$version-linux-$NODE_ARCH/bin/node" "$version" \
            || fail "Node.js archive version differs"
        mv -- "$INSTALL_STAGE/node-$version-linux-$NODE_ARCH" "$target_root"
        rm -rf -- "$INSTALL_STAGE"
        INSTALL_STAGE=""
    fi
    binary_sha="$(sha256sum "$target_root/bin/node" | cut -d' ' -f1)"
    write_tool_receipt node "$version" "$NODE_ARCH" "$sha" "$binary_sha"
    activate_toolchain
}

install_rust() {
    section "Refreshing Rust stable in your home folder"
    if ! command -v rustup >/dev/null 2>&1; then
        temporary_directory
        curl --proto '=https' --tlsv1.2 --fail --location --retry 3 \
            --output "$INSTALL_TEMP/rustup-init.sh" https://sh.rustup.rs
        sh "$INSTALL_TEMP/rustup-init.sh" --default-toolchain none -y
        export PATH="${HOME}/.cargo/bin:$PATH"
    fi
    rustup update "$RUST_CHANNEL" --no-self-update
    rustup component add --toolchain "$RUST_CHANNEL" clippy rustfmt
}

install_python() {
    local force_refresh="${1:-false}"
    if [[ "$force_refresh" != true ]] && python_ready; then return; fi
    section "Refreshing Python design packages"
    uv python install --upgrade "$PYTHON_VERSION"
    if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
        uv venv --python "$PYTHON_VERSION" --seed "$ROOT/.venv"
    elif ! "$ROOT/.venv/bin/python" -c \
        'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)'; then
        fail "$ROOT/.venv uses Python older than 3.11; move it aside and rerun setup"
    fi
    uv pip install --upgrade --no-cache --python "$ROOT/.venv/bin/python" \
        --requirement "$ROOT/engineering/requirements.txt"
    python_ready || fail "Python requirements remain unsatisfied after refresh"
}

install_node_packages() {
    node_packages_ready && return
    section "Installing JavaScript packages"
    (cd "$ROOT" && npm ci)
    printf '%s %s\n' "$(node --version)" "$(sha256sum "$ROOT/package-lock.json" | cut -d' ' -f1)" \
        > "$ROOT/node_modules/.osr-package-lock.sha256"
}

install_playwright() {
    playwright_ready && return
    section "Installing the browser used by deterministic GUI tests"
    if [[ "$DISTRO_FAMILY" == "debian" ]]; then
        (cd "$ROOT" && npx playwright install --with-deps chromium)
    else
        (cd "$ROOT" && npx playwright install chromium)
    fi
}

build_platform() {
    section "Building wheel/station control method kernels"
    (cd "$ROOT" && cargo build --locked --release --jobs "${OSR_CARGO_JOBS:-2}" -p osr-atp --example wheel_station_contract)
    (cd "$ROOT" && ./osr verify)
}

engineering_ready() {
    command -v flatpak >/dev/null 2>&1 || return 1
    flatpak info --user org.freecad.FreeCAD >/dev/null 2>&1 \
        || flatpak info --system org.freecad.FreeCAD >/dev/null 2>&1
}

install_engineering() {
    engineering_ready && return
    section "Installing FreeCAD for native geometry generation"
    command -v flatpak >/dev/null 2>&1 || fail "install Flatpak using your distribution package manager first"
    flatpak remote-add --user --if-not-exists flathub "$FLATHUB_URL"
    flatpak install --user --noninteractive -y flathub org.freecad.FreeCAD
}

verify_core() {
    activate_toolchain
    native_ready || fail "Linux build libraries are incomplete"
    installed_tool_ready node || fail "Node.js installation receipt failed"
    installed_tool_ready uv || fail "uv installation receipt failed"
    rust_ready || fail "Rust installation failed"
    python_ready || fail "Python package installation failed"
    node_packages_ready || fail "JavaScript package installation failed"
    playwright_ready || fail "Playwright browser installation failed"
    build_ready || fail "application build failed"
}

main() {
    local toolchains_only=false refresh_python=false tool
    if [[ "${1:-}" == --help || "${1:-}" == -h ]]; then
        printf 'Usage: ./install.sh [--toolchains-only | --refresh-python]\n  --toolchains-only  Refresh Node LTS, uv stable and Rust stable; skip project rebuilds.\n  --refresh-python   Refresh Python design packages to newest compatible wheels; skip project rebuilds.\n'
        return
    fi
    if [[ $# -eq 1 && "$1" == --toolchains-only ]]; then
        toolchains_only=true
    elif [[ $# -eq 1 && "$1" == --refresh-python ]]; then
        refresh_python=true
    elif (( $# != 0 )); then
        fail "usage: ./install.sh [--toolchains-only | --refresh-python]"
    fi
    detect_host
    activate_toolchain

    if [[ "$toolchains_only" == true ]]; then
        for tool in curl tar xz sha256sum; do
            command -v "$tool" >/dev/null 2>&1 || fail "$tool is needed for toolchain refresh"
        done
        install_uv
        install_node
        install_rust
        activate_toolchain
        installed_tool_ready uv && installed_tool_ready node && rust_ready \
            || fail "toolchain refresh verification failed"
        printf 'Current Node LTS, uv stable and Rust stable are ready.\n'
        return
    fi

    if [[ "$refresh_python" == true ]]; then
        local available_bytes
        available_bytes="$(df -B1 --output=avail "$ROOT" | tail -n 1)"
        (( available_bytes >= 23622320128 )) || fail "Python refresh needs 22 GiB free to preserve the 20 GiB workspace floor"
        install_uv
        activate_toolchain
        install_python true
        printf 'Newest compatible Python design packages are ready. Record exact versions in each new evaluation.\n'
        return
    fi

    printf 'OpenSourceRail setup\n'
    printf '  Linux family: %s\n' "$DISTRO_FAMILY"
    printf '  Architecture: %s\n' "$ARCH"
    printf '  User tools:   %s\n' "$TOOL_ROOT"
    show_core_status

    if ! confirm "Install or refresh the core platform?" yes no; then
        printf '\nCheck complete. No changes were made.\n'
        return
    fi

    install_native_packages
    install_uv
    install_node
    install_rust
    activate_toolchain
    install_python
    install_node_packages
    install_playwright
    build_platform
    verify_core

    if engineering_ready; then
        printf '\nEngineering applications are already available.\n'
    elif confirm "Also install FreeCAD for native geometry?" no no; then
        install_engineering
        engineering_ready || fail "engineering application installation failed"
    else
        printf '\nOptional engineering applications were skipped.\n'
    fi

    printf '\nOpenSourceRail is ready.\n'
    if confirm "Start the Workbench now?" yes no; then
        exec "$ROOT/osr" workbench
    fi
    printf 'Start it later with: ./osr workbench\n'
    printf 'Refresh implemented primary design studies with: ./osr build\n'
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    main "$@"
fi
