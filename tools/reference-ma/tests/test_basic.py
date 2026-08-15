"""Sanity tests mirrored from crates/osr-interlocking/src/ma.rs and
crates/osr-interlocking/src/topology.rs. Run with:

    cd tools/reference-ma
    PYTHONPATH=src python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import unittest

from reference_ma import (
    ConsistDescriptor,
    Direction,
    Entry,
    Line,
    MAX_MA_DISTANCE_MM,
    MA_VALIDITY_WINDOW_NS,
    Network,
    Position,
    Section,
    SectionIntrusion,
    Station,
    TrackRef,
    TrainPositionReport,
    TrainRegistration,
    IntrusionState,
    compute_self_ma,
    derive_state,
    footprint_from,
    forward_chain,
    section_available_to,
)
from reference_ma.log import PositionSource


def simple_linear_network() -> Network:
    """Mirror of `crates/osr-interlocking/src/topology.rs::simple_linear_network`."""
    net = Network()
    for i in range(1, 5):
        net.stations[i] = Station(
            id=i,
            name=f"S{i}",
            charging_power_kw=0,
            dwell_seconds=0,
            is_terminal=(i == 1 or i == 4),
            is_depot=False,
        )
    fwd, rev = [], []
    for i in range(3):
        f = 1000 + i
        r = 2000 + i
        net.sections[f] = Section(
            id=f,
            from_station=i + 1,
            to_station=i + 2,
            length_mm=1_000_000,  # 1 km
            max_speed_mps=22.0,
        )
        net.sections[r] = Section(
            id=r,
            from_station=i + 2,
            to_station=i + 1,
            length_mm=1_000_000,
            max_speed_mps=22.0,
        )
        fwd.append(f)
        rev.append(r)
    net.lines.append(
        Line(
            name="L",
            stations=[1, 2, 3, 4],
            forward_sections=fwd,
            reverse_sections=rev,
            is_ring=False,
        )
    )
    return net


def register(train_id: int, section: int, offset: int, ts_ns: int, entry_id: int) -> Entry:
    payload = TrainRegistration(
        train_id=train_id,
        consist=ConsistDescriptor.reference_3car(),
        initial_position=Position(
            track_ref=TrackRef(
                section=section, offset_mm=offset, direction=Direction.Forward
            ),
            uncertainty_mm=0,
        ),
    )
    return Entry(entry_id=entry_id, term=1, timestamp_ns=ts_ns, payload=payload)


def position(train_id: int, section: int, offset: int, ts_ns: int, entry_id: int) -> Entry:
    payload = TrainPositionReport(
        train_id=train_id,
        head_position=Position(
            track_ref=TrackRef(
                section=section, offset_mm=offset, direction=Direction.Forward
            ),
            uncertainty_mm=0,
        ),
        tail_position=Position(
            track_ref=TrackRef(
                section=section, offset_mm=0, direction=Direction.Forward
            ),
            uncertainty_mm=0,
        ),
        speed_mmps=15_000,
        speed_uncertainty_mmps=500,
        heading=Direction.Forward,
        contributing_sources=[PositionSource.Gnss, PositionSource.Odometry],
        onboard_time_ns=ts_ns,
        pack_soc_ppt=1000,
    )
    return Entry(entry_id=entry_id, term=1, timestamp_ns=ts_ns, payload=payload)


def clear(section: int, entry_id: int) -> Entry:
    return Entry(
        entry_id=entry_id,
        term=1,
        timestamp_ns=0,
        payload=SectionIntrusion(
            section=section,
            state=IntrusionState.Clear,
            issued_by=100,
            observed_at_ns=0,
        ),
    )


class TopologyTests(unittest.TestCase):
    def test_forward_chain_linear_basic(self):
        net = simple_linear_network()
        start = TrackRef(section=1000, offset_mm=500_000, direction=Direction.Forward)
        self.assertEqual(forward_chain(net, start, 1_500_000), [1000, 1001])

    def test_forward_chain_terminates_at_end(self):
        net = simple_linear_network()
        start = TrackRef(section=1002, offset_mm=0, direction=Direction.Forward)
        self.assertEqual(forward_chain(net, start, 5_000_000), [1002])

    def test_footprint_single_section(self):
        net = simple_linear_network()
        head = TrackRef(section=1001, offset_mm=100_000, direction=Direction.Forward)
        self.assertEqual(footprint_from(net, head, 51_000), [1001])

    def test_footprint_crosses_section_boundary(self):
        net = simple_linear_network()
        head = TrackRef(section=1001, offset_mm=20_000, direction=Direction.Forward)
        self.assertEqual(footprint_from(net, head, 51_000), [1001, 1000])


class MaTests(unittest.TestCase):
    def test_no_registration_fail_restrictive(self):
        net = simple_linear_network()
        ma = compute_self_ma(train_id=42, log_prefix=[], network=net, now_ns=0)
        self.assertFalse(ma.has_known_position)
        self.assertEqual(ma.valid_until_ns, MA_VALIDITY_WINDOW_NS)
        self.assertEqual(ma.derived_from_entry_id, None)

    def test_single_train_full_extension(self):
        net = simple_linear_network()
        entries = [register(1, 1000, 51_000, 0, 1), clear(1001, 2)]
        ma = compute_self_ma(1, entries, net, 0)
        self.assertTrue(ma.has_known_position)
        # MA end should advance down the line toward section 1002 (2 km budget).
        # Head offset 51 m into 1000; forward_chain → [1000, 1001, 1002]
        # budget-wise (0.949 + 1 + 1 = 2.949 > 2), so MA end at far end of 1001.
        self.assertEqual(ma.end.section, 1001)
        self.assertEqual(ma.end.offset_mm, 1_000_000)

    def test_other_train_blocks(self):
        net = simple_linear_network()
        entries = [
            register(1, 1000, 51_000, 0, 1),
            register(2, 1001, 51_000, 0, 2),
            position(2, 1001, 51_000, 0, 3),
        ]
        ma = compute_self_ma(1, entries, net, 0)
        self.assertTrue(ma.has_known_position)
        # Train 2 occupies 1001; train 1's MA must stop before 1001.
        self.assertEqual(ma.end.section, 1000)
        self.assertEqual(ma.end.offset_mm, 1_000_000)

    def test_p5_validity_window(self):
        net = simple_linear_network()
        ma = compute_self_ma(1, [], net, now_ns=10**18)
        self.assertEqual(ma.valid_until_ns, 10**18 + MA_VALIDITY_WINDOW_NS)

    def test_section_without_intrusion_verdict_is_fail_restrictive(self):
        net = simple_linear_network()
        state = derive_state([])
        self.assertFalse(section_available_to(1, 1000, state))


if __name__ == "__main__":
    unittest.main()
