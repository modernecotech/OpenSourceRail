"""Bounded dependency graph and selective source-impact queries."""

from __future__ import annotations
from collections import defaultdict, deque
import json
from pathlib import Path

from .registry import ROOT, problems, dependencies


def validate(graph):
    nodes = {r["id"]: r for r in graph["nodes"]}
    if len(nodes) != len(graph["nodes"]) or not 0 < len(nodes) <= 20000:
        raise ValueError("unique bounded dependency nodes required")
    degree = {key: 0 for key in nodes}
    following = defaultdict(set)
    for node in nodes.values():
        if len(node["depends_on"]) != len(set(node["depends_on"])):
            raise ValueError("duplicate dependency edge")
        for parent in node["depends_on"]:
            if parent not in nodes or parent == node["id"]:
                raise ValueError("unknown/self dependency")
            degree[node["id"]] += 1
            following[parent].add(node["id"])
    ready = deque(k for k, n in degree.items() if n == 0)
    visited = []
    while ready:
        key = ready.popleft()
        visited.append(key)
        for child in following[key]:
            degree[child] -= 1
            if degree[child] == 0:
                ready.append(child)
    if len(visited) != len(nodes):
        raise ValueError("dependency graph contains a lineage/publication cycle")
    return graph


def build():
    nodes = {}
    for identifier, charter in problems().items():
        sources = dependencies(charter["adapter"])
        for path, digest in sources.items():
            nodes["source:" + path] = dict(
                id="source:" + path,
                kind="source",
                path=path,
                sha256=digest,
                depends_on=[],
            )
        key = "problem:" + identifier
        nodes[key] = dict(
            id=key, kind="design-problem", depends_on=["source:" + p for p in sources]
        )
    manifest = json.loads(
        (ROOT / "engineering/industrialisation/manifest.json").read_text()
    )
    for path, digest in manifest["sources_sha256"].items():
        nodes["source:" + path] = dict(
            id="source:" + path, kind="source", path=path, sha256=digest, depends_on=[]
        )
    nodes["publication:industrialisation"] = dict(
        id="publication:industrialisation",
        kind="atomic-publication",
        depends_on=["source:" + p for p in manifest["sources_sha256"]],
        closure=[
            "engineering/industrialisation/" + p
            for p in [*manifest["outputs_sha256"], "manifest.json"]
        ],
    )
    return validate(
        dict(
            schema="osr-design-dependency-graph/1",
            nodes=list(nodes.values()),
            physical_release=False,
        )
    )


def affected(graph, paths):
    validate(graph)
    parents = defaultdict(list)
    for node in graph["nodes"]:
        for dependency in node["depends_on"]:
            parents[dependency].append(node["id"])
    todo = deque("source:" + p for p in paths)
    visited = set()
    while todo:
        node = todo.popleft()
        if node in visited:
            continue
        visited.add(node)
        todo.extend(parents[node])
    return sorted(n for n in visited if not n.startswith("source:"))
