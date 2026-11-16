#!/usr/bin/env bash
# Official install-time release resolution. Sourced by install.sh and osr.

osr_release_sha() {
    local text="$1" asset="$2" sha
    sha="$(printf '%s\n' "$text" | awk -v asset="$asset" '$2 == asset { print $1 }')"
    [[ "$sha" =~ ^[[:xdigit:]]{64}$ ]] || return 1
    printf '%s\n' "${sha,,}"
}

osr_node_lts_from_index() {
    local index="$1" arch="$2" version
    [[ "$arch" == x64 || "$arch" == arm64 ]] || return 1
    version="$(printf '%s\n' "$index" | awk -F '\t' -v arch="linux-$arch" '
        NR > 1 && $1 ~ /^v[0-9]+\.[0-9]+\.[0-9]+$/ && $10 != "-" && $10 != "" &&
        index("," $3 ",", "," arch ",") {
            split(substr($1, 2), p, ".")
            if (!found || p[1] > major || (p[1] == major && p[2] > minor) ||
                (p[1] == major && p[2] == minor && p[3] > patch)) {
                found=1; major=p[1]; minor=p[2]; patch=p[3]; version=$1
            }
        }
        END { if (found) print version }
    ')"
    [[ "$version" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] || return 1
    printf '%s\n' "$version"
}

osr_uv_version_from_redirect() {
    local url="$1" version
    [[ "$url" =~ ^https://github\.com/astral-sh/uv/releases/tag/([0-9]+\.[0-9]+\.[0-9]+)$ ]] || return 1
    version="${BASH_REMATCH[1]}"
    printf '%s\n' "$version"
}

osr_resolve_node() {
    local arch="$1" index version asset sums sha url
    index="$(curl --proto '=https' --tlsv1.2 --fail --location --silent --show-error \
        --retry 2 --max-time 30 --max-filesize 2097152 https://nodejs.org/dist/index.tab)" || return 1
    version="$(osr_node_lts_from_index "$index" "$arch")" || return 1
    asset="node-$version-linux-$arch.tar.xz"
    url="https://nodejs.org/dist/$version/$asset"
    sums="$(curl --proto '=https' --tlsv1.2 --fail --location --silent --show-error \
        --retry 2 --max-time 30 --max-filesize 65536 "https://nodejs.org/dist/$version/SHASUMS256.txt")" || return 1
    sha="$(osr_release_sha "$sums" "$asset")" || return 1
    printf '%s\t%s\t%s\n' "$version" "$sha" "$url"
}

osr_resolve_uv() {
    local target="$1" redirect version asset sums sha url
    [[ "$target" == x86_64-unknown-linux-gnu || "$target" == aarch64-unknown-linux-gnu ]] || return 1
    redirect="$(curl --proto '=https' --tlsv1.2 --fail --location --silent --show-error \
        --retry 2 --max-time 30 --output /dev/null --write-out '%{url_effective}' \
        https://github.com/astral-sh/uv/releases/latest)" || return 1
    version="$(osr_uv_version_from_redirect "$redirect")" || return 1
    asset="uv-$target.tar.gz"
    url="https://github.com/astral-sh/uv/releases/download/$version/$asset"
    sums="$(curl --proto '=https' --tlsv1.2 --fail --location --silent --show-error \
        --retry 2 --max-time 30 --max-filesize 4096 "$url.sha256")" || return 1
    sha="$(osr_release_sha "$sums" "$asset")" || return 1
    printf '%s\t%s\t%s\n' "$version" "$sha" "$url"
}

osr_receipt_binary() {
    local tool_root="$1" tool="$2" version arch archive_sha binary_sha extra expected_arch receipt path
    [[ "$tool" == node || "$tool" == uv ]] || return 1
    receipt="$tool_root/$tool-current.receipt"
    [[ -f "$receipt" && ! -L "$receipt" ]] || return 1
    IFS=$'\t' read -r version arch archive_sha binary_sha extra < "$receipt" || return 1
    [[ -z "$extra" && "$archive_sha" =~ ^[[:xdigit:]]{64}$ && "$binary_sha" =~ ^[[:xdigit:]]{64}$ ]] || return 1
    [[ $(wc -l < "$receipt") -eq 1 ]] || return 1
    case "$(uname -m)" in
        x86_64|amd64) expected_arch=x64; [[ "$tool" == uv ]] && expected_arch=x86_64-unknown-linux-gnu ;;
        aarch64|arm64) expected_arch=arm64; [[ "$tool" == uv ]] && expected_arch=aarch64-unknown-linux-gnu ;;
        *) return 1 ;;
    esac
    [[ "$arch" == "$expected_arch" ]] || return 1
    if [[ "$tool" == node ]]; then
        [[ "$version" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] || return 1
        path="$tool_root/node-$version/bin/node"
    else
        [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || return 1
        path="$tool_root/uv-$version/bin/uv"
    fi
    [[ -x "$path" && ! -L "$path" ]] || return 1
    printf '%s\n' "$path"
}

osr_verify_receipt_binary() {
    local tool_root="$1" tool="$2" path version arch archive_sha binary_sha actual_sha
    path="$(osr_receipt_binary "$tool_root" "$tool")" || return 1
    IFS=$'\t' read -r version arch archive_sha binary_sha < "$tool_root/$tool-current.receipt" || return 1
    actual_sha="$(sha256sum "$path" | cut -d' ' -f1)" || return 1
    [[ "$actual_sha" == "$binary_sha" ]] || return 1
    printf '%s\n' "$path"
}
