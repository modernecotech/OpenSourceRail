// Only the containing Workbench can consume these same-origin navigation requests.
if (window.parent !== window) {
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const url = new URL(link.href);
    if (url.origin !== location.origin && !url.pathname.startsWith('/app/') && !url.pathname.startsWith('/home')) return;
    if (url.origin === location.origin && !['/docs/operating/', '/docs/operations-portal/'].some(p => url.pathname.startsWith(p))) return;
    event.preventDefault();
    parent.postMessage({type:'osr:open-link',url:url.href},location.origin);
  });
}
