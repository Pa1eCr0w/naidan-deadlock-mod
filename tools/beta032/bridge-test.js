// Logic simulation only. Does not validate engine rendering or image correctness.
const fs=require('fs'), vm=require('vm'), assert=require('assert');
const source=fs.readFileSync(process.argv[2],'utf8');
const report={status:'PASS',engine:'UNVERIFIED',visual:'UNVERIFIED',cases:[]};
for(const available of [[],['hero_baba'],['hero_atlas'],['hero_baba','hero_atlas']]) {
 try {
  let hero='hero_atlas', active=false, valid=true, queued, mode='normal', count=0;
  const children=[];
  const ancestor={BHasClass:n=>n===hero,GetParent:()=>null};
  const host={RemoveAndDeleteChildren:()=>{children.length=0}};
  const root={IsValid:()=>valid,BHasClass:()=>false,GetParent:()=>ancestor,FindChildInLayoutFile:()=>host,RemoveClass:()=>{active=false},AddClass:()=>{active=true}};
  const api={GetContextPanel:()=>root,Schedule:(t,fn)=>{queued=fn},CreatePanel:(type,parent,id)=>{
   assert.equal(parent,host); let loaded=null,used=false;count++;
   const panel={BLoadLayout:path=>{
    assert(!used,'Panel reused across hero transitions');used=true;
    if(mode==='throw')throw Error('simulated load exception');
    const key=path.split('/').pop().replace('.xml','');loaded=available.includes(key)?key:null;return !!loaded;
   },FindChildInLayoutFile:()=>loaded&&mode!=='missing-marker'?{}:null};children.push(panel);return panel;
  }};
  vm.runInNewContext(source,{$:api});
  for(const next of ['hero_lash','hero_fencer','hero_synth','hero_atlas','hero_baba','hero_atlas']) {
   hero=next;queued();assert.equal(active,available.includes(hero));assert(children.length<=1);
   const before=count;queued();assert.equal(count,before,'Unchanged hero reloaded');
  }
  mode='missing-marker';hero='hero_baba';queued();assert(!active);
  mode='throw';hero='hero_atlas';queued();assert(!active);
  hero='hero_unknown_future';queued();assert(!active);
  const callback=queued;queued=null;valid=false;callback();assert.equal(queued,null,'Invalid root rescheduled');
  report.cases.push({extensions:available,status:'PASS',createdPanels:count});
 } catch(error) {report.status='FAIL';report.cases.push({extensions:available,status:'FAIL',error:String(error)});}
}
console.log(JSON.stringify(report,null,2));process.exitCode=report.status==='PASS'?0:1;
