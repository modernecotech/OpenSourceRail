import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import vm from "node:vm";

const source = fs.readFileSync(new URL("../../docs/operations-portal/app.js", import.meta.url), "utf8");

function app(fetch) {
  const elements = new Map();
  const context = vm.createContext({
    URLSearchParams, Headers, fetch,
    window: { location: { search: "" }, addEventListener() {} },
    location: { pathname: "/operations", origin: "http://localhost" },
    document: {
      addEventListener() {},
      getElementById(id) {
        if (!elements.has(id)) elements.set(id, {});
        return elements.get(id);
      },
    },
    console: { error() {} },
  });
  vm.runInContext(source + `
    renderCore = () => {};
    renderCoreMetrics = () => {};
    state.coreStore = { mode: "sqlite", apiUrl: "/api/ops-core/test" };
    state.core = emptyCoreState();
    state.coreSave.pending = JSON.stringify(state.core);
    globalThis.appState = state;
  `, context);
  return context;
}

for (const status of [400, 401, 403, 409, 500]) {
  test(`HTTP ${status} retains an unsaved draft and server authority`, async () => {
    let calls = 0;
    const context = app(async () => {
      calls++;
      return { ok: false, status, json: async () => ({ error: "Review this rejection" }) };
    });
    await vm.runInContext("flushCoreSave()", context);
    assert.equal(context.appState.coreStore.mode, "sqlite");
    assert.equal(context.appState.coreStore.apiUrl, "/api/ops-core/test");
    assert.equal(context.appState.coreSave.blocked, true);
    assert.match(context.appState.coreSave.error, /Review this rejection/);
    assert.ok(context.appState.coreSave.pending);
    await vm.runInContext("saveCoreState()", context);
    assert.equal(calls, 1, "edits after a rejection must not trigger uncontrolled retries");
  });
}

test("queued edits use the newly committed revision", async () => {
  const requests = [];
  let releaseFirst;
  const context = app(async (_url, options) => {
    const body = JSON.parse(options.body);
    requests.push(body);
    if (requests.length === 1) await new Promise((resolve) => { releaseFirst = resolve; });
    return { ok: true, json: async () => ({ state: { ...body, _revision: body._revision + 1 } }) };
  });
  const first = vm.runInContext("flushCoreSave()", context);
  vm.runInContext('state.core.workOrders.push({ id: "WO-queued" }); saveCoreState()', context);
  releaseFirst();
  await first;
  // flushCoreSave schedules the queued save; drain its promise continuations.
  await new Promise((resolve) => setImmediate(resolve));
  assert.deepEqual(requests.map((row) => row._revision), [0, 1]);
  assert.equal(context.appState.core._revision, 2);
  assert.equal(context.appState.core.workOrders[0].id, "WO-queued");
});

test("a connection failure does not accept the draft locally", async () => {
  const context = app(async () => { throw new Error("connection lost"); });
  await vm.runInContext("flushCoreSave()", context);
  assert.equal(context.appState.coreStore.mode, "sqlite");
  assert.equal(context.appState.coreSave.blocked, true);
  assert.match(context.appState.coreSave.error, /connection lost/);
});

test("latest signed outcome is independent of array order", () => {
  const context = app(async () => {});
  vm.runInContext(`state.core.inspections = [
    { id: "old-pass", wo_id: "WO", result: "pass", server_sequence: 1, signature: {} },
    { id: "new-fail", wo_id: "WO", result: "fail", server_sequence: 2, signature: {} }
  ]`, context);
  assert.equal(vm.runInContext('latestPassingInspection("WO")', context), null);
});
