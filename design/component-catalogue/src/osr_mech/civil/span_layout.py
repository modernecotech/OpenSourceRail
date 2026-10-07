"""Exact-chainage planning spans; surveyed supports and special designs remain gates."""
from __future__ import annotations
import math


def catalogue_counts(length_mm: int) -> tuple[int,int] | None:
    # At most four 20 m members are needed to match a 5 m residue while
    # maximising the number of primary 25 m members.
    for n20 in range(5):
        rest=length_mm-20000*n20
        if rest>=0 and rest%25000==0:
            return rest//25000,n20
    return None


def plan_spans(line: str, intervals: list[tuple[float,float]]) -> list[dict]:
    """Proposed pier chainages partition every interval without rounding length up.

    A non-catalogue remainder is one explicitly unresolved special span. Where
    possible it is kept at least 20 m long rather than creating a tiny closure.
    No fabricated variant, lifting mass, supplier order or structural approval
    is assigned to a special span.
    """
    result=[]
    for run,(start,end) in enumerate(intervals,1):
        if not all(math.isfinite(x) for x in (start,end)) or end<=start:
            raise ValueError('span interval must have finite increasing chainages')
        start_mm=round(start*1000);end_mm=round(end*1000);length=end_mm-start_mm
        if length<=0:
            raise ValueError('span interval is shorter than source millimetre precision')
        counts=catalogue_counts(length)
        if counts:
            ordinary_mm=length
        else:
            ordinary_mm=max(0,(length-20000)//5000*5000)
            while ordinary_mm and catalogue_counts(ordinary_mm) is None:
                ordinary_mm-=5000
            counts=catalogue_counts(ordinary_mm) or (0,0)
        lengths=[25000]*counts[0]+[20000]*counts[1]
        if ordinary_mm<length:
            lengths.append(length-ordinary_mm)
        cursor=start_mm
        for index,span_mm in enumerate(lengths,1):
            identity=f'{line}-run-{run:04d}-span-{index:04d}'
            standard=span_mm in (20000,25000)
            span_end=cursor+span_mm
            result.append(dict(id=identity,line=line,run=run,start_chainage_m=cursor/1000,
                end_chainage_m=span_end/1000,length_m=span_mm/1000,
                beam_variant=f'OSR-Pi{span_mm//1000}' if standard else None,
                pier_a=f'{line}-support-{cursor:012d}',pier_b=f'{line}-support-{span_end:012d}',
                component_ids=[identity+'-track-1',identity+'-track-2'] if standard else [],
                quantity=2 if standard else None,
                classification='catalogue-planning-span' if standard else 'special-design-required',
                structural_qualification='unreleased',pier_location_basis='proposed-chainage-not-surveyed',
                launcher_boundary='independent-access-or-relocation-required' if index==1 and run>1 else 'continuous-run'))
            cursor=span_end
        assert cursor==end_mm
    return result


def span_quantities(spans: list[dict]) -> dict:
    ordinary=[s for s in spans if s['beam_variant']]
    special=[s for s in spans if not s['beam_variant']]
    return dict(total_alignment_m=sum(s['length_m'] for s in spans),
        catalogue_alignment_m=sum(s['length_m'] for s in ordinary),
        special_alignment_m=sum(s['length_m'] for s in special),
        catalogue_bays=len(ordinary),special_spans=len(special),
        pi20_beams=2*sum(s['beam_variant']=='OSR-Pi20' for s in ordinary),
        pi25_beams=2*sum(s['beam_variant']=='OSR-Pi25' for s in ordinary),
        proposed_supports=len({p for s in spans for p in (s['pier_a'],s['pier_b'])}),
        engineered_span_layout_accepted=False)
