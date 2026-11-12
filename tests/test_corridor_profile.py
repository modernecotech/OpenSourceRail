"""Stage accounting must not double count nested cumulative timing."""
import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('corridor_profile',Path(__file__).parents[1]/'engineering/outline/corridor_profile.py')
profile=importlib.util.module_from_spec(spec);spec.loader.exec_module(profile)


def test_exclusive_partition_retains_ambiguous_work():
    stats={('/src/engineering/outline/city_project_cost.py',3,'evaluate'):(1,1,2.,9.,{}),
        ('/src/engineering/station_rail/common.py',4,'encoded'):(1,1,3.,6.,{}),
        ('~',0,'opaque_extension'):(1,1,4.,4.,{})}
    result=profile.aggregate_stats(stats,10.)
    assert result['exclusive_self_seconds']['cost']==2.
    assert result['exclusive_self_seconds']['serialization_hashing']==3.
    assert result['exclusive_self_seconds']['unclassified']==4.
    assert result['accounted_self_seconds']==9.
    assert result['overhead_or_uncaptured_seconds']==1.


def test_failed_call_preserves_profile(tmp_path):
    def fail():raise ValueError('native work never started')
    with pytest.raises(ValueError,match='native work never started'):
        profile.profile_call(fail,tmp_path/'failure.pstats')
    assert (tmp_path/'failure.pstats').stat().st_size>0


def test_refuses_source_output_and_unbounded_trials(tmp_path):
    with pytest.raises(ValueError,match='External'):profile.run(tmp_path,tmp_path/'output')
    with pytest.raises(ValueError,match='bounded trials'):profile.run(tmp_path/'source',tmp_path/'output',trials=5)
