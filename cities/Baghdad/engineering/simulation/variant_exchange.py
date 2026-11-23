"""Candidate-specific IFC4 coordination geometry and draft purchasing/workcell tables."""
from collections import Counter
import csv
from hashlib import sha256
import io
import json
import tomllib
from pathlib import Path
from uuid import UUID, uuid5

HERE=Path(__file__).resolve()
ALPHABET="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$"


def guid(namespace,label):
    value=uuid5(namespace,label).int
    return "'"+''.join(ALPHABET[(value >> (6*i)) & 63] for i in reversed(range(22)))+"'"


def quoted(value):
    return "'"+str(value).replace("'","''")+"'"


def array(values):
    return "("+",".join(values)+")"


def xyz(*values):
    return array(f"{float(x):.6f}" for x in values)


class Layout:
    def __init__(self,physical,evaluation):
        self.namespace=UUID(physical[:32])
        self.counts=Counter()
        self.lines=[]
        self.proxies=[]
        self.point0=self.add("IFCCARTESIANPOINT",xyz(0,0,0))
        self.axis0=self.add("IFCAXIS2PLACEMENT3D",self.point0,"$","$")
        self.root=self.add("IFCLOCALPLACEMENT","$",self.axis0)
        self.context=self.add("IFCGEOMETRICREPRESENTATIONCONTEXT","$","'Model'","3","0.000001",self.axis0,"$")
        unit=self.add("IFCSIUNIT","*",".LENGTHUNIT.","$",".METRE.")
        units=self.add("IFCUNITASSIGNMENT",array([unit]))
        project=self.add("IFCPROJECT",guid(self.namespace,"project"),"$","'Airport planning exchange'",
                         quoted("physical="+physical+" evaluation="+evaluation),"$","$","$",array([self.context]),units)
        self.site=self.add("IFCSITE",guid(self.namespace,"site"),"$","'Flattened route chainage frame'","$","$",
                           self.root,"$","$",".ELEMENT.","$","$","$","$","$")
        self.add("IFCRELAGGREGATES",guid(self.namespace,"project-site"),"$","$","$",project,array([self.site]))
        self.up=self.add("IFCDIRECTION",xyz(0,0,1))

    def add(self,kind,*args):
        ref=f"#{len(self.lines)+1}"
        self.lines.append(ref+"="+kind+"("+",".join(args)+");")
        return ref

    def axis(self,x,y,z):
        point=self.add("IFCCARTESIANPOINT",xyz(x,y,z))
        return self.add("IFCAXIS2PLACEMENT3D",point,"$","$")

    def shape(self,boxes=()):
        solids=[]
        for x,y,z,dx,dy,dz in boxes:
            profile=self.add("IFCRECTANGLEPROFILEDEF",".AREA.","$","$",f"{dx:.6f}",f"{dy:.6f}")
            solids.append(self.add("IFCEXTRUDEDAREASOLID",profile,self.axis(x,y,z),self.up,f"{dz:.6f}"))
        if solids:
            body=self.add("IFCSHAPEREPRESENTATION",self.context,"'Body'","'SweptSolid'",array(solids))
        else:
            points=self.add("IFCGEOMETRICSET",array([self.point0]))
            body=self.add("IFCSHAPEREPRESENTATION",self.context,"'Reference'","'GeometricSet'",array([points]))
        return self.add("IFCPRODUCTDEFINITIONSHAPE","$","$",array([body]))

    def place(self,family,key,point,shape):
        tag=family+"-"+key
        placement=self.add("IFCLOCALPLACEMENT",self.root,self.axis(*point))
        self.proxies.append(self.add("IFCBUILDINGELEMENTPROXY",guid(self.namespace,tag),"$",quoted(tag),
                            "$",quoted(family),placement,shape,quoted(tag),".USERDEFINED."))
        self.counts[family]+=1

    def serialize(self):
        # Split STEP relation lines to remain practical for ordinary IFC readers.
        for i in range(0,len(self.proxies),200):
            self.add("IFCRELCONTAINEDINSPATIALSTRUCTURE",guid(self.namespace,"contained"+str(i)),"$","$","$",
                     array(self.proxies[i:i+200]),self.site)
        header=("ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');\n"
                "FILE_NAME('airport-layout.ifc','2026-11-23T00:00:00',('OpenSourceRail'),('OpenSourceRail'),"
                "'OpenSourceRail','OpenSourceRail','');\nFILE_SCHEMA(('IFC4'));\nENDSEC;\nDATA;\n")
        return (header+"\n".join(self.lines)+"\nENDSEC;\nEND-ISO-10303-21;\n").encode()


def artifacts(result):
    physical=result["identity"]["physical_id"]
    evaluation=result["identity"]["evaluation_id"]
    cfg=result["inputs"]
    stages=result["stages"]
    factory=stages["production"]
    q=factory["quantities"]
    if factory["scenario_id"]!=physical or stages["vehicle"]["selected_span"]["stock_length_m"]!=cfg["span_m"]:
        raise ValueError("Scenario exchange contains mixed physical quantities")
    L=cfg["span_m"]
    stops=stages["corridor"]["stops"]
    sites=stages["motion"]["physical"]["feeder"]["sites"]
    route_m=1000*stops[-1]["chainage_km"]
    n=round(route_m/L)
    if (n*L!=route_m or q["beams"]!=2*n or q["piers"]!=2*(n+1) or q["bearings"]!=8*n or
            q["grid_sites"]!=len(sites) or q["cars"]!=q["sets"]*cfg["cars"] or q["bogies"]!=2*q["cars"]):
        raise ValueError("Unmatched infrastructure, feeder or running gear quantity")
    layout=Layout(physical,evaluation)
    city=HERE.parents[2]
    config_paths=[city/"system.toml", city/"engineering/mechanical/civil/concept.toml",
                  city/"engineering/mechanical/quotation.toml"]
    system,concept,quote=[tomllib.loads(p.read_text()) for p in config_paths]
    vehicle,station_dims=system["vehicle_geometry"],system["station_geometry"]
    half_spacing=station_dims["straight_track_centre_spacing_m"]/2
    B=concept["box"]
    b,h,end,t,slab=(B[k] for k in ("width_m","depth_m","solid_end_m","web_m","slab_m"))
    middle=L-2*end
    x_end=(L-end)/2
    rail_to_beam_top=.25
    soffit=-rail_to_beam_top-h
    bearing_gap=.08
    dim=concept["pier"]
    foot,fh,col,ch,capw,capl,caph=(dim[k] for k in ("footing_width_m","footing_depth_m",
        "column_width_m","column_height_m","cap_width_m","cap_length_m","cap_depth_m"))
    body_length=vehicle["car_body_length_m"]
    reference_cars=system["vehicle"]["cars_per_train"]
    inter_car_gap=(vehicle["train_length_m"]-reference_cars*body_length)/(reference_cars-1)
    inset,d=quote["civil_seat"]["longitudinal_inset_m"],quote["civil_seat"]["lateral_m"]
    # Six non-overlapping prisms. Position refers to the centre of the stock at soffit.
    beam=layout.shape([(-x_end,0,0,end,b,h),(x_end,0,0,end,b,h),
                       (0,0,0,middle,b,slab),(0,0,h-slab,middle,b,slab),
                       (0,-(b-t)/2,slab,middle,t,h-2*slab),(0,(b-t)/2,slab,middle,t,h-2*slab)])
    pier=layout.shape([(0,0,0,foot,foot,fh),(0,0,fh,col,col,ch),(0,0,fh+ch,capl,capw,caph)])
    # Envelope solids and point datums do not supply installed mass/volume.
    body=layout.shape([(0,0,.75,body_length,vehicle["body_width_m"],2.45)])
    depth=concept["platform"]["panel_thickness_m"]
    station=layout.shape([(0,0,-depth,station_dims["platform_clear_length_m"],station_dims["island_width_m"],depth)])
    datum=layout.shape()
    for side,y in enumerate((-half_spacing,half_spacing),1):
        for i in range(n):
            tag=f"{side}-{i+1:04}"
            layout.place("TrackSpan",tag,((i+.5)*L,y,soffit),beam)
            for j,(x,offset_y) in enumerate(((inset,-d),(inset,d),(L-inset,-d),(L-inset,d)),1):
                layout.place("BearingDatum",tag+f"-{j}",(i*L+x,y+offset_y,soffit),datum)
        for i in range(n+1):
            layout.place("PierFooting",f"{side}-{i+1:04}",(i*L,y,soffit-bearing_gap-caph-ch-fh),pier)
    for i,stop in enumerate(stops):
        layout.place("PlatformEnvelope",stop["id"],(1000*stop["chainage_km"],0,1.),station)
    for i,x in enumerate(sites,1):
        layout.place("FeederChainage",str(i),(x,9.,0.),datum)
    # One representative consist on track 1. Depot/fleet positions require a surveyed track plan.
    for i in range(cfg["cars"]):
        centre=1000*stops[1]["chainage_km"]+(i-(cfg["cars"]-1)/2)*(body_length+inter_car_gap)
        layout.place("CarEnvelope",str(i+1),(centre,-half_spacing,0),body)
        for j,x in enumerate(vehicle["bogie_centres_m"],1):
            layout.place("BogiePivot",f"{i+1}-{j}",(centre+x,-half_spacing,0),datum)
    files={"candidate/airport-layout.ifc":layout.serialize()}
    def table(name,headers,rows):
        buf=io.StringIO()
        w=csv.writer(buf)
        w.writerow(["physical_id","evaluation_id",*headers])
        w.writerows([[physical,evaluation,*row] for row in rows])
        files["candidate/"+name]=buf.getvalue().encode()
    table("planning-quantities.csv",["item","quantity","unit","evidence"],
          [(key,value,"km" if key=="track_km" else "each","awaiting return" if value is None else "planning quantity")
           for key,value in q.items()])
    def unit(row):
        if row["lot_id"]=="fleet":
            return f"{cfg['cars']}-car sets"
        if row["quantity_driver"]=="sets":
            return "sets"
        return row["source_unit"]
    table("procurement-lots.csv",["lot","scope","year","quantity","planning_unit","source_unit",
          "low_usd","base_usd","high_usd","quote_status"],
          [(r["lot_id"],r["group"],r["year"],r["quantity"],unit(r),r["source_unit"],
            *(r["usd"][band] for band in ("low","base","high")),"estimate") for r in factory["priced_lots"]])
    table("production-workcells.csv",["scenario","resource","available_units","peak_occupied_units","occupied_resource_days"],
          [(s,k,c,t["peak_resource_occupation"].get(k),t["occupied_resource_workdays"].get(k))
           for s,t in factory["scenarios"].items() for k,c in t["capacity"].items()])
    # One possible division of supply. Finished trainsets own all car/bogie content;
    # civil beam, bearing and pier are disjoint articles. No price is transferred
    # from the aggregate installed civil/vehicle scope to these unit requests.
    requests=[]
    for lot,driver,label in (("fleet","sets",f"{cfg['cars']}-car {cfg['material']} trainset"),
            ("civil-box","beams",f"{L} m single-track box stock"),("civil-bearing","bearings","Bridge bearing"),
            ("civil-pier","piers","Single-track pier/foundation position")):
        code=f"AIR-{physical[:12].upper()}-{lot.upper()}"
        requests.append(dict(doctype="Material Request Item",item_code=code,item_name=label,
                             qty=q[driver],uom="Nos",description=f"Engineering enquiry {physical}; scope {lot}"))
    erp=dict(physical_id=physical,evaluation_id=evaluation,eligible_to_submit=False,
             required_owner_fields=["existing ERPNext Company","required-by schedule_date",
                                    "verified Item master codes and UOM","approved warehouse or project"],
             quantity_boundary="Finished trainsets include constituent cars and bogies. Supply scopes must be reconciled before order.",
             document=dict(doctype="Material Request",docstatus=0,material_request_type="Purchase",
                           title="Airport scenario "+physical[:12],items=requests))
    files["candidate/erpnext-material-request-draft.json"]=json.dumps(erp,sort_keys=True,indent=2).encode()+b"\n"
    descr=dict(physical_id=physical,evaluation_id=evaluation,producer_sha256=sha256(HERE.read_bytes()).hexdigest(),
        definition_source_sha256={str(p.relative_to(city)):sha256(p.read_bytes()).hexdigest() for p in config_paths},
        stage_result_ids=result["provenance"]["stage_result_ids"],counts=dict(layout.counts),fleet_quantity=q,
        candidate_material=cfg["material"],supply_layout=cfg["topology"],span_stock_m=L,
        expected_concrete_m3_per_span=stages["vehicle"]["selected_span"]["span_actions"]["gross_concrete_m3"],
        datum="Flattened 12 km chainage X; straight double-track axes at Y +/-5.425 m; rail-head Z zero. No georeferencing.",
        scope=["Repeated trial box and one-track pier geometry for all placements.",
               "Four bearing reference points per stock span. Thickness and hardware unspecified. Nominal trial 80 mm bearing space; beam top 250 mm below rail.",
               "Platform is a solid clearance envelope, not architectural stock takeoff. Six feeder-site or thirty radial-site centrelines are schematic; parcel side and Y=9 m are hypothetical.",
               "Car envelopes and bogie pivots show one consist only. Finished body, material sections, equipment geometry, restraints and surveyed depot positions remain open.",
               "ERP tables are neutral, draft planning data. No ERP price approval, purchase order, manufacturing release or import transaction."],
        bytes_sha256={k:sha256(v).hexdigest() for k,v in files.items()})
    files["candidate/exchange.json"]=json.dumps(descr,sort_keys=True,indent=2).encode()+b"\n"
    return files
