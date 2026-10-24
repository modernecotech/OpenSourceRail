// Real headless Chromium; Linux device isolation avoids host GPU-driver probes.
import {chromium} from '@playwright/test';
import {spawnSync} from 'node:child_process';
import {mkdtemp,mkdir,writeFile,chmod,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';

const quote=value=>"'"+value.replaceAll("'","'\\''")+"'";
export async function launchBrowser(options={}){
 const args=[...(options.args||[]),'--disable-gpu','--disable-gpu-compositing','--disable-features=Vulkan'];
 let directory,executablePath,mode='software-requested',hidden=false;
 if(process.platform==='linux'&&spawnSync('bwrap',['--version'],{timeout:5000}).status===0){
  // A private minimal /dev prevents even GPU-information ioctls. The host
  // filesystem is read-only; Chromium's temporary profile remains writable.
  const probe=spawnSync('bwrap',['--ro-bind','/','/','--dev','/dev','--bind','/tmp','/tmp','--','/usr/bin/test','!','-e','/dev/dri'],{timeout:10000});
  if(probe.status!==0)throw Error('Browser device isolation could not be verified');
  directory=await mkdtemp(join(tmpdir(),'osr-browser-'));executablePath=join(directory,'chromium');
  await mkdir(join(directory,'config'));await mkdir(join(directory,'cache'));
  await writeFile(executablePath,'#!/bin/sh\nexec bwrap --die-with-parent --ro-bind / / --dev /dev --bind /tmp /tmp --setenv XDG_CONFIG_HOME '+quote(join(directory,'config'))+' --setenv XDG_CACHE_HOME '+quote(join(directory,'cache'))+' -- '+quote(chromium.executablePath())+' "$@"\n');
  await chmod(executablePath,0o700);mode='device-isolated-software';hidden=true;
 }
 try{
  const browser=await chromium.launch({...options,headless:true,args,...(executablePath?{executablePath}:{})});
  browser.osrRendering={mode,hardware_graphics_devices_hidden:hidden,browser_version:browser.version(),node_version:process.versions.node};
  if(directory){const close=browser.close.bind(browser);browser.close=async(...values)=>{try{return await close(...values);}finally{await rm(directory,{recursive:true,force:true});}};}
  return browser;
 }catch(error){if(directory)await rm(directory,{recursive:true,force:true});throw error;}
}
