"""Exercise the installer's actual build/readiness functions without installing tools."""
import os
from pathlib import Path
import re
import subprocess
import sys


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
        '[[ "$*" == "build --locked --release --jobs 2 -p osr-atp --example wheel_station_contract" ]]\n'
        'mkdir -p target/release/examples\n'
        'printf "#!/bin/sh\\nexit 0\\n" > target/release/examples/wheel_station_contract\n'
        'chmod +x target/release/examples/wheel_station_contract\n'
    )
    cargo.chmod(0o755)
    environment = {**os.environ, 'PATH': str(tools) + os.pathsep + os.environ['PATH'],
                   'OSR_CARGO_JOBS': '2'}

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


def test_python_readiness_rejects_stale_native_wheels_and_refreshes(tmp_path):
    installer = Path(__file__).resolve().parents[3] / 'install.sh'
    source = installer.read_text()
    functions = []
    for name in ('python_ready', 'install_python'):
        match = re.search(r'(?ms)^' + name + r'\(\) \{\n.*?^\}\n', source)
        assert match is not None, name
        functions.append(match.group())
    definitions = tmp_path / 'python-functions.sh'
    definitions.write_text('\n'.join(functions))

    root = tmp_path / 'checkout'
    (root / '.venv/bin').mkdir(parents=True)
    (root / '.venv/bin/python').symlink_to(sys.executable)
    requirements = root / 'engineering/requirements.txt'
    requirements.parent.mkdir()
    requirements.write_text('ifcopenshell>=0.9.0.post1\nifctester>=0.9.0\ngmsh>=4.15.2\n')
    site = tmp_path / 'site'
    site.mkdir()
    for name in ('cairosvg', 'mistune', 'numpy', 'scipy', 'matplotlib',
                 'PIL', 'reportlab', 'pytest', 'ifcopenshell', 'ifctester', 'gmsh'):
        (site / (name + '.py')).write_text('')
    for name, version in (('ifcopenshell', '0.8.5'), ('ifctester', '0.8.5'), ('gmsh', '4.14.1')):
        dist = site / f'{name}-{version}.dist-info'
        dist.mkdir()
        (dist / 'METADATA').write_text(f'Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n')
    environment = {**os.environ, 'PYTHONPATH': str(site), 'OSR_TEST_SITE': str(site)}
    shell = (
        'set -euo pipefail; ROOT="$1"; PYTHON_VERSION=3.11; source "$2"; '
        'section() { :; }; fail() { return 1; }; '
        'uv() { if [[ "$1 $2" == "pip install" ]]; then '
        '"$ROOT/.venv/bin/python" - "$OSR_TEST_SITE" <<\'PY\'\n'
        'from pathlib import Path\nimport sys\n'
        'site=Path(sys.argv[1])\n'
        'for name,old,new in (("ifcopenshell","0.8.5","0.9.0.post1"),'
        '("ifctester","0.8.5","0.9.0"),("gmsh","4.14.1","4.15.2")):\n'
        '  old_path=site/f"{name}-{old}.dist-info"\n'
        '  new_path=site/f"{name}-{new}.dist-info"\n'
        '  old_path.rename(new_path)\n'
        '  (new_path/"METADATA").write_text(f"Metadata-Version: 2.1\\nName: {name}\\nVersion: {new}\\n")\n'
        'PY\n'
        'fi; }; '
    )
    def run(action):
        return subprocess.run(['bash', '-c', shell + action, 'installer-test', str(root), str(definitions)],
                              env=environment, capture_output=True, text=True)

    assert run('python_ready').returncode != 0
    refreshed = run('install_python; python_ready')
    assert refreshed.returncode == 0, refreshed.stderr
