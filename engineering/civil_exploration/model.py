"""Native 2D elastic system model with finite supports and moving loads.

Symmetric parallel tracks share piers through rigid cap offsets. Individual
span rotations are released; horizontal and vertical bearing stiffnesses are
finite. Foundation springs are scenario inputs, not geotechnical capacity.
"""
from __future__ import annotations

import csv
import gzip
import math
from pathlib import Path
import shutil

import numpy as np

from osr_mech.civil.exploration import geometry

G = 9.81


def takeoff(candidate, study):
    geo = geometry(candidate['definition'])
    span = candidate['definition']['deck']['span_m']
    spans = round(study['route_length_m']/span)
    supports = spans+1
    density = candidate['material']['density_kg_m3']
    allowance, foundation = candidate['mass_allowances'], candidate['foundation']
    deck_volume = math.fsum((s['end_m']-s['start_m'])*s['area_m2'] for s in geo['deck'])
    pier_volume = math.fsum((s['end_m']-s['start_m'])*s['area_m2'] for s in geo['pier'])
    pile_volume = foundation['pile_count']*math.pi*foundation['pile_diameter_m']**2/4*foundation['pile_length_m']
    foundation_cap = foundation['cap_length_m']*foundation['cap_width_m']*foundation['cap_depth_m']
    fabricated = deck_volume*(density+allowance['reinforcement_kg_m3'])+span*allowance['prestress_kg_m']+allowance['embedded_kg_per_beam']
    concrete = deck_volume*spans*2+(pier_volume+geo['cap_concrete_m3']+pile_volume+foundation_cap)*supports
    reinforcement = concrete*allowance['reinforcement_kg_m3']
    prestress = span*spans*2*allowance['prestress_kg_m']
    embedded = spans*2*allowance['embedded_kg_per_beam']
    track_mass = study['route_length_m']*2*allowance['superimposed_dead_kg_m_per_track']
    return dict(route_length_m=study['route_length_m'], tracks=2, spans=spans, supports=supports,
                concrete_m3=concrete, deck_concrete_m3=deck_volume*spans*2,
                pier_concrete_m3=pier_volume*supports, cap_concrete_m3=geo['cap_concrete_m3']*supports,
                foundation_concrete_m3=(pile_volume+foundation_cap)*supports,
                reinforcement_allowance_kg=reinforcement, prestress_allowance_kg=prestress,
                embedded_allowance_kg=embedded, superimposed_dead_allowance_kg=track_mass,
                installed_study_mass_kg=concrete*density+reinforcement+prestress+embedded+track_mass,
                bare_beam_mass_kg=geo['deck'][1]['area_m2']*span*density,
                fabricated_beam_mass_kg=fabricated, transported_beam_mass_kg=fabricated,
                suspended_mass_kg=fabricated+allowance['rigging_kg_per_lift'],
                bearing_count=spans*8, pile_count=supports*foundation['pile_count'],
                pile_length_m=supports*foundation['pile_count']*foundation['pile_length_m'],
                beam_lifts=spans*2, installed_cost_usd=None, whole_life_cost_usd=None,
                cost_gaps=['supplier material rates', 'bearing and connection quotes', 'ground installation',
                           'transport routes', 'actual crane chart and utilisation', 'temporary works',
                           'production beds, curing and QA', 'maintenance, replacement and possessions'],
                quantities_are_study_allowances=True)


def mesh_positions(span, count, extra=()):
    return sorted(set([round(span*i/count, 12) for i in range(count+1)]+[float(x) for x in extra]))


def axle_nodal_loads(coordinates, front_m, offsets, loads_n):
    """Conserve axle force and moment; linear spatial interpolation is refined."""
    forces = np.zeros(len(coordinates))
    for offset, force in zip(offsets, loads_n):
        x = front_m-offset
        if x < coordinates[0] or x > coordinates[-1]:
            continue
        j = int(np.searchsorted(coordinates, x, side='right'))-1
        j = min(j, len(coordinates)-2)
        fraction = (x-coordinates[j])/(coordinates[j+1]-coordinates[j])
        forces[j] += force*(1-fraction)
        forces[j+1] += force*fraction
    return forces


def distributed_axle_loads(coordinates, front_m, offsets, loads_n, distribution_length):
    """Exact integration of a triangular rail-distribution footprint.

    Integrating linear traction times linear nodal weights with Simpson's rule
    is exact on each split interval. The physical footprint is an explicit
    study assumption, independent of FE mesh size, and needs track validation.
    Partial footprints at the model boundary transfer only their in-domain
    load; the omitted portion belongs to unmodelled adjacent track.
    """
    values = np.zeros(len(coordinates))
    half = distribution_length/2
    for offset, force in zip(offsets, loads_n):
        centre = front_m-offset
        first = max(0, int(np.searchsorted(coordinates, centre-half))-1)
        last = min(len(coordinates)-2, int(np.searchsorted(coordinates, centre+half)))
        for i in range(first, last+1):
            a, b = coordinates[i], coordinates[i+1]
            left, right = max(a, centre-half), min(b, centre+half)
            if right <= left:
                continue
            splits = [left]+([centre] if left < centre < right else [])+[right]
            for lo, hi in zip(splits, splits[1:]):
                for x, coefficient in ((lo, 1.), ((lo+hi)/2, 4.), (hi, 1.)):
                    traction = max(0., 1-abs(x-centre)/half)/half
                    weight = force*coefficient*(hi-lo)/6*traction
                    values[i] += weight*(b-x)/(b-a)
                    values[i+1] += weight*(x-a)/(b-a)
    return values


class System:
    def __init__(self, candidate, study, ground, mesh):
        import openseespy.opensees as ops
        self.ops, self.candidate, self.study = ops, candidate, study
        self.geo = geometry(candidate['definition'])
        self.quantities = takeoff(candidate, study)
        self.next_node = self.next_element = self.next_material = 0
        self.deck_nodes, self.deck_elements, self.deck_spans = [], [], []
        self.fixed_nodes, self.base_nodes, self.top_nodes = [], [], []
        self.seat_nodes = []
        self.gravity_nodes = {}
        self.gravity_elements = []
        self.x = {}
        self.node_coordinates, self.element_definitions, self.rigid_links = {}, [], []
        ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
        ops.geomTransf('Linear', 1)
        material = candidate['material']
        self.E = material['youngs_modulus_pa']*material['stiffness_factor']
        self.G = self.E/(2*(1+material['poisson_ratio']))
        density = material['density_kg_m3']+candidate['mass_allowances']['reinforcement_kg_m3']
        span = candidate['definition']['deck']['span_m']
        height = candidate['definition']['pier']['height_m']
        deck_y = height+self.geo['cap_height_m']+self.geo['deck'][1]['centroid_z_m']
        for support in range(self.quantities['supports']):
            x = support*span
            fixed, base = self.node(x, 0), self.node(x, 0)
            ops.fix(fixed, 1, 1, 1)
            self.fixed_nodes.append(fixed); self.base_nodes.append(base)
            self.spring(fixed, base, (ground['lateral_stiffness_n_m'], ground['axial_stiffness_n_m'], ground['rotational_stiffness_nm_rad']))
            previous = base
            for s in self.geo['pier']:
                node = self.node(x, s['end_m'])
                mass = density*s['area_m2']
                self.beam(previous, node, s, mass)
                weight = mass*(s['end_m']-s['start_m'])*G/2
                self.gravity_nodes[previous] = self.gravity_nodes.get(previous, 0)+weight
                self.gravity_nodes[node] = self.gravity_nodes.get(node, 0)+weight
                previous = node
            self.top_nodes.append(previous)
            seat = self.node(x, deck_y)
            self.seat_nodes.append(seat)
            ops.rigidLink('beam', previous, seat)
            self.rigid_links.append(dict(from_node=previous, to_node=seat, type='rigid-cap-offset'))
            cap_mass = self.geo['cap_concrete_m3']*density
            ops.mass(previous, cap_mass, cap_mass, 0.)
            self.gravity_nodes[previous] = self.gravity_nodes.get(previous, 0)+cap_mass*G
            f = candidate['foundation']
            foundation_cap_mass = f['cap_length_m']*f['cap_width_m']*f['cap_depth_m']*density
            pile_mass = f['pile_count']*math.pi*f['pile_diameter_m']**2/4*f['pile_length_m']*density
            ops.mass(base, foundation_cap_mass, foundation_cap_mass, 0.)
            self.gravity_nodes[base] = self.gravity_nodes.get(base, 0)+(foundation_cap_mass+pile_mass)*G
            self.x[seat] = x
        seats = self.seat_nodes
        allowance = candidate['mass_allowances']
        for bay in range(self.quantities['spans']):
            positions = mesh_positions(span, mesh, (self.geo['deck'][0]['end_m'], self.geo['deck'][-1]['start_m']))
            nodes = [self.node(bay*span+x, deck_y) for x in positions]
            self.spring(seats[bay], nodes[0], (study['bearing']['horizontal_stiffness_n_m']*4, study['bearing']['vertical_stiffness_n_m']*4))
            self.spring(seats[bay+1], nodes[-1], (study['bearing']['horizontal_stiffness_n_m']*4, study['bearing']['vertical_stiffness_n_m']*4))
            self.deck_nodes += nodes
            self.deck_spans.append(nodes)
            for i, (a, b) in enumerate(zip(positions, positions[1:])):
                s = next(s for s in self.geo['deck'] if s['start_m'] <= (a+b)/2 <= s['end_m'])
                per_track = density*s['area_m2']+allowance['prestress_kg_m']+allowance['superimposed_dead_kg_m_per_track']
                if s is not self.geo['deck'][1]:
                    per_track += allowance['embedded_kg_per_beam']/(2*self.geo['deck'][0]['end_m'])
                mass = 2*per_track
                tag = self.beam(nodes[i], nodes[i+1], s, mass, factor=2)
                self.deck_elements.append((tag, s))
                self.gravity_elements.append((tag, mass*G))
        self.gravity()

    def node(self, x, y):
        self.next_node += 1
        self.ops.node(self.next_node, x, y)
        self.x[self.next_node] = x
        self.node_coordinates[str(self.next_node)] = [x, y]
        return self.next_node

    def spring(self, first, second, stiffnesses):
        materials = []
        for k in stiffnesses:
            self.next_material += 1
            self.ops.uniaxialMaterial('Elastic', self.next_material, k)
            materials.append(self.next_material)
        self.next_element += 1
        self.ops.element('zeroLength', self.next_element, first, second, '-mat', *materials,
                         '-dir', *range(1, len(materials)+1), '-doRayleigh', 1)
        self.element_definitions.append(dict(id=self.next_element, nodes=[first, second],
                                              type='foundation-spring' if len(stiffnesses) == 3 else 'bearing-spring',
                                              stiffness=list(stiffnesses), directions=list(range(1, len(materials)+1))))

    def beam(self, first, second, section, mass, factor=1):
        self.next_element += 1
        self.ops.element('ElasticTimoshenkoBeam', self.next_element, first, second,
                         self.E, self.G, section['area_m2']*factor, section['inertia_y_m4']*factor,
                         section['shear_area_m2']*factor, 1, '-mass', mass, '-cMass')
        self.element_definitions.append(dict(id=self.next_element, nodes=[first, second],
                                              type='deck-beam' if factor == 2 else 'pier-beam',
                                              area_m2=section['area_m2']*factor, inertia_m4=section['inertia_y_m4']*factor,
                                              shear_area_m2=section['shear_area_m2']*factor, mass_kg_m=mass,
                                              youngs_modulus_pa=self.E, shear_modulus_pa=self.G))
        return self.next_element

    def assembly(self):
        return dict(schema='osr-civil-planar-assembly/1', coordinates_m=self.node_coordinates,
                    elements=self.element_definitions, rigid_links=self.rigid_links,
                    fixed_nodes=self.fixed_nodes, deck_nodes=self.deck_nodes,
                    foundation_nodes=self.base_nodes, deck_spans=self.deck_spans,
                    active_stage='permanent-assembly', symmetry='two synchronous tracks',
                    units=dict(translation_stiffness='N/m', rotational_stiffness='N*m/rad'),
                    limitations=['rigid transverse cap', 'linear uncracked materials', 'uncalibrated diagonal ground springs'])

    def configure(self, transient=False):
        ops = self.ops
        ops.wipeAnalysis(); ops.constraints('Transformation'); ops.numberer('RCM')
        ops.system('UmfPack'); ops.test('NormDispIncr', 1e-10, 10); ops.algorithm('Linear')
        if transient:
            ops.integrator('Newmark', .5, .25); ops.analysis('Transient')
        else:
            ops.integrator('LoadControl', 1.); ops.analysis('Static')

    def gravity(self):
        ops = self.ops
        ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1)
        for tag, w in self.gravity_elements:
            ops.eleLoad('-ele', tag, '-type', '-beamUniform', -w)
        for node, weight in self.gravity_nodes.items():
            ops.load(node, 0., -weight, 0.)
        self.configure()
        if ops.analyze(1) != 0:
            raise RuntimeError('native gravity analysis did not converge')
        ops.loadConst('-time', 0.)
        self.dead = {n: ops.nodeDisp(n, 2) for n in self.deck_nodes}
        self.check_balance(self.quantities['installed_study_mass_kg']*G)

    def train_forces(self, front):
        # At duplicate span-end positions assign the load once to the following
        # span. Both deck ends retain their own rotational release and bearings.
        unique = {}
        for node in self.deck_nodes:
            unique[self.x[node]] = node
        coordinates = sorted(unique)
        train = self.study['train']
        values = distributed_axle_loads(coordinates, front, train['axle_offsets_m'],
                                        np.asarray(train['axle_loads_kn'])*1000*train['loaded_tracks'],
                                        train['load_distribution_length_m'])
        return {unique[x]: float(v) for x, v in zip(coordinates, values) if v}

    def check_balance(self, expected):
        self.ops.reactions()
        actual = math.fsum(self.ops.nodeReaction(n, 2) for n in self.fixed_nodes)
        if not math.isclose(actual, expected, rel_tol=1e-7, abs_tol=.1):
            raise ValueError(f'global vertical equilibrium failed: {actual} != {expected}')

    def responses(self):
        ops = self.ops
        moments, shears, stresses = [], [], []
        for tag, section in self.deck_elements:
            forces = ops.eleResponse(tag, 'localForce')
            if len(forces) != 6 or not all(math.isfinite(v) for v in forces):
                raise ValueError('invalid native local-force response')
            m = max(abs(forces[2]), abs(forces[5]))
            distance = max(section['top_m']-section['centroid_z_m'], section['centroid_z_m']-section['bottom_m'])
            moments.append(m); shears.append(max(abs(forces[1]), abs(forces[4])))
            stresses.append(m*distance/(2*section['inertia_y_m4'])+max(abs(forces[0]), abs(forces[3]))/(2*section['area_m2']))
        relative = []
        for nodes in self.deck_spans:
            first, last = nodes[0], nodes[-1]
            for n in nodes:
                fraction = (self.x[n]-self.x[first])/(self.x[last]-self.x[first])
                chord = ops.nodeDisp(first, 2)*(1-fraction)+ops.nodeDisp(last, 2)*fraction
                relative.append(abs(ops.nodeDisp(n, 2)-chord))
        return dict(deck_displacement_m=max(abs(ops.nodeDisp(n, 2)) for n in self.deck_nodes),
                    relative_deck_deflection_m=max(relative),
                    incremental_train_displacement_m=max(abs(ops.nodeDisp(n, 2)-self.dead[n]) for n in self.deck_nodes),
                    foundation_settlement_m=max(abs(ops.nodeDisp(n, 2)) for n in self.base_nodes),
                    pier_top_horizontal_m=max(abs(ops.nodeDisp(n, 1)) for n in self.top_nodes),
                    bending_moment_nm=max(moments), shear_n=max(shears),
                    gross_elastic_fibre_stress_pa=max(stresses))

    def static_envelope(self):
        ops = self.ops
        dead = self.responses()
        maximum = dict(dead); governing = {k: 'dead-load' for k in dead}
        length = self.study['route_length_m']+self.study['train']['axle_offsets_m'][-1]
        snapshots = []
        for i, front in enumerate(np.linspace(0, length, self.study['analysis']['static_positions'])):
            forces = self.train_forces(float(front))
            tag = 100+i
            ops.timeSeries('Constant', tag); ops.pattern('Plain', tag, tag)
            for node, force in forces.items():
                ops.load(node, 0., -force, 0.)
            self.configure()
            if ops.analyze(1) != 0:
                raise RuntimeError('moving static analysis did not converge')
            self.check_balance(self.quantities['installed_study_mass_kg']*G+sum(forces.values()))
            values = self.responses()
            snapshots.append(dict(front_m=float(front), **values))
            for key, value in values.items():
                if value > maximum[key]:
                    maximum[key], governing[key] = value, f'train-front-{front:.6g}m'
            ops.remove('loadPattern', tag); ops.remove('timeSeries', tag)
        # Restore the gravity-only state before eigen/transient execution.
        self.configure()
        if ops.analyze(1) != 0:
            raise RuntimeError('gravity restoration failed')
        return dict(dead=dead, envelope=maximum, governing=governing, positions=snapshots)

    def braking(self):
        ops = self.ops
        forces = self.train_forces(self.study['route_length_m']/2+self.study['train']['axle_offsets_m'][-1]/2)
        ops.timeSeries('Constant', 500); ops.pattern('Plain', 500, 500)
        for n, force in forces.items():
            ops.load(n, force*self.study['analysis']['braking_fraction'], -force, 0.)
        self.configure()
        if ops.analyze(1) != 0:
            raise RuntimeError('braking analysis did not converge')
        self.check_balance(self.quantities['installed_study_mass_kg']*G+sum(forces.values()))
        result = self.responses()
        ops.remove('loadPattern', 500); ops.remove('timeSeries', 500)
        self.configure()
        if ops.analyze(1) != 0:
            raise RuntimeError('braking gravity restoration failed')
        return result

    def modes(self):
        eigenvalues = self.ops.eigen('-genBandArpack', 3)
        if any(v <= 0 or not math.isfinite(v) for v in eigenvalues):
            raise ValueError('nonpositive or nonfinite eigenvalue')
        return dict(frequencies_hz=[math.sqrt(v)/(2*math.pi) for v in eigenvalues],
                    shapes=[{str(n): self.ops.nodeEigenvector(n, i+1) for n in self.deck_nodes} for i in range(3)])

    def transient(self, speed, dt, output: Path):
        ops = self.ops
        modes = self.modes()
        w1, w3 = [2*math.pi*modes['frequencies_hz'][i] for i in (0, 2)]
        damping = self.study['analysis']['damping_ratio']
        ops.rayleigh(2*damping*w1*w3/(w1+w3), 0., 0., 2*damping/(w1+w3))
        footprint = self.study['train']['load_distribution_length_m']
        start_front = -footprint/2
        count = math.ceil((self.study['route_length_m']+self.study['train']['axle_offsets_m'][-1]+footprint)/speed/dt)+1
        loads = {}
        for i in range(count+1):
            for node, force in self.train_forces(start_front+i*dt*speed).items():
                loads.setdefault(node, np.zeros(count+1))[i] = -force
        for i, (node, values) in enumerate(sorted(loads.items()), 1000):
            ops.timeSeries('Path', i, '-dt', dt, '-values', *values.tolist())
            ops.pattern('Plain', i, i); ops.load(node, 0., 1., 0.)
        self.configure(transient=True)
        ops.setTime(0.)
        # Collect raw fields in the native engine. Calling Python response
        # methods for every node/element at every step dominates larger runs.
        native = {key: output.with_name(output.stem+'-'+key+'.out') for key in ('displacement', 'acceleration', 'forces', 'foundation')}
        for key, response in (('displacement', 'disp'), ('acceleration', 'accel')):
            ops.recorder('Node', '-file', str(native[key]), '-precision', 17, '-time',
                         '-node', *self.deck_nodes, '-dof', 2, response)
        ops.recorder('Node', '-file', str(native['foundation']), '-precision', 17, '-time',
                     '-node', *self.base_nodes, '-dof', 2, 'disp')
        ops.recorder('Element', '-file', str(native['forces']), '-precision', 17, '-time',
                     '-ele', *[tag for tag, _ in self.deck_elements], 'localForce')
        for step in range(count):
            if ops.analyze(1, dt) != 0:
                raise RuntimeError(f'native transient did not converge at step {step}')
        ops.remove('recorders')
        arrays = {key: np.loadtxt(path, ndmin=2) for key, path in native.items()}
        times = arrays['displacement'][:, 0]
        if any(len(a) != count or not np.isfinite(a).all() or not np.allclose(a[:, 0], times, rtol=0, atol=1e-12) for a in arrays.values()):
            raise ValueError('native history coverage/time/finite-value mismatch')
        if arrays['displacement'].shape[1] != len(self.deck_nodes)+1 or arrays['acceleration'].shape[1] != len(self.deck_nodes)+1:
            raise ValueError('native nodal recorder allocation mismatch')
        if arrays['foundation'].shape[1] != len(self.base_nodes)+1 or arrays['forces'].shape[1] != len(self.deck_elements)*6+1:
            raise ValueError('native foundation/element recorder allocation mismatch')
        force = arrays['forces'][:, 1:].reshape(count, len(self.deck_elements), 6)
        moments = np.max(np.abs(force[:, :, [2, 5]]), axis=2)
        fibre = np.asarray([max(s['top_m']-s['centroid_z_m'], s['centroid_z_m']-s['bottom_m'])/(2*s['inertia_y_m4']) for _, s in self.deck_elements])
        axial = np.asarray([1/(2*s['area_m2']) for _, s in self.deck_elements])
        series = dict(deck_displacement_m=np.max(np.abs(arrays['displacement'][:, 1:]), axis=1),
                      deck_acceleration_m_s2=np.max(np.abs(arrays['acceleration'][:, 1:]), axis=1),
                      incremental_train_displacement_m=np.max(np.abs(arrays['displacement'][:, 1:]-np.asarray([self.dead[n] for n in self.deck_nodes])), axis=1),
                      foundation_settlement_m=np.max(np.abs(arrays['foundation'][:, 1:]), axis=1),
                      bending_moment_nm=np.max(moments, axis=1),
                      shear_n=np.max(np.abs(force[:, :, [1, 4]]), axis=(1, 2)),
                      gross_elastic_fibre_stress_pa=np.max(moments*fibre+np.max(np.abs(force[:, :, [0, 3]]), axis=2)*axial, axis=1))
        history = [dict(time_s=float(t), front_m=start_front+float(t)*speed, **{key: float(values[i]) for key, values in series.items()}) for i, t in enumerate(times)]
        maximum = {key: float(np.max(values)) for key, values in series.items()}
        governing = {key: float(times[np.argmax(values)]) for key, values in series.items()}
        with output.open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(history[0]), lineterminator='\n')
            writer.writeheader(); writer.writerows(history)
        for path in native.values():
            with path.open('rb') as source, Path(str(path)+'.gz').open('wb') as target:
                with gzip.GzipFile(filename='', mode='wb', fileobj=target, mtime=0, compresslevel=3) as compressed:
                    shutil.copyfileobj(source, compressed)
            path.unlink()
        return dict(speed_m_s=speed, time_step_s=dt, damping_ratio=damping,
                    damping_target_frequencies_hz=[w1/(2*math.pi), w3/(2*math.pi)],
                    envelope=maximum, governing_time_s=governing, history_file=output.name, modes=modes,
                    rail_load_distribution_length_m=footprint,
                    native_recorders=dict(files={key: path.name+'.gz' for key, path in native.items()},
                                          deck_node_ids=self.deck_nodes, foundation_node_ids=self.base_nodes,
                                          element_ids=[tag for tag, _ in self.deck_elements],
                                          element_components=['axial_i', 'shear_i', 'moment_i', 'axial_j', 'shear_j', 'moment_j'],
                                          units=dict(time='s', displacement='m', acceleration='m/s2', axial='N', shear='N', moment='N*m')),
                    assembly=self.assembly())


def lifting(candidate, mesh):
    """Native overhanging fabricated beam at 20/80% handling supports."""
    import openseespy.opensees as ops
    geo = geometry(candidate['definition'])
    span = candidate['definition']['deck']['span_m']
    material, allowance = candidate['material'], candidate['mass_allowances']
    E = material['youngs_modulus_pa']*material['stiffness_factor']
    positions = mesh_positions(span, mesh, (.2*span, .8*span, geo['deck'][0]['end_m'], geo['deck'][-1]['start_m']))
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3); ops.geomTransf('Linear', 1)
    for i, x in enumerate(positions, 1):
        ops.node(i, x, 0.)
    first, second = positions.index(.2*span)+1, positions.index(.8*span)+1
    ops.fix(first, 1, 1, 0); ops.fix(second, 0, 1, 0)
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1)
    total = 0.; sections = []
    for tag, (a, b) in enumerate(zip(positions, positions[1:]), 1):
        s = next(s for s in geo['deck'] if s['start_m'] <= (a+b)/2 <= s['end_m'])
        mass = s['area_m2']*(material['density_kg_m3']+allowance['reinforcement_kg_m3'])+allowance['prestress_kg_m']
        if s is not geo['deck'][1]:
            mass += allowance['embedded_kg_per_beam']/(2*geo['deck'][0]['end_m'])
        ops.element('ElasticTimoshenkoBeam', tag, tag, tag+1, E, E/(2*(1+material['poisson_ratio'])), s['area_m2'], s['inertia_y_m4'], s['shear_area_m2'], 1)
        ops.eleLoad('-ele', tag, '-type', '-beamUniform', -mass*G)
        total += mass*(b-a)*G; sections.append(s)
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('BandGeneral'); ops.algorithm('Linear')
    ops.integrator('LoadControl', 1.); ops.analysis('Static')
    if ops.analyze(1) != 0:
        raise RuntimeError('handling model did not converge')
    ops.reactions()
    reactions = [ops.nodeReaction(n, 2) for n in (first, second)]
    if not math.isclose(sum(reactions), total, rel_tol=1e-8):
        raise ValueError('handling reaction balance failed')
    moments = [max(abs(ops.eleResponse(i, 'localForce')[j]) for j in (2, 5)) for i in range(1, len(positions))]
    return dict(support_locations_m=[.2*span, .8*span], support_reactions_n=reactions,
                displacement_m=max(abs(ops.nodeDisp(n, 2)) for n in range(1, len(positions)+1)),
                bending_moment_nm=max(moments), fabricated_weight_n=total,
                rigging_weight_included_in_beam_bending=False, lifting_arrangement_approved=False)


def evaluate(job, output: Path):
    candidate, study, ground = job['candidate'], job['study'], job['ground']
    static, dynamic, handling = [], [], []
    for mesh in study['analysis']['meshes']:
        model = System(candidate, study, ground, mesh)
        static.append(dict(mesh=mesh, **model.static_envelope()))
        handling.append(dict(mesh=mesh, **lifting(candidate, mesh)))
    braking = System(candidate, study, ground, study['analysis']['meshes'][-1]).braking()
    for speed in study['analysis']['speeds_m_s']:
        for mesh, dt in ((study['analysis']['meshes'][-2], study['analysis']['time_step_s']),
                         (study['analysis']['meshes'][-1], study['analysis']['time_step_s']),
                         (study['analysis']['meshes'][-1], study['analysis']['time_step_s']/2)):
            model = System(candidate, study, ground, mesh)
            filename = f'history-v{speed:g}-mesh{mesh}-dt{dt:g}.csv'
            dynamic.append(dict(mesh=mesh, **model.transient(speed, dt, output/filename)))
    convergence = []
    def compare(label, first, second, keys):
        for key in keys:
            a, b = first[key], second[key]
            error = abs(a-b)/max(abs(b), 1e-12)
            convergence.append(dict(check=label, metric=key, relative_change=error,
                                    passed=error <= study['analysis']['convergence_relative_limit']))
    compare('static mesh', static[-2]['envelope'], static[-1]['envelope'], ('deck_displacement_m', 'bending_moment_nm'))
    compare('handling mesh', handling[-2], handling[-1], ('displacement_m', 'bending_moment_nm'))
    for i in range(0, len(dynamic), 3):
        compare(f'dynamic mesh v{dynamic[i]["speed_m_s"]:g}', dynamic[i]['envelope'], dynamic[i+1]['envelope'], ('incremental_train_displacement_m', 'deck_acceleration_m_s2'))
        compare(f'dynamic time v{dynamic[i]["speed_m_s"]:g}', dynamic[i+1]['envelope'], dynamic[i+2]['envelope'], ('incremental_train_displacement_m', 'deck_acceleration_m_s2'))
    # Acceleration maxima are particularly sensitive to point-load spatial and
    # time discretisation; a failed check remains a failed numerical screen.
    fine = dynamic[2::3]
    peaks = {k: max(item['envelope'][k] for item in fine) for k in fine[0]['envelope']}
    quantities = takeoff(candidate, study)
    limits = []
    for key, limit in study['research_limits'].items():
        value = quantities[key] if key == 'suspended_mass_kg' else peaks[key]
        limits.append(dict(metric=key, value=value, limit=limit, status='unresolved' if limit is None else ('passed' if value <= limit else 'failed'), approved=False))
    return dict(schema='osr-civil-evaluation/1', candidate_id=candidate['id'], ground_scenario=ground['name'],
                quantities=quantities, static=static, braking=braking, handling=handling, dynamics=dynamic,
                convergence=convergence, peak_responses=peaks, research_limits=limits,
                numerical_screen_passed=all(c['passed'] for c in convergence),
                engineering_feasibility='unresolved', evidence_maturity='numerically-screened-research',
                physical_release=False, operating_release=False,
                evidence_gaps=['site-calibrated pile-group resistance and stiffness', 'supplier axle distributions and measured damping',
                               'reinforcement, prestress losses, cracking, fatigue and connection resistance',
                               '3D torsion, asymmetric trains, track irregularity and vehicle interaction',
                               'validated rail-distribution footprint and adjacent-track boundary response',
                               'soil nonlinearity, pile-group interaction, ground water, scour and seismic response',
                               'pier P-delta, cyclic ductility, bearing slip and uplift',
                               'local deck/shell stresses, diaphragm eccentricity and interface details',
                               'actual crane chart, dynamic lift allowance and lateral stability',
                               'embedded pile inertia, measured materials and independent physical validation',
                               'accepted railway limits and supplier installed/whole-life prices'])
