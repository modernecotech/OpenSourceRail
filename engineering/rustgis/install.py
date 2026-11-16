"""Resolve and install the current official RustGIS release per user."""
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile
import tempfile
from engineering.toolchain_release import (
    latest_asset, download_asset, tar_member_sha256, file_sha256,
    MAX_UNPACKED_BYTES,
)
from .adapter import lock_record


def refresh_latest():
    """Refresh one official release under the target filesystem's disk floor."""
    from engineering.performance import GIB, disk_reservation
    from engineering.station_rail import ROOT
    target = Path.home()/'.local/share/opensource-rail/toolchains/rustgis'
    with disk_reservation(ROOT, target, 'rustgis-refresh', GIB):
        return _refresh_latest()


def _refresh_latest():
    """Explicit install-time refresh; ordinary GIS evaluations stay offline."""
    path = Path(__file__).with_name('backend.json')
    previous = lock_record()
    release = latest_asset('opengeos/RustGIS', 'RustGIS-{version}-linux-x86_64.tar.gz')
    if (previous['tag'] == release['version']
            and previous['linux_x86_64']['sha256'] == release['asset_sha256']
            and previous['source_revision'] == release['commit']
            and all(isinstance(previous.get('executables_sha256',{}).get(name),str)
                    and len(previous['executables_sha256'][name])==64
                    for name in ('rustgis','rustgis-cli'))):
        return previous
    version = release['version'].removeprefix('v')
    directory = 'RustGIS-'+version+'-linux-x86_64'
    cache = Path.home()/'.local/share/opensource-rail/toolchains/rustgis'/release['asset']
    archive = download_asset(release, cache)
    hashes = {name:tar_member_sha256(archive,directory+'/'+name)
              for name in ('rustgis','rustgis-cli')}
    current = dict(previous, version=version,tag=release['version'],
        source_revision=release['commit'],
        release_url='https://github.com/opengeos/RustGIS/releases/tag/'+release['version'],
        release_immutable=release['release_immutable'],
        release_published_at=release['release_published_at'],
        linux_x86_64=dict(url=release['url'],sha256=release['asset_sha256'],
            bytes=release['bytes'],directory=directory,asset_id=release['asset_id']),
        executables_sha256=hashes)
    replacement = path.with_suffix('.json.refresh')
    if replacement.exists():
        raise ValueError('Interrupted RustGIS manifest refresh retained: '+str(replacement))
    replacement.write_text(json.dumps(current,sort_keys=True,indent=2)+'\n')
    replacement.replace(path)
    return current


def install():
    """Install the resolved release under an explicit extraction reservation."""
    from engineering.performance import GIB, disk_reservation
    from engineering.station_rail import ROOT
    with disk_reservation(ROOT, Path.home()/'.local/opt', 'rustgis-install', 2*GIB):
        return _install()


def _install():
    if platform.system() != 'Linux' or platform.machine() not in ('x86_64', 'AMD64'):
        raise ValueError('Current RustGIS binary targets Linux x86_64')
    pin = refresh_latest();asset = pin['linux_x86_64']
    home = Path.home();target = home/'.local/opt'/('rustgis-'+pin['version'])
    binary = target/asset['directory']
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='rustgis-install-', dir=target.parent) as tmp:
            tmp = Path(tmp)
            release = dict(url=asset['url'],bytes=asset['bytes'],asset_sha256=asset['sha256'])
            archive = download_asset(release,
                home/'.local/share/opensource-rail/toolchains/rustgis'/Path(asset['url']).name)
            unpacked = tmp/'unpacked';unpacked.mkdir()
            with tarfile.open(archive) as f:
                members=f.getmembers()
                if (sum(m.size for m in members)>MAX_UNPACKED_BYTES
                        or len(members)>512
                        or any(not (m.isfile() or m.isdir()) for m in members)):
                    raise ValueError('RustGIS archive exceeds ordinary-file extraction budget')
                f.extractall(unpacked, filter='data')
            for name,h in pin['executables_sha256'].items():
                if file_sha256(unpacked/asset['directory']/name) != h:
                    raise ValueError('RustGIS executable differs: '+name)
            unpacked.rename(target)
    for name,h in pin['executables_sha256'].items():
        if file_sha256(binary/name) != h:
            raise ValueError('Installed RustGIS executable differs: '+name)
        link = home/'.local/bin'/name;link.parent.mkdir(parents=True, exist_ok=True)
        if link.is_symlink() and link.resolve() == binary/name:continue
        if link.is_symlink() and link.resolve().is_relative_to(home/'.local/opt') \
                and link.resolve().parent.name.startswith('RustGIS-'):
            link.unlink()
        if link.exists() or link.is_symlink():raise ValueError('Refusing to replace existing command: '+str(link))
        link.symlink_to(binary/name)
    share = home/'.local/share';applications = share/'applications';applications.mkdir(parents=True, exist_ok=True)
    (applications/'org.opengeos.RustGIS.desktop').write_text(
        '[Desktop Entry]\nType=Application\nName=RustGIS\nComment=OpenSourceRail city GIS projects\n'
        'Exec="'+str(binary/'rustgis')+'" %F\nIcon='+str(binary/'rustgis.png')+'\n'
        'Terminal=false\nCategories=Science;Geography;\nMimeType=application/x-rustgis-project;\n')
    mime = share/'mime/packages';mime.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(binary/'rustgis-mime.xml', mime/'rustgis.xml')
    for command in (['update-mime-database', str(share/'mime')], ['update-desktop-database', str(applications)]):
        if shutil.which(command[0]):subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
    return dict(installed=True, version=pin['version'], directory=str(target),
                bytes=sum(p.stat().st_size for p in target.rglob('*') if p.is_file()))
