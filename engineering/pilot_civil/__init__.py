"""Candidate-bound pilot civil research; no bridge or construction release."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
           operating_release=False,selected_reference_changed=False,configuration_adopted=False,movement_authority=False)
from .design import evaluate, evaluate_portfolio, baseline_train
