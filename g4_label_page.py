r"""
g4_label_page.py - make a labelling web page (one tile at a time, click or press a key).

Run from the project folder (the one that contains the 'data' folder):

  Annotator A (sees the map's first guess):
    python g4_label_page.py --csv data\labelling\annotate_A.csv --mode A --out label_A.html
  Annotator B (blind: no first guess, no group):
    python g4_label_page.py --csv data\labelling\annotate_B_blind.csv --mode B --out label_B.html

Then double-click the .html file. Tiles are read from data\tiles_<REGION>\tiles\ next to it.
Keys: 1 Forest  2 Residential  3 Industrial  4 River  5 SeaLake  6 AnnualCrop
      7 HerbaceousVegetation  8 unsure  0 clear   Left/Right arrows move   Progress is saved in the browser.
Click 'Export CSV' when done: it downloads the CSV with the label column filled in.
"""
import argparse
import json
from pathlib import Path

import pandas as pd

TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tile labelling __MODE__</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#1c2430;--mute:#667085;--line:#d9dee5;--acc:#1f6feb}
@media (prefers-color-scheme:dark){:root{--bg:#12161c;--card:#1b222b;--ink:#e8edf3;--mute:#98a2b3;--line:#303a47;--acc:#5b9dff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,Segoe UI,Roboto,sans-serif}
header{display:flex;gap:12px;align-items:center;flex-wrap:wrap;padding:12px 20px;border-bottom:1px solid var(--line);background:var(--card)}
header h1{font-size:16px;margin:0;font-weight:650}
.pill{padding:2px 10px;border-radius:99px;background:var(--bg);border:1px solid var(--line);color:var(--mute);font-size:13px}
.bar{flex:1;min-width:120px;height:8px;background:var(--line);border-radius:9px;overflow:hidden}.bar>i{display:block;height:100%;background:var(--acc);width:0}
main{display:grid;grid-template-columns:minmax(300px,420px) 1fr;gap:20px;padding:20px;max-width:1100px;margin:0 auto}
@media(max-width:760px){main{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
#img{width:100%;aspect-ratio:1;object-fit:contain;background:#000;border-radius:8px;image-rendering:auto;display:block}
.meta{display:flex;justify-content:space-between;color:var(--mute);font-size:13px;margin-top:8px;gap:8px;flex-wrap:wrap}
.hint{margin-top:10px;padding:8px 10px;border-radius:8px;background:var(--bg);border:1px dashed var(--line);font-size:14px}
.btns{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}
.btns button{display:flex;align-items:center;gap:8px;padding:10px 12px;border:1px solid var(--line);border-radius:9px;background:var(--card);color:var(--ink);font:inherit;cursor:pointer;text-align:left}
.btns button:hover{border-color:var(--acc)}.btns button.on{outline:2px solid var(--acc);background:var(--bg)}
.btns kbd{font:600 12px ui-monospace,monospace;border:1px solid var(--line);border-radius:5px;padding:1px 6px;color:var(--mute)}
.dot{width:12px;height:12px;border-radius:50%;flex:none}
.nav{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}
.nav button,.top button{padding:8px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink);font:inherit;cursor:pointer}
.nav button:hover,.top button:hover{border-color:var(--acc)}
.top{display:flex;gap:8px;flex-wrap:wrap}
.primary{background:var(--acc)!important;color:#fff!important;border-color:var(--acc)!important}
details{margin-top:14px;font-size:14px}summary{cursor:pointer;color:var(--mute)}
details p{margin:6px 0}
#grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(52px,1fr));gap:4px;margin-top:10px}
#grid img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:4px;border:3px solid var(--line);cursor:pointer;display:block}
#grid img.cur{outline:2px solid var(--acc);outline-offset:1px}
.ctx{display:grid;grid-template-columns:repeat(3,1fr);gap:3px;margin-top:10px}
.ctx div{aspect-ratio:1;background:repeating-linear-gradient(45deg,var(--line),var(--line) 4px,transparent 4px,transparent 8px);border-radius:4px;overflow:hidden;position:relative}
.ctx img{width:100%;height:100%;object-fit:cover;display:block}
.ctx div.me{outline:3px solid var(--acc);outline-offset:-3px;z-index:1}
.ctxnote{font-size:12px;color:var(--mute);margin-top:6px}
.leg{display:flex;flex-wrap:wrap;gap:10px;font-size:12px;color:var(--mute);margin-top:8px}.leg span{display:flex;gap:5px;align-items:center}
</style></head><body>
<header>
 <h1>Tile labelling - annotator __MODE__</h1><span class="pill" id="count"></span><div class="bar"><i id="fill"></i></div>
 <div class="top"><button id="jump">Next unlabelled</button><button class="primary" id="export">Export CSV</button></div>
</header>
<main>
 <section class="card">
  <img id="img" alt="tile">
  <div class="meta"><span id="pos"></span><span id="name"></span></div>
  <div class="hint" id="hint" hidden></div>
  <div style="margin-top:12px"><b>Context</b> <span class="pill">tile and its 8 neighbours</span></div>
  <div class="ctx" id="ctx"></div>
  <div class="ctxnote">Striped squares have no tile: dropped for cloud or no-data, or the edge of the scene. Water that continues as a thin line = river; water that opens out = sea or lake.</div>
 </section>
 <section>
  <div class="card">
   <div class="btns" id="btns"></div>
   <div class="nav"><button id="prev">&larr; Back</button><button id="next">Next &rarr;</button><button id="clear">Clear (0)</button></div>
   <details><summary>Class guide</summary>
    <p><b>Forest</b>: dense dark-green, lumpy, no straight edges.</p>
    <p><b>Residential</b>: many small roofs, streets, yards.</p>
    <p><b>Industrial</b>: a few very large roofs, big paved yards, ports.</p>
    <p><b>River</b>: a visible channel crossing the tile (not open sea).</p>
    <p><b>SeaLake</b>: tile mostly open water, flat colour. Fishponds too.</p>
    <p><b>AnnualCrop</b>: neat rectangles of fields with sharp edges.</p>
    <p><b>HerbaceousVegetation</b>: grass, shrubs, brown or green scrub, grazing land (Pasture counts here). Smooth, no field edges, few or scattered trees.</p>
    <p><b>unsure</b>: cloud, haze, a mix, or no decision in ~5 seconds.</p>
    <p>More than half the tile = that class. Otherwise unsure.</p>
   </details>
  </div>
  <div class="card" style="margin-top:14px"><b>Overview</b> <span class="pill">click a tile to jump</span>
   <div class="leg" id="leg"></div><div id="grid"></div></div>
 </section>
</main>
<script>
const MODE="__MODE__";
const ROWS=__DATA__;
const COLS=__COLS__;
const CLASSES=["Forest","Residential","Industrial","River","SeaLake","AnnualCrop","HerbaceousVegetation","unsure"];
const COLORS={Forest:"#2e7d32",Residential:"#e67e22",Industrial:"#8e44ad",River:"#1e88e5",SeaLake:"#00acc1",AnnualCrop:"#c0a000",HerbaceousVegetation:"#9bbb3b",unsure:"#888"};
const HINTS={GrassScrub:"HerbaceousVegetation (grass/scrub)?",Forest:"Forest",AnnualCrop:"AnnualCrop",OpenWater:"SeaLake",BuiltUp:"Residential or Industrial?",NarrowWater:"River?"};
const KEY="g4label_"+MODE+"_"+ROWS.length+"_"+ROWS[0].tile_file;
let labels={};ROWS.forEach(r=>{if(r.label)labels[r.tile_file]=r.label});
try{Object.assign(labels,JSON.parse(localStorage.getItem(KEY)||"{}"))}catch(e){}
let idx=0;
const $=id=>document.getElementById(id);
function save(){try{localStorage.setItem(KEY,JSON.stringify(labels))}catch(e){}}
function done(){return ROWS.filter(r=>labels[r.tile_file]).length}
function nb(r,dr,dc){
 const m=/^(.*)_r(\d{5})_c(\d{5})\.png$/.exec(r.tile_file);if(!m)return null;
 const rr=+m[2]+64*dr,cc=+m[3]+64*dc;if(rr<0||cc<0)return null;
 const f=m[1]+"_r"+String(rr).padStart(5,"0")+"_c"+String(cc).padStart(5,"0")+".png";
 return r.src.slice(0,r.src.lastIndexOf("/")+1)+f}
function ctx(r){
 const box=$("ctx");box.innerHTML="";
 for(let dr=-1;dr<=1;dr++)for(let dc=-1;dc<=1;dc++){
  const d=document.createElement("div");if(!dr&&!dc)d.className="me";
  const u=(!dr&&!dc)?r.src:nb(r,dr,dc);
  if(u){const i=document.createElement("img");i.src=u;i.onerror=()=>i.remove();d.appendChild(i)}
  box.appendChild(d)}}
function render(){
 const r=ROWS[idx];$("img").src=r.src;ctx(r);$("pos").textContent="Tile "+(idx+1)+" of "+ROWS.length;$("name").textContent=r.tile_file;
 const h=$("hint");
 if(MODE==="A"&&r.group){h.hidden=false;h.textContent="Map first guess: "+(HINTS[r.group]||r.group)+"  (the map is only a hint: check the picture)"}else h.hidden=true;
 document.querySelectorAll("#btns button").forEach(b=>b.classList.toggle("on",b.dataset.c===labels[r.tile_file]));
 const d=done();$("count").textContent=d+" / "+ROWS.length+" labelled";$("fill").style.width=(100*d/ROWS.length)+"%";
 document.querySelectorAll("#grid img").forEach((g,i)=>{const l=labels[ROWS[i].tile_file];g.style.borderColor=l?COLORS[l]:"var(--line)";g.classList.toggle("cur",i===idx)});
}
function setLabel(c){const f=ROWS[idx].tile_file;if(c)labels[f]=c;else delete labels[f];save();if(c&&idx<ROWS.length-1)idx++;render()}
function go(i){idx=Math.max(0,Math.min(ROWS.length-1,i));render()}
CLASSES.forEach((c,i)=>{const b=document.createElement("button");b.dataset.c=c;b.innerHTML='<i class="dot" style="background:'+COLORS[c]+'"></i>'+c+' <kbd>'+(i+1)+'</kbd>';b.onclick=()=>setLabel(c);$("btns").appendChild(b);
 const s=document.createElement("span");s.innerHTML='<i class="dot" style="background:'+COLORS[c]+'"></i>'+c;$("leg").appendChild(s)});
ROWS.forEach((r,i)=>{const g=document.createElement("img");g.src=r.src;g.loading="lazy";g.title=(i+1)+"";g.onclick=()=>go(i);$("grid").appendChild(g)});
$("prev").onclick=()=>go(idx-1);$("next").onclick=()=>go(idx+1);$("clear").onclick=()=>setLabel(null);
$("jump").onclick=()=>{for(let k=1;k<=ROWS.length;k++){const j=(idx+k)%ROWS.length;if(!labels[ROWS[j].tile_file]){go(j);return}}alert("All tiles are labelled.")};
document.addEventListener("keydown",e=>{
 if(e.key>="1"&&e.key<="8")setLabel(CLASSES[+e.key-1]);else if(e.key==="0")setLabel(null);
 else if(e.key==="ArrowRight")go(idx+1);else if(e.key==="ArrowLeft")go(idx-1)});
function q(v){v=(v==null?"":String(v));return /[",\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v}
$("export").onclick=()=>{
 const lines=[COLS.join(",")];
 ROWS.forEach(r=>lines.push(COLS.map(c=>q(c==="label"?(labels[r.tile_file]||""):r[c])).join(",")));
 const blob=new Blob([lines.join("\n")+"\n"],{type:"text/csv"});const a=document.createElement("a");
 a.href=URL.createObjectURL(blob);a.download="annotate_"+MODE+"_labelled.csv";document.body.appendChild(a);a.click();a.remove()};
const first=ROWS.findIndex(r=>!labels[r.tile_file]);idx=first<0?0:first;render();
</script></body></html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--mode", choices=["A", "B"], required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--data", default="data", help="folder that holds tiles_<REGION>\\tiles (relative to the html)")
    a = ap.parse_args()

    df = pd.read_csv(a.csv).fillna("")
    if "label" not in df:
        df["label"] = ""
    if a.mode == "B":  # blind: no hints
        df = df.drop(columns=[c for c in ("group", "prelabel", "region") if c in df], errors="ignore")
    cols = list(df.columns)
    rows = df.to_dict("records")
    for r in rows:
        reg = str(r["tile_file"]).split("_")[0]
        r["src"] = f"{a.data}/tiles_{reg}/tiles/{r['tile_file']}"
    html = (TEMPLATE.replace("__MODE__", a.mode)
            .replace("__COLS__", json.dumps(cols))
            .replace("__DATA__", json.dumps(rows).replace("</", "<\\/")))
    Path(a.out).write_text(html, encoding="utf-8")
    print(f"{len(rows)} tiles -> {a.out}  (open it in your browser)")


if __name__ == "__main__":
    main()
