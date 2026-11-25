// Component-level tests with a minimal DOM double; no browser automation.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const model=JSON.parse(fs.readFileSync(path.join(root,'results/high-level-connections/dimensions-levels/high-level-dimensions-levels-sankey.json'),'utf8'));
const html=fs.readFileSync(path.join(root,'scripts/templates/high_level_sankey.html'),'utf8');
const code=html.slice(html.indexOf('  const tooltip='),html.indexOf('  function paint('));
assert(code.includes('function showNode')&&code.includes('function nodeDetails'));
class Element {
  constructor(){this.children=[];this.style={};this.textContent='';this.offsetWidth=440;this.offsetHeight=240;this.hidden=false}
  append(...children){this.children.push(...children)}
  replaceChildren(...children){this.children=[...children]}
  setAttribute(key,value){this[key]=value}
}
const handlers={},details=new Element(),selected=new Element();
const context={model,innerWidth:1200,innerHeight:800,details,paint:()=>{},report:()=>{},sourceHref:x=>x,
  document:{body:new Element(),createElement:()=>new Element(),addEventListener:(name,fn)=>handlers[name]=fn,getElementById:()=>selected},
  add:(tag,value,parent=details)=>{const e=new Element();e.tag=tag;e.textContent=value;parent.append(e);return e}};
vm.createContext(context);vm.runInContext(code,context);
const evaluate=script=>vm.runInContext(script,context);
let count=0;
for(const node of model.nodes.filter(n=>n.comment)){
  context.nodeID=node.id;
  evaluate('showNode(nodeID,{clientX:1180,clientY:790})');
  assert.equal(evaluate('tooltip.hidden'),false);
  assert.equal(evaluate('tooltip.children[1].textContent'),node.comment);
  assert.equal(evaluate('tooltip.style.left'),'748px');assert.equal(evaluate('tooltip.style.top'),'548px');
  evaluate('hideNode()');assert.equal(evaluate('tooltip.hidden'),true);
  evaluate('showNode(nodeID,{currentTarget:{getBoundingClientRect:()=>({right:100,top:50})}})');
  assert.equal(evaluate('tooltip.style.left'),'116px');assert.equal(evaluate('tooltip.hidden'),false);
  evaluate('nodeDetails(nodeID)');assert(details.children.some(e=>e.tag==='p'&&e.textContent===node.comment));
  handlers.keydown({key:'Escape'});assert.equal(evaluate('tooltip.hidden'),true);
  count++;
}
assert.equal(count,42);
evaluate("showNode('urn:fair-dama-fairmm:alignment:D7',{})");assert.equal(evaluate('tooltip.hidden'),true);
console.log(`Passed hover, focus-anchor, dismissal, viewport and selection component checks for ${count} RDF descriptor comments.`);
