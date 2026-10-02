//! Explicit opt-in conversion of legacy wire positions; never reinterpret layouts.
use crate::{bad, io, FrozenRailway, TrainId};
use osr_core::{Direction, Position, TrackRef};
use osr_interlocking::{PositionSource, TrainPositionReport};
pub fn position_report(
    wire: osr_proto::TrainPositionReport,
    frozen: &FrozenRailway,
    now: u64,
) -> io::Result<TrainPositionReport> {
    let train = frozen
        .model()
        .trains
        .iter()
        .find(|t| t.config.owner.train == TrainId(wire.train_id.0))
        .ok_or_else(|| bad("unresolved train identity"))?;
    let route = frozen
        .model()
        .routes
        .iter()
        .find(|r| r.id == train.permitted_route)
        .ok_or_else(|| bad("route"))?;
    let direction = |d| match d {
        osr_proto::Direction::Forward => Ok(Direction::Forward),
        osr_proto::Direction::Reverse => Ok(Direction::Reverse),
        _ => Err(bad("unspecified direction")),
    };
    let position = |p: osr_proto::Position| -> io::Result<Position> {
        let resource = frozen
            .model()
            .resources
            .iter()
            .find(|r| r.section.0 == p.track_ref.section.0)
            .ok_or_else(|| bad("unresolved section identity"))?;
        let segment = route
            .segments
            .iter()
            .find(|s| s.resource == resource.id)
            .ok_or_else(|| bad("section outside registered route"))?;
        if p.track_ref.offset_mm < 0
            || p.track_ref.offset_mm as u64 > segment.end_mm - segment.start_mm
            || p.uncertainty_mm > train.config.maximum_position_uncertainty_mm
            || direction(p.track_ref.direction)? != route.direction
        {
            return Err(bad("position range/direction"));
        }
        Ok(Position {
            track_ref: TrackRef {
                section: resource.section,
                offset_mm: p.track_ref.offset_mm,
                direction: route.direction,
            },
            uncertainty_mm: p.uncertainty_mm,
        })
    };
    if !wire.speed_mps.is_finite()
        || !(0.0..=100.0).contains(&wire.speed_mps)
        || !wire.speed_uncertainty_mps.is_finite()
        || !(0.0..=100.0).contains(&wire.speed_uncertainty_mps)
        || !wire.pack_state_of_charge.is_finite()
        || !(0.0..=1.0).contains(&wire.pack_state_of_charge)
        || wire.onboard_time_ns == 0
        || wire.onboard_time_ns > now
        || now - wire.onboard_time_ns > 1_000_000_000
        || direction(wire.heading)? != route.direction
        || wire.contributing_sources.is_empty()
        || wire.contributing_sources.len() > 4
    {
        return Err(bad("legacy units/range/freshness"));
    }
    let sources = wire
        .contributing_sources
        .iter()
        .map(|s| match s {
            osr_proto::PositionSource::Gnss => Ok(PositionSource::Gnss),
            osr_proto::PositionSource::Imu => Ok(PositionSource::Imu),
            osr_proto::PositionSource::Odometry => Ok(PositionSource::Odometry),
            osr_proto::PositionSource::Beacon => Ok(PositionSource::Beacon),
            _ => Err(bad("unspecified position source")),
        })
        .collect::<io::Result<_>>()?;
    Ok(TrainPositionReport {
        train_id: train.config.owner.train,
        head_position: position(wire.head_position)?,
        tail_position: position(wire.tail_position)?,
        speed_mmps: (f64::from(wire.speed_mps) * 1000.0).round() as i64,
        // Round uncertainty outwards, including the half-unit speed conversion error.
        speed_uncertainty_mmps: (f64::from(wire.speed_uncertainty_mps) * 1000.0 + 0.5).ceil()
            as u32,
        heading: route.direction,
        contributing_sources: sources,
        onboard_time_ns: wire.onboard_time_ns,
        pack_soc_ppt: (wire.pack_state_of_charge * 1000.0).round() as u16,
    })
}
