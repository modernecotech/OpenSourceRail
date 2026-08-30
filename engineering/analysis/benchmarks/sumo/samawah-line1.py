#!/usr/bin/env python3
"""Compatibility entry point for the original Samawah Line 1 benchmark."""

from city_timetable import REPO_ROOT, main


if __name__ == "__main__":
    raise SystemExit(
        main(
            default_design=REPO_ROOT / "cities/catalogue/west-asia/Iraq/Samawah/design.toml",
            default_lines={"line-1"},
        )
    )
