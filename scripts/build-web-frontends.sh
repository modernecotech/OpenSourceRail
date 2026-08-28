#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v trunk >/dev/null 2>&1; then
    echo "error: trunk 0.21.8 is required (cargo install trunk --version 0.21.8 --locked)" >&2
    exit 1
fi
if ! rustup target list --installed | grep -qx wasm32-unknown-unknown; then
    echo "error: wasm32-unknown-unknown is required (rustup target add wasm32-unknown-unknown)" >&2
    exit 1
fi

actual_trunk="$(trunk --version | awk '{print $2}')"
if [[ "$actual_trunk" != "0.21.8" ]]; then
    echo "error: deterministic frontend build requires trunk 0.21.8; found $actual_trunk" >&2
    exit 1
fi

mkdir -p "$ROOT/build/frontend"
cargo build -p osr-city-studio
(
    cd "$ROOT/crates/osr-sim-gui"
    env -u NO_COLOR trunk build web/index.html --release --public-url ./ --dist "$ROOT/build/frontend/sim"
)
(
    cd "$ROOT/crates/osr-occ-gui"
    env -u NO_COLOR trunk build web/index.html --release --public-url ./ --dist "$ROOT/build/frontend/occ"
)
