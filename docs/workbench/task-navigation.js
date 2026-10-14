// Pure task metadata shared by the shell and its acceptance tests.
export const AREAS = ["Plan", "Design", "Deliver", "Operate", "Maintain", "Assure"];
export function areaFor(modules, id) {
  return modules.find(row => row.id === id)?.group || "Plan";
}
export function validateNavigation(registry) {
  if (JSON.stringify(registry.task_areas) !== JSON.stringify(AREAS)) throw Error("Six controlled task areas required");
  const ids = new Set();
  for (const row of registry.modules) {
    if (ids.has(row.id) || !AREAS.includes(row.group) || !row.path.startsWith("/") || !["local", "erp", "fuxa"].includes(row.service)) throw Error("Invalid or duplicate task route");
    ids.add(row.id);
  }
  return registry;
}
