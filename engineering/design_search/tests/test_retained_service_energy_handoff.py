import os
from pathlib import Path
import shutil
import stat

import pytest

from engineering.design_search import retained_source_epoch as retained
from engineering.station_rail import ROOT


def _inventory(folder):
    folder=retained._ordinary(folder,directory=True);files={};directories=set();count=0;total=0
    for path in folder.rglob('*'):
        info=path.lstat();count+=1
        if count>512:raise ValueError('Worker inventory entry limit exceeded')
        name=path.relative_to(folder)
        if stat.S_ISDIR(info.st_mode):directories.add(name)
        elif stat.S_ISREG(info.st_mode):
            total+=info.st_size
            if info.st_size>16*1024*1024 or total>64*1024*1024:
                raise ValueError('Worker inventory byte limit exceeded')
            files[name]=retained._file_data(path)[0]
        else:raise ValueError('Only regular files and directories are permitted')
    implied={parent for name in files for parent in name.parents if parent!=Path('.')}
    if directories!=implied:raise ValueError('Empty or undeclared directories are not permitted')
    return {name.as_posix():sha for name,sha in files.items() if name!=Path('handoff.json')}


def test_externally_pinned_worker_handoff_and_complete_inventory():
    folder=Path(ROOT)/'docs/design-engine/retained-service-energy-extra/original/worker-v7'
    handoff=retained._json(retained._file_data(folder/'handoff.json',1024*1024,materialize=True)[1])
    expected='d60030093812acc4ea0da1b2b618b17474d59232c7d65fb24bf78e04cfbd0c9b'
    assert handoff['handoff_id']==expected
    assert retained._id({k:v for k,v in handoff.items() if k!='handoff_id'})==expected
    actual=_inventory(folder)
    assert actual==handoff['files_sha256']
    assert handoff['archive_id']=='d2f4511f180592083945bb993658353218b9efcf91d0dd3f21d02e58399967b9'
    assert handoff['pins_id']=='91d8be8f7893aea692e90683c214bbda0d35c4dbe1a652c7cb8908e3d3a4f050'
    assert retained._file_data(Path(ROOT)/'engineering/design_search/retained_service_energy_epoch.py')[0]==handoff['capture_producer_sha256']
    assert all(handoff[key] is False for key in ('physical_accepted','engineering_accepted',
        'manufacturing_release','operating_release','numerical_reexecuted','current_evaluator_admission'))


@pytest.mark.parametrize('kind',['empty-directory','fifo'])
def test_worker_inventory_rejects_extra_directories_and_special_files(tmp_path,kind):
    source=Path(ROOT)/'docs/design-engine/retained-service-energy-extra/original/worker-v7'
    folder=tmp_path/'worker';shutil.copytree(source,folder);folder.chmod(0o700)
    extra=folder/'unexpected'
    if kind=='fifo':os.mkfifo(extra)
    else:extra.mkdir()
    with pytest.raises(ValueError):_inventory(folder)
