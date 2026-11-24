"""Six-stop Airport planning corridor, demand allocation and GTFS handoff."""
import argparse
import csv
from hashlib import sha256
import io
import json
import math
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo

CITY = Path(__file__).resolve().parents[2]
PACKET = CITY/"engineering/prototype/airport-prototype.zip"
REGISTER = CITY/"station-register.json"
# Relative hourly shares for hours beginning 06 through 23 local. Study weights.
PROFILES = {
    "local_journeys": (1,2,3,2,1,1,1,1,1,1,2,3,2,1.5,1,.8,.6,.4),
    "air_journeys": (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1),
    "airport_workers_and_visitors": (3,2,1,1,.6,.6,1,1,1,2,3,2,1,.8,.6,.6,.6,.6),
}


def sources():
    with ZipFile(PACKET) as z:
        manifest=json.loads(z.read("manifest.json"))
        def read(name):
            data=z.read(name)
            if sha256(data).hexdigest()!=manifest["sha256"][name]:
                raise ValueError(f"Released member changed: {name}")
            return json.loads(data)
        opening,service=read("opening.json"),read("service.json")
    register=json.loads(REGISTER.read_bytes())
    if (manifest["candidate_id"] != opening["candidate_id"] or
            opening["bundle"]["stops"] != [s["id"] for s in service["group"]["outward_stops"]] or
            opening["bundle"]["route_km"] != service["group"]["one_way_km"]):
        raise ValueError("Opening candidate differs from packet")
    for path,fingerprint in register["map_source_sha256"].items():
        if sha256((CITY.parents[1]/path).read_bytes()).hexdigest()!=fingerprint:
            raise ValueError("Station register references a different map")
    hashes={name:manifest["sha256"][name] for name in ("opening.json","service.json")}
    hashes.update({"station-register.json":sha256(REGISTER.read_bytes()).hexdigest(),
                   "corridor.py":sha256(Path(__file__).read_bytes()).hexdigest(),**register["map_source_sha256"]})
    return opening,service,register,hashes


def distance_km(a,b):
    lon1,lat1=map(math.radians,a)
    lon2,lat2=map(math.radians,b)
    h=math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 12742*math.asin(math.sqrt(h))


def evaluate(inputs=None):
    opt={"headway_min":15,"grade_pct":0.,"demand":"central","cars":6,**(inputs or {})}
    headway,grade,demand,cars=(opt[k] for k in ("headway_min","grade_pct","demand","cars"))
    if headway not in (15,20,30) or cars not in (3,6) or demand not in ("downside","central","upside") or not -2<=grade<=2:
        raise ValueError("Unsupported Airport headway, formation, demand or grade")
    opening,service,register,hashes=sources()
    group=service["group"]
    lookup={r["id"]:r for r in register["networks"]["first"]["mapped_points"]}
    stops=[]
    for s in group["outward_stops"]:
        ref=lookup.get(s["register_id"])
        if s["register_id"] and (not ref or ref["label"]!=s["label"] or ref["route_hint"]!="Airport"):
            raise ValueError("Service stop does not match station register")
        km=group["one_way_km"]*s["fraction"]
        stops.append(dict(id=s["id"],label=s["label"],register_id=s["register_id"],chainage_km=round(km,9),
                          longitude_latitude=ref["longitude_latitude"] if ref else None,
                          location_scope=s["location_scope"],approved_station_site=False,
                          elevation_relative_to_origin_m=10*grade*km))
    totals=opening["iraq_operations"]["cases"][demand]
    od=[[[0.]*6 for _ in stops] for _ in range(24)]
    for kind,profile in PROFILES.items():
        for hour,weight in enumerate(profile,6):
            count=totals[kind]*weight/(365*sum(profile))
            # Direction 0 is airport towards city. Weekday peaks describe directional bias only.
            share=(.35 if hour<10 else .65 if 16<=hour<20 else .5) if kind!="air_journeys" else .5
            for reverse,portion in ((False,share),(True,1-share)):
                if kind=="local_journeys":
                    local=list(range(5,0,-1) if reverse else range(1,6))
                    for i,origin in enumerate(local[:-1]):
                        destinations=local[i+1:]
                        for target in destinations:
                            od[hour][origin][target]+=count*portion/(4*len(destinations))
                else:
                    for city in range(1,6):
                        origin,target=(city,0) if reverse else (0,city)
                        od[hour][origin][target]+=count*portion/5
    peak=queue=passenger_km=daily=0.
    for matrix in od:
        for a,row in enumerate(matrix):
            for b,flow in enumerate(row):
                daily+=flow
                passenger_km+=flow*abs(stops[a]["chainage_km"]-stops[b]["chainage_km"])
            for portion in (row[:a],row[a+1:]):
                queue=max(queue,sum(portion)*headway/60)
        for leg in range(5):
            for flow in (sum(matrix[a][b] for a in range(leg+1) for b in range(leg+1,6)),
                         sum(matrix[b][a] for a in range(leg+1) for b in range(leg+1,6))):
                peak=max(peak,flow*headway/60)
    if not math.isclose(daily*365,totals["all_journeys"],abs_tol=1e-6):
        raise ArithmeticError("Daily OD conservation failed")
    mapped=[s for s in stops if s["longitude_latitude"]]
    lower=sum(distance_km(a["longitude_latitude"],b["longitude_latitude"]) for a,b in zip(mapped,mapped[1:]))
    dwell=service["patterns"][0][1]["departure_s"]-service["patterns"][0][1]["arrival_s"]
    route=dict(parent=opening["candidate_id"],stops=[(s["id"],s["chainage_km"],s["register_id"]) for s in stops],grade_pct=grade,cars=cars)
    return dict(candidate_id=sha256(json.dumps(route,sort_keys=True).encode()).hexdigest(),parent_candidate_id=opening["candidate_id"],
                source_sha256=hashes,service_evaluation_id=service["evaluation_id"],opening_evaluation_id=opening["evaluation_id"],
                demand=demand,cars=cars,headway_min=headway,grade_pct=grade,hourly_od=od,
                annual_paid_journeys=totals["paid_journeys"],annual_all_journeys=totals["all_journeys"],
                annual_journeys_by_source={k:totals[k] for k in PROFILES},annual_od_balance_journeys=daily*365-totals["all_journeys"],
                mean_trip_km=passenger_km/daily,busiest_departure_load=peak,platform_queue=queue,
                peak_leg_over_places=max(0,peak-700*cars/6),headway_wait_min=headway/2,
                stops=stops,chainages_km=[s["chainage_km"] for s in stops],dwell_s=dwell,
                walking_transfer_cases=[dict(trial_path_m=m,walking_speed_m_s=speed,
                    extra_crossing_or_lift_wait_s=wait,transfer_minutes=(m/speed+wait)/60)
                    for m,speed,wait in ((100,1.2,20),(300,1.,60),(600,.75,120))],
                mapped_centroid_order_straight_segments_km=lower,
                geometry_scope="Uniform planning chainages. Centroids are enquiry areas. Um Al Tubol and all entrances lack confirmed sites. Constant signed grade from arbitrary zero is a sensitivity; no surveyed vertical curve, obstacle clearance or pedestrian connection.",
                demand_scope="Mean daily journeys distributed by study hour and direction. Peak queue is new boarders per train on one platform, before capacity carryover and perturbations; walking times are scenarios, not mapped routes.")


def gtfs(record,path,*,service_date="20261123"):
    """Make a valid mapped-stop subset feed; retain full stop times for survey reconciliation."""
    from cities.Baghdad.engineering.simulation import motion_power
    case=motion_power.normalize(dict(headway_min=record["headway_min"],cars=record["cars"],
                                    chainages_km=record["chainages_km"],dwell_s=record["dwell_s"]))
    group,trips,patterns,*_=motion_power.service(case)
    written=write_booked_gtfs(record["stops"],trips,patterns,path,service_date=service_date)
    return dict(motion_timetable_source_sha256=sha256(Path(motion_power.__file__).read_bytes()).hexdigest(),
                source_sha256=record["source_sha256"],candidate_id=record["candidate_id"],gtfs_sha256=sha256(Path(path).read_bytes()).hexdigest(),
                mapped_stop_ids=written["mapped_stop_ids"],held_stop_ids=written["held_stop_ids"],
                trips=len(trips),full_six_stop_times=written["full_six_stop_times"],terminal_B_phase_s=group["terminal_B_phase_s"],
                service_date=service_date,scope="Planning feed of five mapped centroids. Full six-stop times supplied separately. No OTP routing or accessible transfers verified. Requires local pedestrian OSM extract and field survey.")


def write_booked_gtfs(stops,trips,patterns,path,*,service_date):
    """Write the common booked timetable tables for historic and audited Airport offers."""
    from datetime import datetime
    from re import fullmatch
    datetime.strptime(service_date,"%Y%m%d")
    if (len(patterns)!=2 or len(stops)!=6
            or any(not fullmatch(r"[A-Za-z0-9_-]+",s["id"]) for s in stops)
            or any(not fullmatch(r"[A-Za-z0-9_-]+",unit) or side not in (0,1)
                   for unit,side,_,_ in trips)):
        raise ValueError("GTFS requires six safe stop IDs and two directional booked trip patterns")
    mapped={s["id"] for s in stops if s["longitude_latitude"]}
    def clock(seconds):
        return f"{seconds//3600:02d}:{seconds//60%60:02d}:{seconds%60:02d}"
    tables={
        "agency.txt":(["agency_name","agency_url","agency_timezone"],[["OpenSourceRail planning","https://github.com/modernecotech/OpenSourceRail","Asia/Baghdad"]]),
        "stops.txt":(["stop_id","stop_name","stop_lat","stop_lon"],[[s["id"],s["label"],*s["longitude_latitude"][::-1]] for s in stops if s["id"] in mapped]),
        "routes.txt":(["route_id","route_short_name","route_long_name","route_type"],[["AIR","AIR","Baghdad Airport study",1]]),
        "calendar_dates.txt":(["service_id","date","exception_type"],[["STUDY",service_date,1]]),
        "trips.txt":(["route_id","service_id","trip_id","direction_id","block_id"],[]),
        "stop_times.txt":(["trip_id","arrival_time","departure_time","stop_id","stop_sequence"],[]),
    }
    full=[]
    for index,(unit,side,start,_) in enumerate(trips):
        trip=f"AIR-{index+1:03}"
        tables["trips.txt"][1].append(["AIR","STUDY",trip,side,unit])
        for seq,s in enumerate(patterns[side],1):
            row=[trip,clock(start+s["arrival_s"]),clock(start+s["departure_s"]),s["id"],seq]
            full.append(row)
            if s["id"] in mapped:
                tables["stop_times.txt"][1].append(row)
    with ZipFile(path,"w") as z:
        for name,(fields,rows) in tables.items():
            buf=io.StringIO()
            writer=csv.writer(buf)
            writer.writerow(fields)
            writer.writerows(rows)
            z.writestr(ZipInfo(name,(1980,1,1,0,0,0)),buf.getvalue(),compress_type=ZIP_DEFLATED)
    return dict(mapped_stop_ids=sorted(mapped),held_stop_ids=[s["id"] for s in stops if s["id"] not in mapped],
                full_six_stop_times=full)


if __name__=="__main__":
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--gtfs",type=Path,required=True)
    cli.add_argument("--headway",type=int,default=15)
    cli.add_argument("--date",default="20261123")
    args=cli.parse_args()
    result=gtfs(evaluate(dict(headway_min=args.headway)),args.gtfs,service_date=args.date)
    args.gtfs.with_suffix(".json").write_text(json.dumps(result,indent=2)+"\n")
