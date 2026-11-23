"""Quasi-static two-track sectional DC network reduced to moving train ports.

The longitudinal positive and return resistances are in series in a loop.
A branch common to two ports contributes to both impedance matrix entries.
An ideal non-reversible rectifier supplies positive current. Regeneration is
limited by demand and dissipated locally if the section cannot accept it.
"""

from bisect import bisect_right
from dataclasses import dataclass


@dataclass(frozen=True)
class Feeder:
    name: str
    sites: tuple
    droop: float
    outward: float
    return_path: float
    paths: int
    trunk_factor: float = 1.0

    def circuit(self, condition, failed_site=None, failed_path=None):
        hot = condition != "normal"
        stress = condition == "combined"
        hot_factor = (1.10 if hot else 1.0) * (1.05 if stress else 1.0)
        site = failed_site if condition in ("site_out", "combined") else None
        path = failed_path if condition in ("path_out", "combined") else None
        live = tuple((i, x) for i, x in enumerate(self.sites) if i != site)
        # A failed interior bus isolates the two restored radial halves. An
        # end outage extends the adjacent source to the line boundary.
        cuts = tuple(
            self.sites[a + 1] if b > a + 1 else (x + y) / 2
            for (a, x), (b, y) in zip(live, live[1:])
        )
        return Circuit(live, cuts, 1485.0 if stress else 1500.0,
                       hot_factor * self.droop,
                       hot_factor * (self.outward + self.return_path) * self.trunk_factor / 1000,
                       .001 * (1.05 if stress else 1) if self.paths == 2 else 0,
                       self.paths, path, self.sites)


@dataclass(frozen=True)
class Circuit:
    live: tuple
    cuts_m: tuple
    source_v: float
    source_ohm: float
    loop_ohm_m: float
    contact_ohm: float
    paths: int
    failed_path: int | None
    sites_m: tuple

    def port(self, position_m, track):
        site, origin = self.live[bisect_right(self.cuts_m, position_m)]
        branch = (track, position_m >= origin)
        distance = abs(position_m - origin)
        outage_overlap = 0.0
        if self.failed_path is not None:
            lo, hi = self.sites_m[self.failed_path:self.failed_path + 2]
            outage_overlap = max(0.0, min(max(position_m, origin), hi) - max(min(position_m, origin), lo))
            if outage_overlap > 0 and self.paths == 1:
                return None
        line = self.loop_ohm_m * (distance / self.paths + outage_overlap / 2)
        return site, branch, line


def loadflow(circuit, ports, requests_w, current_a):
    """Solve nonlinear moving constant-power loads with voltage/current control.

    Explicit limits smooth constant-power collapse below the planning floor.
    A damped current-injection iteration closes the full port voltage equations.
    Returns collector voltage, port W, source current, network loss and residual.
    """
    size = len(ports)
    if not size:
        return [], [], 0.0, 0.0, 0.0, 0.0
    source = circuit.source_v
    resistance = [
        [circuit.source_ohm + (min(a[2], b[2]) if a[1] == b[1] else 0)
         + (circuit.contact_ohm if i == j else 0)
         for j, b in enumerate(ports)]
        for i, a in enumerate(ports)
    ]
    voltage = [source] * size
    injections = [0.0] * size
    for iteration in range(48):
        draw = sink = 0.0
        for j, (v, w) in enumerate(zip(voltage, requests_w)):
            if w >= 0:
                injections[j] = min(w / max(1., v), current_a * max(0., min(1., (v - 1050.) / 300.)))
                draw += injections[j]
            else:
                injections[j] = max(w / max(v, 1.), -current_a) * max(0., min(1., (1650. - v) / 150.))
                sink -= injections[j]
        if sink > draw:
            injections = [i * draw / sink if i < 0 else i for i in injections]
        solved = [source - sum(r * a for r, a in zip(row, injections)) for row in resistance]
        residual = max(abs(old - new) for old, new in zip(voltage, solved))
        if residual < .01:
            break
        damping = .28 if iteration >= 10 or min(solved) < 1350 else .81
        voltage = [v + damping * (s - v) for v, s in zip(voltage, solved)]
    power = [v * i for v, i in zip(solved, injections)]
    supplied = max(0., sum(injections))
    loss = sum(a * sum(r * b for r, b in zip(row, injections))
               for a, row in zip(injections, resistance))
    # A branch peak is the signed sum on the first segment or on a downstream
    # segment between train taps. Rating enquiry assumes no paired current split.
    branch_peak = max(
        abs(sum(other_i for other, other_i in zip(ports, injections)
                if other[1] == port[1] and other[2] >= port[2]))
        for port in ports
    )
    return solved, power, supplied, loss, residual, branch_peak
