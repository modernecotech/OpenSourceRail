"""Source-specific terminal material normalization, never canonical admission.

Known CSG and drawings remain physical records. Packaging/inertia proxies never
replace known cut material. Missing drawing/joint facts create named work, not
invented material or an exemption from vehicle_composition validation.
"""
from copy import deepcopy
from hashlib import sha256
from math import isfinite,fsum,sqrt,pi
import json,zlib

SOURCE=dict(candidate_id='339689820cde417f85a426c5ac4dfee96fcdee9db6f69107776f17874caa878b',
 evaluation_id='91a013cdd8cc6757b06769f963f75d52499cc58c2de1936c7cc52685aa7d9ec0',
 raw_sha256='cdef7bfebda549f45a4e1c160c58b07f584c610782c56528c541bf8e43bcb82c')
PARENT=dict(candidate_id='5a3a6cd74fd33ab6d85e0a264afc899a5fff319e16e7fd94189637a6bfba44f3',evaluation_id='d1339473c06dd9dc5a6187b9aed70aa025b4a0c0d2caa33ccd430a939f28f9ea',raw_sha256='f639405395242bd5987651a1e61a8a7fd4264cf23f2a5494825ca495381c4b23')
SOURCE_FILES={'engineering/terminal_installation.py':'f1b83a2ee0c13e14b2bb72a321caab632f72ca14c2f6d7c728d0398c4cee43e9',
 'engineering/station_rail/common.py':'691787a2cd1d5e751c188cf729432f35883a2882cdb1f543e3e49286dc8576ec',
 'engineering/design_search/requirement_policy.py':'fa2c12bc0ff302dd4e05986d0f79e03556d9c45a683f3e8d91df8536baa4be2c'}
I=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
CASES=('low','base','high')
FLAGS=dict(canonical_admitted=False,installed_assembly_accepted=False,native_eligible=False,physical_accepted=False,manufacturing_release=False,operating_release=False,selected_reference_changed=False)

def identity(x):return sha256((json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()
def seal(x):return dict(deepcopy(x),evaluation_id=identity(x))
def scalar(x,positive=False):
 if type(x) not in (int,float) or not isfinite(x) or positive and x<=0:raise ValueError('Finite nonboolean SI scalar required')
 return float(x)
def vector(x,n=3):
 if not isinstance(x,(list,tuple)) or len(x)!=n:raise ValueError('Explicit finite vector required')
 return [scalar(v) for v in x]
def rotation(R):
 if not isinstance(R,list) or len(R)!=3:raise ValueError('Proper rigid rotation required')
 for row in R:vector(row)
 if any(abs(fsum(R[k][i]*R[k][j] for k in range(3))-(1 if i==j else 0))>1e-10 for i in range(3) for j in range(3)):raise ValueError('Nonrigid frame')
 d=R[0][0]*(R[1][1]*R[2][2]-R[1][2]*R[2][1])-R[0][1]*(R[1][0]*R[2][2]-R[1][2]*R[2][0])+R[0][2]*(R[1][0]*R[2][1]-R[1][1]*R[2][0])
 if abs(d-1)>1e-10:raise ValueError('Reflection refused')
 return R
def local(p,T,R):return [fsum(R[k][j]*(p[k]-T[k]) for k in range(3)) for j in range(3)]
def relative(Q,R):return [[fsum(R[k][i]*Q[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def finite(x):identity(x) # recursive NaN/JSON rejection; not geometric validation
def positive_cases(x):
 if not isinstance(x,dict) or set(x)!=set(CASES):raise ValueError('Three explicit mass/cost cases required')
 for v in x.values():scalar(v,True)
 if [x[k] for k in CASES]!=sorted(x.values()):raise ValueError('Ordered low/base/high cases required')
def polygon(points):
 for p in points:vector(p,2)
 if len({tuple(p) for p in points})!=len(points):raise ValueError('Repeated polygon vertex')
 edges=list(zip(points,points[1:]+points[:1]))
 orient=lambda a,b,c:(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 for i,(a,b) in enumerate(edges):
  for j,(c,d) in enumerate(edges):
   if j<=i or j==i+1 or i==0 and j==len(edges)-1:continue
   overlap=all(max(min(a[k],b[k]),min(c[k],d[k]))<=min(max(a[k],b[k]),max(c[k],d[k])) for k in (0,1))
   if overlap and orient(a,b,c)*orient(a,b,d)<=0 and orient(c,d,a)*orient(c,d,b)<=0:raise ValueError('Selfintersecting polygon')

def geometry(g,T,R,*,absolute,depth=0):
 """Preserve finite source grammar; no kernel/volume/qualification claim."""
 if depth>16 or not isinstance(g,dict):raise ValueError('Bounded explicit CSG tree required')
 finite(g);kind=g.get('kind');out=deepcopy(g)
 if kind=='difference':
  out['outer']=geometry(g['outer'],T,R,absolute=absolute,depth=depth+1);out['void']=geometry(g['void'],T,R,absolute=absolute,depth=depth+1);return out
 if kind=='union-material':
  if not isinstance(g.get('pieces'),list) or not 1<=len(g['pieces'])<=128:raise ValueError('Finite material-piece roster required')
  out['pieces']=[geometry(p,T,R,absolute=absolute,depth=depth+1) for p in g['pieces']]
  if 'analytical_volume_m3' in g:scalar(g['analytical_volume_m3'],True)
  return out
 if kind not in ('box','rhs','annulus','profile-prism','poly-prism'):raise ValueError('Unsupported finite material primitive:'+str(kind))
 if kind in ('box','rhs','poly-prism'):
  size=vector(g['size_m'])
  if min(size)<=0:raise ValueError('Positive stock dimensions required')
  if kind=='rhs' and not 0<2*scalar(g['wall_m'],True)<min(size[1:]):raise ValueError('Invalid RHS wall')
 if kind=='annulus':
  L=scalar(g.get('length_m',g.get('size_m',[None])[0]),True)
  ro=scalar(g.get('outer_radius_m',g.get('outer_diameter_m',0)/2),True);ri=scalar(g.get('inner_radius_m',g.get('inner_diameter_m',0)/2))
  if not 0<=ri<ro:raise ValueError('Invalid annular material')
  if 'size_m' in g and any(abs(a-b)>1e-10 for a,b in zip(vector(g['size_m']),[L,2*ro,2*ro])):raise ValueError('Annular size/radius disagreement')
 if kind in ('profile-prism','poly-prism'):
  pts=g['points_yz_m'] if kind=='profile-prism' else g['finished_profile_xz_m']
  if not isinstance(pts,list) or not 3<=len(pts)<=256:raise ValueError('Finite extrusion polygon required')
  polygon(pts)
  if abs(fsum(a[0]*b[1]-a[1]*b[0] for a,b in zip(pts,pts[1:]+pts[:1])))<1e-18:raise ValueError('Degenerate profile')
  if kind=='profile-prism':scalar(g['length_m'],True)
 if absolute:
  at=vector(g['at_m']);Q=rotation(g['rotation']);out['at_m']=local(at,T,R);out['rotation']=relative(Q,R)
 else:
  out['at_m']=vector(g.get('at_m',[0.,0.,0.]));out['rotation']=rotation(g.get('rotation',I))
 for h in g.get('holes',[]):
  if set(h)!={'axis','centre_m','radius_m','length_m'} or type(h['axis']) is not int or h['axis'] not in (0,1,2):raise ValueError('Explicit normalized cylinder cut required')
  vector(h['centre_m']);scalar(h['radius_m'],True);scalar(h['length_m'],True)
 return out

def source_cuts(cuts,T,R):
 out=[]
 for h in cuts:
  if h.get('kind')!='cylinder-cut':raise ValueError('Unsupported source cut')
  p=vector(h['at_m']);axis=vector(h['axis'])
  if abs(fsum(x*x for x in axis)-1)>1e-10:raise ValueError('Unit source cut axis required')
  D=scalar(h['diameter_m'],True);L=scalar(h['length_m'],True)
  out.append(dict(kind='finite-cylinder-void',centre_m=local(p,T,R),axis=[fsum(R[k][j]*axis[k] for k in range(3)) for j in range(3)],radius_m=D/2,length_m=L,source_cut=deepcopy(h)))
 return out

def drawing_record(e,weld):
 d=e.get('physical_drawing');holds=[]
 if d is None:return None,holds
 finite(d);kind=d.get('kind');out=dict(source=deepcopy(d),coordinate_domain='As declared source drawing; not a replacement envelope',material_graph=None)
 if kind=='two-explicit-extruded-triangular-weld-profiles':
  ps=d['profile_vertices_UV_from_station_m'];lo,hi=vector(d['W_from_station_m'],2)
  if hi<=lo or len(ps)!=2 or d.get('triangle_orientation_defined') is not True or weld is None:raise ValueError('Explicit two triangles/station required')
  T=vector(weld['at_uvw_m']);graphs=[]
  for tri in ps:
   if len(tri)!=3:raise ValueError('Three triangle vertices required')
   for p in tri:vector(p,2)
   if abs((tri[1][0]-tri[0][0])*(tri[2][1]-tri[0][1])-(tri[1][1]-tri[0][1])*(tri[2][0]-tri[0][0]))<1e-18:raise ValueError('Degenerate deposited triangle')
   graphs.append(dict(kind='six-vertex-triangle-prism',vertices_m=[local([T[0]+u,T[1]+v,T[2]+w],e['at_m'],e['rotation']) for w in (lo,hi) for u,v in tri]))
  size=vector(e['geometry']['size_m'])
  if any(abs(p[i])>size[i]/2+1e-10 for g in graphs for p in g['vertices_m'] for i in range(3)):raise ValueError('Declared seam exceeds source packaging bounds')
  out['material_graph']=dict(kind='union-material',pieces=graphs)
  holds.append('weld-runout-WPS-contact-and-load-qualification')
 elif kind=='triangular-weld-seams':
  scalar(d['leg_m'],True)
  for line in d['local_segments_m']:
   if len(line)!=2 or vector(line[0])==vector(line[1]):raise ValueError('Finite nonzero seam required')
  holds.append('weld-cross-section-orientation-not-declared; preserve deposited-volume and path, not filled box')
 elif kind in ('revolved-frustum','nested-revolved-frusta'):
  scalar(d['height_m'],True)
  if kind=='revolved-frustum':
   if not 0<scalar(d['small_radius_m'],True)<=scalar(d['large_radius_m'],True):raise ValueError('Invalid frustum radii')
  else:
   a=vector(d['inner_radius_ends_m'],2);b=vector(d['outer_radius_ends_m'],2)
   if any(not 0<x<y for x,y in zip(a,b)):raise ValueError('Invalid nested frusta')
  holds.append('exact-signed-frustum-axis-plane-and-drive-profile-binding-required')
 elif kind in ('box-minus-6revolvedcounterbores','box-minus-2revolvedcounterbores'):
  scalar(d['height_m'],True);a,b=vector(d['outer_cone_radius_ends_m'],2)
  if not 0<a<b:raise ValueError('Invalid cone interval')
  holds.append('exact-clipped-counterbore-segments-and-parent-frame-binding-required')
 elif kind=='tie-with-two-bores-and-four-open-roundended-extractor-slots':
  spec=d['slot_spec'];width=scalar(spec['width_m'],True);r=scalar(spec['end_radius_m'],True);depth=scalar(spec['depth_m'],True)
  if abs(width-2*r)>1e-10 or len(d['slot_U_centres_local_m'])!=4 or len(d['removed_centroids_local_m'])!=4:raise ValueError('Exact four roundended slots required')
  for p in d['removed_centroids_local_m']:vector(p)
  if depth>=vector(d['original_box_size_m'])[1]:raise ValueError('Slot consumes full tie')
  holds.append('roundended-slot-signed-depth-and-source-bore-union-adapter-required')
 else:holds.append('unsupported-finished-drawing:'+str(kind))
 return out,holds

def joint_record(j):
 finite(j);kind=j.get('kind');status='held-exact-counterpart-member-binding-required'
 if not isinstance(j.get('id'),str) or not j['id']:raise ValueError('Named source joint required')
 if kind in ('ordered-through-stack','blind-threaded-boss','blind-threaded-endplate'):
  if type(j['axis']) is not int or j['axis'] not in (0,1,2) or type(j['direction']) is not int or j['direction'] not in (-1,1):raise ValueError('Explicit joint axis/direction required')
  vector(j['origin_m']);s=j['stack'];at=0.
  for layer in s['layers']:
   a=scalar(layer['start_m']);b=scalar(layer['end_m'])
   if abs(a-at)>1e-10 or b<=a:raise ValueError('Ordered adjacent real layers required')
   at=b
  if kind=='ordered-through-stack':
   if abs(at-s['grip_m'])>1e-10 or abs(s['nut_m'][0]-at)>1e-10 or s['nut_m'][1]<=at or s['bolt_tip_m']-s['nut_m'][1]<s['minimum_projection_m']-1e-10:raise ValueError('Invalid finite through stack')
  elif s['pilot_depth_m']<=s['thread_engagement_m'] or s['remaining_pilot_bound_m']<=0 or s['liner_ID_m']>=s['liner_OD_m']:raise ValueError('Invalid finite blind receiver/liner')
 elif kind=='blind tapped removablepanel joint':
  for k in ('overall_length_m','shaft_underhead_m','thread_engagement_m','remaining_pilot_bound_m','tool_insertion_m','tool_radius_m'):scalar(j[k],True)
 elif kind not in ('internal RHS-to-composite-root endweld','continuous underframe hanger','rigid nut-retaining cage/closed tip hood','finite exposedface connector weld','new closed postbottom'):
  status='held-unsupported-source-joint-kind:'+str(kind)
 return dict(id='terminal-source-joint/'+j['id'],schema='osr-terminal-unresolved-source-contract/1',source_joint_id=j['id'],source_contract=deepcopy(j),status=status,
  validation_scope='Finite scalar/ordered-layer sanity only; complete real member/void/contact/tool/load contract still required',resolved=False,physical_accepted=False)

def physical_projection(d):
 return dict(schema='osr-terminal-canonical-draft-physical/1',units='m',bindings=deepcopy(d['bindings']),
  entities=[{k:deepcopy(e[k]) for k in ('id','part_id','material_id','at_m','rotation','frame','scope','functions','finished_spec')} for e in d['entities']],
  required_counterpart_obligations=deepcopy(d['required_counterpart_obligations']))

def normalize(raw,*,pin,request_id):
 """Future singleton actual adapter; source phase permits invented fixtures only."""
 if pin!=SOURCE or type(raw) is not bytes or len(raw)>4*1024**2 or sha256(raw).hexdigest()!=pin['raw_sha256']:raise ValueError('Exact run03 raw/source pin required')
 if not isinstance(request_id,str) or len(request_id)!=64 or any(c not in '0123456789abcdef' for c in request_id):raise ValueError('Exact request identity required')
 if raw[:2]==b'\x1f\x8b':
  z=zlib.decompressobj(31);payload=z.decompress(raw,64*1024**2)
  if not z.eof or z.unused_data or z.unconsumed_tail:raise ValueError('Single bounded gzip member required')
 else:payload=raw
 src=json.loads(payload)
 if src['evaluation_id']!=identity({k:v for k,v in src.items() if k!='evaluation_id'}) or src['evaluation_id']!=pin['evaluation_id'] or identity(src['physical_definition'])!=src['candidate_id'] or src['candidate_id']!=pin['candidate_id'] or src['parent']!=PARENT or src['source_sha256']!=SOURCE_FILES:raise ValueError('Mixed/stale terminal/P1/source identity')
 c=src['component_proposal']
 if any(src.get(k) is not False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release','native_eligible','selected_reference_changed','movement_authority')) or c.get('composition_admitted') is not False:raise ValueError('Source research holds cannot be promoted')
 if c['evaluation_id']!=identity({k:v for k,v in c.items() if k!='evaluation_id'}) or c['definition_id']!=src['physical_definition']['local_definition_id']:raise ValueError('Source component identity differs')
 if c['required_bindings']!=src['component_bindings'] or len(src['component_bindings'])!=2:raise ValueError('Two exact bindings required')
 for b in src['component_bindings']:vector(b['at_m']);rotation(b['rotation'])
 es={e['id']:e for e in c['entities']};groups=c['stock_groups']
 if len(es)!=len(c['entities']) or len({g['id'] for g in groups})!=len(groups):raise ValueError('Duplicate source entity/stock owner')
 owned=set()
 for g in groups:
  if not g['entity_ids'] or any(x in owned or x not in es for x in g['entity_ids']):raise ValueError('Unowned/duplicated source stock')
  owned.update(g['entity_ids'])
  for k in ('net_mass_kg','gross_mass_kg','direct_cost_usd'):positive_cases(g[k])
  for case in CASES:
   if scalar(g['scrap_mass_kg'][case])<0 or abs(g['gross_mass_kg'][case]-g['net_mass_kg'][case]-g['scrap_mass_kg'][case])>1e-8 or abs(fsum(es[x]['mass_kg'][case] for x in g['entity_ids'])-g['net_mass_kg'][case])>1e-8:raise ValueError('Stock mass conservation failed')
  if abs(fsum(es[x]['cost_share'] for x in g['entity_ids'])-1)>1e-10:raise ValueError('Source price allocation differs')
 if owned!=set(es):raise ValueError('Missing source stock owner')
 welds={w['id']:w for w in src['new_welds']};out=[];work=[]
 for e in c['entities']:
  vector(e['at_m']);rotation(e['rotation']);positive_cases(e['mass_kg']);vector(e['centroid_local_m']);vector(e['uncertainty_m'])
  if min(e['uncertainty_m'])<0:raise ValueError('Negative source position uncertainty')
  if e['frame']!='terminal-local-UVW':raise ValueError('Explicit terminal-local entity frame required')
  x=deepcopy(e);old=e.get('exact_CSG_entity');holds=[];material=None
  if old is not None:
   if old.get('geometry') is None:holds.append('source-finished-geometry-and-supplier-material-not-declared')
   else:
    try:material=dict(base=geometry(old['geometry'],e['at_m'],e['rotation'],absolute=True),voids=source_cuts(old.get('holes',[]),e['at_m'],e['rotation']),additional_voids=[geometry(g,e['at_m'],e['rotation'],absolute=True) for g in old.get('additional_voids',[])])
    except ValueError as err:holds.append(str(err))
  else:
   if e['geometry'].get('kind')=='envelope' and e.get('physical_drawing') is not None:material=None
   else:
    try:material=dict(base=geometry(e['geometry'],e['at_m'],e['rotation'],absolute=False),voids=[])
    except ValueError as err:holds.append(str(err))
  drawing,dh=drawing_record(e,welds.get(e['id']));holds.extend(dh)
  if drawing is not None:
   if drawing['material_graph'] is not None:material=drawing['material_graph']
   else:material=None
  if material is not None and old is not None and (old.get('holes') or old.get('additional_voids') or old['geometry']['kind'] in ('union-material','difference')):
   holds.append('finite-CSG-union-containment-and-mass-moment-equivalence-evaluator-required')
  x['finished_spec']=dict(schema='osr-terminal-source-finished-material/1',coordinate_frame='entity-local',source_exact_CSG_entity=deepcopy(old),source_physical_drawing=deepcopy(e.get('physical_drawing')),
   normalized_material_graph=material,drawing_record=drawing,source_packaging_proxy=deepcopy(e['geometry']),packaging_is_finished_material=False,domain='finite nominal declared source graph; no kernel/material/qualification result',holds=holds)
  out.append(x)
  for h in holds:work.append(dict(entity_id=e['id'],required_work=h))
 contracts=[joint_record(j) for j in c['actual_joint_contracts']]
 if len({j['id'] for j in contracts})!=len(contracts):raise ValueError('Repeated counterpart obligation')
 for j in contracts:work.append(dict(source_joint_id=j['source_joint_id'],required_work=j['status']))
 draft=dict(schema='osr-terminal-canonical-component-draft/1',target_schema='osr-composition-component/1',units='m',bindings=deepcopy(src['component_bindings']),entities=out,stock_groups=deepcopy(groups),required_counterpart_obligations=contracts,
  required_counterpart_ids=[j['id'] for j in contracts],joint_dispositions={j['source_joint_id']:dict(status='unresolved-normalization',reason=j['status']) for j in contracts},
  source_account_coverage=deepcopy(src['local_account_coverage']),source_person_hours=deepcopy(src['person_hours']),unsupported_work=work,admission='Not accepted by current composer schema; explicit reviewed finite-CSG/contract support and unresolved facts required',**FLAGS)
 draft['definition_id']=identity(physical_projection(draft));draft=seal(draft)
 value=dict(schema='osr-terminal-canonical-normalization-packet/1',source_pin=deepcopy(pin),source_parent=deepcopy(src['parent']),source_request_id=request_id,canonical_draft=draft,
  source_physical_definition=deepcopy(src['physical_definition']),source_machining_train_once=deepcopy(src['source_machining']),old_leaf_replacements_train_once=deepcopy(src['old_leaf_replacements']),
  floor_wear_patch_unapplied=deepcopy(src['floor_wear_patch']),applied_body_operations=[],source_bindings=deepcopy(src['component_bindings']),
  lifecycle_workshop=dict(quantity_scope='Train-once separately; never per installed end',shared_fixture=deepcopy(src['consumables']['shared_fixture']),shared_extractor=deepcopy(src['consumables']['shared_extractor'])),
  source_holds=deepcopy(src['holds']),normalization_status='held-required-material-and-counterpart-work' if work else 'finite-draft-generated; composer-adapter-review-required',
  mass_price_inertia_and_stock_unchanged=True,canonical_parent_or_body_generated=False,**FLAGS)
 return seal(value)
