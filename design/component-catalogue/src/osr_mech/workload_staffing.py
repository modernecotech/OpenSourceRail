"""Measured labour and simultaneous posts, distinct from budget redistribution."""
from collections import defaultdict
from datetime import date,timedelta
import math
from .industrialisation import nonnegative
from .provenance import stable_sum

ABSENCES=('leave_hours','training_hours','sickness_hours','holiday_hours','handover_hours')


def workload_staffing(operations,calendar):
    missing=[key for key in ('paid_hours_year',*ABSENCES) if calendar.get(key) is None]
    productive=None
    if not missing:
        for key in ('paid_hours_year',*ABSENCES):nonnegative(calendar[key],key)
        productive=calendar['paid_hours_year']-stable_sum(calendar[k] for k in ABSENCES)
        if productive<=0:raise ValueError('positive productive annual hours required')
    roles=defaultdict(lambda:dict(hours=[],missing=[],groups=defaultdict(int),sources=[]))
    ids=set()
    for op in operations:
        if op['id'] in ids:raise ValueError('duplicate workload operation')
        ids.add(op['id']);qty=op['qualified_people_per_task'];peak=op['simultaneous_tasks']
        if type(qty) is not int or qty<1 or type(peak) is not int or peak<0:
            raise ValueError('integer required role quantity and peak concurrency required')
        row=roles[op['role']];row['groups'][op['simultaneous_group']]+=qty*peak
        if op.get('annual_tasks') is None or op.get('worker_minutes_per_task') is None or not op.get('measurement_record'):
            row['missing'].append(op['id'])
        else:
            row['hours'].append(nonnegative(op['annual_tasks'],'annual tasks')*
                nonnegative(op['worker_minutes_per_task'],'measured worker minutes')*qty/60)
            row['sources'].append(op['measurement_record'])
    result=[]
    for role,row in sorted(roles.items()):
        known=stable_sum(row['hours']);peak=max(row['groups'].values(),default=0)
        labour=None if row['missing'] else known
        fte=max(peak,math.ceil(labour/productive)) if labour is not None and productive is not None else None
        result.append(dict(role=role,known_measured_person_hours=known,complete_person_hours=labour,
            peak_simultaneous_qualified_posts=peak,required_establishment_fte=fte,
            missing_measurements=row['missing'],measurement_records=row['sources'],funded_posts=None,
            qualified_named_people=None,work_authorisation_granted=False))
    return dict(roles=result,productive_hours_year=productive,missing_calendar_inputs=missing,
        budget_headcount_reallocated=False,operational_release=False,
        boundary='Declared simultaneous groups are workload bounds; task windows, shifts, leave, rest and independent acceptance still govern actual reservations.')


def recruitment_backplan(ready_on,qualified_posts,training):
    if ready_on is None or qualified_posts is None:return dict(target_ready_on=ready_on,recruitment_open_on=None,missing_readiness_or_workload=True,work_authority_granted=False)
    if type(qualified_posts) is not int or qualified_posts<1:raise ValueError('positive qualification target required')
    keys=('recruitment_days','induction_days','course_days','learners_per_cohort','parallel_cohorts','supervised_practice_days','assessment_days','assessor_people_per_day')
    if any(training.get(k) is None for k in keys):return dict(target_ready_on=ready_on,recruitment_open_on=None,missing_training_inputs=True,work_authority_granted=False)
    for k in keys:
        if type(training[k]) is not int or training[k]<1:raise ValueError('positive integer training capacity/lead time required')
    cohorts=math.ceil(qualified_posts/training['learners_per_cohort'])
    course_days=math.ceil(cohorts/training['parallel_cohorts'])*training['course_days']
    assessment=math.ceil(qualified_posts/training['assessor_people_per_day'])*training['assessment_days']
    ready=date.fromisoformat(ready_on);assess=ready-timedelta(days=assessment)
    practice=assess-timedelta(days=training['supervised_practice_days'])
    course=practice-timedelta(days=course_days);induction=course-timedelta(days=training['induction_days'])
    recruitment=induction-timedelta(days=training['recruitment_days'])
    return dict(target_ready_on=ready_on,recruitment_open_on=recruitment.isoformat(),induction_on=induction.isoformat(),
        course_start_on=course.isoformat(),supervised_practice_on=practice.isoformat(),assessment_on=assess.isoformat(),
        cohorts=cohorts,calendar_basis='elapsed planning days; employment calendar acceptance remains open',
        attendance_equals_equipment_authority=False,funding_approved=False,work_authority_granted=False)
