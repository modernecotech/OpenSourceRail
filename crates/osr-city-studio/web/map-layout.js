// Visual hit targets only. Surveyed station coordinates remain unchanged.
globalThis.OSRStationMarkerLayout = function stationMarkerLayout(points, separation = 24) {
  const placed = [];
  return points.map((point) => {
    let chosen;
    for (let ring = 0; ring <= 50 && !chosen; ring += 1) {
      const count = ring === 0 ? 1 : ring * 8;
      for (let i = 0; i < count; i += 1) {
        const angle = 2 * Math.PI * i / count;
        const x = point.x + Math.cos(angle) * ring * separation;
        const y = point.y + Math.sin(angle) * ring * separation;
        if (x < 12 || x > 988 || y < 12 || y > 608) continue;
        if (placed.every((p) => Math.hypot(p.x - x, p.y - y) >= separation - 1e-8)) {
          chosen = { id: point.id, x, y, sourceX: point.x, sourceY: point.y };
          break;
        }
      }
    }
    if (!chosen) throw new Error("Station display is too dense; use the station picker or a smaller scope.");
    placed.push(chosen);
    return chosen;
  });
};

// Collapse only declared cross-line complexes. Selecting a platform expands
// its own complex for editing without changing any physical coordinates.
globalThis.OSRJunctionMarkerLayout = function junctionMarkerLayout(points, selectedId = null) {
  const selected = points.find(point => point.id === selectedId);
  const groups = new Map();
  for (const point of points) {
    const grouped = point.junction_group !== undefined && point.junction_group !== null;
    const key = grouped ? `junction:${point.junction_group}` : `station:${point.id}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(point);
  }
  const symbols = [];
  for (const members of groups.values()) {
    const lines = [...new Set(members.map(point => point.line))];
    const expanded = selected && selected.junction_group !== undefined && selected.junction_group !== null
      && selected.junction_group === members[0].junction_group;
    if (lines.length < 2 || expanded) {
      symbols.push(...members.map(point => ({ ...point, memberIds: [point.id], lines: [point.line] })));
      continue;
    }
    const distanceSum = point => members.reduce((sum, other) => sum +
      (point.x - other.x) ** 2 + (point.y - other.y) ** 2, 0);
    const representative = [...members].sort((a, b) => distanceSum(a) - distanceSum(b)
      || a.id.localeCompare(b.id))[0];
    symbols.push({ ...representative, memberIds: members.map(point => point.id), lines });
  }
  return OSRStationMarkerLayout(symbols).map((marker, index) => ({ ...symbols[index], ...marker }));
};
