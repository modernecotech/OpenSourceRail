from pathlib import Path
import stat

from engineering.design_search import retained_source_epoch as retained
from engineering.station_rail import ROOT


def test_streaming_worker_handoff_is_externally_pinned_and_complete():
    folder=Path(ROOT)/'docs/design-engine/retained-service-energy-extra/original/materializer-streaming'
    manifest_path=folder/'manifest.json'
    sha,raw,_=retained._file_data(manifest_path,1024*1024,materialize=True)
    assert sha=='b6e42bd5fd53a407d78dadc7d5ee7699093d3eb3406d56cec5c1e08f563b57f6'
    manifest=retained._json(raw)
    assert manifest['schema']=='osr-materializer-handoff/1'
    assert manifest['audit_result_id']=='5c355ba03ecd4bdc5a76aa694802c90e65f7049384fc27074b365f752288781d'
    assert manifest['archive_id']=='d2f4511f180592083945bb993658353218b9efcf91d0dd3f21d02e58399967b9'
    files={};directories=set();count=0;total=0
    for path in folder.rglob('*'):
        info=path.lstat();count+=1;name=path.relative_to(folder)
        assert count<=512
        if stat.S_ISDIR(info.st_mode):directories.add(name)
        else:
            assert stat.S_ISREG(info.st_mode)
            total+=info.st_size;assert info.st_size<=16*1024*1024 and total<=64*1024*1024
            if name!=Path('manifest.json'):files[name.as_posix()]=retained._file_data(path)[0]
    all_files={Path(name) for name in files}|{Path('manifest.json')}
    assert directories=={parent for name in all_files for parent in name.parents if parent!=Path('.')}
    assert files==manifest['files_sha256']
    source=Path(ROOT)/'engineering/design_search/retained_service_energy_materialize.py'
    assert retained._file_data(source)[0]==files['source/retained_service_energy_materialize.py']
    audit=retained._json(retained._file_data(folder/'audit/result.json',16*1024*1024,materialize=True)[1])
    assert audit['result_id']==manifest['audit_result_id']
    assert retained._id({k:v for k,v in audit.items() if k!='result_id'})==audit['result_id']
    assert audit['mode']=='audit' and audit['root_written'] is False
    assert audit['full_packet_verifier_executed'] is False
    assert all(audit[k] is False for k in ('physical_accepted','engineering_accepted',
        'manufacturing_release','operating_release','current_evaluator_admission','numerical_reexecuted'))
