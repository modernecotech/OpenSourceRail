"""Offline boundaries using compact-drive source DATA, never hardware acceptance.

The embedded three part definitions and36 counted patterns came from the held
compact-737-h150 phase1 record. Its source epoch was checked before extraction.
No historical body or evaluation is resealed. fixture_body creates a NEW,
explicitly synthetic three-type body, with test-only make/buy conversion and
no inherited whole-train geometry, mass, native result or engineering evidence.
"""
from collections import Counter
from copy import deepcopy
from math import fsum
import json
from pathlib import Path

import pytest

from engineering.railway_project import delivery, drawings
from engineering.pilot_delivery import model, review
from engineering.station_rail.common import identity, digest
from engineering.station_pair.lifecycle import OWNER_SCOPES
from engineering.design_search.model_cost import SCOPES

SOURCE_DATA = {'assembly_occurrences': {'research/compact-drive/integration': [{'at_m': [8.5, 0.0, 0.0],
                                                                  'bogie_index': None,
                                                                  'car_allocation': [[0, 1.0]],
                                                                  'id': 'compact/0/None/None/integration'},
                                                                 {'at_m': [26.15, 0.0, 0.0],
                                                                  'bogie_index': None,
                                                                  'car_allocation': [[1, 1.0]],
                                                                  'id': 'compact/1/None/None/integration'},
                                                                 {'at_m': [43.8, 0.0, 0.0],
                                                                  'bogie_index': None,
                                                                  'car_allocation': [[2, 1.0]],
                                                                  'id': 'compact/2/None/None/integration'},
                                                                 {'at_m': [61.449999999999996, 0.0, 0.0],
                                                                  'bogie_index': None,
                                                                  'car_allocation': [[3, 1.0]],
                                                                  'id': 'compact/3/None/None/integration'},
                                                                 {'at_m': [79.1, 0.0, 0.0],
                                                                  'bogie_index': None,
                                                                  'car_allocation': [[4, 1.0]],
                                                                  'id': 'compact/4/None/None/integration'},
                                                                 {'at_m': [96.75, 0.0, 0.0],
                                                                  'bogie_index': None,
                                                                  'car_allocation': [[5, 1.0]],
                                                                  'id': 'compact/5/None/None/integration'}],
                          'research/compact-drive/motor': [{'at_m': [8.5, 0.0, 0.0],
                                                            'bogie_index': 0,
                                                            'car_allocation': [[0, 1.0]],
                                                            'id': 'compact/0/0/0/motor'},
                                                           {'at_m': [8.5, 0.0, 0.0],
                                                            'bogie_index': 0,
                                                            'car_allocation': [[0, 1.0]],
                                                            'id': 'compact/0/0/1/motor'},
                                                           {'at_m': [8.5, 0.0, 0.0],
                                                            'bogie_index': 1,
                                                            'car_allocation': [[0, 1.0]],
                                                            'id': 'compact/0/1/2/motor'},
                                                           {'at_m': [8.5, 0.0, 0.0],
                                                            'bogie_index': 1,
                                                            'car_allocation': [[0, 1.0]],
                                                            'id': 'compact/0/1/3/motor'},
                                                           {'at_m': [26.15, 0.0, 0.0],
                                                            'bogie_index': 2,
                                                            'car_allocation': [[1, 1.0]],
                                                            'id': 'compact/1/2/4/motor'},
                                                           {'at_m': [26.15, 0.0, 0.0],
                                                            'bogie_index': 2,
                                                            'car_allocation': [[1, 1.0]],
                                                            'id': 'compact/1/2/5/motor'},
                                                           {'at_m': [26.15, 0.0, 0.0],
                                                            'bogie_index': 3,
                                                            'car_allocation': [[1, 1.0]],
                                                            'id': 'compact/1/3/6/motor'},
                                                           {'at_m': [26.15, 0.0, 0.0],
                                                            'bogie_index': 3,
                                                            'car_allocation': [[1, 1.0]],
                                                            'id': 'compact/1/3/7/motor'},
                                                           {'at_m': [43.8, 0.0, 0.0],
                                                            'bogie_index': 4,
                                                            'car_allocation': [[2, 1.0]],
                                                            'id': 'compact/2/4/8/motor'},
                                                           {'at_m': [43.8, 0.0, 0.0],
                                                            'bogie_index': 4,
                                                            'car_allocation': [[2, 1.0]],
                                                            'id': 'compact/2/4/9/motor'},
                                                           {'at_m': [43.8, 0.0, 0.0],
                                                            'bogie_index': 5,
                                                            'car_allocation': [[2, 1.0]],
                                                            'id': 'compact/2/5/10/motor'},
                                                           {'at_m': [43.8, 0.0, 0.0],
                                                            'bogie_index': 5,
                                                            'car_allocation': [[2, 1.0]],
                                                            'id': 'compact/2/5/11/motor'},
                                                           {'at_m': [61.449999999999996, 0.0, 0.0],
                                                            'bogie_index': 6,
                                                            'car_allocation': [[3, 1.0]],
                                                            'id': 'compact/3/6/12/motor'},
                                                           {'at_m': [61.449999999999996, 0.0, 0.0],
                                                            'bogie_index': 6,
                                                            'car_allocation': [[3, 1.0]],
                                                            'id': 'compact/3/6/13/motor'},
                                                           {'at_m': [61.449999999999996, 0.0, 0.0],
                                                            'bogie_index': 7,
                                                            'car_allocation': [[3, 1.0]],
                                                            'id': 'compact/3/7/14/motor'},
                                                           {'at_m': [61.449999999999996, 0.0, 0.0],
                                                            'bogie_index': 7,
                                                            'car_allocation': [[3, 1.0]],
                                                            'id': 'compact/3/7/15/motor'},
                                                           {'at_m': [79.1, 0.0, 0.0],
                                                            'bogie_index': 8,
                                                            'car_allocation': [[4, 1.0]],
                                                            'id': 'compact/4/8/16/motor'},
                                                           {'at_m': [79.1, 0.0, 0.0],
                                                            'bogie_index': 8,
                                                            'car_allocation': [[4, 1.0]],
                                                            'id': 'compact/4/8/17/motor'},
                                                           {'at_m': [79.1, 0.0, 0.0],
                                                            'bogie_index': 9,
                                                            'car_allocation': [[4, 1.0]],
                                                            'id': 'compact/4/9/18/motor'},
                                                           {'at_m': [79.1, 0.0, 0.0],
                                                            'bogie_index': 9,
                                                            'car_allocation': [[4, 1.0]],
                                                            'id': 'compact/4/9/19/motor'},
                                                           {'at_m': [96.75, 0.0, 0.0],
                                                            'bogie_index': 10,
                                                            'car_allocation': [[5, 1.0]],
                                                            'id': 'compact/5/10/20/motor'},
                                                           {'at_m': [96.75, 0.0, 0.0],
                                                            'bogie_index': 10,
                                                            'car_allocation': [[5, 1.0]],
                                                            'id': 'compact/5/10/21/motor'},
                                                           {'at_m': [96.75, 0.0, 0.0],
                                                            'bogie_index': 11,
                                                            'car_allocation': [[5, 1.0]],
                                                            'id': 'compact/5/11/22/motor'},
                                                           {'at_m': [96.75, 0.0, 0.0],
                                                            'bogie_index': 11,
                                                            'car_allocation': [[5, 1.0]],
                                                            'id': 'compact/5/11/23/motor'}]},
 'materials': [{'basis': 'Proposed dimensional/material hypothesis, not a certificate or an approved railway '
                         'grade',
                'density_kg_m3': None,
                'form': 'qualified purchased component',
                'id': 'running/mixed-module',
                'qualification_required': True,
                'specification': 'Explicitly bounded multi-material purchased module, no complete assembly '
                                 'weight hidden'},
               {'basis': 'Proposed dimensional density hypothesis, not measured stock or certified '
                         'properties',
                'density_kg_m3': 7850,
                'form': 'plate/section',
                'id': 'body/steel',
                'qualification_required': True,
                'specification': 'Proposed weldable structural steel with traceable grade and impact '
                                 'properties'}],
 'parts': [{'BOP_partition': False,
            'assembly_id': 'research/compact-drive/motor',
            'candidate_id': '50af70c100ce71812ebc32c8e733850a5b621f41acaad5bf08fcdb9ae044ec7f',
            'component_definition_id': '50af70c100ce71812ebc32c8e733850a5b621f41acaad5bf08fcdb9ae044ec7f',
            'cost_basis': 'Declared Chinese/bulk source material/yield/process/labour/QA/overhead rates or '
                          'positive equipment allowance; no quotation, final integration or qualification',
            'direct_cost_each_usd': {'base': 5000, 'high': 9000, 'low': 2500},
            'finish': 'Declared corrosion/isolation protection; actual specification open',
            'id': 'compact-drive/vendor-motor',
            'inspection': ['Source/material identity and nominal dimensions',
                           'Bore/shaft/pilot/bolt-axis survey and fit record',
                           'Gear tooth/root/hardness/runout or pressure/insulation checks as applicable; '
                           'acceptance limits pending'],
            'joining': 'Explicit proposed axes, holes and mating interfaces; strength/fatigue not qualified',
            'maintenance_removal': 'Isolate and support machine, remove named guards and flexible services, '
                                   'retain fasteners and use supported finite removal path',
            'make_buy': 'bounded-purchase-or-process',
            'manufacturing': ['Identify material and stock; machine/drill stated interfaces',
                              'Fixture and assemble with retained fasteners, documented tools and access',
                              'Inspect geometry, torque, balance, insulation/pressure as appropriate; record '
                              'finished mass'],
            'mass_basis': {'description': 'Gross stock/explicit bounds; not measured installed mass',
                           'kind': 'positive-bounded-component'},
            'mass_each_kg': {'base': 22.3, 'high': 22.3, 'low': 22.3},
            'material_id': 'running/mixed-module',
            'mounting': 'Explicitbogie frame; proposed stock/hole/retention interfaces require independent '
                        'verification',
            'name': 'vendor-motor',
            'open_tasks': ['Detailed tolerance, contact/fatigue, actual capacity, access and release '
                           'evidence'],
            'process_quantities': {'allowance_not_quotation': True,
                                   'extra_labour_h_each': 0.0,
                                   'gear_heat_treatment_allowance_usd': None},
            'quantity_per_assembly': 1,
            'quantity_per_train': 24,
            'research_geometry': {'frame': 'bogie',
                                  'group': 'motor',
                                  'internal_bearings': 2,
                                  'internal_bearings_mass_owned': True,
                                  'role': 'equipment-envelope',
                                  'scope': 'Official casing dimensions plus explicit terminal/shaft '
                                           'required-space provision; actual privateSTEP import and revision '
                                           'compatibility pending. No fabricated supplier housing.',
                                  'vendor': {'STEP': {'bytes': 31676116,
                                                      'model_B_datasheet_C_compatibility_verified': False,
                                                      'native_length_unit': 'mm',
                                                      'private_only': True,
                                                      'redistribution_licence_verified': False,
                                                      'sha256': 'fa9122c9e87022b174040c2871f4851061d2bdc3835a7722a330ecc37f989545',
                                                      'simplified': True,
                                                      'url': 'https://emrax.com/wp-content/uploads/2025/09/268_MVHV_1UVW_LC_SS_PP_SE268P_B.step'},
                                             'back_mounts': {'count': 16,
                                                             'thread': 'M8',
                                                             'unused_not_additional_mounts': True},
                                             'casing_diameter_m': 0.268,
                                             'casing_length_m': 0.094,
                                             'catalogue': {'conditions': 'Catalogue conditions only; '
                                                                         'repeated duty, inverter/voltage '
                                                                         'and heat rejection must be '
                                                                         'calculated independently at actual '
                                                                         'ambient. Do not use old1.6 '
                                                                         'continuous117kW/250Nm or source '
                                                                         'TSA/ABB force maps.',
                                                           'continuous_current_A': 220,
                                                           'continuous_power_W': 91000,
                                                           'continuous_torque_Nm': 205,
                                                           'coolant_max_C': 50,
                                                           'coolant_min_l_min': 6,
                                                           'maximum_rpm': 4500,
                                                           'peak_current_A': 500,
                                                           'peak_duration_s': 30,
                                                           'peak_torque_Nm': 500,
                                                           'peak_voltage_V': 830,
                                                           'requires_rotor_airflow': True},
                                             'datasheet': {'sha256': 'a3c527667ddcaafd3f49be6f06599cf2316fca12d60e8fe5b7f789e9f6f532ab',
                                                           'url': 'https://emrax.com/wp-content/uploads/2026/08/EMRAX_268_datasheet_v1.7_version-C.pdf'},
                                             'dimension_image': {'sha256': 'e6bdeeaa4812ced712e4a89ba187ab20fec60cf2e0c6e7c1ec515d1d96c74190',
                                                                 'url': 'https://emrax.com/wp-content/uploads/2025/08/dimensions268-1c.png'},
                                             'drawing_length_m': 0.0933,
                                             'drawing_length_tolerance_m': 0.00015,
                                             'dry_mass_kg': 22.3,
                                             'engineering_accepted': False,
                                             'front_mounts': {'axis': 'motor shaft axis; verify actual '
                                                                      'STEP/drawing datums',
                                                              'count': 6,
                                                              'pitch_circle_m': 0.094,
                                                              'thread': 'M10'},
                                             'manufacturing_release': False,
                                             'operating_release': False,
                                             'physical_accepted': False,
                                             'product': 'EMRAX268-C v1.7 MV LC',
                                             'role': 'New PM-powered research alternative only; not '
                                                     'selected, railway-qualified or hot-duty admitted',
                                             'schema': 'osr-compact-drive-vendor-facts/1',
                                             'selected_reference_changed': False}},
            'source_ids': ['emrax/268-v1.7-C'],
            'source_part_id': None,
            'stock': {'kind': 'envelope', 'size_m': [0.308, 0.18, 0.308]},
            'tolerance_and_fits': 'Nominal research geometry with explicit policy uncertainty/tolerance; no '
                                  'approved manufacturing fit or safety limit',
            'unit': 'item'},
           {'BOP_partition': False,
            'assembly_id': 'research/compact-drive/integration',
            'candidate_id': '8bd6784835c1c12bf79c9f7d794fbf1de1a2168d4e3bec76c3c3b37a1498a130',
            'component_definition_id': '8bd6784835c1c12bf79c9f7d794fbf1de1a2168d4e3bec76c3c3b37a1498a130',
            'cost_basis': 'Declared Chinese/bulk source material/yield/process/labour/QA/overhead rates or '
                          'positive equipment allowance; no quotation, final integration or qualification',
            'direct_cost_each_usd': {'base': 1600, 'high': 3200, 'low': 800},
            'finish': 'Declared corrosion/isolation protection; actual specification open',
            'id': 'compact-drive/inverter',
            'inspection': ['Source/material identity and nominal dimensions',
                           'Bore/shaft/pilot/bolt-axis survey and fit record',
                           'Gear tooth/root/hardness/runout or pressure/insulation checks as applicable; '
                           'acceptance limits pending'],
            'joining': 'Explicit proposed axes, holes and mating interfaces; strength/fatigue not qualified',
            'maintenance_removal': 'Isolate and support machine, remove named guards and flexible services, '
                                   'retain fasteners and use supported finite removal path',
            'make_buy': 'bounded-purchase-or-process',
            'manufacturing': ['Identify material and stock; machine/drill stated interfaces',
                              'Fixture and assemble with retained fasteners, documented tools and access',
                              'Inspect geometry, torque, balance, insulation/pressure as appropriate; record '
                              'finished mass'],
            'mass_basis': {'description': 'Gross stock/explicit bounds; not measured installed mass',
                           'kind': 'positive-bounded-component'},
            'mass_each_kg': {'base': 30, 'high': 50, 'low': 18},
            'material_id': 'body/steel',
            'mounting': 'Explicitbody frame; proposed stock/hole/retention interfaces require independent '
                        'verification',
            'name': 'inverter',
            'open_tasks': ['Detailed tolerance, contact/fatigue, actual capacity, access and release '
                           'evidence'],
            'process_quantities': {'allowance_not_quotation': True,
                                   'extra_labour_h_each': 0.0,
                                   'gear_heat_treatment_allowance_usd': None},
            'quantity_per_assembly': 4,
            'quantity_per_train': 24,
            'research_geometry': {'capacity_not_verified': True,
                                  'frame': 'body',
                                  'group': 'integration',
                                  'remaining_positive_unknown': True,
                                  'role': 'equipment-envelope'},
            'source_ids': ['osr/compact-drive-calculated'],
            'source_part_id': None,
            'stock': {'kind': 'envelope', 'size_m': [0.45, 0.25, 0.2]},
            'tolerance_and_fits': 'Nominal research geometry with explicit policy uncertainty/tolerance; no '
                                  'approved manufacturing fit or safety limit',
            'unit': 'item'},
           {'BOP_partition': False,
            'assembly_id': 'research/compact-drive/integration',
            'candidate_id': '138e5f1f4d06f90465a9dd8778b008000bb2b1e7543062eb27f6b9698cf22632',
            'component_definition_id': '138e5f1f4d06f90465a9dd8778b008000bb2b1e7543062eb27f6b9698cf22632',
            'cost_basis': 'Declared Chinese/bulk source material/yield/process/labour/QA/overhead rates or '
                          'positive equipment allowance; no quotation, final integration or qualification',
            'direct_cost_each_usd': {'base': 10000, 'high': 25000, 'low': 4000},
            'finish': 'Declared corrosion/isolation protection; actual specification open',
            'id': 'compact-drive/integration-reserve',
            'inspection': ['Source/material identity and nominal dimensions',
                           'Bore/shaft/pilot/bolt-axis survey and fit record',
                           'Gear tooth/root/hardness/runout or pressure/insulation checks as applicable; '
                           'acceptance limits pending'],
            'joining': 'Explicit proposed axes, holes and mating interfaces; strength/fatigue not qualified',
            'maintenance_removal': 'Isolate and support machine, remove named guards and flexible services, '
                                   'retain fasteners and use supported finite removal path',
            'make_buy': 'bounded-purchase-or-process',
            'manufacturing': ['Identify material and stock; machine/drill stated interfaces',
                              'Fixture and assemble with retained fasteners, documented tools and access',
                              'Inspect geometry, torque, balance, insulation/pressure as appropriate; record '
                              'finished mass'],
            'mass_basis': {'description': 'Gross stock/explicit bounds; not measured installed mass',
                           'kind': 'positive-bounded-component'},
            'mass_each_kg': {'base': 400, 'high': 800, 'low': 200},
            'material_id': 'body/steel',
            'mounting': 'Explicitbody frame; proposed stock/hole/retention interfaces require independent '
                        'verification',
            'name': 'integration-reserve',
            'open_tasks': ['Detailed tolerance, contact/fatigue, actual capacity, access and release '
                           'evidence'],
            'process_quantities': {'allowance_not_quotation': True,
                                   'extra_labour_h_each': 0.0,
                                   'gear_heat_treatment_allowance_usd': None},
            'quantity_per_assembly': 1,
            'quantity_per_train': 6,
            'research_geometry': {'capacity_not_verified': True,
                                  'frame': 'body',
                                  'group': 'integration',
                                  'remaining_positive_unknown': True,
                                  'role': 'allocation'},
            'source_ids': ['osr/compact-drive-calculated'],
            'source_part_id': None,
            'stock': {'kind': 'envelope', 'size_m': [1.2, 1.0, 0.5]},
            'tolerance_and_fits': 'Nominal research geometry with explicit policy uncertainty/tolerance; no '
                                  'approved manufacturing fit or safety limit',
            'unit': 'item'}],
 'pattern_groups': [{'common': {'assembly_id': 'research/compact-drive/motor',
                                'count': 1,
                                'direct_cost_usd': {'base': 5000, 'high': 9000, 'low': 2500},
                                'geometry': {'definition_basis': 'catalogue-equipment-envelope',
                                             'exact_stock': False,
                                             'finished_geometry_verified': False,
                                             'kind': 'envelope',
                                             'size_m': [0.308, 0.18, 0.308],
                                             'source_stock': {'kind': 'envelope',
                                                              'size_m': [0.308, 0.18, 0.308]}},
                                'make_buy': 'bounded-purchase-or-process',
                                'mass_kg': {'base': 22.3, 'high': 22.3, 'low': 22.3},
                                'material_id': 'running/mixed-module',
                                'part_id': 'compact-drive/vendor-motor',
                                'proposed_position_not_measurement': True,
                                'shape_I_per_kg': [[0.010605333333333333, 0.0, 0.0],
                                                   [0.0, 0.015810666666666667, 0.0],
                                                   [0.0, 0.0, 0.010605333333333333]],
                                'source_part_id': None,
                                'uncertainty_m': [0.05, 0.05, 0.05]},
                     'rows': [{'assembly_occurrence_id': 'compact/0/0/0/motor',
                               'bogie_index': 0,
                               'car_allocation': [[0, 1.0]],
                               'centroid_m': [1.4562202752569844, -0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/0/0/0/motor',
                               'positions_m': [[1.4562202752569844, -0.38, 0.43]],
                               'rotation': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/0/0/1/motor',
                               'bogie_index': 0,
                               'car_allocation': [[0, 1.0]],
                               'centroid_m': [2.743779724743015, 0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/0/0/1/motor',
                               'positions_m': [[2.743779724743015, 0.38, 0.43]],
                               'rotation': [[-1.0, -0.0, -0.0], [-0.0, -1.0, -0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/0/1/2/motor',
                               'bogie_index': 1,
                               'car_allocation': [[0, 1.0]],
                               'centroid_m': [14.256220275256986, -0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/0/1/2/motor',
                               'positions_m': [[14.256220275256986, -0.38, 0.43]],
                               'rotation': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/0/1/3/motor',
                               'bogie_index': 1,
                               'car_allocation': [[0, 1.0]],
                               'centroid_m': [15.543779724743015, 0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/0/1/3/motor',
                               'positions_m': [[15.543779724743015, 0.38, 0.43]],
                               'rotation': [[-1.0, -0.0, -0.0], [-0.0, -1.0, -0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/1/2/4/motor',
                               'bogie_index': 2,
                               'car_allocation': [[1, 1.0]],
                               'centroid_m': [19.106220275256984, -0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/1/2/4/motor',
                               'positions_m': [[19.106220275256984, -0.38, 0.43]],
                               'rotation': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/1/2/5/motor',
                               'bogie_index': 2,
                               'car_allocation': [[1, 1.0]],
                               'centroid_m': [20.393779724743016, 0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/1/2/5/motor',
                               'positions_m': [[20.393779724743016, 0.38, 0.43]],
                               'rotation': [[-1.0, -0.0, -0.0], [-0.0, -1.0, -0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/1/3/6/motor',
                               'bogie_index': 3,
                               'car_allocation': [[1, 1.0]],
                               'centroid_m': [31.90622027525698, -0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/1/3/6/motor',
                               'positions_m': [[31.90622027525698, -0.38, 0.43]],
                               'rotation': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/1/3/7/motor',
                               'bogie_index': 3,
                               'car_allocation': [[1, 1.0]],
                               'centroid_m': [33.19377972474301, 0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/1/3/7/motor',
                               'positions_m': [[33.19377972474301, 0.38, 0.43]],
                               'rotation': [[-1.0, -0.0, -0.0], [-0.0, -1.0, -0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/2/4/8/motor',
                               'bogie_index': 4,
                               'car_allocation': [[2, 1.0]],
                               'centroid_m': [36.756220275256986, -0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/2/4/8/motor',
                               'positions_m': [[36.756220275256986, -0.38, 0.43]],
                               'rotation': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/2/4/9/motor',
                               'bogie_index': 4,
                               'car_allocation': [[2, 1.0]],
                               'centroid_m': [38.04377972474301, 0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/2/4/9/motor',
                               'positions_m': [[38.04377972474301, 0.38, 0.43]],
                               'rotation': [[-1.0, -0.0, -0.0], [-0.0, -1.0, -0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/2/5/10/motor',
                               'bogie_index': 5,
                               'car_allocation': [[2, 1.0]],
                               'centroid_m': [49.55622027525698, -0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/2/5/10/motor',
                               'positions_m': [[49.55622027525698, -0.38, 0.43]],
                               'rotation': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/2/5/11/motor',
                               'bogie_index': 5,
                               'car_allocation': [[2, 1.0]],
                               'centroid_m': [50.84377972474301, 0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/2/5/11/motor',
                               'positions_m': [[50.84377972474301, 0.38, 0.43]],
                               'rotation': [[-1.0, -0.0, -0.0], [-0.0, -1.0, -0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/3/6/12/motor',
                               'bogie_index': 6,
                               'car_allocation': [[3, 1.0]],
                               'centroid_m': [54.406220275256985, -0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/3/6/12/motor',
                               'positions_m': [[54.406220275256985, -0.38, 0.43]],
                               'rotation': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/3/6/13/motor',
                               'bogie_index': 6,
                               'car_allocation': [[3, 1.0]],
                               'centroid_m': [55.69377972474301, 0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/3/6/13/motor',
                               'positions_m': [[55.69377972474301, 0.38, 0.43]],
                               'rotation': [[-1.0, -0.0, -0.0], [-0.0, -1.0, -0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/3/7/14/motor',
                               'bogie_index': 7,
                               'car_allocation': [[3, 1.0]],
                               'centroid_m': [67.20622027525698, -0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/3/7/14/motor',
                               'positions_m': [[67.20622027525698, -0.38, 0.43]],
                               'rotation': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/3/7/15/motor',
                               'bogie_index': 7,
                               'car_allocation': [[3, 1.0]],
                               'centroid_m': [68.493779724743, 0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/3/7/15/motor',
                               'positions_m': [[68.493779724743, 0.38, 0.43]],
                               'rotation': [[-1.0, -0.0, -0.0], [-0.0, -1.0, -0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/4/8/16/motor',
                               'bogie_index': 8,
                               'car_allocation': [[4, 1.0]],
                               'centroid_m': [72.05622027525698, -0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/4/8/16/motor',
                               'positions_m': [[72.05622027525698, -0.38, 0.43]],
                               'rotation': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/4/8/17/motor',
                               'bogie_index': 8,
                               'car_allocation': [[4, 1.0]],
                               'centroid_m': [73.343779724743, 0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/4/8/17/motor',
                               'positions_m': [[73.343779724743, 0.38, 0.43]],
                               'rotation': [[-1.0, -0.0, -0.0], [-0.0, -1.0, -0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/4/9/18/motor',
                               'bogie_index': 9,
                               'car_allocation': [[4, 1.0]],
                               'centroid_m': [84.85622027525699, -0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/4/9/18/motor',
                               'positions_m': [[84.85622027525699, -0.38, 0.43]],
                               'rotation': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/4/9/19/motor',
                               'bogie_index': 9,
                               'car_allocation': [[4, 1.0]],
                               'centroid_m': [86.14377972474301, 0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/4/9/19/motor',
                               'positions_m': [[86.14377972474301, 0.38, 0.43]],
                               'rotation': [[-1.0, -0.0, -0.0], [-0.0, -1.0, -0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/5/10/20/motor',
                               'bogie_index': 10,
                               'car_allocation': [[5, 1.0]],
                               'centroid_m': [89.70622027525698, -0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/5/10/20/motor',
                               'positions_m': [[89.70622027525698, -0.38, 0.43]],
                               'rotation': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/5/10/21/motor',
                               'bogie_index': 10,
                               'car_allocation': [[5, 1.0]],
                               'centroid_m': [90.993779724743, 0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/5/10/21/motor',
                               'positions_m': [[90.993779724743, 0.38, 0.43]],
                               'rotation': [[-1.0, -0.0, -0.0], [-0.0, -1.0, -0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/5/11/22/motor',
                               'bogie_index': 11,
                               'car_allocation': [[5, 1.0]],
                               'centroid_m': [102.506220275257, -0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/5/11/22/motor',
                               'positions_m': [[102.506220275257, -0.38, 0.43]],
                               'rotation': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]},
                              {'assembly_occurrence_id': 'compact/5/11/23/motor',
                               'bogie_index': 11,
                               'car_allocation': [[5, 1.0]],
                               'centroid_m': [103.79377972474302, 0.38, 0.43],
                               'id': 'compact-drive/vendor-motor@compact/5/11/23/motor',
                               'positions_m': [[103.79377972474302, 0.38, 0.43]],
                               'rotation': [[-1.0, -0.0, -0.0], [-0.0, -1.0, -0.0], [0.0, 0.0, 1.0]]}]},
                    {'common': {'assembly_id': 'research/compact-drive/integration',
                                'bogie_index': None,
                                'count': 4,
                                'direct_cost_usd': {'base': 6400, 'high': 12800, 'low': 3200},
                                'geometry': {'definition_basis': 'catalogue-equipment-envelope',
                                             'exact_stock': False,
                                             'finished_geometry_verified': False,
                                             'kind': 'envelope',
                                             'size_m': [0.45, 0.25, 0.2],
                                             'source_stock': {'kind': 'envelope',
                                                              'size_m': [0.45, 0.25, 0.2]}},
                                'make_buy': 'bounded-purchase-or-process',
                                'mass_kg': {'base': 120, 'high': 200, 'low': 72},
                                'material_id': 'body/steel',
                                'part_id': 'compact-drive/inverter',
                                'proposed_position_not_measurement': True,
                                'rotation': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
                                'source_part_id': None,
                                'uncertainty_m': [0.05, 0.05, 0.05]},
                     'rows': [{'assembly_occurrence_id': 'compact/0/None/None/integration',
                               'car_allocation': [[0, 1.0]],
                               'centroid_m': [8.5, 0.0, 0.8],
                               'id': 'compact-drive/inverter@compact/0/None/None/integration',
                               'positions_m': [[4.0, -1.08, 0.8],
                                               [4.0, -0.72, 0.8],
                                               [13.0, 0.72, 0.8],
                                               [13.0, 1.08, 0.8]],
                               'shape_I_per_kg': [[0.850941666666668, -4.05, 0.0],
                                                  [-4.05, 20.270208333333333, 0.0],
                                                  [0.0, 0.0, 21.114483333333336]]},
                              {'assembly_occurrence_id': 'compact/1/None/None/integration',
                               'car_allocation': [[1, 1.0]],
                               'centroid_m': [26.15, 0.0, 0.8],
                               'id': 'compact-drive/inverter@compact/1/None/None/integration',
                               'positions_m': [[21.65, -1.08, 0.8],
                                               [21.65, -0.72, 0.8],
                                               [30.65, 0.72, 0.8],
                                               [30.65, 1.08, 0.8]],
                               'shape_I_per_kg': [[0.850941666666668, -4.05, 0.0],
                                                  [-4.05, 20.270208333333333, 0.0],
                                                  [0.0, 0.0, 21.114483333333336]]},
                              {'assembly_occurrence_id': 'compact/2/None/None/integration',
                               'car_allocation': [[2, 1.0]],
                               'centroid_m': [43.8, 0.0, 0.8],
                               'id': 'compact-drive/inverter@compact/2/None/None/integration',
                               'positions_m': [[39.3, -1.08, 0.8],
                                               [39.3, -0.72, 0.8],
                                               [48.3, 0.72, 0.8],
                                               [48.3, 1.08, 0.8]],
                               'shape_I_per_kg': [[0.850941666666668, -4.05, 0.0],
                                                  [-4.05, 20.270208333333333, 0.0],
                                                  [0.0, 0.0, 21.114483333333336]]},
                              {'assembly_occurrence_id': 'compact/3/None/None/integration',
                               'car_allocation': [[3, 1.0]],
                               'centroid_m': [61.44999999999999, 0.0, 0.8],
                               'id': 'compact-drive/inverter@compact/3/None/None/integration',
                               'positions_m': [[56.949999999999996, -1.08, 0.8],
                                               [56.949999999999996, -0.72, 0.8],
                                               [65.94999999999999, 0.72, 0.8],
                                               [65.94999999999999, 1.08, 0.8]],
                               'shape_I_per_kg': [[0.850941666666668, -4.049999999999997, 0.0],
                                                  [-4.049999999999997, 20.2702083333333, 0.0],
                                                  [0.0, 0.0, 21.114483333333304]]},
                              {'assembly_occurrence_id': 'compact/4/None/None/integration',
                               'car_allocation': [[4, 1.0]],
                               'centroid_m': [79.1, 0.0, 0.8],
                               'id': 'compact-drive/inverter@compact/4/None/None/integration',
                               'positions_m': [[74.6, -1.08, 0.8],
                                               [74.6, -0.72, 0.8],
                                               [83.6, 0.72, 0.8],
                                               [83.6, 1.08, 0.8]],
                               'shape_I_per_kg': [[0.850941666666668, -4.05, 0.0],
                                                  [-4.05, 20.270208333333333, 0.0],
                                                  [0.0, 0.0, 21.114483333333336]]},
                              {'assembly_occurrence_id': 'compact/5/None/None/integration',
                               'car_allocation': [[5, 1.0]],
                               'centroid_m': [96.75, 0.0, 0.8],
                               'id': 'compact-drive/inverter@compact/5/None/None/integration',
                               'positions_m': [[92.25, -1.08, 0.8],
                                               [92.25, -0.72, 0.8],
                                               [101.25, 0.72, 0.8],
                                               [101.25, 1.08, 0.8]],
                               'shape_I_per_kg': [[0.850941666666668, -4.05, 0.0],
                                                  [-4.05, 20.270208333333333, 0.0],
                                                  [0.0, 0.0, 21.114483333333336]]}]},
                    {'common': {'assembly_id': 'research/compact-drive/integration',
                                'bogie_index': None,
                                'count': 1,
                                'direct_cost_usd': {'base': 10000, 'high': 25000, 'low': 4000},
                                'geometry': {'definition_basis': 'catalogue-equipment-envelope',
                                             'exact_stock': False,
                                             'finished_geometry_verified': False,
                                             'kind': 'envelope',
                                             'size_m': [1.2, 1.0, 0.5],
                                             'source_stock': {'kind': 'envelope', 'size_m': [1.2, 1.0, 0.5]}},
                                'make_buy': 'bounded-purchase-or-process',
                                'mass_kg': {'base': 400, 'high': 800, 'low': 200},
                                'material_id': 'body/steel',
                                'part_id': 'compact-drive/integration-reserve',
                                'proposed_position_not_measurement': True,
                                'rotation': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
                                'shape_I_per_kg': [[0.10416666666666667, 0.0, 0.0],
                                                   [0.0, 0.14083333333333334, 0.0],
                                                   [0.0, 0.0, 0.20333333333333334]],
                                'source_part_id': None,
                                'uncertainty_m': [0.05, 0.05, 0.05]},
                     'rows': [{'assembly_occurrence_id': 'compact/0/None/None/integration',
                               'car_allocation': [[0, 1.0]],
                               'centroid_m': [8.5, 0.0, 2.05],
                               'id': 'compact-drive/integration-reserve@compact/0/None/None/integration',
                               'positions_m': [[8.5, 0.0, 2.05]]},
                              {'assembly_occurrence_id': 'compact/1/None/None/integration',
                               'car_allocation': [[1, 1.0]],
                               'centroid_m': [26.15, 0.0, 2.05],
                               'id': 'compact-drive/integration-reserve@compact/1/None/None/integration',
                               'positions_m': [[26.15, 0.0, 2.05]]},
                              {'assembly_occurrence_id': 'compact/2/None/None/integration',
                               'car_allocation': [[2, 1.0]],
                               'centroid_m': [43.8, 0.0, 2.05],
                               'id': 'compact-drive/integration-reserve@compact/2/None/None/integration',
                               'positions_m': [[43.8, 0.0, 2.05]]},
                              {'assembly_occurrence_id': 'compact/3/None/None/integration',
                               'car_allocation': [[3, 1.0]],
                               'centroid_m': [61.449999999999996, 0.0, 2.05],
                               'id': 'compact-drive/integration-reserve@compact/3/None/None/integration',
                               'positions_m': [[61.449999999999996, 0.0, 2.05]]},
                              {'assembly_occurrence_id': 'compact/4/None/None/integration',
                               'car_allocation': [[4, 1.0]],
                               'centroid_m': [79.1, 0.0, 2.05],
                               'id': 'compact-drive/integration-reserve@compact/4/None/None/integration',
                               'positions_m': [[79.1, 0.0, 2.05]]},
                              {'assembly_occurrence_id': 'compact/5/None/None/integration',
                               'car_allocation': [[5, 1.0]],
                               'centroid_m': [96.75, 0.0, 2.05],
                               'id': 'compact-drive/integration-reserve@compact/5/None/None/integration',
                               'positions_m': [[96.75, 0.0, 2.05]]}]}],
 'source_bytes_sha256': 'f639405395242bd5987651a1e61a8a7fd4264cf23f2a5494825ca495381c4b23',
 'source_candidate_id': '5a3a6cd74fd33ab6d85e0a264afc899a5fff319e16e7fd94189637a6bfba44f3',
 'source_evaluation_id': 'd1339473c06dd9dc5a6187b9aed70aa025b4a0c0d2caa33ccd430a939f28f9ea',
 'track_interface': {'contact_datum': 'nominal rail head centres',
                     'inner_face_gauge_m': 1.435,
                     'nominal_contact_centres_y_m': [-0.7525, 0.7525],
                     'nominal_rail_head_width_m': 0.07,
                     'real_profile_verified': False,
                     'schema': 'osr-wheel-rail-interface/1'},
 'unlocated_reserve': {'base': 5000, 'high': 10000, 'low': 2000}}

def seal(v):
    v.pop('evaluation_id', None)
    v['evaluation_id'] = identity(v)
    return v


def fixture_body(*, unsupported_category=False):
    data = deepcopy(SOURCE_DATA)
    parts = data['parts']; patterns = [dict(deepcopy(g['common']), **r) for g in data['pattern_groups'] for r in g['rows']]
    for p in parts:
        if not unsupported_category:
            assert p['make_buy'] == 'bounded-purchase-or-process'
            p['make_buy'] = 'bounded-purchased-or-processed'
    for p in patterns:
        if not unsupported_category:
            p['make_buy'] = 'bounded-purchased-or-processed'
    physical = dict(schema='osr-test-delivery-body-physical/1', label='THREE-TYPE SYNTHETIC SOFTWARE CONTROL ONLY',
        parts=[{k:p[k] for k in ('id','source_part_id','component_definition_id','quantity_per_train','material_id','stock','mass_each_kg')} for p in parts],
        occurrence_patterns=[{k:p[k] for k in ('id','part_id','count','geometry','positions_m','rotation')} for p in patterns])
    return seal(dict(schema='osr-vehicle-installation/1',physical_definition=physical,candidate_id=identity(physical),
        parent_bundle_id=identity(dict(ancestry='Source-data unit control',source_candidate=SOURCE_DATA['source_candidate_id'])),
        source_sha256={'tests/test_railway_project_delivery.py':digest(__file__)},
        fixture_provenance=dict(source_body_candidate_id=SOURCE_DATA['source_candidate_id'],source_body_evaluation_id=SOURCE_DATA['source_evaluation_id'],
            source_bytes_sha256=SOURCE_DATA['source_bytes_sha256'],historical_evidence_reused=False,
            test_only_category_conversion=None if unsupported_category else 'bounded-purchase-or-process → bounded-purchased-or-processed'),
        compact_drive_contract=dict(mass_ownership=dict(all_new_drive_components_in_body_BOM=True,additional_external_drive_mass_kg=0.,remaining_unknown_mass_positive=True)),
        installed_mass_complete=False,layout_definition_complete=False,parts=parts,patterns=patterns,materials=data['materials'],assembly_occurrences=data['assembly_occurrences'],
        assembly_plans=dict(plans=[],accepted=False,test_scope='No controlled route inherited'),total_occurrences=sum(p['quantity_per_train'] for p in parts),
        direct_parts_process_usd={c:fsum(p['direct_cost_usd'][c] for p in patterns) for c in model.CASES},
        nominal_part_mass_kg={c:fsum(p['mass_kg'][c] for p in patterns) for c in model.CASES},
        policy=dict(track_interface=data['track_interface'],evaluation=dict(unlocated_installation_reserve_kg=data['unlocated_reserve'])),**delivery.FLAGS))


def mapped_inputs(body=None):
    b=fixture_body() if body is None else body
    source={'tests/test_railway_project_delivery.py':digest(__file__)}
    alignment_id=identity(dict(test_alignment=2234.5)); alignment_eval=identity(dict(test_alignment_evaluation=2234.5))
    route=2234.5; bays=112
    cp=dict(schema='osr-project-civil-layout/1',label='SYNTHETIC QUANTITY CONTROL, NOT A BRIDGE',alignment_candidate_id=alignment_id,bays=bays,standard_span_m=20.,
        station_centre_to_centre_route_m=route,track_centres_y_m=[-1.6,1.6],span_geometry=dict(track_interface=b['policy']['track_interface'],material_specification=None))
    accounts=[dict(owner=owner,quantity=224,unit='synthetic-account-units',cost_usd=dict(low=100.,base=200.,high=400.),basis='Synthetic account control only')
              for group in delivery.GROUPS.values() for owner in group]
    civil=seal(dict(schema=delivery.SCHEMAS[2],candidate_id=identity(cp),physical_definition=cp,vehicle_candidate_id=b['candidate_id'],body_evaluation_id=b['evaluation_id'],
        alignment_candidate_id=alignment_id,alignment_evaluation_id=alignment_eval,quantities=dict(beams=224,shared_bents=113,main_running_track_m=2*route,nominal_span_track_m=4480.),
        cost=dict(accounts=accounts),source_sha256=source,holds=['Synthetic civil input; no FEM or construction evidence'],**delivery.FLAGS))
    sp=dict(schema='osr-project-station-geometry/1',alignment_candidate_id=alignment_id,track_centres_y_m=[-3.,3.],stations=[dict(id='A'),dict(id='B'),dict(id='C')])
    station=seal(dict(schema=delivery.SCHEMAS[3],candidate_id=identity(sp),physical_definition=sp,body_candidate_id=b['candidate_id'],body_evaluation_id=b['evaluation_id'],
        alignment_candidate_id=alignment_id,alignment_evaluation_id=alignment_eval,quantities=dict(stations=3,boarding_faces=6),source_sha256=source,holds=['No station assembly'],**delivery.FLAGS))
    tp=dict(schema='osr-station-track-spread-geometry/1',alignment_candidate_id=alignment_id,station_geometry_candidate_id=station['candidate_id'],running_track_centres_y_m=[-1.6,1.6],station_track_centres_y_m=[-3.,3.])
    tracks=seal(dict(schema=delivery.SCHEMAS[4],candidate_id=identity(tp),physical_definition=tp,station_candidate_id=station['candidate_id'],station_evaluation_id=station['evaluation_id'],
        alignment_candidate_id=alignment_id,alignment_evaluation_id=alignment_eval,quantities=dict(total_track_m=4740.,total_rail_m=9480.,terminal_extension_track_m=250.,spread_additional_track_m=21.),
        source_sha256=source,holds=['No terminal protection'],**delivery.FLAGS))
    bp=dict(schema='osr-mapped-railway-project-physical/1',body_candidate_id=b['candidate_id'],alignment_candidate_id=alignment_id,civil_layout_candidate_id=civil['candidate_id'],
        station_geometry_candidate_id=station['candidate_id'],station_track_geometry_candidate_id=tracks['candidate_id'])
    bundle=seal(dict(schema=delivery.SCHEMAS[0],candidate_id=identity(bp),physical_definition=bp,body_evaluation_id=b['evaluation_id'],civil_evaluation_id=civil['evaluation_id'],
        station_evaluation_id=station['evaluation_id'],station_track_evaluation_id=tracks['evaluation_id'],alignment_evaluation_id=alignment_eval,source_sha256=source,**delivery.FLAGS))
    service=seal(dict(schema=delivery.SCHEMAS[5],candidate_id=bundle['candidate_id'],bundle_evaluation_id=bundle['evaluation_id'],route_m=route,
        total_trainsets=3,active_trainsets=2,spare_trainsets=1,headway_s=200.,native_service_complete=False,source_sha256=source,**delivery.FLAGS))
    owned=[dict(owner=name,quantity=3 if name=='rolling-stock-delivered' else 1,unit='synthetic-account-unit',basis='Test arithmetic only',
        cost_usd=dict(low=300.,base=600.,high=1200.)) for name in [*OWNER_SCOPES,'rolling-stock-delivered']]
    common=dict(candidate_id=bundle['candidate_id'],body_candidate_id=b['candidate_id'],body_bundle_id=b['parent_bundle_id'],mass_evaluation_id=b['evaluation_id'],
        service={k:service[k] for k in ('headway_s','active_trainsets','spare_trainsets','total_trainsets')},source_sha256=source,**delivery.FLAGS)
    core=seal(dict(schema='osr-station-pair-cost/1',accounts=owned,**common))
    methods=[dict(method='synthetic-cost-control',scope_totals_usd={s:dict(low=None,base=None,high=None) if s=='energy' else dict(low=10.,base=20.,high=40.) for s in SCOPES},
        installed_capital_usd=dict(low=1e6,base=2e6,high=4e6),whole_life_NPV_usd=dict(low=None,base=None,high=None),site_specific_prices_verified=False)]
    full=seal(dict(schema='osr-station-pair-lifecycle/1',input_cost_evaluation_id=core['evaluation_id'],route_km=route/1000,
        required_cost_scopes=list(SCOPES),methods=methods,extra_accounts=[],**common))
    cost=seal(dict(schema=delivery.SCHEMAS[6],candidate_id=bundle['candidate_id'],bundle_evaluation_id=bundle['evaluation_id'],body_evaluation_id=b['evaluation_id'],civil_evaluation_id=civil['evaluation_id'],
        service_evaluation_id=service['evaluation_id'],core=core,full_scope=full,route_m=route,delivered_train_unit_usd=dict(low=100.,base=200.,high=400.),
        additional_terminal_and_spread_track_m=260.,standard_bay_credit_track_m=11.,additional_legacy_drive_charge_usd=0.,zero_is_exact_in_BOM_ownership=True,source_sha256=source,
        limitations=['Synthetic mapped cost, never an actual railway estimate'],**delivery.FLAGS))
    return bundle,b,civil,station,tracks,service,cost


@pytest.fixture(scope='module')
def inputs():
    return mapped_inputs()


@pytest.fixture(scope='module')
def proposal(inputs):
    return delivery.compile_proposal(*inputs)


def test_mapped_protocol_has_typed_context_and_exact_thirteen_bindings(inputs,proposal):
    assert model.validate_proposal(proposal)
    assert review.contract.identities(proposal['identities'])==proposal['identities']
    p,b,c,s,t,v,cost=inputs;ids=proposal['identities'];context=proposal['delivery_context']
    assert len(ids)==13 and ids['study_id']==context['context_id']
    assert context['schema']=='osr-mapped-project-delivery-context/1'
    assert context['context_id']==identity({k:v for k,v in context.items() if k!='context_id'})
    assert context['inputs']=={k:r['evaluation_id'] for k,r in zip(('bundle','body','civil','station','tracks','service','cost'),inputs)}
    assert ids['installed_component_candidate_id']==b['candidate_id'] and ids['installed_mass_evaluation_id']==b['evaluation_id']
    assert ids['lifecycle_evaluation_id']==cost['full_scope']['evaluation_id']
    assert proposal['status']=='DRAFT' and all(proposal[k] is False for k in delivery.FLAGS)


def test_all_real_source_drive_quantities_routes_materials_and_unknowns_retained(inputs,proposal):
    b=inputs[1];items={p['id']:p for p in proposal['items']}
    assert len(items)==3 and items['compact-drive/vendor-motor']['quantity_project']==72
    assert items['compact-drive/inverter']['quantity_per_train']==24
    assert items['compact-drive/integration-reserve']['quantity_per_train']==6
    assert proposal['materials']==b['materials'] and len(proposal['occurrence_patterns'])==36
    assert len(proposal['assembly_routes'])==2
    assert all(p['make_buy']=='bounded-purchased-or-processed' for p in items.values())
    assert proposal['capacity']['provisional_vehicle_person_h'] is None
    assert proposal['capacity']['actual_crew_count'] is None and proposal['capacity']['calendar_duration_days'] is None
    assert proposal['capacity']['unknown_part_process_hour_ids']==list(items)
    reserve=next(p for p in proposal['external_inventory'] if p['id']=='body/unlocated-installation-reserve')
    assert reserve['mass_kg_per_train']==b['policy']['evaluation']['unlocated_installation_reserve_kg']
    assert reserve['geometry'] is None and reserve['additional_to_body'] is False
    assert not any(p['id'] in ('traction-motor','gearbox-including-couplings','inverter-cooling-mounting-collector-reserve') for p in proposal['external_inventory'])
    assert all(p['additive_procurement'] is False for p in proposal['external_inventory'])


def test_fourteen_cost_views_and_mapped_civil_are_nonadditive_and_unknown_not_free(proposal):
    view=proposal['cost_views'][0]
    assert len(view['scope_totals_usd'])==14 and view['scope_totals_usd']['energy']['base'] is None
    assert view['whole_life_NPV_usd']['base'] is None
    row=proposal['civil_requirements'][0]
    assert row['quantity_project']==224 and row['additive_mass_or_cost_ledger'] is False
    assert row['geometry'] is None and row['validated_person_h'] is None
    assert proposal['construction_route']['lifting'] is None and proposal['construction_route']['hours'] is None
    assert proposal['summary']['engineering_release_held'] is True


@pytest.mark.parametrize('fault',['body-revision','service-candidate','cost-service','legacy-drive','civil-count','track-count','part-count','physical-pattern','duplicate-material','source-epoch','approval'])
def test_mixed_or_resealed_inputs_cannot_cross_boundary(inputs,fault):
    values=deepcopy(inputs);p,b,c,s,t,v,cost=values
    if fault=='body-revision': b['installed_mass_complete']=True;seal(b)
    elif fault=='service-candidate': v['candidate_id']='f'*64;seal(v)
    elif fault=='cost-service': cost['service_evaluation_id']='f'*64;seal(cost)
    elif fault=='legacy-drive': cost['additional_legacy_drive_charge_usd']=9552.;seal(cost)
    elif fault=='civil-count': c['quantities']['beams']+=2;seal(c)
    elif fault=='track-count': t['quantities']['total_track_m']+=1;seal(t)
    elif fault=='part-count': b['parts'][0]['quantity_per_train']+=1;seal(b)
    elif fault=='physical-pattern': b['patterns'][0]['positions_m'][0][0]+=1;seal(b)
    elif fault=='duplicate-material': b['materials'].append(deepcopy(b['materials'][0]));seal(b)
    elif fault=='source-epoch':
        v['source_sha256']=dict(v['source_sha256']);v['source_sha256']['VERSION']='0'*64;seal(v)
    else: cost['operating_release']=True;seal(cost)
    with pytest.raises(ValueError): delivery.compile_proposal(*values)


def test_unsupported_historical_category_is_never_silently_remapped():
    with pytest.raises(ValueError,match='Unclassified make/buy'):
        delivery.compile_proposal(*mapped_inputs(fixture_body(unsupported_category=True)))


def test_current_drawings_and_review_contract_consume_exact_source_items(tmp_path,inputs,proposal):
    body=inputs[1];pid='compact-drive/vendor-motor'
    scope=drawings.describe(body,proposal,[pid]);item=scope['selected'][0]['part']
    assert item==next(p for p in proposal['items'] if p['id']==pid)
    # Existing controlled-document unit helper builds explicit synthetic payloads;
    # this is software compatibility, not a hardware drawing or release claim.
    from test_pilot_delivery_review import documents
    index,conversions=documents(tmp_path,proposal)
    # Source unit=item has no implicit Nos conversion in the retained protocol.
    with pytest.raises(ValueError,match='UOM conversion'):
        review.compile_review_pack(proposal,index,conversions,artifact_root=tmp_path,city='synthetic-unit-control')
    first=proposal['items'][0]
    rate=first['counted_direct_parts_process_usd_per_train']['base']/first['quantity_per_train']
    conversions[first['id']]=dict(valuation_mode='quantified-source-stock',source_part_sha256=identity(first),
        stock_inputs=[dict(id=first['id'],uom='Nos',net_quantity=1.,gross_quantity=1.,waste_fraction=0.,
            unit_rate_usd=rate-1.,source_sha256=identity(first),basis='SYNTHETIC reviewed item-to-Nos and stock/process split; not a real procurement quote')],
        direct_process_allowance_usd=1.)
    pack=review.compile_review_pack(proposal,index,conversions,artifact_root=tmp_path,city='synthetic-unit-control')
    assert review.verify_artifacts(pack,tmp_path)
    assert pack['coverage']['complete'] is False
    assert pack['components'][0]['source_part']==proposal['items'][0]
    assert pack['components'][0]['source_part_sha256']==identity(proposal['items'][0])
    assert all(pack[k] is False for k in review.contract.FLAGS)


def test_source_epoch_and_counted_mass_are_checked_after_consistent_rebinding():
    b=fixture_body();b['source_sha256']['VERSION']='0'*64;seal(b)
    with pytest.raises(ValueError,match='source changed'):
        delivery.compile_proposal(*mapped_inputs(b))
    b=fixture_body();b['nominal_part_mass_kg']['base']+=1.;seal(b)
    with pytest.raises(ValueError,match='stock mass'):
        delivery.compile_proposal(*mapped_inputs(b))


def test_core_fleet_quantity_cannot_be_resealed_into_a_second_train_purchase(inputs):
    values=deepcopy(inputs);cost=values[-1];core=cost['core'];full=cost['full_scope']
    next(a for a in core['accounts'] if a['owner']=='rolling-stock-delivered')['quantity']=4
    seal(core);full['input_cost_evaluation_id']=core['evaluation_id'];seal(full);seal(cost)
    with pytest.raises(ValueError,match='counted fleet'):
        delivery.compile_proposal(*values)


def test_stock_drawing_export_retains_partial_coverage_and_research_holds(tmp_path,inputs,proposal):
    out=tmp_path/'stock-drawings'
    result=drawings.export(inputs[1],proposal,out,['compact-drive/vendor-motor'],{})
    assert list(out.rglob('*.svg'))
    assert result['coverage']['documented_part_ids']==[]
    assert result['coverage']['whole_vehicle_finished_drawing_coverage_complete'] is False
    assert result['manufacturing_readiness']=='held'
    assert all(result[k] is False for k in review.contract.FLAGS)


def test_same_candidate_rebinding_cannot_hide_wrong_physical_pattern():
    b=fixture_body();b['patterns'][0]['positions_m']=deepcopy(b['patterns'][0]['positions_m'])
    b['patterns'][0]['positions_m'][0][0]+=1.;seal(b)
    with pytest.raises(ValueError,match='Occurrence differs'):
        delivery.compile_proposal(*mapped_inputs(b))


def test_extra_cost_cannot_duplicate_existing_owner_or_inherit_another_candidate(inputs):
    for fault in ('duplicate','candidate'):
        values=deepcopy(inputs);cost=values[-1];full=cost['full_scope']
        full['extra_accounts']=[dict(owner='wayside-propulsion' if fault=='duplicate' else 'new-support',candidate_id='f'*64 if fault=='candidate' else values[0]['candidate_id'],
            quantity=1,unit='proposed package',scope='construction',cost_usd=dict(low=100.,base=200.,high=400.))]
        seal(full);seal(cost)
        with pytest.raises(ValueError,match='duplicates|Mixed extra'):
            delivery.compile_proposal(*values)


def test_planning_policy_cannot_promote_unmeasured_hours_or_an_actual_crew(inputs):
    policy=json.loads((delivery.ROOT/model.POLICY).read_bytes())
    policy['controlled_cycle_times_available']=True
    with pytest.raises(ValueError,match='Unmeasured planning policy'):
        delivery.compile_proposal(*inputs,policy=policy)


def test_empty_lifecycle_methods_cannot_claim_fourteen_cost_views(inputs):
    values=deepcopy(inputs);cost=values[-1];full=cost['full_scope']
    assert len(full['required_cost_scopes'])==14 and full['methods']
    full['methods']=[]
    # Keep the outer records valid: absence of methods must fail independently
    # of seal checks or the presence of the fourteen scope names.
    seal(full);seal(cost)
    with pytest.raises(ValueError,match='At least one lifecycle cost method'):
        delivery.compile_proposal(*values)
