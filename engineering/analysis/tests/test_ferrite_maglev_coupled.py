"""Independent beam benchmarks and two-way Rust-control numerical co-simulation."""
from dataclasses import replace
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from engineering.ferrite_maglev import coupled


@pytest.fixture(scope="module")
def bridge():
    subprocess.run(["cargo", "build", "-p", "osr-maglev-control", "--release", "--example", "coupled_bridge"],
                   cwd=ROOT, check=True, capture_output=True, text=True, timeout=120)
    return ROOT/"target/release/examples/coupled_bridge"


def test_fe_point_load_and_modal_frequencies_have_independent_controls():
    result = coupled.static_benchmark()
    assert result["centre_closed_form_m"] == pytest.approx(0.005604002832523057)
    assert result["centre_relative_error"] < 1e-8
    assert result["distributed_point_load_max_error_m"] < 1e-9
    assert result["modal_frequency_max_relative_error"] < 2e-5
    a=coupled.BeamAssumptions()
    expected=np.pi/(2*a.span_m**2)*np.sqrt(a.young_pa*a.second_moment_m4/a.line_mass_kg_m)
    assert result["modal_frequency_hz"][0] == pytest.approx(expected, rel=1e-6)
    assert result["modal_static_truncation_max_m"] < 1e-6


def test_fe_shape_and_load_transfer_conserve_virtual_work():
    beam = coupled.FlexibleGuideway()
    displacement = np.linspace(-0.001, 0.002, len(beam.free))
    forces = np.arange(24)*120.0+1000.0
    attachment_work = forces@(beam.local_shape@displacement)
    beam_work = (beam.local_shape.T@forces)@displacement
    assert attachment_work == pytest.approx(beam_work, abs=1e-12)
    # Both transverse rows are attached to the same assumed bending beam.
    assert np.allclose(beam.local_shape[::2], beam.local_shape[1::2])
    assert np.array_equal(coupled.MODULE_Y_M, np.tile([-0.88, 0.88], 12))
    # Pinned end displacements vanish; endpoint rotations remain free DOFs.
    assert np.max(np.abs(beam.shape(np.array([0.0, 25.0])))) == 0


def test_exact_modal_step_preserves_undamped_equilibrium_energy():
    beam = coupled.FlexibleGuideway(replace(coupled.BeamAssumptions(), damping_ratio=0.0))
    forces = np.full(24, 11_000.0)
    beam.initialise_static(forces)
    equilibrium = beam.q.copy()
    beam.q[0] += 0.001
    beam.velocity[1] = 0.002
    def energy():
        return 0.5*np.sum(beam.velocity**2+beam.omega_rad_s**2*(beam.q-equilibrium)**2)
    before = energy()
    for _ in range(1000):
        beam.advance(forces)
    assert energy() == pytest.approx(before, rel=1e-9)


def test_static_reaction_response_is_linear_and_mesh_converges():
    coarse = coupled.FlexibleGuideway(replace(coupled.BeamAssumptions(), elements=25))
    fine = coupled.FlexibleGuideway()
    forces = np.linspace(8000.0, 12_000.0, 24)
    d1 = fine.local_shape@fine.static(forces)
    d2 = fine.local_shape@fine.static(2*forces)
    assert np.max(np.abs(d2-2*d1)) < 1e-12
    coarse_d = coarse.local_shape@coarse.static(forces)
    assert np.max(np.abs(coarse_d-d1)) < 2e-6
    assert np.max(np.abs(fine.stiffness@fine.static(forces)-fine.local_shape.T@forces)) < 1e-5


def test_two_way_rust_loop_uses_local_gap_not_global_deflection(bridge):
    result = coupled.cosimulate(bridge, duration_s=3.0)
    assert result["status"] == "hypothetical-two-way-offline-cosimulation"
    assert result["peak_global_incremental_beam_displacement_m"] > 0.013
    assert 0.003 < result["minimum_relative_gap_m"] < 0.008
    assert 0.008 < result["maximum_relative_gap_m"] < 0.013
    assert result["peak_fitted_relative_heave_error_m"] > 0.0008  # reaction-load feedback and declared pulse
    assert abs(result["final_fitted_relative_heave_error_m"]) < 0.0001
    assert abs(result["final_roll_rad"]) < 1e-6
    assert abs(result["final_pitch_rad"]) < 1e-6
    assert 0 < result["peak_station_force_n"] <= 20_000
    assert result["physical_output_authorised"] is False
    assert result["structural_acceptance"] is False


def test_modal_truncation_sensitivity_is_visible_in_two_way_loop(bridge):
    a = coupled.cosimulate(bridge, duration_s=0.5, assumptions=replace(coupled.BeamAssumptions(), retained_modes=4))
    b = coupled.cosimulate(bridge, duration_s=0.5)
    assert a["retained_vertical_beam_modes"] == 4
    assert b["retained_vertical_beam_modes"] == 6
    assert abs(a["minimum_relative_gap_m"]-b["minimum_relative_gap_m"]) < 2e-5
    assert abs(a["maximum_relative_gap_m"]-b["maximum_relative_gap_m"]) < 2e-5


def test_excess_gap_and_replayed_frames_are_rejected_by_actual_rust_core(bridge):
    with pytest.raises(RuntimeError, match="rejected frame"):
        coupled.cosimulate(bridge, duration_s=0.02, initial_down_error_m=0.01)
    with coupled.RustController(bridge) as controller:
        forces, _, _ = controller.tick(1, np.full(24, 0.008))
        assert forces.sum() == pytest.approx(27_750*9.81, rel=1e-10)
        with pytest.raises(RuntimeError, match="rejected frame"):
            controller.tick(1, np.full(24, 0.008))


@pytest.mark.parametrize("kwargs", [dict(young_pa=float("nan")), dict(second_moment_m4=0),
                                    dict(span_m=10), dict(line_mass_kg_m=-1), dict(elements=201),
                                    dict(retained_modes=0), dict(elements=20.5), dict(young_pa=1e300), dict(damping_ratio=-0.01)])
def test_invalid_beam_assumptions_fail_before_numerics(kwargs):
    with pytest.raises(ValueError):
        coupled.FlexibleGuideway(replace(coupled.BeamAssumptions(), **kwargs))


def test_numeric_input_bounds_reject_invalid_force_shapes_and_duration(bridge):
    beam = coupled.FlexibleGuideway()
    for force in (np.zeros(23), np.full(24, np.nan), np.full(24, 1e7)):
        with pytest.raises(ValueError):
            beam.advance(force)
    for duration in (0, 10.01, float("inf")):
        with pytest.raises(ValueError):
            coupled.cosimulate(bridge, duration_s=duration)
    with pytest.raises(ValueError):
        coupled.point_load_deflection(np.array([-1]), 12.5, 1000, coupled.BeamAssumptions())


@pytest.fixture(scope="module")
def publication(tmp_path_factory):
    directory = tmp_path_factory.mktemp("coupled-publication")
    coupled.publish(directory)
    return directory


@pytest.fixture
def publication_copy(publication, tmp_path):
    import shutil
    directory = tmp_path/"copy"
    shutil.copytree(publication, directory)
    return directory


def test_publication_receipt_binds_actual_run_and_verifies_without_recomputation(publication, monkeypatch):
    import json
    from hashlib import sha256
    receipt = json.loads((publication/"receipt.json").read_text())
    result = json.loads((publication/"result.json").read_text())
    assert receipt["source_sha256"] == result["source_sha256"] == coupled.sources()
    assert receipt["files_sha256"] == {"result.json": sha256((publication/"result.json").read_bytes()).hexdigest()}
    assert receipt["execution"] == result["execution"]
    assert receipt["execution"]["build_command"] == coupled.BUILD_COMMAND
    assert len(receipt["execution"]["bridge_sha256"]) == 64
    assert "coupled.py" in " ".join(receipt["source_sha256"])
    assert "array.rs" in " ".join(receipt["source_sha256"])
    assert result["coupled_replay"]["virtual_duration_s"] == 3.0
    assert result["physical_output_authorised"] is False
    assert result["structural_acceptance"] is False
    assert "timestamp" not in (publication/"receipt.json").read_text()
    # Canonical bytes and verification need no simulation, binary or compiler.
    assert coupled._encoded(receipt) == (publication/"receipt.json").read_bytes()
    assert coupled._encoded(result) == (publication/"result.json").read_bytes()
    def forbidden(*args, **kwargs):
        pytest.fail("verification must not build or rerun simulation")
    monkeypatch.setattr(coupled, "_build_bridge", forbidden)
    monkeypatch.setattr(coupled, "cosimulate", forbidden)
    assert coupled.verify(publication) == receipt


def test_corrupt_publication_payload_is_detected_without_replay(publication_copy):
    with (publication_copy/"result.json").open("ab") as output:
        output.write(b"\n")
    with pytest.raises(ValueError, match="checksum differs"):
        coupled.verify(publication_copy)


@pytest.mark.parametrize("change", ["source", "runtime", "schema", "inventory", "malformed-inventory"])
def test_corrupt_receipt_identity_is_detected(publication_copy, change):
    import json
    path = publication_copy/"receipt.json"
    receipt = json.loads(path.read_text())
    if change == "source":
        receipt["source_sha256"]["engineering/ferrite_maglev/coupled.py"] = "0"*64
    elif change == "runtime":
        receipt["runtime"]["numpy"] = "corrupt"
    elif change == "schema":
        receipt["schema"] = "other-study"
    elif change == "inventory":
        receipt["files_sha256"]["extra.json"] = "0"*64
    else:
        receipt["files_sha256"] = None
    path.write_bytes(coupled._encoded(receipt))
    with pytest.raises(ValueError):
        coupled.verify(publication_copy)


def test_rehashed_result_cannot_grant_physical_acceptance(publication_copy):
    import json
    from hashlib import sha256
    result_path = publication_copy/"result.json"
    receipt_path = publication_copy/"receipt.json"
    result = json.loads(result_path.read_text())
    receipt = json.loads(receipt_path.read_text())
    result["coupled_replay"]["structural_acceptance"] = True
    result_path.write_bytes(coupled._encoded(result))
    receipt["files_sha256"]["result.json"] = sha256(result_path.read_bytes()).hexdigest()
    receipt_path.write_bytes(coupled._encoded(receipt))
    with pytest.raises(ValueError, match="must remain false"):
        coupled.verify(publication_copy)


def test_unexpected_file_and_unowned_destination_are_rejected(publication_copy, tmp_path, monkeypatch):
    (publication_copy/"extra.json").write_text("{}")
    with pytest.raises(ValueError, match="inventory"):
        coupled.verify(publication_copy)
    directory = tmp_path/"unowned"
    directory.mkdir()
    (directory/"keep.txt").write_text("user material")
    def forbidden():
        pytest.fail("invalid destination must fail before expensive build")
    monkeypatch.setattr(coupled, "_build_bridge", forbidden)
    with pytest.raises(ValueError, match="not an owned"):
        coupled.publish(directory)
    assert (directory/"keep.txt").read_text() == "user material"


def test_declared_car_mass_changes_actual_rust_gravity_trim(bridge):
    import numpy as np
    with coupled.RustController(bridge,car_mass_kg=30000.) as controller:
        upward,_,_=controller.tick(1,np.full(24,.008))
    assert sum(upward)==pytest.approx(30000*9.81,abs=2)
    r=coupled.cosimulate(bridge,duration_s=.1,car_mass_kg=30000.)
    assert r['car_mass_kg']==30000. and not r['physical_output_authorised']


@pytest.mark.parametrize('mass',[0.,float('nan'),100001.])
def test_invalid_car_mass_does_not_start_a_rust_process(mass):
    with pytest.raises(ValueError):coupled.RustController(Path('/not-a-controller'),car_mass_kg=mass)
