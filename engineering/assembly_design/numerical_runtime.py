"""Extend the established runtime receipt for signed evidence and IFC/IDS."""
import importlib.metadata
from pathlib import Path
import shutil
from engineering.continuous_design import runtime


def capture():
    result=runtime.capture()
    for package in ('ifctester','xmlschema','elementpath','shapely','python-dateutil','matplotlib','pillow'):
        try:dist=importlib.metadata.distribution(package)
        except importlib.metadata.PackageNotFoundError:extra=dict(available=False)
        else:
            files={}
            for member in dist.files or []:
                if str(member).endswith(('.py','/RECORD')) or '.so' in Path(member).name:
                    path=Path(dist.locate_file(member)).resolve()
                    if path.is_file():files[str(path)]=runtime.file_hash(path)
            extra=dict(version=dist.version,files_sha256=files)
        result['packages'][package]=extra
    binary=shutil.which('openssl')
    result['signed_evidence_runtime']=dict(path=binary,sha256=runtime.file_hash(Path(binary).resolve()) if binary else None)
    result['media_runtime']={name:dict(path=shutil.which(name),sha256=runtime.file_hash(Path(shutil.which(name)).resolve()) if shutil.which(name) else None)
        for name in ('ffmpeg','ffprobe')}
    return result
