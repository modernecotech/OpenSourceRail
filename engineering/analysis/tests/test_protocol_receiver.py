"""Independent worktree qualification of the new receiver capability."""
import pytest
from engineering.continuous_design import protocol_receiver as receiver
from engineering.continuous_design.receiver_reference import Oracle,frame,cases


@pytest.mark.parametrize("decoder",["struct","bytes"])
@pytest.mark.parametrize("capacity",[1,4,8])
def test_generated_implementations_match_fixed_temporal_oracle_and_remain_bounded(tmp_path,decoder,capacity):
    result=receiver.evaluate(dict(decoder=decoder,history_capacity=capacity,sequence_policy="modular",reset_policy="standstill"),tmp_path)
    assert result["study_pass"] and result["metrics"]["reference_sequences"]>1000
    assert result["metrics"]["maximum_retained_history"]==capacity
    assert result["metrics"]["observed_state_bytes"]<4096
    assert not result["physical_release"]


@pytest.mark.parametrize("mutation",[dict(sequence_policy="linear"),dict(reset_policy="unconditional")])
def test_independent_oracle_rejects_harmful_sequence_and_reset_changes(tmp_path,mutation):
    p=dict(decoder="struct",history_capacity=4,sequence_policy="modular",reset_policy="standstill");p.update(mutation)
    result=receiver.evaluate(p,tmp_path)
    assert not result["study_pass"] and result["counterexamples"]


def test_reference_fault_latches_through_moving_reset_and_recovers_at_standstill():
    o=Oracle();assert not o.receive(b"corrupt",0)
    assert not o.reset(False) and not o.receive(frame(),1000)
    assert o.reset(True) and o.receive(frame(65535,1000),1000)
    assert o.receive(frame(0,1001),1001)


def test_oversized_packet_and_nonfinite_receipt_are_explicit_adverse_cases():
    values=list(cases())
    assert any(any(e[0]=="frame" and type(e[1]) is bytes and len(e[1])==10000 for e in events) for _,events in values)
    assert any(name=="invalid-receipt" for name,_ in values)
