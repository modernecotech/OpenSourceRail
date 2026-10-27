"""Exercise the installer's actual build/readiness functions without installing tools."""
import os
from pathlib import Path
import re
import subprocess


def test_current_install_build_and_readiness_agree_without_historical_binaries(tmp_path):
    installer = Path(__file__).resolve().parents[3] / 'install.sh'
    source = installer.read_text()
    functions = []
    for name in ('build_platform', 'build_ready'):
        match = re.search(r'(?ms)^' + name + r'\(\) \{\n.*?^\}\n', source)
        assert match is not None, 'Installer function missing: ' + name
        functions.append(match.group())
    definitions = tmp_path / 'installer-functions.sh'
    definitions.write_text('\n'.join(functions))

    root = tmp_path / 'fresh checkout'
    root.mkdir()
    workbench = root / 'docs/workbench/current/index.html'
    workbench.parent.mkdir(parents=True)
    workbench.write_text('<html>Current wheel/station research Workbench</html>')
    osr = root / 'osr'
    osr.write_text('#!/usr/bin/env bash\n[[ "$*" == verify ]]\n')
    osr.chmod(0o755)
    tools = tmp_path / 'tools'
    tools.mkdir()
    cargo = tools / 'cargo'
    cargo.write_text(
        '#!/usr/bin/env bash\nset -euo pipefail\n'
        '[[ "$*" == "build --locked --release -p osr-atp --example wheel_station_contract" ]]\n'
        'mkdir -p target/release/examples\n'
        'printf "#!/bin/sh\\nexit 0\\n" > target/release/examples/wheel_station_contract\n'
        'chmod +x target/release/examples/wheel_station_contract\n'
    )
    cargo.chmod(0o755)
    environment = {**os.environ, 'PATH': str(tools) + os.pathsep + os.environ['PATH']}

    def run(action):
        return subprocess.run(
            ['bash', '-c', 'set -euo pipefail; ROOT="$1"; source "$2"; '
             'section() { :; }; ' + action, 'installer-test', str(root), str(definitions)],
            env=environment, capture_output=True, text=True,
        )

    result = run('build_platform; build_ready')
    assert result.returncode == 0, result.stderr
    current = root / 'target/release/examples/wheel_station_contract'
    assert not (current.parent / 'sbc_replay').exists()
    assert not (current.parent / 'coupled_bridge').exists()

    # Readiness requires the current executable and current Workbench together.
    current.chmod(0o644)
    assert run('build_ready').returncode != 0
    current.chmod(0o755)
    workbench.unlink()
    assert run('build_ready').returncode != 0
    workbench.write_text('Current Workbench')

    # Retained maglev binaries must not satisfy a missing current build.
    current.unlink()
    for name in ('sbc_replay', 'coupled_bridge'):
        legacy = current.parent / name
        legacy.write_text('#!/bin/sh\nexit 0\n')
        legacy.chmod(0o755)
    assert run('build_ready').returncode != 0
