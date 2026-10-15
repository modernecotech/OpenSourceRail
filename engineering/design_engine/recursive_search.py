"""Deterministic, bounded, feedback-driven numerical design exploration.

A proposal or confirmation, including a contextual cache hit, consumes one policy
budget unit. Runtime callers separately account for actual solver cases/resources.
Checks are explicitly partitioned: physical qualification is retained but is never
established by this numerical search. A callback is responsible for truthful native
checks; this policy neither manufactures native passes nor runs hidden solvers.
"""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal, ROUND_HALF_EVEN
import math
import re

from .contracts import STATES, canonical, fingerprint, identity, problem, problem_fingerprint, variables

PASSED = {"passed", "numerically-verified"}
KNOWN_OUTCOME = PASSED | {"failed"}


class RecursiveSearchStop(RuntimeError):
    """A callback may stop safely while retaining its completed search history."""

    def __init__(self, reason="budget", message="external execution limit reached"):
        if reason not in {"budget", "cancelled"}:
            raise ValueError("budget or cancelled stop reason required")
        self.reason = reason
        super().__init__(message)


def _bound(value, name, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"bounded integer {name} required ({low}..{high})")
    return value


def _context(value):
    required = {"identity", "source_sha256", "toolchain", "request"}
    if not isinstance(value, dict) or not required <= value.keys():
        raise ValueError("cache context needs full identity, source, toolchain and request")
    identity(value["identity"])
    source = value["source_sha256"]
    hashes = source.values() if isinstance(source, dict) and source else [source]
    if not all(isinstance(item, str) and re.fullmatch(r"[a-f0-9]{64}", item) for item in hashes):
        raise ValueError("actual source SHA256 context required")
    if not isinstance(value["toolchain"], dict) or not value["toolchain"] or not value["request"]:
        raise ValueError("nonempty toolchain and exact request context required")
    canonical(value)
    return deepcopy(value)


def _policy(charter, supplied):
    if not isinstance(supplied, dict):
        raise ValueError("explicit numerical/native/physical check policy required")
    allowed = {"evaluations", "iterations", "confirmations", "objective_axes", "screening_checks",
               "native_checks", "physical_checks", "real_intervals", "refinements", "stall_rounds",
               "finite_exhaustive", "max_space", "seed"}
    if supplied.keys() - allowed:
        raise ValueError("unsupported recursive policy fields: " + ", ".join(sorted(supplied.keys() - allowed)))
    result = deepcopy(supplied)
    for field in ("screening_checks", "native_checks", "physical_checks"):
        checks = result.get(field)
        if not isinstance(checks, list) or any(not isinstance(key, str) for key in checks) or len(set(checks)) != len(checks):
            raise ValueError("explicit distinct check categories required: " + field)
    groups = [set(result[key]) for key in ("screening_checks", "native_checks", "physical_checks")]
    mandatory = set(charter["applicability"]["mandatory_checks"])
    if any(groups[i] & groups[j] for i in range(3) for j in range(i)) or set.union(*groups) != mandatory:
        raise ValueError("every mandatory check must belong to exactly one check category")
    if not groups[0] or not groups[1]:
        raise ValueError("screening and actual native check requirements cannot be empty")
    # These common external-authority labels cannot be promoted by a numerical preset.
    external = {"physical_correlation", "independent_acceptance", "supplier_calibration"}
    if mandatory & external - groups[2]:
        raise ValueError("physical correlation/acceptance must remain physical qualification")
    axes = result.setdefault("objective_axes", [charter["objectives"][0]])
    if not isinstance(axes, list) or not axes or len(axes) != len(set(axes)) or any(axis not in charter["objectives"] for axis in axes):
        raise ValueError("distinct declared objective axes required (all minimized)")
    limit = result.setdefault("evaluations", charter["budget"]["evaluations"])
    _bound(limit, "evaluations", 1, charter["budget"]["evaluations"])
    _bound(result.setdefault("iterations", limit), "iterations", 1, 4096)
    _bound(result.setdefault("confirmations", limit // 2), "confirmations", 0, limit)
    _bound(result.setdefault("real_intervals", 2), "real_intervals", 2, 32)
    _bound(result.setdefault("refinements", 4), "refinements", 0, 12)
    _bound(result.setdefault("stall_rounds", max(8, limit)), "stall_rounds", 1, 4096)
    _bound(result.setdefault("max_space", 4096), "max_space", 1, 100000)
    if type(result.setdefault("finite_exhaustive", False)) is not bool:
        raise ValueError("finite_exhaustive must be boolean")
    seed = result.setdefault("seed", None)
    if seed is not None:
        _bound(seed, "seed", 0, 2**32 - 1)
    return result


def validate_policy(charter, policy):
    """Validate a controlled preset plus bounded tuning without mutating either."""
    problem(charter)
    return _policy(charter, policy)


class _Domain:
    def __init__(self, spec, settings):
        self.spec = spec
        self.kind = spec["kind"]
        self.settings = settings
        if self.kind == "choice":
            self.size = len(spec["choices"])
        else:
            self.low, self.high = map(lambda value: Decimal(str(value)), spec["bounds"])
            self.steps = (int(self.high - self.low) if self.kind == "integer"
                          else (settings["real_intervals"] * 2**settings["refinements"] if self.low != self.high else 0))
            self.size = self.steps + 1

    def value(self, index):
        if self.kind == "choice":
            return deepcopy(self.spec["choices"][index])
        if self.kind == "integer":
            return int(self.low) + index
        if not self.steps:
            return float(self.low)
        return float(self.low + (self.high - self.low) * Decimal(index) / Decimal(self.steps))

    def index(self, value):
        if self.kind == "choice":
            return next(i for i, option in enumerate(self.spec["choices"]) if fingerprint(option) == fingerprint(value))
        if not self.steps:
            return 0
        position = ((Decimal(str(value)) - self.low) / (self.high - self.low)) * self.steps
        return max(0, min(self.steps, int(position.to_integral_value(rounding=ROUND_HALF_EVEN))))

    def neighbours(self, value, depth):
        current = self.index(value)
        if self.kind == "choice":
            indices = [i for i in range(self.size) if i != current]
        else:
            # Coarse moves shrink deterministically; the last level connects the lattice.
            step = (1 if depth == self.settings["refinements"] else
                    max(1, math.ceil(self.steps / (2**(depth + 1)))))
            indices = sorted({max(0, current - step), min(self.size - 1, current + step), 0, self.size - 1} - {current})
        return [self.value(i) for i in indices]


def _objective(candidate, axes):
    metrics = candidate.get("metrics", {})
    values = []
    for axis in axes:
        value = metrics.get(axis)
        if isinstance(value, dict):
            if value.get("state") not in {"nominal", "synthetic", "supplier", "measured"}:
                return None
            value = value.get("value")
        if type(value) not in (float, int) or not math.isfinite(value):
            return None
        values.append(value)
    return values


def _outcome(candidate, settings, confirmed):
    checks = candidate.get("checks", {})
    numerical = settings["screening_checks"] + settings["native_checks"]
    selected = numerical if confirmed else settings["screening_checks"]
    states = [checks.get(key, {}).get("state", "unknown") for key in selected]
    objective = _objective(candidate, settings["objective_axes"])
    screen = objective is not None and all(checks.get(key, {}).get("state") in PASSED for key in settings["screening_checks"])
    verified = confirmed and objective is not None and all(state in PASSED for state in states)
    # An already failed native check is never a feasible screen recommendation.
    native_failed = any(checks.get(key, {}).get("state") in {"failed", "outside-domain", "unavailable", "stale", "cancelled", "budget-exceeded"} for key in settings["native_checks"])
    return dict(objectives=objective, feasible_screen=screen and not native_failed and (not confirmed or all(checks.get(key, {}).get("state") in PASSED for key in settings["native_checks"])),
                numerically_verified=verified,
                failed_checks=sum(state in {"failed", "outside-domain"} for state in states),
                unresolved_checks=sum(state not in KNOWN_OUTCOME for state in states),
                native_complete=confirmed and objective is not None and all(checks.get(key, {}).get("state") in KNOWN_OUTCOME for key in numerical))


def _pareto(nodes, predicate):
    rows = [row for row in nodes if row["outcome"][predicate]]
    return [row["candidate"]["id"] for row in sorted(rows, key=lambda row: row["candidate"]["id"])
            if not any(all(a <= b for a, b in zip(other["outcome"]["objectives"], row["outcome"]["objectives"]))
                       and any(a < b for a, b in zip(other["outcome"]["objectives"], row["outcome"]["objectives"]))
                       for other in rows)]


def recursive_search(charter, evaluate, confirm, *, context, initial=None, policy=None,
                     cache=None, stop_exceptions=(), checkpoint=None):
    """Explore full variable maps using actual screening and confirmation feedback.

    ``evaluate(values, phase, parent_id)`` and ``confirm(candidate)`` return common
    candidate dictionaries. ``stop_exceptions`` are retained as partial termination;
    callers can persist the report and re-raise their common terminal exception.
    ``checkpoint`` receives a defensive copy after every attempt and round. Cache
    hits consume this policy's budget, never silently consume native solver work.
    """
    problem(charter)
    settings = _policy(charter, policy)
    scoped = _context(context)
    if not callable(evaluate) or not callable(confirm):
        raise ValueError("evaluation and actual native confirmation callbacks required")
    if not isinstance(stop_exceptions, tuple) or any(not isinstance(cls, type) or not issubclass(cls, Exception) for cls in stop_exceptions):
        raise ValueError("stop_exceptions must be exception classes")
    if cache is None:
        cache = {}
    if not isinstance(cache, dict):
        raise ValueError("context-keyed cache mapping required")
    keys = sorted(charter["variables"])
    if not keys:
        raise ValueError("at least one physical design variable required")
    domains = {name: _Domain(charter["variables"][name], settings) for name in keys}
    lattice_size = math.prod(domain.size for domain in domains.values())
    choices_only = all(domain.kind == "choice" for domain in domains.values())
    if settings["finite_exhaustive"] and (not choices_only or lattice_size > settings["max_space"]):
        raise ValueError("exhaustive search needs a bounded all-choice domain")
    namespace = fingerprint(dict(context=scoped, problem_sha256=problem_fingerprint(charter), policy=settings))
    nodes = {}; history = []; pending = []; seen_ids = {}; iterations = 0
    spent = calls = hits = confirmations = fallback_cursor = 0
    termination = None; stop = None; stagnant = 0; best_progress = None; in_flight = None

    def normalized(value):
        value = variables(charter, value)
        return {key: domains[key].value(domains[key].index(value[key])) for key in keys}

    if initial is None:
        first = {key: domains[key].value(0 if settings["seed"] is None else int(fingerprint([settings["seed"], key]), 16) % domains[key].size) for key in keys}
        initial = [first]
    if not isinstance(initial, list) or not initial or len(initial) > 128:
        raise ValueError("bounded nonempty initial full-variable maps required")
    starts = sorted({fingerprint(normalized(value)): normalized(value) for value in initial}.items())

    def rank(node):
        outcome = node["outcome"]
        tier = 0 if outcome["numerically_verified"] else 1 if outcome["feasible_screen"] else 2
        return (tier, tuple(outcome["objectives"] or []) if tier < 2 else
                (outcome["failed_checks"], outcome["unresolved_checks"]), node["candidate"]["id"])

    def report():
        ordered = sorted(nodes.values(), key=lambda node: node["candidate"]["id"])
        verified = [node for node in ordered if node["outcome"]["numerically_verified"]]
        incumbent = min(verified, key=rank)["candidate"]["id"] if verified else None
        domain_complete = choices_only and len(nodes) == lattice_size
        native_complete = domain_complete and all(node["outcome"]["native_complete"] for node in ordered)
        return dict(schema="osr-recursive-design-search/1", policy_revision="deterministic-recursive/1", problem_sha256=problem_fingerprint(charter),
                    charter=deepcopy(charter), context=deepcopy(scoped), context_sha256=fingerprint(scoped), cache_namespace_sha256=namespace, policy=deepcopy(settings), initial_requested=deepcopy(initial), initial_quantized=[deepcopy(value) for _, value in starts],
                    quantization="Decimal(str(bounds)) rational lattice with ROUND_HALF_EVEN; declared choice order and typed integers retained",
                    candidates=[deepcopy(node["candidate"]) for node in ordered],
                    outcomes={node["candidate"]["id"]: deepcopy(node["outcome"]) for node in ordered},
                    lineage=deepcopy(history), in_flight_attempt=deepcopy(in_flight), iterations=iterations, evaluations=spent,
                    proposals=sum(event["phase"] != "confirm" for event in history) + int(in_flight is not None and in_flight["phase"] != "confirm"), completed_unique_candidates=len(nodes), confirmations=confirmations, oracle_calls=calls, cache_hits=hits,
                    deduplicated_initial_values=len(initial) - len(starts),
                    conditional_screen_frontier=_pareto(ordered, "feasible_screen"),
                    verified_frontier=_pareto(ordered, "numerically_verified"), incumbent_id=incumbent,
                    termination_reason=termination or "running", stop=deepcopy(stop),
                    finite_domain_size=lattice_size if choices_only else None,
                    quantized_lattice_size=lattice_size, finite_domain_complete=domain_complete,
                    native_domain_complete=native_complete,
                    best_verified_in_tested_domain_claimed=bool(incumbent and native_complete),
                    best_verified_claim_scope="declared finite choices and numerical checks only" if incumbent and native_complete else None,
                    ranking_axes=deepcopy(settings["objective_axes"]), objectives_direction="minimize",
                    unknown_objective_axes=[axis for axis in charter["objectives"] if axis not in settings["objective_axes"]],
                    physical_qualification={node["candidate"]["id"]: {key: deepcopy(node["candidate"].get("checks", {}).get(key, {"state": "unknown"})) for key in settings["physical_checks"]} for node in ordered},
                    unconfirmed_candidate_ids=[nodes[key]["candidate"]["id"] for key in pending if not nodes[key].get("confirmation_attempted")],
                    policy_evaluation_accounting="each proposal/confirmation including cache hit; actual solver cases charged separately by caller",
                    seed_independent=settings["seed"] is None, replay_complete=stop is None or stop.get("type")=="iteration-limit",
                    determinism_basis="fixed source/tool/request/policy and callback outcome transcript; native output bitwise determinism is not assumed",
                    global_optimum_claimed=False,
                    physical_release=False, independently_accepted=False)

    def snapshot():
        if checkpoint is not None:
            checkpoint(deepcopy(report()))

    def validate(candidate, values, previous):
        if not isinstance(candidate, dict) or not isinstance(candidate.get("id"), str) or not candidate["id"]:
            raise ValueError("callback must return an identified common candidate")
        if normalized(candidate.get("variables", {})) != values or variables(charter, candidate["variables"]) != values:
            raise ValueError("callback changed or omitted the requested full physical variables")
        if candidate.get("identity") != scoped["identity"]:
            raise ValueError("callback candidate crossed identity scope")
        if candidate.get("problem_sha256") != problem_fingerprint(charter):
            raise ValueError("callback candidate crossed problem scope")
        mandatory = set(charter["applicability"]["mandatory_checks"])
        checks = candidate.get("checks")
        if not isinstance(checks, dict) or set(checks) != mandatory:
            raise ValueError("callback omitted or invented mandatory checks")
        if any(not isinstance(row, dict) or row.get("state") not in STATES or not row.get("basis") for row in checks.values()):
            raise ValueError("callback checks require explicit state and basis")
        digest = candidate.get("definition_sha256")
        potential = _outcome(candidate, settings, False)["feasible_screen"]
        if digest is not None and (not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest)):
            raise ValueError("exact physical definition SHA256 required")
        if (previous is not None or potential) and digest is None:
            raise ValueError("eligible/native candidate must bind its physical definition SHA256")
        if previous is not None:
            for field in ("id", "definition_sha256"):
                if previous.get(field) is not None and candidate.get(field) != previous[field]:
                    raise ValueError("confirmation changed candidate physical identity: " + field)
        key = fingerprint(values)
        if candidate["id"] in seen_ids and seen_ids[candidate["id"]] != key:
            raise ValueError("candidate ID reused for another full variable assignment")
        # Reject non-JSON/nonfinite output instead of caching or ranking it.
        canonical(candidate)
        candidate = deepcopy(candidate)
        candidate["physical_release"] = False
        candidate["independently_accepted"] = False
        return candidate

    def attempt(values, phase, parent_id=None, previous=None):
        nonlocal spent, calls, hits, confirmations, stop, termination, in_flight
        if spent >= settings["evaluations"]:
            return None
        spent += 1
        if phase == "confirm":
            confirmations += 1
        value_key = fingerprint(values)
        key = fingerprint([namespace, phase, values, fingerprint(previous) if previous else None])
        event = dict(index=len(history), iteration=iterations, phase=phase, parent_id=parent_id,
                     variables=deepcopy(values), values_sha256=value_key, cache_hit=False,
                     policy_evaluations=spent)
        cached = key in cache
        if not cached:
            calls += 1
        in_flight = deepcopy(event)
        snapshot()  # Persist started work before a long native callback can be killed.
        try:
            if cached:
                entry = cache[key]
                if entry.get("schema") != "osr-recursive-search-cache/1" or entry.get("namespace") != namespace or entry.get("phase") != phase or entry.get("values_sha256") != value_key:
                    raise ValueError("cache entry does not match exact contextual source/tool/request scope")
                result = deepcopy(entry["candidate"]); hits += 1; event["cache_hit"] = True
            else:
                result = confirm(deepcopy(previous)) if phase == "confirm" else evaluate(deepcopy(values), phase, parent_id)
            candidate = validate(result, values, previous)
            if not event["cache_hit"]:
                cache[key] = dict(schema="osr-recursive-search-cache/1", namespace=namespace,
                                  phase=phase, values_sha256=value_key, candidate=deepcopy(candidate))
        except (RecursiveSearchStop, *stop_exceptions) as error:
            stop = dict(type=type(error).__name__, message=str(error))
            termination = error.reason if isinstance(error, RecursiveSearchStop) else "budget" if "budget" in type(error).__name__.lower() else "cancelled"
            event.update(stopped=True, error=deepcopy(stop)); history.append(event); in_flight = None; snapshot()
            return None
        except Exception as error:
            event["error"] = dict(type=type(error).__name__, message=str(error))
            candidate = deepcopy(previous) if previous else dict(schema="osr-design-candidate/1", id="failed-" + value_key, variables=deepcopy(values), identity=deepcopy(scoped["identity"]), problem_sha256=problem_fingerprint(charter), definition_sha256=None, evidence_state="failed", error=str(error), metrics={}, checks={key: dict(state="unknown", basis="evaluation did not return valid evidence") for key in charter["applicability"]["mandatory_checks"]})
            for name in (settings["native_checks"] if phase == "confirm" else settings["screening_checks"]):
                candidate["checks"][name] = dict(state="failed", basis="callback failed: " + str(error))
            candidate.update(evidence_state="failed", error=str(error), physical_release=False, independently_accepted=False)
        outcome = _outcome(candidate, settings, phase == "confirm")
        event.update(candidate_id=candidate["id"], result_sha256=fingerprint(candidate), outcome=deepcopy(outcome))
        history.append(event)
        in_flight = None
        seen_ids[candidate["id"]] = value_key
        old = nodes.get(value_key)
        nodes[value_key] = dict(candidate=candidate, outcome=outcome, depth=old["depth"] if old else 0, confirmation_attempted=phase=="confirm")
        if phase != "confirm" and outcome["feasible_screen"]:
            pending.append(value_key)
        snapshot()
        return nodes[value_key]

    def confirm_next():
        if pending and confirmations < settings["confirmations"] and spent < settings["evaluations"]:
            key = pending[0]
            node = nodes[key]
            attempt(node["candidate"]["variables"], "confirm", node["candidate"]["id"], node["candidate"])
            if termination is None:
                pending.pop(0)
            return True
        return False

    def fallback():
        nonlocal fallback_cursor
        while fallback_cursor < lattice_size:
            index = fallback_cursor; fallback_cursor += 1
            digits = {}
            for name in reversed(keys):
                index, offset = divmod(index, domains[name].size)
                digits[name] = domains[name].value(offset)
            value = {name: digits[name] for name in keys}
            if fingerprint(value) not in nodes:
                return value
        return None

    def next_proposal():
        # Exhaustive coverage changes stopping/space bounds, not feedback: native
        # outcomes still choose the next anchor before the unseen-space fallback.
        for node in sorted(nodes.values(), key=rank):
            while node["depth"] <= settings["refinements"]:
                base = node["candidate"]["variables"]
                for name in keys:
                    for value in domains[name].neighbours(base[name], node["depth"]):
                        proposal = {**base, name: value}
                        if fingerprint(proposal) not in nodes:
                            return proposal, node["candidate"]["id"]
                node["depth"] += 1
        return fallback(), min(nodes.values(), key=rank)["candidate"]["id"] if nodes else None

    for _, value in starts:
        if spent >= settings["evaluations"] or termination:
            break
        attempt(value, "screen")
        if not termination:
            confirm_next()
    while termination is None:
        if len(nodes) == lattice_size and (not pending or confirmations >= settings["confirmations"]):
            termination = "finite-space-exhausted"; break
        if spent >= settings["evaluations"]:
            termination = "budget"; break
        if iterations >= settings["iterations"]:
            termination = "budget"; stop = dict(type="iteration-limit", message="recursive round budget exhausted"); break
        # FIFO confirmation gives each newly eligible candidate the same opportunity.
        if confirm_next():
            if termination:
                break
        if spent >= settings["evaluations"]:
            termination = "budget"; break
        if len(nodes) == lattice_size:
            termination = "finite-space-exhausted"; break
        proposal, parent = next_proposal()
        if proposal is None:
            termination = "finite-space-exhausted" if len(nodes) == lattice_size else "stall"; break
        iterations += 1
        attempt(proposal, "screen", parent)
        if not termination:
            confirm_next()
        if termination:
            break
        progress = min((rank(node)[:2] for node in nodes.values()), default=None)
        if best_progress is None or progress < best_progress:
            best_progress = progress; stagnant = 0
        else:
            stagnant += 1
        snapshot()
        if not settings["finite_exhaustive"] and stagnant >= settings["stall_rounds"] and len(nodes) < lattice_size:
            termination = "stall"
    snapshot()
    return report()
