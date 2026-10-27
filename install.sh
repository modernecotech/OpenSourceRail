#!/usr/bin/env bash
# Check, install, and run OpenSourceRail with one command.
set -euo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly TOOL_ROOT="${HOME}/.local/share/opensource-rail/toolchains"
readonly TOOL_BIN="$TOOL_ROOT/bin"
readonly NODE_VERSION="22.23.2"
readonly NODE_ROOT="$TOOL_ROOT/node-v$NODE_VERSION"
readonly RUST_VERSION="1.92.0"
readonly UV_VERSION="0.11.20"
readonly PYTHON_VERSION="3.11.13"
readonly PLAYWRIGHT_ROOT="$TOOL_ROOT/playwright"
readonly FLATHUB_URL="https://dl.flathub.org/repo/flathub.flatpakrepo"

INSTALL_TEMP=""
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
            NODE_SHA="d60acfe00a2932254bb0ad20e01b0d74397a0875595de719654b214f4b03f307"
            UV_SHA="5de211d9278af365497d387e25316907b3b4a9f25b4476dd6dbf238d6f85cff3"
            ;;
        aarch64|arm64)
            ARCH="aarch64"
            NODE_ARCH="arm64"
            UV_TARGET="aarch64-unknown-linux-gnu"
            NODE_SHA="fff4078c5def658577f92c88db7db3bc0072924bfb93fe52c1e744a54e94abb8"
            UV_SHA="c8b5b7f9c804b640da0bb66cddddf0a00ce971f64d8076622d70bd141bc80857"
            ;;
        *)
            fail "supported CPU architectures are x86_64 and aarch64"
            ;;
    esac
}

activate_toolchain() {
    export PATH="$ROOT/.venv/bin:$TOOL_BIN:$NODE_ROOT/bin:${HOME}/.cargo/bin:$PATH"
    export PLAYWRIGHT_BROWSERS_PATH="$PLAYWRIGHT_ROOT"
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
        && "$command_name" --version 2>/dev/null | head -n 1 | grep -Fq "$expected"
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
    [[ -x "$ROOT/.venv/bin/python" ]] \
        && "$ROOT/.venv/bin/python" -c \
            'import cairosvg, mistune, numpy, scipy, matplotlib, PIL, reportlab, pytest' \
            >/dev/null 2>&1
}

rust_ready() {
    command -v rustup >/dev/null 2>&1 \
        && rustup toolchain list | grep -q "^$RUST_VERSION"
}

node_packages_ready() {
    local stamp="$ROOT/node_modules/.osr-package-lock.sha256"
    [[ -f "$stamp" && -f "$ROOT/package-lock.json" ]] || return 1
    [[ "$(<"$stamp")" == "$(sha256sum "$ROOT/package-lock.json" | cut -d' ' -f1)" ]]
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
    command_version_is node "v$NODE_VERSION" && status_line "Node.js $NODE_VERSION" yes \
        || status_line "Node.js $NODE_VERSION" no
    command_version_is uv "$UV_VERSION" && status_line "uv $UV_VERSION" yes \
        || status_line "uv $UV_VERSION" no
    rust_ready && status_line "Rust $RUST_VERSION" yes \
        || status_line "Rust $RUST_VERSION" no
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
        --output "$output" "$url"
    printf '%s  %s\n' "$expected_sha" "$output" | sha256sum --check --status \
        || fail "checksum mismatch for $url"
}

install_uv() {
    command_version_is uv "$UV_VERSION" && return
    section "Installing uv $UV_VERSION in your home folder"
    temporary_directory
    mkdir -p "$TOOL_BIN"
    local archive="$INSTALL_TEMP/uv.tar.gz"
    download_checked \
        "https://github.com/astral-sh/uv/releases/download/$UV_VERSION/uv-$UV_TARGET.tar.gz" \
        "$UV_SHA" "$archive"
    tar -xzf "$archive" -C "$INSTALL_TEMP"
    install -m 0755 "$INSTALL_TEMP/uv-$UV_TARGET/uv" "$TOOL_BIN/uv"
    install -m 0755 "$INSTALL_TEMP/uv-$UV_TARGET/uvx" "$TOOL_BIN/uvx"
}

install_node() {
    command_version_is node "v$NODE_VERSION" && return
    section "Installing Node.js $NODE_VERSION in your home folder"
    temporary_directory
    local archive_name="node-v$NODE_VERSION-linux-$NODE_ARCH.tar.xz"
    local archive="$INSTALL_TEMP/$archive_name"
    download_checked "https://nodejs.org/dist/v$NODE_VERSION/$archive_name" \
        "$NODE_SHA" "$archive"
    tar -xJf "$archive" -C "$INSTALL_TEMP"
    mkdir -p "$TOOL_ROOT"
    if [[ -e "$NODE_ROOT" ]]; then
        fail "$NODE_ROOT exists but is not the required Node.js release"
    fi
    cp -a "$INSTALL_TEMP/node-v$NODE_VERSION-linux-$NODE_ARCH" "$NODE_ROOT"
}

install_rust() {
    rust_ready && return
    section "Installing Rust $RUST_VERSION in your home folder"
    if ! command -v rustup >/dev/null 2>&1; then
        temporary_directory
        curl --proto '=https' --tlsv1.2 --fail --location --retry 3 \
            --output "$INSTALL_TEMP/rustup-init.sh" https://sh.rustup.rs
        sh "$INSTALL_TEMP/rustup-init.sh" --default-toolchain none -y
        export PATH="${HOME}/.cargo/bin:$PATH"
    fi
    rustup toolchain install "$RUST_VERSION" --profile minimal \
        --component clippy --component rustfmt
}

install_python() {
    python_ready && return
    section "Installing Python design packages"
    uv python install "$PYTHON_VERSION"
    if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
        uv venv --python "$PYTHON_VERSION" --seed "$ROOT/.venv"
    elif ! "$ROOT/.venv/bin/python" -c \
        'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)'; then
        fail "$ROOT/.venv uses Python older than 3.11; move it aside and rerun setup"
    fi
    uv pip install --python "$ROOT/.venv/bin/python" pytest \
        --requirement "$ROOT/engineering/requirements.txt"
}

install_node_packages() {
    node_packages_ready && return
    section "Installing JavaScript packages"
    (cd "$ROOT" && npm ci)
    sha256sum "$ROOT/package-lock.json" | cut -d' ' -f1 \
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
    (cd "$ROOT" && cargo build --locked --release -p osr-atp --example wheel_station_contract)
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
    command_version_is node "v$NODE_VERSION" || fail "Node.js installation failed"
    command_version_is uv "$UV_VERSION" || fail "uv installation failed"
    rust_ready || fail "Rust installation failed"
    python_ready || fail "Python package installation failed"
    node_packages_ready || fail "JavaScript package installation failed"
    playwright_ready || fail "Playwright browser installation failed"
    build_ready || fail "application build failed"
}

main() {
    (( $# == 0 )) || fail "run ./install.sh without options"
    detect_host
    activate_toolchain

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

main "$@"
