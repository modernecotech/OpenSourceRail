# Research policy only; fixed wrapper validates facts and latches faults.
def closure_request(*, train_stopped, hvil_closed, insulation_ok, main_feedback_open, return_feedback_closed, precharge_feedback_closed, voltage_ready, timeout_ok, data_valid, age_valid, sequence_valid, clocks_valid):
    return train_stopped and hvil_closed and insulation_ok and main_feedback_open and return_feedback_closed and precharge_feedback_closed and voltage_ready and timeout_ok and data_valid and age_valid and sequence_valid and clocks_valid
