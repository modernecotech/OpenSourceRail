#!/usr/bin/env bash

# Run a GUI command without assuming Debian's xvfb-run wrapper exists.
run_headless_gui() {
    if command -v xvfb-run >/dev/null 2>&1; then
        xvfb-run -a "$@"
        return
    fi
    if [[ -n "${DISPLAY:-}" ]]; then
        "$@"
        return
    fi
    if ! command -v Xvfb >/dev/null 2>&1; then
        echo "A graphical display, xvfb-run, or Xvfb is required." >&2
        return 127
    fi

    local display=":$((90 + ($$ % 900)))"
    Xvfb "$display" -screen 0 1920x1080x24 -nolisten tcp >/dev/null 2>&1 &
    local xvfb_pid=$!
    local status=0
    if DISPLAY="$display" "$@"; then
        status=0
    else
        status=$?
    fi
    kill "$xvfb_pid" >/dev/null 2>&1 || true
    wait "$xvfb_pid" 2>/dev/null || true
    return "$status"
}
