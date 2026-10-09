"""Expanded publications preserve every byte across deterministic bounded parts."""
import hashlib
import os
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from proposal_archives import write_parts, read_members


def test_bounded_parts_restore_all_members_and_reject_drift_and_duplicates(tmp_path):
    members={}
    for index in range(5):
        source=tmp_path/f'input-{index}.bin';source.write_bytes(os.urandom(1800))
        members[source.name]=source
    parts=write_parts(tmp_path,members,'2026-10-09',4096)
    assert len(parts)>1
    receipts={name:{'bytes':(tmp_path/name).stat().st_size,
                   'sha256':hashlib.sha256((tmp_path/name).read_bytes()).hexdigest()} for name in parts}
    assert all(value['bytes']<=4096 for value in receipts.values())
    manifest={'supporting_archives':parts,'archive_members':sorted(members),'outputs':receipts}
    assert read_members(tmp_path,tmp_path,manifest,list(members))=={name:p.read_bytes() for name,p in members.items()}
    assert write_parts(tmp_path,members,'2026-10-09',4096)==parts
    assert all(hashlib.sha256((tmp_path/name).read_bytes()).hexdigest()==value['sha256'] for name,value in receipts.items())
    names=list(parts);parts[names[1]].append(parts[names[0]][0])
    with pytest.raises(ValueError,match='Duplicate'):read_members(tmp_path,tmp_path,manifest,list(members))
    parts[names[1]].pop();(tmp_path/names[-1]).write_bytes(b'changed')
    with pytest.raises(ValueError,match='archive differs'):read_members(tmp_path,tmp_path,manifest,list(members))


def test_single_oversize_member_is_rejected_before_publication(tmp_path):
    source=tmp_path/'large.bin';source.write_bytes(os.urandom(5000))
    with pytest.raises(ValueError,match='One compressed evidence member'):
        write_parts(tmp_path,{'large.bin':source},'2026-10-09',4096)
    assert not (tmp_path/'Baghdad-Proposal-Supporting-Data.zip').exists()
