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
