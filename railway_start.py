"""Railway entry point with CORS, web UI, city autocomplete, booking links, hub search."""
import os
import uvicorn
from fli.mcp.server import mcp
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from starlette.routing import Route

HTML_PAGE = r'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>Fli</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,500;9..40,700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#0a0e1a;--sf:#111827;--sf2:#1a2236;--bd:#1e293b;--ac:#f59e0b;--acd:rgba(245,158,11,.12);--t:#f1f5f9;--t2:#94a3b8;--t3:#64748b;--g:#10b981;--r:#ef4444;--rd:14px}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--t);min-height:100dvh;overflow-x:hidden;-webkit-tap-highlight-color:transparent}
.hd{padding:20px 20px 12px;display:flex;align-items:center;justify-content:space-between}
.logo{font-family:'Space Mono',monospace;font-size:26px;font-weight:700;letter-spacing:-1px;color:var(--ac)}
.logo span{color:var(--t3);font-weight:400;font-size:14px;margin-left:6px;letter-spacing:0}
.sb{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--t3)}
.dot{width:10px;height:10px;border-radius:50%;background:var(--r);box-shadow:0 0 8px var(--r);transition:.4s}
.dot.on{background:var(--g);box-shadow:0 0 8px var(--g)}
.tabs{display:flex;gap:4px;margin:0 16px 16px;background:var(--sf);border-radius:10px;padding:4px}
.tab{flex:1;text-align:center;padding:10px;border-radius:8px;font-weight:500;font-size:14px;color:var(--t3);cursor:pointer;transition:.25s;border:none;background:none}
.tab.on{background:var(--acd);color:var(--ac);font-weight:700}
.fc{margin:0 16px 16px;background:var(--sf);border:1px solid var(--bd);border-radius:var(--rd);padding:20px}
.fr{display:flex;gap:10px;margin-bottom:12px;min-width:0}
.fg{flex:1;display:flex;flex-direction:column;gap:5px;min-width:0;position:relative}
label{font-size:11px;font-weight:500;color:var(--t3);text-transform:uppercase;letter-spacing:.8px}
input:not([type=checkbox]),select{background:var(--sf2);border:1px solid var(--bd);border-radius:8px;padding:11px 12px;color:var(--t);font-family:'DM Sans',sans-serif;font-size:15px;outline:none;transition:border-color .2s;-webkit-appearance:none;appearance:none;width:100%}
select{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%2394a3b8'%3E%3Cpath d='M6 8.5L1 3.5h10z'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 12px center;padding-right:32px}
input:not([type=checkbox]):focus,select:focus{border-color:var(--ac)}
input::placeholder{color:var(--t3)}
input[type="date"]{color-scheme:dark}
.big{text-transform:uppercase;text-align:center;font-size:18px;font-weight:700;letter-spacing:2px}
.arrow{display:flex;align-items:flex-end;padding-bottom:10px;color:var(--t3);font-size:18px}
.btn{width:100%;padding:14px;background:linear-gradient(135deg,var(--ac),#d97706);color:var(--bg);border:none;border-radius:10px;font-family:'DM Sans',sans-serif;font-size:16px;font-weight:700;cursor:pointer;box-shadow:0 4px 20px rgba(245,158,11,.25);margin-top:4px}
.btn:active{transform:scale(.98)}.btn:disabled{opacity:.5;cursor:not-allowed;box-shadow:none}
.btn2{width:100%;padding:12px;background:var(--sf2);color:var(--ac);border:1px solid var(--ac);border-radius:10px;font-family:'DM Sans',sans-serif;font-size:14px;font-weight:700;cursor:pointer;margin-top:8px}
.btn2:active{transform:scale(.98)}.btn2:disabled{opacity:.5}
.chk{display:flex;align-items:center;gap:8px;margin-top:4px;font-size:13px;color:var(--t2)}
.chk input[type=checkbox]{width:18px;height:18px;accent-color:var(--ac)}
.ra{padding:0 16px 100px}
.rh{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:12px}
.rh h2{font-size:18px;font-weight:700}.rh span{font-size:13px;color:var(--t3)}
.card{background:var(--sf);border:1px solid var(--bd);border-radius:var(--rd);padding:16px;margin-bottom:10px;animation:fi .35s ease-out both}
@keyframes fi{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
.ct{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px}
.cp{font-family:'Space Mono',monospace;font-size:24px;font-weight:700;color:var(--ac)}
.cs{font-size:12px;color:var(--t3);background:var(--sf2);padding:4px 10px;border-radius:20px}
.cs.ns{color:var(--g);background:rgba(16,185,129,.1)}
.cr{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.ca{font-family:'Space Mono',monospace;font-size:16px;font-weight:700}
.cl{flex:1;height:1px;background:var(--bd);position:relative}
.cl::after{content:'\2708';position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:14px;color:var(--t3)}
.cd{display:flex;gap:16px;flex-wrap:wrap}
.ci{font-size:13px;color:var(--t2)}.ci strong{color:var(--t);font-weight:500}
.legs{margin-top:10px;padding-top:10px;border-top:1px solid var(--bd)}
.leg{display:flex;align-items:center;gap:8px;padding:6px 0;font-size:13px;color:var(--t2);flex-wrap:wrap}
.la{font-weight:500;color:var(--t);min-width:40px}
.links{display:flex;gap:8px;margin-top:10px;padding-top:10px;border-top:1px solid var(--bd)}
.links a{flex:1;text-align:center;padding:8px;border-radius:8px;font-size:12px;font-weight:700;text-decoration:none;color:var(--t);background:var(--sf2);border:1px solid var(--bd);transition:.2s}
.links a:active{transform:scale(.96)}
.dc{background:var(--sf);border:1px solid var(--bd);border-radius:var(--rd);padding:16px;margin-bottom:10px;animation:fi .35s ease-out both}
.dc-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.dc-dates{display:flex;align-items:center;gap:8px}
.dc-d{font-family:'Space Mono',monospace;font-size:15px;font-weight:700}
.dc-arr{color:var(--t3);font-size:13px}
.dp{font-family:'Space Mono',monospace;font-size:20px;font-weight:700;color:var(--ac)}
.dch .dp{color:var(--g)}
.dc-sub{font-size:12px;color:var(--t3);margin-bottom:8px}
.hub-tag{display:inline-block;background:rgba(59,130,246,.12);color:#60a5fa;font-size:11px;font-weight:700;padding:3px 8px;border-radius:12px;margin-left:6px}
.msg{text-align:center;padding:40px 20px;color:var(--t3);font-size:14px;line-height:1.6}
.msg .ic{font-size:32px;margin-bottom:8px}
.ld{display:flex;justify-content:center;padding:30px}
.ld .d{width:8px;height:8px;border-radius:50%;background:var(--ac);margin:0 4px;animation:bn 1.2s infinite}
.ld .d:nth-child(2){animation-delay:.15s}.ld .d:nth-child(3){animation-delay:.3s}
@keyframes bn{0%,80%,100%{transform:scale(.6);opacity:.3}40%{transform:scale(1);opacity:1}}
.acl{position:absolute;top:100%;left:0;right:0;background:var(--sf);border:1px solid var(--bd);border-radius:8px;max-height:200px;overflow-y:auto;z-index:99;display:none}
.acl.open{display:block}
.aci{padding:10px 12px;font-size:14px;cursor:pointer;border-bottom:1px solid var(--bd)}
.aci:last-child{border:none}.aci:active{background:var(--acd)}
.aci small{color:var(--t3);font-size:12px}
.aci .code{font-family:'Space Mono',monospace;color:var(--ac);font-weight:700}
.sep{margin:24px 16px 16px;padding-top:16px;border-top:1px solid var(--bd);font-size:14px;font-weight:700;color:var(--t2)}
.hid{display:none!important}
</style>
</head>
<body>
<div class="hd"><div class="logo">fli<span>flight search</span></div><div class="sb"><span id="st">connecting...</span><div class="dot" id="sd"></div></div></div>
<div class="tabs"><button class="tab on" onclick="stab('f')">Flights</button><button class="tab" onclick="stab('d')">Best Dates</button></div>

<div class="fc" id="pf">
  <div class="fr">
    <div class="fg" style="flex:1"><label>From</label><input class="big" id="fo" placeholder="City" maxlength="30" autocomplete="off"><div class="acl" id="fo_ac"></div></div>
    <div class="arrow">&rarr;</div>
    <div class="fg" style="flex:1"><label>To</label><input class="big" id="fd" placeholder="City" maxlength="30" autocomplete="off"><div class="acl" id="fd_ac"></div></div>
  </div>
  <div class="fr"><div class="fg"><label>Departure</label><input type="date" id="ff"></div><div class="fg"><label>Return</label><input type="date" id="fret"></div></div>
  <div class="fr"><div class="fg"><label>Class</label><select id="fc2"><option value="ECONOMY">Economy</option><option value="PREMIUM_ECONOMY">Premium Eco</option><option value="BUSINESS">Business</option><option value="FIRST">First</option></select></div><div class="fg"><label>Stops</label><select id="fs"><option value="ANY">Any</option><option value="NON_STOP">Non-stop</option><option value="ONE_STOP">1 stop</option><option value="TWO_PLUS_STOPS">2+</option></select></div></div>
  <div class="fr"><div class="fg"><label>Sort</label><select id="fso"><option value="CHEAPEST">Cheapest</option><option value="DURATION">Duration</option><option value="DEPARTURE_TIME">Departure</option><option value="ARRIVAL_TIME">Arrival</option></select></div><div class="fg" style="flex:.5"><label>Pax</label><input type="number" id="fp" value="1" min="1" max="9"></div></div>
  <div class="chk"><input type="checkbox" id="fhub"><label for="fhub" style="text-transform:none;font-size:13px;color:var(--t2);letter-spacing:0">Search cheaper routes via hubs (GRU, MIA, BOG...)</label></div>
  <button class="btn" id="bf" onclick="sF()" disabled>Search Flights</button>
</div>

<div class="fc hid" id="pd">
  <div class="fr">
    <div class="fg" style="flex:1"><label>From</label><input class="big" id="dor" placeholder="City" maxlength="30" autocomplete="off"><div class="acl" id="do_ac"></div></div>
    <div class="arrow">&rarr;</div>
    <div class="fg" style="flex:1"><label>To</label><input class="big" id="dde" placeholder="City" maxlength="30" autocomplete="off"><div class="acl" id="dd_ac"></div></div>
  </div>
  <div class="fr"><div class="fg"><label>From date</label><input type="date" id="dfr"></div><div class="fg"><label>To date</label><input type="date" id="dto"></div></div>
  <div class="fr"><div class="fg"><label>Trip days</label><input type="number" id="du" value="5" min="1" max="30"></div><div class="fg"><label>Round trip</label><select id="dr"><option value="true">Yes</option><option value="false">One-way</option></select></div></div>
  <div class="fr"><div class="fg"><label>Class</label><select id="dc3"><option value="ECONOMY">Economy</option><option value="PREMIUM_ECONOMY">Premium Eco</option><option value="BUSINESS">Business</option><option value="FIRST">First</option></select></div><div class="fg"><label>Stops</label><select id="ds"><option value="ANY">Any</option><option value="NON_STOP">Non-stop</option><option value="ONE_STOP">1 stop</option></select></div></div>
  <button class="btn" id="bd" onclick="sD()" disabled>Find Best Dates</button>
</div>

<div class="ra" id="ra"></div>

<script>
var sid=null,conn=false,rid=0,MCP=location.origin+'/mcp';
function $(i){return document.getElementById(i)}
var MONTHS=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
var DAYS=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];

function niceDate(s){
  if(!s)return'--';
  var d=new Date(s);
  if(isNaN(d))return s.substring(0,10);
  return DAYS[d.getDay()]+' '+d.getDate()+' '+MONTHS[d.getMonth()];
}
function isoDate(s){
  if(!s)return'';
  if(s.length>=10)return s.substring(0,10);
  return s;
}

var DB=[
["Buenos Aires","EZE","Argentina"],["Buenos Aires Aeroparque","AEP","Argentina"],
["Barcelona","BCN","Espana"],["Madrid","MAD","Espana"],["Malaga","AGP","Espana"],
["Sevilla","SVQ","Espana"],["Valencia","VLC","Espana"],["Bilbao","BIO","Espana"],
["Palma de Mallorca","PMI","Espana"],["Alicante","ALC","Espana"],["Ibiza","IBZ","Espana"],
["Tenerife Sur","TFS","Espana"],["Gran Canaria","LPA","Espana"],
["Lisboa","LIS","Portugal"],["Porto","OPO","Portugal"],["Faro","FAO","Portugal"],
["London Heathrow","LHR","UK"],["London Gatwick","LGW","UK"],["London Stansted","STN","UK"],
["Paris CDG","CDG","France"],["Paris Orly","ORY","France"],
["Roma Fiumicino","FCO","Italia"],["Milan Malpensa","MXP","Italia"],
["Amsterdam","AMS","Netherlands"],["Frankfurt","FRA","Germany"],["Munich","MUC","Germany"],
["Berlin","BER","Germany"],["Zurich","ZRH","Switzerland"],["Bruxelles","BRU","Belgium"],
["Dublin","DUB","Ireland"],["Vienna","VIE","Austria"],["Prague","PRG","Czech Rep"],
["Warsaw","WAW","Poland"],["Budapest","BUD","Hungary"],["Athens","ATH","Greece"],
["Istanbul","IST","Turkey"],["Marrakech","RAK","Morocco"],
["New York JFK","JFK","USA"],["New York Newark","EWR","USA"],["Miami","MIA","USA"],
["Los Angeles","LAX","USA"],["Chicago","ORD","USA"],["San Francisco","SFO","USA"],
["Bogota","BOG","Colombia"],["Medellin","MDE","Colombia"],
["Santiago","SCL","Chile"],["Lima","LIM","Peru"],
["Sao Paulo","GRU","Brasil"],["Rio de Janeiro","GIG","Brasil"],
["Mexico City","MEX","Mexico"],["Cancun","CUN","Mexico"],
["Panama City","PTY","Panama"],["Montevideo","MVD","Uruguay"],
["Dubai","DXB","UAE"],["Doha","DOH","Qatar"],["Tokyo Narita","NRT","Japan"],
["Singapore","SIN","Singapore"],["Bangkok","BKK","Thailand"],["Sydney","SYD","Australia"]
];

// Hubs to try for cheaper connecting flights
var HUBS=['GRU','MIA','BOG','SCL','GIG','LIM','MEX','PTY','MAD','LIS','CDG','FCO','AMS','FRA','LHR','IST'];

function acS(q){q=q.toLowerCase().trim();if(q.length<2)return[];var r=[];for(var i=0;i<DB.length;i++){var d=DB[i];if(d[0].toLowerCase().indexOf(q)>=0||d[1].toLowerCase()===q||d[2].toLowerCase().indexOf(q)>=0)r.push(d)}if(q.length===3&&r.length===0)r.push([q.toUpperCase(),q.toUpperCase(),'']);return r.slice(0,8)}

function sAC(iid,lid){var inp=$(iid),list=$(lid);inp.addEventListener('input',function(){var res=acS(inp.value);if(!res.length){list.classList.remove('open');return}var h='';for(var i=0;i<res.length;i++){var d=res[i];h+='<div class="aci" data-c="'+d[1]+'"><span class="code">'+d[1]+'</span> '+d[0]+'<br><small>'+d[2]+'</small></div>'}list.innerHTML=h;list.classList.add('open');var items=list.querySelectorAll('.aci');for(var j=0;j<items.length;j++){items[j].addEventListener('click',function(){inp.value=this.getAttribute('data-c');inp.setAttribute('data-r',this.getAttribute('data-c'));list.classList.remove('open')})}});inp.addEventListener('blur',function(){setTimeout(function(){list.classList.remove('open')},200)})}
sAC('fo','fo_ac');sAC('fd','fd_ac');sAC('dor','do_ac');sAC('dde','dd_ac');

function gC(id){var inp=$(id);var r=inp.getAttribute('data-r');if(r)return r.toUpperCase();var v=inp.value.trim().toUpperCase();if(v.length===3)return v;var res=acS(v);return res.length>0?res[0][1]:v}

function bL(o,d,date,ret){
  var gf='https://www.google.com/travel/flights?q=flights+'+o+'+to+'+d+'+on+'+date;
  var sk='https://www.skyscanner.com/transport/flights/'+o.toLowerCase()+'/'+d.toLowerCase()+'/'+date.replace(/-/g,'');
  if(ret)sk+='/'+ret.replace(/-/g,'');
  var ky='https://www.kayak.com/flights/'+o+'-'+d+'/'+date;if(ret)ky+='/'+ret;
  var itaJson={type:ret?"round-trip":"one-way",slices:[{origin:[o],dest:[d],dates:{searchDateType:"specific",departureDate:date}}],options:{cabin:"COACH",stops:"-1",extraStops:"1",allowAirportChanges:"true",showOnlyAvailable:"true"},pax:{adults:"1"}};
  if(ret){itaJson.slices[0].dates.returnDate=ret}
  var ita='https://matrix.itasoftware.com/flights?search='+btoa(JSON.stringify(itaJson));
  return '<div class="links"><a href="'+gf+'" target="_blank">Google</a><a href="'+sk+'" target="_blank">Skyscanner</a><a href="'+ky+'" target="_blank">Kayak</a><a href="'+ita+'" target="_blank">ITA Matrix</a></div>';
}

var today=new Date();var m1=new Date(today);m1.setDate(today.getDate()+30);var m2=new Date(today);m2.setDate(today.getDate()+60);
$('ff').value=fmt(m1);$('dfr').value=fmt(m1);$('dto').value=fmt(m2);
function fmt(d){return d.toISOString().split('T')[0]}
function stab(t){var tabs=document.querySelectorAll('.tab');tabs[0].classList.toggle('on',t==='f');tabs[1].classList.toggle('on',t==='d');$('pf').classList.toggle('hid',t!=='f');$('pd').classList.toggle('hid',t!=='d')}

async function mp(b,n){var h={'Content-Type':'application/json','Accept':'application/json, text/event-stream'};if(sid)h['Mcp-Session-Id']=sid;var res=await fetch(MCP,{method:'POST',headers:h,body:JSON.stringify(b)});var s=res.headers.get('Mcp-Session-Id');if(s)sid=s;if(n){try{await res.text()}catch(e){}return null}var txt=await res.text();var lines=txt.replace(/\r/g,'').split('\n');var results=[];for(var i=0;i<lines.length;i++){var ln=lines[i].trim();if(ln.indexOf('data: ')===0){try{results.push(JSON.parse(ln.substring(6)))}catch(e){}}}if(results.length>0)return results[results.length-1];try{return JSON.parse(txt)}catch(e){return null}}

async function connect(){$('st').textContent='connecting...';$('sd').classList.remove('on');try{var r=await mp({jsonrpc:'2.0',id:++rid,method:'initialize',params:{protocolVersion:'2025-03-26',capabilities:{},clientInfo:{name:'fli-web',version:'3.0'}}});if(!r||!r.result)throw new Error('x');await mp({jsonrpc:'2.0',method:'notifications/initialized'},true);conn=true;$('st').textContent='connected';$('sd').classList.add('on');$('bf').disabled=false;$('bd').disabled=false}catch(e){$('st').textContent='offline';setTimeout(connect,5000)}}

// ====== SEARCH FLIGHTS ======
async function sF(){
  if(!conn){await connect();if(!conn)return}
  $('bf').disabled=true;$('bf').textContent='Searching...';
  $('ra').innerHTML='<div class="ld"><div class="d"></div><div class="d"></div><div class="d"></div></div>';
  var o=gC('fo'),d=gC('fd');
  var p={origin:o,destination:d,departure_date:$('ff').value,cabin_class:$('fc2').value,max_stops:$('fs').value,sort_by:$('fso').value,passengers:parseInt($('fp').value)||1};
  if($('fret').value)p.return_date=$('fret').value;
  try{
    var res=await mp({jsonrpc:'2.0',id:++rid,method:'tools/call',params:{name:'search_flights',arguments:p}});
    var html=rF(res,p);

    // Hub search if checked
    if($('fhub').checked){
      html+='<div class="sep">Alternative routes via hubs</div>';
      html+='<div id="hubResults"><div class="ld"><div class="d"></div><div class="d"></div><div class="d"></div></div></div>';
      $('ra').innerHTML=html;
      var hubHtml=await searchHubs(o,d,p);
      $('hubResults').innerHTML=hubHtml||'<div class="msg">No cheaper hub routes found.</div>';
    } else {
      $('ra').innerHTML=html;
    }
  }catch(e){$('ra').innerHTML='<div class="msg"><div class="ic">&#9888;</div>'+e.message+'</div>'}
  $('bf').disabled=false;$('bf').textContent='Search Flights';
}

async function searchHubs(origin,dest,baseParams){
  // Filter hubs: exclude origin and dest
  var hubs=[];
  for(var i=0;i<HUBS.length;i++){if(HUBS[i]!==origin&&HUBS[i]!==dest)hubs.push(HUBS[i])}
  // Search top 4 most likely hubs
  var candidates=hubs.slice(0,6);
  var results=[];
  for(var i=0;i<candidates.length;i++){
    var hub=candidates[i];
    try{
      // Search origin->hub on same date
      var r1=await mp({jsonrpc:'2.0',id:++rid,method:'tools/call',params:{name:'search_flights',arguments:{origin:origin,destination:hub,departure_date:baseParams.departure_date,cabin_class:baseParams.cabin_class,max_stops:'ANY',sort_by:'CHEAPEST',passengers:baseParams.passengers||1}}});
      var d1=extractFlights(r1);
      if(!d1.length)continue;
      // Search hub->dest on same date
      var r2=await mp({jsonrpc:'2.0',id:++rid,method:'tools/call',params:{name:'search_flights',arguments:{origin:hub,destination:dest,departure_date:baseParams.departure_date,cabin_class:baseParams.cabin_class,max_stops:'ANY',sort_by:'CHEAPEST',passengers:baseParams.passengers||1}}});
      var d2=extractFlights(r2);
      if(!d2.length)continue;
      var combo=d1[0].price+d2[0].price;
      results.push({hub:hub,price:combo,leg1:d1[0],leg2:d2[0]});
    }catch(e){}
  }
  results.sort(function(a,b){return a.price-b.price});
  var html='';
  for(var i=0;i<Math.min(results.length,4);i++){
    var r=results[i];
    html+='<div class="card" style="animation-delay:'+(i*.08)+'s">';
    html+='<div class="ct"><div class="cp">$'+r.price+'<span class="hub-tag">via '+r.hub+'</span></div></div>';
    html+='<div class="cr"><span class="ca">'+origin+'</span><div class="cl"></div><span class="ca">'+r.hub+'</span><div class="cl"></div><span class="ca">'+dest+'</span></div>';
    html+='<div class="cd"><div class="ci">Leg 1: $'+r.leg1.price+' ('+r.leg1.airline+')</div><div class="ci">Leg 2: $'+r.leg2.price+' ('+r.leg2.airline+')</div></div>';
    html+=bL(origin,r.hub,baseParams.departure_date,'');
    html+='</div>';
  }
  return html;
}

function extractFlights(res){
  var sc=res&&res.result?res.result.structuredContent:null;
  var ct=res&&res.result?res.result.content:null;
  var data=null;
  if(sc){data=sc}else if(ct&&ct.length>0){var t='';for(var i=0;i<ct.length;i++)t+=(ct[i].text||'');try{data=JSON.parse(t)}catch(e){}}
  if(!data||!data.flights)return[];
  var fl=data.flights;var out=[];
  for(var i=0;i<Math.min(fl.length,3);i++){
    var f=fl[i];var legs=f.legs||[];
    out.push({price:f.price,airline:legs.length>0?legs[0].airline:'?'});
  }
  return out;
}

// ====== SEARCH DATES ======
async function sD(){
  if(!conn){await connect();if(!conn)return}
  $('bd').disabled=true;$('bd').textContent='Searching...';
  $('ra').innerHTML='<div class="ld"><div class="d"></div><div class="d"></div><div class="d"></div></div>';
  var o=gC('dor'),d=gC('dde');
  var p={origin:o,destination:d,start_date:$('dfr').value,end_date:$('dto').value,trip_duration:parseInt($('du').value)||5,is_round_trip:$('dr').value==='true',cabin_class:$('dc3').value,max_stops:$('ds').value,sort_by_price:true,passengers:1};
  try{var res=await mp({jsonrpc:'2.0',id:++rid,method:'tools/call',params:{name:'search_dates',arguments:p}});$('ra').innerHTML=rD(res,p)}
  catch(e){$('ra').innerHTML='<div class="msg"><div class="ic">&#9888;</div>'+e.message+'</div>'}
  $('bd').disabled=false;$('bd').textContent='Find Best Dates';
}

// ====== RENDER FLIGHTS (returns HTML) ======
function rF(res,p){
  try{
    var sc=res&&res.result?res.result.structuredContent:null;
    var ct=res&&res.result?res.result.content:null;var data=null;
    if(sc){data=sc}else if(ct&&ct.length>0){var t='';for(var i=0;i<ct.length;i++)t+=(ct[i].text||'');data=JSON.parse(t)}
    if(!data)return '<div class="msg"><div class="ic">&#128269;</div>No results.</div>';
    if(data.success===false)return '<div class="msg"><div class="ic">&#9888;</div>'+(data.error||'Error')+'</div>';
    var fl=data.flights;if(!fl||!fl.length)return '<div class="msg"><div class="ic">&#128269;</div>No flights found.</div>';

    var h='<div class="rh"><h2>'+p.origin+' &rarr; '+p.destination+'</h2><span>'+fl.length+' flights</span></div>';
    for(var i=0;i<fl.length;i++){
      var f=fl[i];var price=f.price!=null?f.price:'--';var legs=f.legs||[];
      var stops=Math.max(0,legs.length-1);var tm=0;for(var j=0;j<legs.length;j++)tm+=(legs[j].duration||0);
      var sT=stops===0?'Non-stop':stops+' stop'+(stops>1?'s':'');var sC=stops===0?'ns':'';
      var fL=legs[0]||{};var lL=legs[legs.length-1]||fL;
      var dT=fL.departure_time?fL.departure_time.substring(11,16):'';
      var aT=lL.arrival_time?lL.arrival_time.substring(11,16):'';
      var depD=fL.departure_time?fL.departure_time.substring(0,10):'';

      h+='<div class="card" style="animation-delay:'+(i*.05)+'s">';
      h+='<div class="ct"><div class="cp">$'+price+'</div><div class="cs '+sC+'">'+sT+'</div></div>';
      h+='<div class="cr"><span class="ca">'+p.origin+'</span><div class="cl"></div><span class="ca">'+p.destination+'</span></div>';
      h+='<div class="cd"><div class="ci">'+dT+' &rarr; '+aT+'</div>';
      if(tm>0)h+='<div class="ci"><strong>'+fDu(tm)+'</strong></div>';
      if(fL.airline)h+='<div class="ci">'+fL.airline+'</div>';
      h+='</div>';
      if(legs.length>0){h+='<div class="legs">';for(var k=0;k<legs.length;k++){var l=legs[k];h+='<div class="leg"><span class="la">'+(l.airline||'')+'</span> <span>'+(l.flight_number||'')+'</span> <span>'+(l.departure_time?l.departure_time.substring(11,16):'')+' &rarr; '+(l.arrival_time?l.arrival_time.substring(11,16):'')+'</span>';if(l.duration)h+=' <span style="color:var(--t3);font-size:11px">'+fDu(l.duration)+'</span>';h+='</div>'}h+='</div>'}
      h+=bL(p.origin,p.destination,depD||p.departure_date,p.return_date||'');
      h+='</div>';
    }
    return h;
  }catch(e){return '<div class="msg"><div class="ic">&#9888;</div>'+e.message+'</div>'}
}

// ====== RENDER DATES (returns HTML) ======
function rD(res,p){
  try{
    var sc=res&&res.result?res.result.structuredContent:null;
    var ct=res&&res.result?res.result.content:null;var data=null;
    if(sc){data=sc}else if(ct&&ct.length>0){var t='';for(var i=0;i<ct.length;i++)t+=(ct[i].text||'');data=JSON.parse(t)}
    if(!data)return '<div class="msg"><div class="ic">&#128269;</div>No results.</div>';
    if(data.success===false)return '<div class="msg"><div class="ic">&#9888;</div>'+(data.error||'Error')+'</div>';
    var dates=data.dates;if(!dates||!dates.length)return '<div class="msg"><div class="ic">&#128269;</div>No dates.</div>';

    var mn=Infinity;for(var i=0;i<dates.length;i++){if(dates[i].price<mn)mn=dates[i].price}

    var h='<div class="rh"><h2>'+p.origin+' &rarr; '+p.destination+'</h2><span>'+dates.length+' dates</span></div>';
    for(var i=0;i<dates.length;i++){
      var d=dates[i];var ch=d.price===mn;
      // Parse date field - can be array [dep,ret] or string
      var depStr='',retStr='',depIso='',retIso='';
      if(Array.isArray(d.date)){
        depStr=niceDate(d.date[0]);retStr=niceDate(d.date[1]);
        depIso=isoDate(d.date[0]);retIso=isoDate(d.date[1]);
      }else{
        depStr=niceDate(d.date);depIso=isoDate(d.date);
        if(d.return_date){retStr=niceDate(d.return_date);retIso=isoDate(d.return_date)}
      }

      h+='<div class="dc'+(ch?' dch':'')+'" style="animation-delay:'+(i*.04)+'s">';
      h+='<div class="dc-top">';
      h+='<div class="dc-dates"><span class="dc-d">'+depStr+'</span>';
      if(retStr)h+='<span class="dc-arr">&rarr; '+retStr+'</span>';
      h+='</div>';
      h+='<div class="dp">'+(ch?'&#9733; ':'')+'$'+d.price+'</div>';
      h+='</div>';
      if(retStr){var days=Math.round((new Date(retIso)-new Date(depIso))/(86400000));h+='<div class="dc-sub">'+days+' days</div>'}
      h+=bL(p.origin,p.destination,depIso,retIso);
      h+='</div>';
    }
    return h;
  }catch(e){return '<div class="msg"><div class="ic">&#9888;</div>'+e.message+'</div>'}
}

function fDu(m){var h=Math.floor(m/60);var mm=m%60;return h>0?h+'h '+mm+'m':mm+'m'}
connect();
</script>
</body>
</html>'''


async def homepage(request):
    return HTMLResponse(HTML_PAGE)

app = mcp.http_app(path="/mcp")
app.routes.insert(0, Route("/", homepage))
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], expose_headers=["Mcp-Session-Id"])

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host=host, port=port)
