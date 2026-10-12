const CACHE='osr-field-shell-v1';
const ROOT=new URL('./',self.location.href).pathname;
const FILES=['index.html','app.js','style.css'].map(name=>ROOT+name);
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(FILES)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('fetch',event=>{
  const url=new URL(event.request.url);
  // Never cache API results, authorization headers, credentials or ERP pages.
  if(event.request.method!=='GET'||url.origin!==self.location.origin)return;
  const path=url.pathname===ROOT?ROOT+'index.html':url.pathname;
  if(!FILES.includes(path))return;
  event.respondWith(fetch(event.request).catch(()=>caches.open(CACHE).then(cache=>cache.match(path))));
});
