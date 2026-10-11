"""Complete-scope installed lifecycle ledger; missing prices remain unrankable."""
from engineering.industrialisation.common import finite, fingerprint

REQUIRED={'manufacture','transport','erection','temporary-works','land-access','inspection','maintenance','replacement','disruption','decommission'}


def installed_cost(entries,*,years,discount_rate):
    years=finite(years,'study life',1.);r=finite(discount_rate,'real discount',0.)
    ids=set();present=0.;unpriced=[];categories=set();quoted=True
    for row in entries:
        if not row['id'] or row['id'] in ids:raise ValueError('duplicate lifecycle line')
        ids.add(row['id']);categories.add(row['category'])
        if row['category'] not in REQUIRED:raise ValueError('unsupported lifecycle category')
        t=finite(row['year'],'cashflow year',0.);quantity=finite(row['quantity'],'quantity',0.)
        if t>years:raise ValueError('cashflow outside common lifetime')
        price=row['unit_price_usd']
        if price is None:unpriced.append(row['id']);continue
        price=finite(price,'unit price',0.);present+=quantity*price/(1+r)**t
        quoted=quoted and row.get('quote_sha256') is not None
    missing=sorted(REQUIRED-categories);complete=not missing and not unpriced
    return dict(schema='osr-installed-lifecycle-cost/1',ledger_sha256=fingerprint(entries),study_life_years=years,real_discount_rate=r,
        priced_subtotal_present_usd=present,complete_installed_lifecycle_present_usd=present if complete else None,
        missing_categories=missing,unpriced_lines=unpriced,complete_scope=complete,supplier_quotes_complete=complete and quoted,
        eligible_for_cost_ranking=complete,commercially_accepted=False,physical_validation=False)


def resistance(demands,capacities):
    names=('deck-flexure','deck-shear','deck-torsion','local-buckling','anchorage','pier-biaxial','cap','foundation','cracking','prestress','erection')
    if set(demands)!=set(names) or set(capacities)!=set(names):raise ValueError('complete installed civil limit-state register required')
    checks={}
    for name in names:
        demand=finite(demands[name],'civil demand '+name,0.);cap=capacities[name]
        checks[name]=dict(demand=demand,capacity=cap,passed=None if cap is None else demand<=finite(cap,'civil capacity '+name,1e-12))
    return dict(checks=checks,capacity_inputs_complete=all(r['passed'] is not None for r in checks.values()),
        within_declared_limits=all(r['passed'] is True for r in checks.values()),nonlinear_stiffness_feedback_qualified=False,physical_validation=False)
