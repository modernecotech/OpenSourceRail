"""Typed rigid frames for bounded powered-bogie fit studies (SI units)."""
from dataclasses import dataclass
from math import cos, sin


@dataclass(frozen=True)
class Transform:
    """Rigid transform mapping child coordinates into the named parent frame."""
    parent: str
    child: str
    matrix: tuple

    def apply(self, point):
        if len(point) != 3:
            raise ValueError("point must contain x,y,z")
        m = self.matrix
        return tuple(sum(m[i][j] * point[j] for j in range(3)) + m[i][3]
                     for i in range(3))


def compose(a: Transform, b: Transform) -> Transform:
    """Return a<-c from a<-b and b<-c; reject untyped/misordered frames."""
    if a.child != b.parent:
        raise ValueError(f"frame mismatch: {a.child} != {b.parent}")
    x, y = a.matrix, b.matrix
    r = tuple(tuple(sum(x[i][k] * y[k][j] for k in range(3)) for j in range(3))
              for i in range(3))
    t = tuple(sum(x[i][k] * y[k][3] for k in range(3)) + x[i][3]
              for i in range(3))
    return Transform(a.parent, b.child, tuple(tuple(r[i][j] for j in range(3)) + (t[i],)
                                               for i in range(3)))


def rigid(parent, child, translation=(0., 0., 0.), yaw=0., roll=0.):
    """Z-up rotation Rz(yaw)Rx(roll), then child origin translation."""
    cy, sy, cr, sr = cos(yaw), sin(yaw), cos(roll), sin(roll)
    r = ((cy, -sy*cr, sy*sr), (sy, cy*cr, -cy*sr), (0., sr, cr))
    return Transform(parent, child, tuple(tuple(r[i][j] for j in range(3)) +
                                           (translation[i],) for i in range(3)))


def canonical_frames(origin=(0., 0., 0.), yaw=0., roll=0., primary=0., secondary=0.,
                     gear_roll=0., lateral=0.):
    """Track/contact -> wheelset -> gear; wheelset/primary -> bogie -> body."""
    track_wheelset = rigid("track/contact", "wheelset", (origin[0], origin[1],
        origin[2]), yaw, roll)
    wheelset_gear = rigid("wheelset", "gear", (-1.05, 0., 0.), 0., gear_roll)
    wheelset_bogie = rigid("wheelset", "bogie-frame", (0., lateral, primary))
    bogie_body = rigid("bogie-frame", "body", (0., 0., secondary))
    return {"track_to_wheelset": track_wheelset,
            "track_to_gear": compose(track_wheelset, wheelset_gear),
            "track_to_bogie": compose(track_wheelset, wheelset_bogie),
            "track_to_body": compose(compose(track_wheelset, wheelset_bogie), bogie_body)}
