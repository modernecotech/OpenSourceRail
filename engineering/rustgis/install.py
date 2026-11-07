"""Install pinned upstream binaries per user, without a compiler or runtime."""
from hashlib import sha256
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from .adapter import lock_record


def install():
    if platform.system() != 'Linux' or platform.machine() not in ('x86_64', 'AMD64'):
        raise ValueError('This verified binary pin targets Linux x86_64')
    pin = lock_record();asset = pin['linux_x86_64']
    home = Path.home();target = home/'.local/opt'/('rustgis-'+pin['version'])
    binary = target/asset['directory']
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='rustgis-install-', dir=target.parent) as tmp:
            tmp = Path(tmp);archive = tmp/'upstream.tar.gz'
            urllib.request.urlretrieve(asset['url'], archive)
            if archive.stat().st_size != asset['bytes'] or sha256(archive.read_bytes()).hexdigest() != asset['sha256']:
                raise ValueError('RustGIS release size/checksum differs')
            unpacked = tmp/'unpacked';unpacked.mkdir()
            with tarfile.open(archive) as f:f.extractall(unpacked, filter='data')
            for name,h in pin['executables_sha256'].items():
                if sha256((unpacked/asset['directory']/name).read_bytes()).hexdigest() != h:
                    raise ValueError('RustGIS executable differs: '+name)
            unpacked.rename(target)
    for name,h in pin['executables_sha256'].items():
        if sha256((binary/name).read_bytes()).hexdigest() != h:
            raise ValueError('Installed RustGIS executable differs: '+name)
        link = home/'.local/bin'/name;link.parent.mkdir(parents=True, exist_ok=True)
        if link.is_symlink() and link.resolve() == binary/name:continue
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
