window.osr_open_lifecycle = function(context) {
  const allowed = frappe.boot.osr_workbench_origins || ['http://127.0.0.1:8090','http://localhost:8090','http://127.0.0.1:4177'];
  let parentOrigin;
  try { parentOrigin = new URL(document.referrer).origin; } catch {}
  if (parent !== window && allowed.includes(parentOrigin)) {
    parent.postMessage({type:'osr:navigate',module:'lifecycle',context},parentOrigin);
  } else {
    window.open(allowed[0]+'/?'+new URLSearchParams({module:'lifecycle',...context}),'_blank','noopener');
  }
};
