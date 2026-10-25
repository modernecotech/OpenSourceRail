"""Immutable, reconstructable EPM experiment packets; root publishes after review."""
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

from engineering.design_search.storage import atomic_immutable
from . import ROOT, FLAGS
from . import catalogue
from .study import study, sources


def _plot(value):
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(13,4),layout='constrained')
    for ax,entry in zip(axes,value['summary']):
        rows=[r for r in value['pulse_cases'] if r['settings']['candidate_id']==entry['candidate_id']]
        for T in (20,80):
            chosen=[r for r in rows if r['settings']['coil_initial_temperature_C']==T]
            ax.plot([r['settings']['L_H']*1000 for r in chosen],[r['linear_RLC']['peak_current_A'] for r in chosen],'o-',label=f'Cu starts {T} °C')
        ax.axhline(entry['conditional_magnetizing_current_A'],color='firebrick',linestyle='--',label='Conditional Hmag/B demand')
        ax.set_xscale('log');ax.set_xlabel('Unmeasured L sensitivity (mH)');ax.set_ylabel('Current (A)');ax.set_title(entry['name']);ax.legend(fontsize=7)
    fig.suptitle('Linear capacitor-pulse screening; no magnetic switching or rail force qualified')
    stream=BytesIO();fig.savefig(stream,format='png',dpi=140,metadata={'Software':'OpenSourceRail EPM research'});plt.close(fig)
    return stream.getvalue()


def _readme(value):
    rows=['# Electropermanent next experiments','',
          'Three counted onboard EPM/Halbach coupons were screened with linear pulse circuits and explicit parallel-branch load lines. No switching, retained bias, lift or integrated train is accepted.','',
          '| Candidate | Added stock kg/module | Turns | Nominal pulse A | Conditional magnetizing A | Bank J/car |',
          '|---|---:|---:|---:|---:|---:|']
    for q in value['summary']:
        energy='unknown count' if q['capacitor_energy_per_car_J'] is None else f'{q["capacitor_energy_per_car_J"]:.1f}'
        rows.append(f'|{q["name"]}|{q["added_counted_stock_kg_per_module"]:.3f}|{q["turns"]}|{q["nominal_RLC_peak_current_A"]:.2f}|{q["conditional_magnetizing_current_A"]:.2f}|{energy}|')
    rows+=['','Nominal means 20 °C copper, assumed 5 mH, 20 ms. Demand covers both pulse directions and prescribed AlNiCo magnitudes 1.25 / 1.5 T at general 240 kA/m magnetizing guidance; these are not measured switching states. Capacitor/driver/protection/retention installation mass remains unknown.','',
       '[Machine results](study.json) · [Exact candidate stock](candidates.json) · [Pulse cases](pulse-cases.json) · [Load-line cases](loadline-cases.json) · [Source receipt](manifest.json)','',
       '![Linear pulse comparison](pulse-current.png)','',
       'The two 12 mm rail gaps substantially change the shared hard/soft magnetic load line. A 51 kA/m normal coercivity reference is neither a full magnetizing field nor an irreversible knee. Below that reference retention remains unknown; crossing it fails the stated positive-state necessary screen. No contact holding force is extrapolated to rail clearance.','',
       'Even with the wider endcaps, the declared zero-current/no-leakage circuit has no positive-AlNiCo-branch interval at 12 mm: the hard-Nd branch requires gap B ≥ 0.184 T while remaining above the normal-Hc reference requires B ≤ 0.134 T. This is a failed necessary model screen, not proof of physical irreversibility. A pole area ≥ 0.00661 m² or magnet length ≥ 0.0689 m is required merely to reopen that interval; neither change would qualify the unknown hysteresis, leakage or force.','',
       'Use EPMs as a candidate for slow load/bias adjustment. Active fast suspension remains necessary; its authority is not established here. Station, cassette and parking experiments have separate gap, wear and mechanical load interfaces; capture and door locks remain separate qualified mechanisms.','',
       'The next experiment measures protected positive/negative pulse current/voltage, flux minor loops and retention at several gaps and temperatures, plus hard-PM remanence before/after. Hysteresis/core/eddy losses, nonlinear L and switching rate require identification before any force/current map.','',
       'The pooled bank must recharge between modules. Timing records include 24 pulse slots and capacitor-reset energy at declared 1 kW / 90% charger assumptions; the parallel 24-bank comparison trades stored energy/hardware against programming latency. Residual inductor energy after 20 ms still needs a clamp/recovery circuit. Truncated pulse I²R is not complete-cycle heat or switching energy.','',
       'The discarded 10 mm rail endcap bridge would require 4.68 T to carry nominal Nd flux internally under the zero-external-flux hypothesis. The counted 40 mm endcaps reduce that necessary density to 1.17 T, with added steel. This fixes a cheap geometric bottleneck but does not prove an OFF state; steel MMF, leakage and AlNiCo state remain unresolved.','',
       'Sources: [Knaian MIT thesis](https://cba.mit.edu/docs/theses/10.06.knaian.pdf), [identified laboratory gravity-compensation study](https://doi.org/10.1016/j.ifacol.2023.10.180), [EA cast Alnico table](https://eamagnetics.com/product/alnico), [Arnold magnetizing guidance](https://www.arnoldmagnetics.com/products/alnico-magnets/). The laboratory 19 N/s result is not a rail actuator rate. Grade/data/PDF digests are retained in the source provenance.','']
    rows+=['| Application | Disposition | Missing evidence |','|---|---|---|']
    rows += [f'|{r["application"]}|{r["state"]}|{r["reason"]}|' for r in value['application_dispositions']]
    rows.append('')
    return '\n'.join(rows).encode()


def payload(root=ROOT):
    value=study(root)
    result={'study.json':catalogue.encoded(value),'candidates.json':catalogue.encoded(value['candidates']),
            'pulse-cases.json':catalogue.encoded(value['pulse_cases']),
            'loadline-cases.json':catalogue.encoded(value['loadline_cases']),
            'README.md':_readme(value),'pulse-current.png':_plot(value)}
    return value,result


def run(output,root=ROOT):
    output=Path(output)
    if output.is_symlink() or any(p.is_symlink() for p in output.parents):raise ValueError('ordinary output required')
    if output.exists() and (not output.is_dir() or any(output.iterdir())):raise ValueError('fresh/empty immutable packet directory required')
    before=sources(root);value,files=payload(root)
    if sources(root)!=before:raise ValueError('source changed before publishing EPM packet')
    output.mkdir(parents=True,exist_ok=True)
    for name,raw in files.items():atomic_immutable(output/name,raw)
    manifest=dict(schema='osr-electropermanent-publication/1',study_id=value['study_id'],source_snapshot=before,
        source_sha256={**before['code_sha256'],**before['retained_sha256']},
        counts=value['counts'],environment=value['environment'],files_sha256={name:sha256(raw).hexdigest() for name,raw in files.items()},**FLAGS)
    manifest['manifest_id']=catalogue.identity(manifest)
    atomic_immutable(output/'manifest.json',catalogue.encoded(manifest))
    return manifest


def verify(output,root=ROOT):
    output=Path(output)
    if output.is_symlink() or not output.is_dir():raise ValueError('ordinary retained packet required')
    raw=(output/'manifest.json').read_bytes();manifest=json.loads(raw)
    if manifest.get('schema')!='osr-electropermanent-publication/1' or any(manifest.get(k) is not False for k in FLAGS):raise ValueError('EPM packet cannot assert release/acceptance')
    if manifest.get('manifest_id')!=catalogue.identity({k:v for k,v in manifest.items() if k!='manifest_id'}):raise ValueError('EPM receipt identity differs')
    if manifest.get('source_snapshot')!=sources(root):raise ValueError('EPM source bindings changed')
    if manifest.get('source_sha256')!={**manifest['source_snapshot']['code_sha256'],**manifest['source_snapshot']['retained_sha256']}:raise ValueError('EPM flat source bindings differ')
    value,expected=payload(root)
    if manifest['study_id']!=value['study_id'] or set(p.name for p in output.iterdir())!=set(expected)|{'manifest.json'}:raise ValueError('EPM study/inventory differs')
    if manifest.get('counts')!=value['counts'] or manifest.get('environment')!=value['environment'] or set(manifest['files_sha256'])!=set(expected):raise ValueError('EPM derived counts/environment/inventory differ')
    for name,source in expected.items():
        path=output/name
        if path.is_symlink() or not path.is_file() or path.read_bytes()!=source or manifest['files_sha256'].get(name)!=sha256(source).hexdigest():raise ValueError('EPM retained/fresh output differs: '+name)
    if sources(root)!=manifest['source_snapshot']:raise ValueError('EPM sources changed during verification')
    return dict(verified=True,study_id=value['study_id'],counts=value['counts'],physical_accepted=False)


def publish(output,root=ROOT):
    """Same immutable generator; parent chooses reviewed public destination."""
    return run(output,root)
