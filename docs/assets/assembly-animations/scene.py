"""Geometry and shot descriptions for the CAD assembly films."""

from dataclasses import dataclass
from functools import cached_property

import numpy as np


@dataclass(eq=False)
class Mesh:
    name: str
    vertices: np.ndarray
    faces: tuple

    @cached_property
    def bounds(self):
        return self.vertices.min(axis=0), self.vertices.max(axis=0)

    @cached_property
    def face_groups(self):
        groups = {}
        for face in self.faces:
            groups.setdefault(len(face), []).append(face)
        return [np.asarray(faces) for faces in groups.values()]


def box(name, lower, upper):
    x, y, z = lower
    x2, y2, z2 = upper
    vertices = np.array(((x, y, z), (x2, y, z), (x2, y2, z), (x, y2, z),
                         (x, y, z2), (x2, y, z2), (x2, y2, z2), (x, y2, z2)), dtype=float)
    faces = ((0, 3, 2, 1), (0, 1, 5, 4), (1, 2, 6, 5),
             (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7))
    return Mesh(name, vertices, faces)


def load_obj(data):
    """Load named OBJ objects and retain their original polygon faces."""
    vertices = []
    groups = {}
    name = "default"
    for line in data.splitlines():
        fields = line.split()
        if not fields:
            continue
        kind, *values = fields
        if kind == "v":
            vertices.append(tuple(float(value) for value in values[:3]))
        elif kind == "o":
            name = " ".join(values)
            if name in groups:
                raise ValueError(f"Repeated OBJ object {name}")
            groups[name] = []
        elif kind == "f":
            indices = [int(field.split("/")[0]) for field in values]
            groups.setdefault(name, []).append(
                tuple(index - 1 if index > 0 else len(vertices) + index for index in indices))
    meshes = {}
    for label, faces in groups.items():
        if not faces:
            continue
        indices = sorted({index for face in faces for index in face})
        mapping = {index: local for local, index in enumerate(indices)}
        meshes[label] = Mesh(label, np.asarray([vertices[index] for index in indices], dtype=float),
                             tuple(tuple(mapping[index] for index in face) for face in faces))
    if not meshes:
        raise ValueError("OBJ has no polygon geometry")
    return meshes


def combine(name, meshes):
    vertices, faces = [], []
    start = 0
    for mesh in meshes:
        vertices.append(mesh.vertices)
        faces.extend(tuple(index + start for index in face) for face in mesh.faces)
        start += len(mesh.vertices)
    return Mesh(name, np.concatenate(vertices), tuple(faces))


@dataclass(frozen=True)
class Item:
    mesh: Mesh
    color: str
    offset: tuple = (0, 0, 0)
    scale: tuple = (1, 1, 1)
    pivot: tuple = (0, 0, 0)
    yaw: float = 0
    outline: bool = True
    layer: int = 0


@dataclass(frozen=True)
class Camera:
    target: tuple
    yaw: float
    elevation: float
    width: float


@dataclass(frozen=True)
class Frame:
    camera: Camera
    items: list
    title: str
    caption: str
    tags: tuple = ()
