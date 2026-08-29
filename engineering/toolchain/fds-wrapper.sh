#!/usr/bin/env bash
set -euo pipefail

FDS_INSTALL_ROOT="${OSR_FDS_ROOT:-${XDG_DATA_HOME:-${HOME}/.local/share}/opensource-rail/native/FDS-6.11.1_SMV-6.11.2}"

if [[ ! -x "$FDS_INSTALL_ROOT/bin/fds" ]]; then
    printf 'FDS executable not found under %s\n' "$FDS_INSTALL_ROOT" >&2
    exit 127
fi

# The official Linux release bundles the Intel MPI/runtime libraries and its
# generated environment file owns the required PATH/LD_LIBRARY_PATH values.
LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}"
export LD_LIBRARY_PATH
# shellcheck disable=SC1091
source "$FDS_INSTALL_ROOT/bin/FDS6VARS.sh"
exec "$FDS_INSTALL_ROOT/bin/fds" "$@"
