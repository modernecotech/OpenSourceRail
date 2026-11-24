use crate::model::{invalid, Shift, FULL_AVAILABILITY_BPS};
use arrow_array::{builder::UInt64Builder, Array, UInt64Array};
use serde::Serialize;
use std::{collections::BTreeMap, io};

const BPS_SQUARED: u128 = FULL_AVAILABILITY_BPS as u128 * FULL_AVAILABILITY_BPS as u128;

#[derive(Clone, Copy, Debug)]
pub struct Assessment {
    pub capacity: Option<u64>,
    pub stressed_capacity: Option<u64>,
    pub shortage: Option<u64>,
    pub stressed_shortage: Option<u64>,
    pub costs: Option<[u64; 3]>,
}

fn to_u64(value: u128) -> io::Result<u64> {
    value
        .try_into()
        .map_err(|_| invalid("Result exceeds the supported integer range"))
}

fn capacity(minutes: u128, utilisation: u64, availability: u64) -> io::Result<u64> {
    let fraction = u128::from(utilisation) * u128::from(availability);
    let scaled = minutes
        .checked_mul(fraction)
        .ok_or_else(|| invalid("Capacity overflow"))?;
    to_u64(scaled / BPS_SQUARED)
}

pub struct NumericInputs {
    pub minutes_per_shift: UInt64Array,
    pub days: UInt64Array,
    pub assigned_posts: UInt64Array,
    pub required: UInt64Array,
    pub paid: UInt64Array,
    pub utilisation: UInt64Array,
    pub rates: [UInt64Array; 3],
}

impl NumericInputs {
    pub fn from_shifts(shifts: &[Shift]) -> Self {
        Self {
            minutes_per_shift: shifts.iter().map(|row| row.minutes_per_shift).collect(),
            days: shifts.iter().map(|row| row.days).collect(),
            assigned_posts: shifts.iter().map(|row| row.assigned_posts).collect(),
            required: shifts.iter().map(|row| row.required_minutes).collect(),
            paid: shifts.iter().map(|row| row.paid_minutes).collect(),
            utilisation: UInt64Array::from_iter_values(
                shifts.iter().map(|row| row.utilisation_bps),
            ),
            rates: std::array::from_fn(|index| {
                shifts
                    .iter()
                    .map(|row| row.rates_cents_per_hour.map(|rates| rates[index]))
                    .collect()
            }),
        }
    }
}

pub struct NumericResults {
    pub capacity: UInt64Array,
    pub stressed_capacity: UInt64Array,
    pub shortage: UInt64Array,
    pub stressed_shortage: UInt64Array,
    pub costs: [UInt64Array; 3],
}

pub fn nullable_value(column: &UInt64Array, row: usize) -> Option<u64> {
    column.is_valid(row).then(|| column.value(row))
}

impl NumericResults {
    pub fn row(&self, index: usize) -> Assessment {
        Assessment {
            capacity: nullable_value(&self.capacity, index),
            stressed_capacity: nullable_value(&self.stressed_capacity, index),
            shortage: nullable_value(&self.shortage, index),
            stressed_shortage: nullable_value(&self.stressed_shortage, index),
            costs: nullable_value(&self.costs[0], index)
                .zip(nullable_value(&self.costs[1], index))
                .zip(nullable_value(&self.costs[2], index))
                .map(|((low, base), high)| [low, base, high]),
        }
    }
}

fn cost_column(minutes: &UInt64Array, rates: &UInt64Array) -> io::Result<UInt64Array> {
    let mut costs = UInt64Builder::with_capacity(minutes.len());
    for (paid, rate) in minutes.iter().zip(rates.iter()) {
        match paid.zip(rate) {
            Some((paid, rate)) => {
                // Round half up once from paid minutes into integer cents.
                let cents = (u128::from(paid) * u128::from(rate) + 30) / 60;
                costs.append_value(to_u64(cents)?);
            }
            None => costs.append_null(),
        }
    }
    Ok(costs.finish())
}

fn shortage_column(demand: &UInt64Array, supply: &UInt64Array) -> UInt64Array {
    demand
        .iter()
        .zip(supply)
        .map(|(demand, supply)| {
            demand
                .zip(supply)
                .map(|(demand, supply)| demand.saturating_sub(supply))
        })
        .collect()
}

/// Evaluate entire batches in typed primitive columns. Each row is a repeated
/// shift pattern, so the kernel never expands individual workers or dates.
pub fn evaluate_columns(
    input: &NumericInputs,
    availability_bps: u64,
) -> io::Result<NumericResults> {
    let length = input.utilisation.len();
    let mut baseline = UInt64Builder::with_capacity(length);
    let mut stressed = UInt64Builder::with_capacity(length);
    for (index, ((posts, days), duration)) in input
        .assigned_posts
        .iter()
        .zip(&input.days)
        .zip(&input.minutes_per_shift)
        .enumerate()
    {
        match (posts, days, duration) {
            (Some(posts), Some(days), Some(duration)) => {
                // The product of two u64 values fits in u128.
                let gross = (u128::from(posts) * u128::from(days))
                    .checked_mul(u128::from(duration))
                    .ok_or_else(|| invalid("Gross scheduled minutes overflow"))?;
                let utilisation = input.utilisation.value(index);
                let normal = capacity(gross, utilisation, FULL_AVAILABILITY_BPS)?;
                baseline.append_value(normal);
                stressed.append_value(if availability_bps == FULL_AVAILABILITY_BPS {
                    normal
                } else {
                    capacity(gross, utilisation, availability_bps)?
                });
            }
            _ => {
                baseline.append_null();
                stressed.append_null();
            }
        }
    }
    let baseline = baseline.finish();
    let stressed = stressed.finish();
    let [low, base, high] = &input.rates;
    Ok(NumericResults {
        shortage: shortage_column(&input.required, &baseline),
        stressed_shortage: shortage_column(&input.required, &stressed),
        costs: [
            cost_column(&input.paid, low)?,
            cost_column(&input.paid, base)?,
            cost_column(&input.paid, high)?,
        ],
        capacity: baseline,
        stressed_capacity: stressed,
    })
}

#[derive(Debug, Default, Serialize)]
pub struct Totals {
    pub row_count: u64,
    pub known_required_minutes: u64,
    pub known_paid_minutes: u64,
    pub known_capacity_minutes: u64,
    pub known_stressed_capacity_minutes: u64,
    pub known_shortage_minutes: u64,
    pub known_stressed_shortage_minutes: u64,
    pub known_cost_cents: [u64; 3],
    pub unknown_required_rows: u64,
    pub unknown_capacity_rows: u64,
    pub unknown_paid_rows: u64,
    pub unknown_shortage_rows: u64,
    pub unpriced_rows: u64,
    pub known_unpriced_paid_minutes: u64,
}

#[derive(Debug, Serialize)]
pub struct Group<'a> {
    pub phase: &'a str,
    pub cost_account: &'a str,
    #[serde(flatten)]
    pub totals: Totals,
}

fn add(total: &mut u64, value: u64) -> io::Result<()> {
    *total = total
        .checked_add(value)
        .ok_or_else(|| invalid("Workforce subtotal overflow"))?;
    Ok(())
}

impl Totals {
    fn include(&mut self, shift: &Shift, result: Assessment) -> io::Result<()> {
        self.row_count += 1;
        if result.costs.is_none() {
            self.unpriced_rows += 1;
            add(
                &mut self.known_unpriced_paid_minutes,
                shift.paid_minutes.unwrap_or_default(),
            )?;
        }
        self.unknown_required_rows += u64::from(shift.required_minutes.is_none());
        self.unknown_paid_rows += u64::from(shift.paid_minutes.is_none());
        self.unknown_capacity_rows += u64::from(result.capacity.is_none());
        self.unknown_shortage_rows += u64::from(result.shortage.is_none());
        for (total, value) in [
            (&mut self.known_required_minutes, shift.required_minutes),
            (&mut self.known_paid_minutes, shift.paid_minutes),
            (&mut self.known_capacity_minutes, result.capacity),
            (
                &mut self.known_stressed_capacity_minutes,
                result.stressed_capacity,
            ),
            (&mut self.known_shortage_minutes, result.shortage),
            (
                &mut self.known_stressed_shortage_minutes,
                result.stressed_shortage,
            ),
        ] {
            if let Some(amount) = value {
                add(total, amount)?;
            }
        }
        if let Some(costs) = result.costs {
            for (total, amount) in self.known_cost_cents.iter_mut().zip(costs) {
                add(total, amount)?;
            }
        }
        Ok(())
    }
}

#[derive(Debug, Default)]
pub struct GroupedTotals<'a>(BTreeMap<(&'a str, &'a str), Totals>);

impl<'a> GroupedTotals<'a> {
    pub fn include(&mut self, row: &'a Shift, result: Assessment) -> io::Result<()> {
        self.0
            .entry((&row.phase, &row.cost_account))
            .or_default()
            .include(row, result)
    }

    pub fn finish(self) -> Vec<Group<'a>> {
        self.0
            .into_iter()
            .map(|((phase, cost_account), totals)| Group {
                phase,
                cost_account,
                totals,
            })
            .collect()
    }
}
