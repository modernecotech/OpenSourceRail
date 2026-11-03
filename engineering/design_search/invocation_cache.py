"""Bounded in-memory reuse populated only by this invocation's computations.

Nothing is loaded from persisted evidence. Callers must supply the complete
semantic input and an epoch guard that checks current sources and runtime. This
is cooperative consistency checking, not authentication or an OS sandbox.
"""
from collections import OrderedDict
from copy import deepcopy
import json

from engineering.station_rail.common import encoded, identity

PRODUCER = "engineering/design_search/invocation_cache.py"
KINDS = ("axial-assessment",)


class InvocationCache:
    def __init__(self, guard, *, enabled=True, maximum_entries=64, maximum_bytes=16*1024**2):
        if type(enabled) is not bool:
            raise ValueError("Explicit invocation reuse policy required")
        if (type(maximum_entries) is not int or not 1 <= maximum_entries <= 64
                or type(maximum_bytes) is not int or not 1 <= maximum_bytes <= 16*1024**2):
            raise ValueError("Bounded invocation cache resources required")
        self._guard = guard
        self._context = identity(guard())
        self._enabled = enabled
        self._maximum_entries = maximum_entries
        self._maximum_bytes = maximum_bytes
        self._entries = OrderedDict()
        self._bytes = self._peak_bytes = 0
        self._counts = {kind:dict(computations=0,reused=0,failed=0,oversize=0,evicted=0) for kind in KINDS}

    def _check(self):
        if identity(self._guard()) != self._context:
            raise RuntimeError("Invocation source/runtime context changed")

    def evaluate(self, kind, inputs, compute):
        if kind not in KINDS:
            raise ValueError("Explicit invocation evaluation kind required")
        self._check()
        key = (kind, identity(inputs))
        counts = self._counts[kind]
        if self._enabled and key in self._entries:
            raw = self._entries.pop(key)
            self._entries[key] = raw
            value = json.loads(raw)
            self._check()
            counts["reused"] += 1
            return value
        counts["computations"] += 1
        try:
            value = compute()
            raw = encoded(value)
            self._check()
        except Exception:
            counts["failed"] += 1
            raise
        if self._enabled:
            if len(raw) > self._maximum_bytes:
                counts["oversize"] += 1
            else:
                while self._entries and (len(self._entries) >= self._maximum_entries
                        or self._bytes + len(raw) > self._maximum_bytes):
                    old_key, old_raw = self._entries.popitem(last=False)
                    self._bytes -= len(old_raw)
                    self._counts[old_key[0]]["evicted"] += 1
                self._entries[key] = raw
                self._bytes += len(raw)
                self._peak_bytes = max(self._peak_bytes,self._bytes)
        # Canonical JSON copies protect both first and reused callers from aliases.
        return json.loads(raw)

    def statistics(self):
        return dict(enabled=self._enabled, scope="fresh-computations-in-this-invocation-only",
            context_id=self._context, counts=deepcopy(self._counts), entries=len(self._entries),
            retained_bytes=self._bytes, peak_retained_bytes=self._peak_bytes,
            maximum_entries=self._maximum_entries, maximum_bytes=self._maximum_bytes,
            persisted_evidence_loaded=False, native_solver_results_cached=False)
