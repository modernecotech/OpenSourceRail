#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
# shellcheck source=tools/automation/toolchain-release.sh
source "$ROOT/tools/automation/toolchain-release.sh"

fail() { printf 'toolchain test failed: %s\n' "$*" >&2; exit 1; }
assert_eq() { [[ "$1" == "$2" ]] || fail "expected [$2], got [$1]"; }

index=$'version\tdate\tfiles\tnpm\tv8\tuv\tzlib\topenssl\tmodules\tlts\tsecurity\n'\
$'v27.0.0-alpha.0\t2026-11-12\tlinux-x64,linux-arm64\t-\t-\t-\t-\t-\t-\t-\t-\n'\
$'v26.13.1\t2026-11-10\tlinux-x64,linux-arm64\t-\t-\t-\t-\t-\t-\tLithium\t-\n'\
$'v24.22.2\t2026-10-28\tlinux-x64,linux-arm64\t-\t-\t-\t-\t-\t-\tKrypton\t-'
assert_eq "$(osr_node_lts_from_index "$index" x64)" v26.13.1
assert_eq "$(osr_node_lts_from_index "$index" arm64)" v26.13.1
if osr_node_lts_from_index "$index" ppc64 >/dev/null; then fail 'unsupported Node architecture accepted'; fi
assert_eq "$(osr_uv_version_from_redirect 'https://github.com/astral-sh/uv/releases/tag/0.13.8')" 0.13.8
if osr_uv_version_from_redirect 'https://github.com/astral-sh/uv/releases/tag/0.14.0rc1' >/dev/null; then
    fail 'uv prerelease accepted'
fi
sha="$(printf '%064d' 0)"
assert_eq "$(osr_release_sha "$sha  archive.tar.gz" archive.tar.gz)" "$sha"
if osr_release_sha "$sha  other.tar.gz" archive.tar.gz >/dev/null; then fail 'wrong archive checksum accepted'; fi

tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT
mkdir -p "$tmp/repo/tools/automation" "$tmp/home/.local/share/opensource-rail/toolchains"
cp "$ROOT/osr" "$tmp/repo/osr"
cp "$ROOT/tools/automation/toolchain-release.sh" "$tmp/repo/tools/automation/toolchain-release.sh"
cat > "$tmp/repo/tools/automation/osr-python" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "${OSR_NODE_BINARY:-status-ok}"
EOF
chmod +x "$tmp/repo/osr" "$tmp/repo/tools/automation/osr-python"
HOME="$tmp/home" "$tmp/repo/osr" help >/dev/null || fail 'help needs an install'
assert_eq "$(HOME="$tmp/home" "$tmp/repo/osr" status)" status-ok
if HOME="$tmp/home" "$tmp/repo/osr" test >"$tmp/out" 2>"$tmp/err"; then fail 'missing receipt accepted for Node-dependent command'; fi
grep -q 'release receipt or installed binary is missing or invalid' "$tmp/err" || fail 'missing receipt reason absent'

case "$(uname -m)" in
    x86_64|amd64) arch=x64 ;;
    aarch64|arm64) arch=arm64 ;;
    *) fail 'unsupported test host' ;;
esac
tool_root="$tmp/home/.local/share/opensource-rail/toolchains"
mkdir -p "$tool_root/node-v26.13.1/bin"
cat > "$tool_root/node-v26.13.1/bin/node" <<'EOF'
#!/usr/bin/env bash
printf 'v26.13.1\n'
EOF
chmod +x "$tool_root/node-v26.13.1/bin/node"
binary_sha="$(sha256sum "$tool_root/node-v26.13.1/bin/node" | cut -d' ' -f1)"
printf 'v26.13.1\t%s\t%s\t%s\n' "$arch" "$sha" "$binary_sha" > "$tool_root/node-current.receipt"
assert_eq "$(HOME="$tmp/home" "$tmp/repo/osr" status)" "$tool_root/node-v26.13.1/bin/node"
assert_eq "$(HOME="$tmp/home" "$tmp/repo/osr" test)" "$tool_root/node-v26.13.1/bin/node"
printf '\n# changed\n' >> "$tool_root/node-v26.13.1/bin/node"
if HOME="$tmp/home" "$tmp/repo/osr" test >/dev/null 2>&1; then fail 'modified Node binary accepted'; fi
printf 'v26.13.1\twrong\t%s\t%s\n' "$sha" "$sha" > "$tool_root/node-current.receipt"
if HOME="$tmp/home" "$tmp/repo/osr" test >/dev/null 2>&1; then fail 'wrong receipt architecture accepted'; fi

PATH=/usr/bin:/bin HOME="$tmp/empty-home" bash -c '
    source "$1/install.sh"
    activate_toolchain
    [[ ":$PATH:" != *::* ]]
' bash "$ROOT" || fail 'fresh install PATH contains an empty entry'
assert_eq "$("$ROOT/install.sh" --help | head -n 1)" 'Usage: ./install.sh [--toolchains-only]'
PATH=/usr/bin:/bin HOME="$tmp/empty-home" bash -c '
    source "$1/install.sh"
    detect_host() { :; }
    install_uv() { printf "uv\n"; }
    install_node() { printf "node\n"; }
    install_rust() { printf "rust\n"; }
    installed_tool_ready() { return 0; }
    rust_ready() { return 0; }
    install_python() { exit 89; }
    install_node_packages() { exit 89; }
    build_platform() { exit 89; }
    main --toolchains-only
' bash "$ROOT" > "$tmp/toolchains-only.out" || fail 'toolchains-only dispatch failed'
assert_eq "$(head -n 3 "$tmp/toolchains-only.out")" $'uv\nnode\nrust'
printf 'toolchain release and launcher tests passed\n'
