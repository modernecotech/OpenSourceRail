"""Rust ask/evaluate/tell search using existing physical grammar productions.

Rust generates new programs and Pareto fronts; NumPy screens large proposal
batches. Only a bounded subset receives exact nominal-stock geometry and cost,
then a smaller subset receives the existing DFMA/interface checks. Neither a
proposal nor a proxy is physical evidence. Expensive native solvers are not
dispatched by this stage-zero/partial-stage-one adapter.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
import gzip
import fcntl
from io import BytesIO
import json
import os
from math import isfinite
from pathlib import Path
import platform
import stat
import time
import tomllib
import tempfile

import numpy as np

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from . import design_grammar as grammar, design_portfolio, model_cost, shape_families
from . import native_search
NativeSearch = native_search.NativeSearch

PRODUCER = "engineering/design_search/native_campaign.py"
CONFIG = "campaigns/rust-design-search.toml"
FLAGS = dict(design_portfolio.FLAGS, physical_journey_completed=False,
             selected_reference_changed=False, native_dispatch_allowed=False)
OBJECTIVES = ("nominal_stock_kg", "factory_gate_base_iqd", "factory_process_hours")
OPEN = ["Complete installed mass/CG/inertia, attachments and equipment remain unknown",
        "Structural, fatigue, fire, braking and propulsion evidence is not supplied by search",
        "Curved/implicit/cellular geometry and new architecture adapters require separate implementations",
        "Whole-railway installed/lifecycle comparison requires same-candidate downstream propagation",
        "No trained surrogate or high-fidelity solver is supplied by this bounded adapter"]
EXECUTING = {Path(module.__file__): digest(module.__file__) for module in (
    grammar, design_portfolio, model_cost, shape_families, native_search)}
EXECUTING[Path(__file__)]=digest(__file__)


def specification(root=ROOT):
    value = tomllib.loads((Path(root)/CONFIG).read_text())
    if (value.get("schema") != "osr-native-generative-search/1"
            or value.get("purpose") != "next-experiment" or value.get("change_selected_reference") is not False
            or value.get("exploration_weights") != [50, 30, 20]):
        raise ValueError("Explicit non-promoting native search contract required")
    for key, low, high in (("generations", 0, 8), ("proposals_per_generation", 1, 10000),
            ("evaluations_per_generation", 1, 64), ("detailed_finalists", 0, 18),
            ("maximum_seconds", 1, 600), ("seed", 0, 2**64-1)):
        if type(value.get(key)) is not int or not low <= value[key] <= high:
            raise ValueError("Bounded search invocation required: " + key)
    expected = {"bay_pitch_m", "frame_depth_m", "chord_wall_m", "skin_thickness_m",
                "core_thickness_m", "modular_length_m", "braced", "integrated_roof"}
    if set(value.get("axes", {})) != expected:
        raise ValueError("Explicit supported grammar axes required")
    for name, choices in value["axes"].items():
        if not isinstance(choices, list) or not choices or len(choices) != len(set(choices)):
            raise ValueError("Unique nonempty choices required")
        if name in ("braced", "integrated_roof"):
            valid = all(type(x) is bool for x in choices)
        else:
            valid = all(type(x) in (int, float) and isfinite(x) and x > 0 for x in choices)
        if not valid or grammar.parameters()[name] not in choices:
            raise ValueError("Finite typed axes containing the declared seed required: " + name)
    return value


def axes(root=ROOT):
    spec = specification(root)
    return {"family": sorted(shape_families.registry(root)), **spec["axes"]}


def _sources(root):
    return {**design_portfolio.sources(root), PRODUCER: digest(Path(root)/PRODUCER),
            "engineering/design_search/native_search.py": digest(Path(root)/"engineering/design_search/native_search.py"),
            CONFIG: digest(Path(root)/CONFIG)}


def _store(path, value):
    """Immutable canonical JSON: a conflicting existing record is an error."""
    raw = encoded(value)
    if len(raw)>native_search.MAX_BYTES:
        raise RuntimeError("Search record exceeds reader budget; retain prior checkpoint and generation journals")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if _read_cache(path,parse=False) != raw:
            raise RuntimeError("Conflicting immutable search record: " + str(path))
    else:
        with path.open("xb") as handle:
            handle.write(raw)


def _read_cache(path,*,parse=True,compressed=False):
    try:
        raw=native_search._read(path)
        if compressed:
            with gzip.GzipFile(fileobj=BytesIO(raw)) as handle:
                raw=handle.read(native_search.MAX_BYTES+1)
            if len(raw)>native_search.MAX_BYTES:raise ValueError("decompressed size budget")
        return native_search._parse(raw) if parse else raw
    except (ValueError,OSError,EOFError) as exc:
        raise RuntimeError("Cache integrity/read failure: "+str(path)) from exc


def _seal(value, key="evaluation_id"):
    value[key] = identity(value)
    return value


def _check_epoch(root, expected):
    if any(digest(path)!=value for path,value in EXECUTING.items()):
        raise RuntimeError("Executing search source changed after import")
    if _sources(root) != expected:
        raise ValueError("Search sources changed during execution; retain this interrupted run")
    if any(digest(Path(root)/name)!=value for name,value in expected.items()):
        raise RuntimeError("A retained source binding differs from current file bytes")


def _geometry_key(parameters, recipes, root):
    # Price, optimizer and service changes do not invalidate unchanged geometry.
    return dict(parameters=parameters, recipes=recipes, runtime=_runtime(),
        source_sha256={name: digest(Path(root)/name) for name in (
            grammar.PRODUCER, "engineering/design_search/remit.py", "engineering/station_rail/common.py")},
        retained_equipment_sources=grammar._reference_equipment()[2])


def _geometry(parameters, recipes, state, root):
    request = _geometry_key(parameters, recipes, root)
    key = identity(request); path = state/"geometry"/(key+".json.gz")
    candidate = grammar.build(parameters, recipes=recipes, reason="Native-search materialisation; ancestry is bound by the proposal record")
    if path.exists():
        record = _read_cache(path,compressed=True)
        if (record.get("request") != request or record.get("record_id") != identity(
                {k:v for k,v in record.items() if k != "record_id"})):
            raise RuntimeError("Geometry cache identity differs")
        if record.get("candidate") != candidate:
            raise RuntimeError("Cached geometry does not replay from the declared materialiser")
        return candidate, True
    record = _seal(dict(request=request, candidate=candidate), "record_id")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = gzip.compress(encoded(record), mtime=0)
    with path.open("xb") as handle:
        handle.write(raw)
    return candidate, False


def _evaluate(candidate, assumptions, state, root):
    # Exact material/cost dependencies, not optimizer or descriptor-cell bytes.
    dependencies = {k:v for k,v in design_portfolio.sources(root).items()
                    if k not in ("engineering/design_search/quality_diversity.py", shape_families.PRODUCER)}
    dependencies[PRODUCER]=digest(Path(root)/PRODUCER)
    request = dict(candidate_id=candidate["candidate_id"], definition_id=candidate["definition_id"],runtime=_runtime(),
        assumption_id=assumptions["assumption_id"], evaluator_sources=dependencies, fidelity=0,
        requirements=deepcopy(candidate["requirements"]) if "requirements" in candidate else candidate["requirement_revision"])
    key = identity(request); path = state/"stock-cost"/(key+".json")
    cost = design_portfolio._factory_gate_stock_estimate(candidate, assumptions, root)
    mass = sum(part["mass_kg"] for part in candidate["parts"])
    record = _seal(dict(request=request, candidate_id=candidate["candidate_id"],
        definition_id=candidate["definition_id"], descriptor={"family":candidate["parameters"]["family"]},
        metrics=dict(nominal_stock_kg=mass, factory_gate_base_iqd=cost["scenarios_iqd"]["base"],
                     factory_process_hours=cost["process_hours"]["base"]), cost_estimate=cost,
        complete_installed_mass_kg=None, complete_installed_cost_iqd=None,
        execution="completed", engineering_screen="unknown", structural_analysis="not-run",
        fidelity=0, evidence_maturity="conditional-nominal-stock-and-Class-C-cost", **FLAGS))
    exists=path.exists()
    _store(path, record)  # Cheap replay prevents resealed zero-cost/mass records.
    return record, exists


def screen_programs(programs, domains, recipes):
    """Vectorised indicative stock proxy for experiment ordering, not rejection.

    The proxy counts full envelope panels and four longitudinal RHS members. It
    omits openings and detailed ribs/joints. Its error is not calibrated; it is
    never a candidate quantity, cost, stiffness or compliance result.
    """
    names = list(domains)
    def column(name):
        i = names.index(name)
        return np.asarray([domains[name][p["genes"][i]] for p in programs])
    if not programs:
        return []
    family = column("family")
    rho = np.asarray([2710. if recipes[x]["frame"] == "aluminium_reference" else 1900. for x in family])
    sandwich = np.asarray([recipes[x]["shell"] != "skin" for x in family])
    skins = np.where(sandwich, 2., 1.)
    shell_area = 2*17*3.7+17*2.65+2*2.65*3.7
    defaults = grammar.parameters(); w=defaults["chord_width_m"]; h=defaults["chord_height_m"]
    t = column("chord_wall_m").astype(float)
    proxy = (4*17*(w*h-(w-2*t)*(h-2*t))*rho
        + shell_area*skins*column("skin_thickness_m").astype(float)*1900
        + shell_area*sandwich*column("core_thickness_m").astype(float)*85.)
    return [float(x) for x in proxy]


def _shortlist(programs, proxies, limit):
    # Keep the proposed 50/30/20 allocation among actual evaluations, not only
    # among generated programs. Highest-remainder deterministic apportionment.
    labels = ("exploit", "alternative-family", "unconventional")
    quotas = [limit*w//100 for w in (50,30,20)]
    for i in sorted(range(3), key=lambda i: (-(limit*(50,30,20)[i]%100), i))[:limit-sum(quotas)]:
        quotas[i] += 1
    ordered = sorted(range(len(programs)), key=lambda i: (proxies[i], tuple(programs[i]["genes"])))
    chosen = []
    for label, quota in zip(labels, quotas):
        chosen.extend([i for i in ordered if programs[i]["operator"] == label][:quota])
    chosen.extend(i for i in ordered if i not in chosen and len(chosen)<limit)
    return chosen


def _checkpoint(path, value):
    value = _seal(deepcopy(value), "checkpoint_id")
    raw=encoded(value)
    if len(raw)>native_search.MAX_BYTES:
        raise RuntimeError("Checkpoint exceeds reader budget; prior checkpoint and generation journals retained")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():raise RuntimeError("Symlinked checkpoint destination is not permitted")
    if path.exists():
        native_search._regular(path)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".checkpoint-", delete=False) as handle:
        temporary=Path(handle.name);handle.write(raw)
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _runtime():
    return dict(python_implementation=platform.python_implementation(),python_version=platform.python_version(),
                numpy_version=np.__version__,proxy_dtype="float64",coordinator_workers=1)


def _verify_frontier(data,contract_id,state,kernel,domains,recipes):
    """Replay Rust requests and bind resumable programs to their exact journals."""
    known={};expected_seen=[p["genes"] for p in data["attempts"] if p["operator"]=="seed"]
    defaults=grammar.parameters()
    seed_genes={tuple(values.index(family if name=="family" else defaults[name]) for name,values in domains.items())
                for family in domains["family"]}
    seed_records=[*data["seed_pending"],*[p for p in data["attempts"] if p["operator"]=="seed"]]
    if len(seed_records)!=len(seed_genes) or {tuple(p["genes"]) for p in seed_records}!=seed_genes:
        raise RuntimeError("Checkpoint seed coverage/uniqueness differs")
    for p in seed_records:
        if tuple(p["genes"]) not in seed_genes or p["parent_candidate_ids"] or p["generation"]!=0:
            raise RuntimeError("Checkpoint seed differs from the declared grammar registry")
    for ordinal,generation in enumerate(data["generations"],1):
        packet=native_search._parse(native_search._read(state/"generated"/(generation["generation_id"]+".json")))
        req=packet["request"]
        declared=data["contract"]["specification"]
        count=generation["parent_attempt_count"]
        if type(count) is not int or not 0<=count<=len(data["attempts"]):
            raise RuntimeError("Generation parent attempt prefix differs")
        parent_rows={};parent_genes={}
        for attempt in data["attempts"][:count]:
            if attempt.get("evaluation_id") in data["all_evaluations"]:
                cid=attempt["candidate_id"]
                parent_rows.setdefault(cid,data["all_evaluations"][attempt["evaluation_id"]])
                parent_genes.setdefault(cid,attempt["genes"])
        parent_archive=kernel.archive(list(parent_rows.values()),OBJECTIVES,("family",))
        expected_parents=[dict(candidate_id=cid,genes=parent_genes[cid]) for cid in parent_archive["retained_candidate_ids"]]
        if (generation["generation"]!=ordinal or req["generation"]!=ordinal
                or req["parents"]!=expected_parents or generation["parent_archive_id"]!=parent_archive["archive_id"]
                or req["weights"]!=declared["exploration_weights"] or req["limit"]!=declared["proposals_per_generation"]
                or req["max_attempts"]!=min(1000000,declared["proposals_per_generation"]*20) or req["family_axis"]!=0
                or req["seen"]!=expected_seen or req["seed"]!=data["contract"]["specification"]["seed"]
                or req["axes"]!=[dict(name=name,choices=len(values)) for name,values in domains.items()]
                or generation["generation_id"]!=identity(dict(contract_id=contract_id,generation=generation["generation"],request=req))
                or packet["generated"]!=kernel.propose(**req)):
            raise RuntimeError("Checkpoint generation does not replay from its Rust request")
        native={tuple(p["genes"]):p for p in packet["generated"]["proposals"]}
        expected_seen.extend(p["genes"] for p in packet["generated"]["proposals"])
        proxies=dict(zip((tuple(p["genes"]) for p in packet["generated"]["proposals"]),
                         screen_programs(packet["generated"]["proposals"],domains,recipes)))
        if (len(packet["programs"])!=len(native)
                or {tuple(p["genes"]) for p in packet["programs"]}!=set(native)
                or len({p["proposal_id"] for p in packet["programs"]})!=len(native)):
            raise RuntimeError("Generation program coverage/uniqueness differs")
        for p in packet["programs"]:
            genes=tuple(p["genes"]);core=native.get(genes)
            if (core is None or any(p[k]!=core[k] for k in ("genes","operator","parent_candidate_ids"))
                    or p["proxy_stock_kg"]!=proxies[genes] or p["generation"]!=generation["generation"]
                    or p["proposal_id"]!=identity(dict(program={k:v for k,v in p.items() if k!="proposal_id"},contract_id=contract_id))):
                raise RuntimeError("Generation program differs from its Rust provenance")
            known[p["proposal_id"]]=p
    for p in [*data["pending"],*data["deferred"],*data["attempts"]]:
        base={k:v for k,v in p.items() if k not in ("candidate_id","definition_id","evaluation_id","state","reason")}
        if p["operator"]!="seed" and known.get(p.get("proposal_id"))!=base:
            raise RuntimeError("Checkpoint program differs from immutable generation journal")
        refs=p.get("parent_evaluations",[])
        if ([r["candidate_id"] for r in refs]!=p["parent_candidate_ids"]
                or any(data["all_evaluations"].get(r["evaluation_id"],{}).get("candidate_id")!=r["candidate_id"]
                       or data["rows"].get(r["candidate_id"],{}).get("evaluation_id")!=r["evaluation_id"] for r in refs)):
            raise RuntimeError("Checkpoint parent evaluation lineage differs")
    tracked=[p["proposal_id"] for p in [*data["pending"],*data["deferred"],*data["attempts"]] if p["operator"]!="seed"]
    if len(tracked)!=len(set(tracked)) or set(tracked)!=set(known):
        raise RuntimeError("Checkpoint proposal coverage/uniqueness differs")
    if any(any(k in p for k in ("state","candidate_id","evaluation_id","definition_id"))
           for p in [*data["pending"],*data["deferred"],*data["seed_pending"]]):
        raise RuntimeError("Unexecuted checkpoint program contains a result")
    states={"evaluated-nominal-stock","duplicate-physical-geometry",
            "definition-or-model-domain-unresolved","cost-model-domain-unresolved"}
    if any(p.get("state") not in states for p in data["attempts"]):
        raise RuntimeError("Checkpoint attempt lifecycle differs")
    if data["seen"]!=expected_seen or data["next_generation"]!=len(data["generations"])+1:
        raise RuntimeError("Checkpoint continuation/seen frontier differs")


def _run(*, root=ROOT, state=None, generations=None, binary=None, maximum_new_evaluations=None):
    root=Path(root).resolve()
    if root != ROOT.resolve():
        raise ValueError("Execute the coordinator from its imported source checkout")
    spec=specification(root)
    target_generation=spec["generations"] if generations is None else generations
    if type(target_generation) is not int or not 0<=target_generation<=8:
        raise ValueError("Zero-to-eight generations required")
    budget=spec["evaluations_per_generation"]*target_generation if maximum_new_evaluations is None else maximum_new_evaluations
    if type(budget) is not int or not 0<=budget<=512:
        raise ValueError("Zero-to-512 new evaluation budget required")
    kernel=NativeSearch(root=root,binary=binary)
    state=Path(state) if state is not None else root/"build/native-design-search"
    if state.is_symlink():raise ValueError("Regular campaign state directory required")
    source=_sources(root);_check_epoch(root,source)
    recipes=shape_families.registry(root);domains=axes(root)
    assumptions=model_cost.assumptions(root);start=time.monotonic()
    search_spec={k:v for k,v in spec.items() if k not in (
        "generations","maximum_seconds","evaluations_per_generation","detailed_finalists")}
    contract=dict(specification=search_spec,sources=source,runtime=_runtime(),binary_sha256=kernel.receipt["binary_sha256"],
        kernel_build_receipt_id=kernel.receipt["receipt_id"],variable_registry_id=identity(dict(axes=domains,recipes=recipes)),
        requirements_context="Six 17 m cars, 44 seats plus two wheelchair places per car; same development service")
    contract_id=identity(contract);_store(state/"contracts"/(contract_id+".json"),contract)
    checkpoint_path=state/"checkpoints"/(contract_id+".json")
    if checkpoint_path.exists():
        data=native_search._parse(native_search._read(checkpoint_path))
        if data.get("checkpoint_id")!=identity({k:v for k,v in data.items() if k!="checkpoint_id"}) or data.get("contract")!=contract:
            raise RuntimeError("Campaign checkpoint source/identity differs")
        data.pop("checkpoint_id")
    else:
        defaults=grammar.parameters();seed_programs=[]
        for family in domains["family"]:
            genes=[values.index(family if name=="family" else defaults[name]) for name,values in domains.items()]
            seed_programs.append(dict(genes=genes,operator="seed",parent_candidate_ids=[],generation=0))
        data=dict(contract=contract,rows={},all_evaluations={},genes_by_id={},seen=[],attempts=[],
            pending=[],deferred=[],seed_pending=seed_programs,generations=[],next_generation=1)
    _verify_frontier(data,contract_id,state,kernel,domains,recipes)
    stats=dict(geometry_cache_replayed=0,geometry_new=0,cost_cache_replayed=0,cost_new=0,
               completed_attempts_resumed=len(data["attempts"]),new_successor_evaluations=0)
    used=0
    def save(force=False):
        _check_epoch(root,source)
        if force or len(data["attempts"])%8==0:_checkpoint(checkpoint_path,data)
    def evaluate(program):
        nonlocal used
        program=deepcopy(program)
        if (len(program["genes"])!=len(domains) or any(type(i) is not int or not 0<=i<len(values)
                for i,values in zip(program["genes"],domains.values()))
                or program["operator"] not in ("seed","exploit","alternative-family","unconventional")):
            raise RuntimeError("Invalid resumed proposal genes/operator")
        parameters=grammar.parameters()
        parameters.update({name:values[index] for (name,values),index in zip(domains.items(),program["genes"])})
        program.setdefault("parent_evaluations",[dict(candidate_id=cid,evaluation_id=data["rows"][cid]["evaluation_id"])
            for cid in program["parent_candidate_ids"]])
        if ([p["candidate_id"] for p in program["parent_evaluations"]]!=program["parent_candidate_ids"]
                or any(data["all_evaluations"].get(p["evaluation_id"],{}).get("candidate_id")!=p["candidate_id"]
                       for p in program["parent_evaluations"])):
            raise RuntimeError("Proposal parent evaluation lineage differs")
        program["variable_registry_id"]=contract["variable_registry_id"]
        program["requirement_context"]=contract["requirements_context"]
        program.setdefault("proposal_id",identity(dict(program=program,contract_id=contract_id)))
        try:
            candidate,hit=_geometry(parameters,recipes,state,root)
        except ValueError as exc:
            program.update(state="definition-or-model-domain-unresolved",reason=str(exc),candidate_id=None)
        else:
            stats["geometry_cache_replayed" if hit else "geometry_new"]+=1
            try:
                row,hit=_evaluate(candidate,assumptions,state,root)
            except ValueError as exc:
                program.update(state="cost-model-domain-unresolved",reason=str(exc),
                               candidate_id=candidate["candidate_id"],definition_id=candidate["definition_id"])
                data["attempts"].append(program);_store(state/"attempts"/(program["proposal_id"]+".json"),program)
                if program["operator"]!="seed":used+=1;stats["new_successor_evaluations"]+=1
                return
            stats["cost_cache_replayed" if hit else "cost_new"]+=1
            cid=candidate["candidate_id"]
            program.update(candidate_id=cid,definition_id=candidate["definition_id"],evaluation_id=row["evaluation_id"],
                state="duplicate-physical-geometry" if cid in data["rows"] else "evaluated-nominal-stock")
            # A physical alias never overwrites the first archive context or its
            # genes. Every distinct definition/evaluation remains independently linked.
            data["all_evaluations"][row["evaluation_id"]]=row
            data["rows"].setdefault(cid,row);data["genes_by_id"].setdefault(cid,program["genes"])
        data["attempts"].append(program)
        _store(state/"attempts"/(program["proposal_id"]+".json"),program)
        if program["operator"]!="seed":used+=1;stats["new_successor_evaluations"]+=1
    # Completed cheap stages are replay-checked before using a checkpoint's
    # archive. This is inexpensive integrity validation, not a saved solver run.
    by_evaluation={p.get("evaluation_id"):p for p in data["attempts"] if p.get("evaluation_id")}
    for eid,row in data["all_evaluations"].items():
        if eid not in by_evaluation or row.get("evaluation_id")!=eid:
            raise RuntimeError("Checkpoint lost an evaluation's materialisation lineage")
        program=by_evaluation[eid]
        parameters=grammar.parameters()
        parameters.update({name:values[index] for (name,values),index in zip(domains.items(),program["genes"])})
        candidate,_=_geometry(parameters,recipes,state,root);expected,_=_evaluate(candidate,assumptions,state,root)
        if row!=expected:raise RuntimeError("Checkpoint evaluation does not replay")
    for cid,row in data["rows"].items():
        if (row.get("candidate_id")!=cid or data["all_evaluations"].get(row.get("evaluation_id"))!=row
                or by_evaluation[row["evaluation_id"]]["genes"]!=data["genes_by_id"].get(cid)):
            raise RuntimeError("Checkpoint archive mixed physical/definition/gene contexts")
    while data["seed_pending"] and time.monotonic()-start<spec["maximum_seconds"]:
        program=data["seed_pending"].pop(0);data["seen"].append(program["genes"]);evaluate(program);save()
    if not data["rows"]:raise ValueError("No executable seed; retain definitions before extending adapters")
    # Resume the recorded frontier before allocating new generation work.
    while data["pending"] and used<budget and time.monotonic()-start<spec["maximum_seconds"]:
        evaluate(data["pending"].pop(0));save()
    # Once the requested generations exist, a repeated invocation advances the
    # lower-priority retained frontier instead of repeating the same shortlist.
    while (data["next_generation"]>target_generation and data["deferred"] and used<budget
            and time.monotonic()-start<spec["maximum_seconds"]):
        evaluate(data["deferred"].pop(0));save()
    archive=kernel.archive(list(data["rows"].values()),OBJECTIVES,("family",))
    while (not data["seed_pending"] and not data["pending"] and data["next_generation"]<=target_generation
            and used<budget and time.monotonic()-start<spec["maximum_seconds"]):
        generation=data["next_generation"];_check_epoch(root,source)
        parent_ids=archive["retained_candidate_ids"]
        request=dict(seed=spec["seed"],generation=generation,limit=spec["proposals_per_generation"],
            max_attempts=min(1000000,spec["proposals_per_generation"]*20),
            axes=[dict(name=name,choices=len(values)) for name,values in domains.items()],family_axis=0,
            parents=[dict(candidate_id=cid,genes=data["genes_by_id"][cid]) for cid in parent_ids],
            seen=deepcopy(data["seen"]),weights=spec["exploration_weights"])
        generated=kernel.propose(**request);programs=generated["proposals"]
        data["seen"].extend(p["genes"] for p in programs)
        proxies=screen_programs(programs,domains,recipes)
        chosen=_shortlist(programs,proxies,min(spec["evaluations_per_generation"],budget-used))
        ordered=chosen+[i for i in sorted(range(len(programs)),key=lambda i:(proxies[i],tuple(programs[i]["genes"]))) if i not in chosen]
        prepared=[]
        for i in ordered:
            program=dict(programs[i],generation=generation,proxy_stock_kg=proxies[i],
                parent_evaluations=[dict(candidate_id=cid,evaluation_id=data["rows"][cid]["evaluation_id"])
                    for cid in programs[i]["parent_candidate_ids"]],
                variable_registry_id=contract["variable_registry_id"],requirement_context=contract["requirements_context"])
            program["proposal_id"]=identity(dict(program=program,contract_id=contract_id));prepared.append(program)
        generation_id=identity(dict(contract_id=contract_id,generation=generation,request=request))
        _store(state/"generated"/(generation_id+".json"),dict(request=request,generated=generated,programs=prepared))
        data["generations"].append(dict(generation=generation,generation_id=generation_id,
            generated_programs=len(programs),proxy_kind="uncalibrated-full-panel-and-four-RHS-stock-heuristic",
            parent_attempt_count=len(data["attempts"]),parent_archive_id=archive["archive_id"],
            kernel_provenance=generated["provenance"]))
        data["pending"].extend(prepared[:len(chosen)])
        data["deferred"].extend(prepared[len(chosen):])
        data["next_generation"]+=1;save(force=True)
        # Spend this invocation's budget; preserve every unexecuted program.
        while data["pending"] and used<budget and time.monotonic()-start<spec["maximum_seconds"]:
            evaluate(data["pending"].pop(0));save()
        archive=kernel.archive(list(data["rows"].values()),OBJECTIVES,("family",))
    detailed=[]
    for cell in archive["cells"]:
        if len(detailed)>=spec["detailed_finalists"] or time.monotonic()-start>=spec["maximum_seconds"]:break
        cid=cell["retained_candidate_ids"][0];parameters=grammar.parameters()
        parameters.update({name:values[index] for (name,values),index in zip(domains.items(),data["genes_by_id"][cid])})
        candidate,_=_geometry(parameters,recipes,state,root)
        detail=design_portfolio._evaluate(candidate,recipes[parameters["family"]],"native-search-finalist",assumptions,root)
        if detail["candidate_id"]!=cid or detail["definition_id"]!=data["rows"][cid]["definition_id"]:
            raise RuntimeError("Detailed evaluator mixed physical/definition identity")
        detailed.append(detail)
    save(force=True)
    value=_seal(dict(schema="osr-native-generative-search-result/1",contract_id=contract_id,contract=contract,
        sources=source,axes=domains,candidate_count=len(data["rows"]),evaluations=sorted(data["all_evaluations"].values(),key=lambda r:r["evaluation_id"]),
        archive_contexts={cid:row["evaluation_id"] for cid,row in data["rows"].items()},
        attempts=data["attempts"],generations=data["generations"],pending=data["pending"],deferred=data["deferred"],seed_pending=data["seed_pending"],
        archive=archive,detailed_finalists=detailed,cache_statistics=stats,integrated_selection=None,
        complete_installed_mass_kg=None,maximum_seconds_is_cooperative=True,numerical_solver_dispatch_count=0,
        cache_scope="Cheap geometry/cost replay-checked; no avoided high-fidelity solver runtime is claimed",
        unresolved=OPEN,**FLAGS),"run_id")
    _store(state/"runs"/(value["run_id"]+".json"),value)
    return dict(run_id=value["run_id"],candidate_count=len(data["rows"]),
        generated_programs=sum(g["generated_programs"] for g in data["generations"]),pending_programs=len(data["pending"]),
        deferred_programs=len(data["deferred"]),
        detailed_finalists=len(detailed),cache_statistics=stats,output=str(state/"runs"/(value["run_id"]+".json")),
        elapsed_s=time.monotonic()-start,integrated_selection=None,**FLAGS)


@contextmanager
def _state_lock(state):
    state=Path(state)
    if state.is_symlink():raise RuntimeError("Symlinked campaign state is not permitted")
    state.mkdir(parents=True,exist_ok=True)
    try:
        descriptor=os.open(state/"coordinator.lock",os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW|os.O_NONBLOCK,0o600)
    except OSError as exc:
        raise RuntimeError("Regular campaign coordinator lock required") from exc
    with os.fdopen(descriptor,"a+b") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):raise RuntimeError("Regular campaign coordinator lock required")
        try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc:raise RuntimeError("Campaign state already has an active coordinator") from exc
        try:yield
        finally:fcntl.flock(handle,fcntl.LOCK_UN)


def run(*,root=ROOT,state=None,**kwargs):
    state=Path(state) if state is not None else Path(root)/"build/native-design-search"
    with _state_lock(state):
        return _run(root=root,state=state,**kwargs)


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state",type=Path);parser.add_argument("--generations",type=int)
    parser.add_argument("--binary",type=Path)
    parser.add_argument("--evaluations",type=int,help="New successor evaluations in this invocation; seeds are separate")
    args=parser.parse_args()
    print(json.dumps(run(state=args.state,generations=args.generations,binary=args.binary,
                         maximum_new_evaluations=args.evaluations),indent=2))
