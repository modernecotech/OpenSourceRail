"""Bounded physical station-drive redesigns and next-experiment Pareto frontier."""
from . import ROOT,FLAGS,identity
from . import alternatives


def run(vehicle,base_bundle,*,root=ROOT):
    parent=alternatives.evaluate(vehicle,base_bundle,kind='station-pinch-rollers',distance_m=2000.,root=root)
    results=[parent];trials=[]
    for banks in (3,5,7):
        for pairs in (1,2,3,4):
            # This is a genuinely different count/location/clamp hardware
            # design; it is not a new label on unchanged force assumptions.
            step=412./(banks-1)
            changes=dict(bank_starts_m=[-12.+i*step for i in range(banks)],roller_pairs_per_bank=pairs,motor_count=2*pairs)
            candidate=(parent if all(parent['parameters'][k]==v for k,v in changes.items()) else
                alternatives.revise(vehicle,parent,changes,base_bundle,root=root))
            results.append(candidate)
            min_pairs=candidate['contact_geometry']['minimum_active_pairs'];cap=alternatives.force_model(candidate)
            # Segment/contact events are already exactly enumerated by the
            # geometry evaluator. Sampling here is a separate power screen.
            minimum_force=min(cap(x,20.)['force_N'][0] for x in range(501))
            required=next(r['required_force_N'] for r in candidate['load_cases'] if r['load']=='normal')
            trials.append(dict(candidate_id=candidate['candidate_id'],evaluation_id=candidate['evaluation_id'],parent_candidate_id=parent['candidate_id'],
                banks=banks,roller_pairs_per_bank=pairs,installed_motors=banks*2*pairs,minimum_active_pairs=min_pairs,
                exact_geometric_contact_m=candidate['contact_geometry']['powered_distance_m'],
                sampled_force_lower_cap_at20_N=minimum_force,normal_required_force_at20_N=required,
                necessary_force_screen_passed=minimum_force>=required,source_published_motor_mass_kg=candidate['published_catalogue_mass_subtotal_kg'],
                failure_kind='physical-necessary-bound' if minimum_force<required else 'conditional-contact-power-bound-only',
                unknown_mass_items=candidate['unknown_installed_mass_items'],complete_installed_cost_usd=None,
                next_action='Revise bank/contact count or motor/gearing/clamp architecture' if minimum_force<required else 'Prototype contact/thermal/control and attachment tests; simulate complete installed architecture'))
    supported=[r for r in trials if r['necessary_force_screen_passed']]
    frontier=[]
    for row in supported:
        dominated=any(p['source_published_motor_mass_kg']<=row['source_published_motor_mass_kg'] and p['installed_motors']<=row['installed_motors'] and
            (p['source_published_motor_mass_kg']<row['source_published_motor_mass_kg'] or p['installed_motors']<row['installed_motors']) for p in supported)
        if not dominated:frontier.append(row['candidate_id'])
    value=dict(schema='osr-physical-station-drive-redesigns/1',body_candidate_id=vehicle['candidate_id'],
        parent_candidate_id=parent['candidate_id'],trials=trials,trial_budget=12,native_solves=0,
        next_experiment_frontier=frontier,selection_purpose='Conditional minimum-count/catalogue-mass experiment selection only',
        qualified_integrated_frontier=[],integrated_winner=None,**FLAGS)
    value['evaluation_id']=identity(value);return value
