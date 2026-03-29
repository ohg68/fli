"""Railway entry point with CORS support and embedded web UI."""
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
<title>Fli · Flight Search</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,500;0,9..40,700;1,9..40,300&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0e1a;
    --surface: #111827;
    --surface2: #1a2236;
    --border: #1e293b;
    --accent: #f59e0b;
    --accent2: #fbbf24;
    --accent-dim: rgba(245,158,11,0.12);
    --text: #f1f5f9;
    --text2: #94a3b8;
    --text3: #64748b;
    --green: #10b981;
    --red: #ef4444;
    --blue: #3b82f6;
    --radius: 14px;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100dvh;
    overflow-x: hidden;
    -webkit-tap-highlight-color: transparent;
  }
  .header {
    padding: 20px 20px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .logo {
    font-family: 'Space Mono', monospace;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -1px;
    color: var(--accent);
  }
  .logo span { color: var(--text3); font-weight: 400; font-size: 14px; margin-left: 6px; letter-spacing: 0; }
  .status-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--text3);
  }
  .status-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: var(--red);
    box-shadow: 0 0 8px var(--red);
    transition: all 0.4s;
  }
  .status-dot.connected {
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
  }
  .status-text { font-family: 'Space Mono', monospace; }
  .tabs {
    display: flex;
    gap: 4px;
    margin: 0 16px 16px;
    background: var(--surface);
    border-radius: 10px;
    padding: 4px;
  }
  .tab {
    flex: 1;
    text-align: center;
    padding: 10px;
    border-radius: 8px;
    font-weight: 500;
    font-size: 14px;
    color: var(--text3);
    cursor: pointer;
    transition: all 0.25s;
    border: none;
    background: none;
  }
  .tab.active {
    background: var(--accent-dim);
    color: var(--accent);
    font-weight: 700;
  }
  .form-card {
    margin: 0 16px 16px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
  }
  .form-row {
    display: flex;
    gap: 10px;
    margin-bottom: 12px;
    min-width: 0;
  }
  .form-group {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 5px;
    min-width: 0;
  }
  label {
    font-size: 11px;
    font-weight: 500;
    color: var(--text3);
    text-transform: uppercase;
    letter-spacing: 0.8px;
  }
  input, select {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 11px 12px;
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    outline: none;
    transition: border-color 0.2s;
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
  }
  select {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%2394a3b8'%3E%3Cpath d='M6 8.5L1 3.5h10z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 12px center;
    padding-right: 32px;
  }
  input:focus, select:focus { border-color: var(--accent); }
  input::placeholder { color: var(--text3); }
  input[type="date"] { color-scheme: dark; }
  .search-btn {
    width: 100%;
    padding: 14px;
    background: linear-gradient(135deg, var(--accent), #d97706);
    color: var(--bg);
    border: none;
    border-radius: 10px;
    font-family: 'DM Sans', sans-serif;
    font-size: 16px;
    font-weight: 700;
    cursor: pointer;
    letter-spacing: 0.3px;
    transition: transform 0.15s, box-shadow 0.25s;
    box-shadow: 0 4px 20px rgba(245,158,11,0.25);
    margin-top: 4px;
  }
  .search-btn:active { transform: scale(0.98); }
  .search-btn:disabled { opacity: 0.5; cursor: not-allowed; box-shadow: none; }
  .results-area { padding: 0 16px 100px; }
  .results-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px; }
  .results-header h2 { font-size: 18px; font-weight: 700; }
  .results-header span { font-size: 13px; color: var(--text3); }
  .flight-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px;
    margin-bottom: 10px;
    animation: fadeSlideIn 0.35s ease-out both;
  }
  @keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .fc-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
  .fc-price { font-family: 'Space Mono', monospace; font-size: 24px; font-weight: 700; color: var(--accent); }
  .fc-stops { font-size: 12px; color: var(--text3); background: var(--surface2); padding: 4px 10px; border-radius: 20px; }
  .fc-stops.nonstop { color: var(--green); background: rgba(16,185,129,0.1); }
  .fc-route { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
  .fc-airport { font-family: 'Space Mono', monospace; font-size: 16px; font-weight: 700; }
  .fc-line { flex: 1; height: 1px; background: var(--border); position: relative; }
  .fc-line::after { content: '\2708'; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 14px; color: var(--text3); }
  .fc-details { display: flex; gap: 16px; flex-wrap: wrap; }
  .fc-detail { font-size: 13px; color: var(--text2); }
  .fc-detail strong { color: var(--text); font-weight: 500; }
  .fc-legs { margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border); }
  .fc-leg { display: flex; align-items: center; gap: 8px; padding: 6px 0; font-size: 13px; color: var(--text2); flex-wrap: wrap; }
  .fc-leg-airline { font-weight: 500; color: var(--text); min-width: 40px; }
  .date-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 16px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    animation: fadeSlideIn 0.35s ease-out both;
  }
  .dc-date { font-size: 15px; font-weight: 500; }
  .dc-price { font-family: 'Space Mono', monospace; font-size: 18px; font-weight: 700; color: var(--accent); }
  .dc-cheapest .dc-price { color: var(--green); }
  .msg { text-align: center; padding: 40px 20px; color: var(--text3); font-size: 14px; line-height: 1.6; }
  .msg .icon { font-size: 32px; margin-bottom: 8px; }
  .loader { display: flex; justify-content: center; padding: 30px; }
  .loader .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); margin: 0 4px; animation: bounce 1.2s infinite; }
  .loader .dot:nth-child(2) { animation-delay: 0.15s; }
  .loader .dot:nth-child(3) { animation-delay: 0.3s; }
  @keyframes bounce { 0%, 80%, 100% { transform: scale(0.6); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
  .hidden { display: none !important; }
</style>
</head>
<body>

<div class="header">
  <div class="logo">fli<span>flight search</span></div>
  <div class="status-bar">
    <span class="status-text" id="statusText">connecting...</span>
    <div class="status-dot" id="statusDot"></div>
  </div>
</div>

<div class="tabs">
  <button class="tab active" data-tab="flights" onclick="switchTab('flights')">Flights</button>
  <button class="tab" data-tab="dates" onclick="switchTab('dates')">Best Dates</button>
</div>

<div class="form-card" id="flightsForm">
  <div class="form-row">
    <div class="form-group" style="flex:1">
      <label>From</label>
      <input type="text" id="f_origin" placeholder="BCN" maxlength="3" style="text-transform:uppercase;text-align:center;font-size:18px;font-weight:700;letter-spacing:2px">
    </div>
    <div style="display:flex;align-items:flex-end;padding-bottom:10px;color:var(--text3);font-size:18px">&rarr;</div>
    <div class="form-group" style="flex:1">
      <label>To</label>
      <input type="text" id="f_dest" placeholder="LIS" maxlength="3" style="text-transform:uppercase;text-align:center;font-size:18px;font-weight:700;letter-spacing:2px">
    </div>
  </div>
  <div class="form-row">
    <div class="form-group"><label>Departure</label><input type="date" id="f_date"></div>
    <div class="form-group"><label>Return (opt)</label><input type="date" id="f_return"></div>
  </div>
  <div class="form-row">
    <div class="form-group"><label>Class</label>
      <select id="f_class"><option value="ECONOMY">Economy</option><option value="PREMIUM_ECONOMY">Premium Eco</option><option value="BUSINESS">Business</option><option value="FIRST">First</option></select>
    </div>
    <div class="form-group"><label>Stops</label>
      <select id="f_stops"><option value="ANY">Any</option><option value="NON_STOP">Non-stop</option><option value="ONE_STOP">1 stop</option><option value="TWO_PLUS_STOPS">2+</option></select>
    </div>
  </div>
  <div class="form-row">
    <div class="form-group"><label>Sort by</label>
      <select id="f_sort"><option value="CHEAPEST">Cheapest</option><option value="DURATION">Duration</option><option value="DEPARTURE_TIME">Departure</option><option value="ARRIVAL_TIME">Arrival</option></select>
    </div>
    <div class="form-group" style="flex:0.5"><label>Pax</label><input type="number" id="f_pax" value="1" min="1" max="9"></div>
  </div>
  <button class="search-btn" id="searchFlightsBtn" onclick="searchFlights()" disabled>Search Flights</button>
</div>

<div class="form-card hidden" id="datesForm">
  <div class="form-row">
    <div class="form-group" style="flex:1">
      <label>From</label>
      <input type="text" id="d_origin" placeholder="BCN" maxlength="3" style="text-transform:uppercase;text-align:center;font-size:18px;font-weight:700;letter-spacing:2px">
    </div>
    <div style="display:flex;align-items:flex-end;padding-bottom:10px;color:var(--text3);font-size:18px">&rarr;</div>
    <div class="form-group" style="flex:1">
      <label>To</label>
      <input type="text" id="d_dest" placeholder="LIS" maxlength="3" style="text-transform:uppercase;text-align:center;font-size:18px;font-weight:700;letter-spacing:2px">
    </div>
  </div>
  <div class="form-row">
    <div class="form-group"><label>From date</label><input type="date" id="d_from"></div>
    <div class="form-group"><label>To date</label><input type="date" id="d_to"></div>
  </div>
  <div class="form-row">
    <div class="form-group"><label>Trip days</label><input type="number" id="d_duration" value="5" min="1" max="30"></div>
    <div class="form-group"><label>Round trip</label>
      <select id="d_round"><option value="true">Yes</option><option value="false">One-way</option></select>
    </div>
  </div>
  <div class="form-row">
    <div class="form-group"><label>Class</label>
      <select id="d_class"><option value="ECONOMY">Economy</option><option value="PREMIUM_ECONOMY">Premium Eco</option><option value="BUSINESS">Business</option><option value="FIRST">First</option></select>
    </div>
    <div class="form-group"><label>Stops</label>
      <select id="d_stops"><option value="ANY">Any</option><option value="NON_STOP">Non-stop</option><option value="ONE_STOP">1 stop</option></select>
    </div>
  </div>
  <button class="search-btn" id="searchDatesBtn" onclick="searchDates()" disabled>Find Best Dates</button>
</div>

<div class="results-area" id="resultsArea"></div>

<script>
var sessionId = null;
var connected = false;
var requestId = 0;
var MCP_URL = window.location.origin + '/mcp';

function $(id) { return document.getElementById(id); }

var today = new Date();
var inMonth = new Date(today); inMonth.setDate(today.getDate() + 30);
var inMonth2 = new Date(today); inMonth2.setDate(today.getDate() + 60);
$('f_date').value = fmt(inMonth);
$('d_from').value = fmt(inMonth);
$('d_to').value = fmt(inMonth2);

function fmt(d) { return d.toISOString().split('T')[0]; }

function switchTab(tab) {
  document.querySelectorAll('.tab').forEach(function(t) { t.classList.toggle('active', t.dataset.tab === tab); });
  $('flightsForm').classList.toggle('hidden', tab !== 'flights');
  $('datesForm').classList.toggle('hidden', tab !== 'dates');
}

function setStatus(text, ok) {
  $('statusText').textContent = text;
  $('statusDot').classList.toggle('connected', ok);
}

async function mcpPost(body, isNotification) {
  var headers = { 'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream' };
  if (sessionId) headers['Mcp-Session-Id'] = sessionId;

  var res = await fetch(MCP_URL, { method: 'POST', headers: headers, body: JSON.stringify(body) });

  var sid = res.headers.get('Mcp-Session-Id');
  if (sid) sessionId = sid;

  if (isNotification) { try { await res.text(); } catch(e) {} return null; }

  var text = await res.text();
  var lines = text.replace(/\r/g, '').split('\n');
  var results = [];
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim();
    if (line.indexOf('data: ') === 0) {
      try { results.push(JSON.parse(line.substring(6))); } catch(e) {}
    }
  }
  if (results.length > 0) return results[results.length - 1];
  try { return JSON.parse(text); } catch(e) { return null; }
}

async function connect() {
  setStatus('connecting...', false);
  try {
    var initRes = await mcpPost({
      jsonrpc: '2.0', id: ++requestId, method: 'initialize',
      params: { protocolVersion: '2025-03-26', capabilities: {}, clientInfo: { name: 'fli-web', version: '1.0.0' } }
    });
    if (!initRes || !initRes.result) throw new Error('bad init');
    await mcpPost({ jsonrpc: '2.0', method: 'notifications/initialized' }, true);
    connected = true;
    setStatus('connected', true);
    $('searchFlightsBtn').disabled = false;
    $('searchDatesBtn').disabled = false;
  } catch(e) {
    setStatus('offline - tap to retry', false);
    $('statusBar') && $('statusBar').onclick == null && ($('statusText').onclick = function() { connect(); });
  }
}

async function searchFlights() {
  if (!connected) { await connect(); if (!connected) return; }
  $('searchFlightsBtn').disabled = true;
  $('searchFlightsBtn').textContent = 'Searching...';
  $('resultsArea').innerHTML = '<div class="loader"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>';

  var params = {
    origin: $('f_origin').value.toUpperCase(),
    destination: $('f_dest').value.toUpperCase(),
    departure_date: $('f_date').value,
    cabin_class: $('f_class').value,
    max_stops: $('f_stops').value,
    sort_by: $('f_sort').value,
    passengers: parseInt($('f_pax').value) || 1
  };
  if ($('f_return').value) params.return_date = $('f_return').value;

  try {
    var res = await mcpPost({ jsonrpc: '2.0', id: ++requestId, method: 'tools/call', params: { name: 'search_flights', arguments: params } });
    renderFlightResults(res, params);
  } catch(e) {
    $('resultsArea').innerHTML = '<div class="msg"><div class="icon">&#9888;</div>Error: ' + e.message + '</div>';
  }
  $('searchFlightsBtn').disabled = false;
  $('searchFlightsBtn').textContent = 'Search Flights';
}

async function searchDates() {
  if (!connected) { await connect(); if (!connected) return; }
  $('searchDatesBtn').disabled = true;
  $('searchDatesBtn').textContent = 'Searching...';
  $('resultsArea').innerHTML = '<div class="loader"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>';

  var params = {
    origin: $('d_origin').value.toUpperCase(),
    destination: $('d_dest').value.toUpperCase(),
    start_date: $('d_from').value,
    end_date: $('d_to').value,
    trip_duration: parseInt($('d_duration').value) || 5,
    is_round_trip: $('d_round').value === 'true',
    cabin_class: $('d_class').value,
    max_stops: $('d_stops').value,
    sort_by_price: true,
    passengers: 1
  };

  try {
    var res = await mcpPost({ jsonrpc: '2.0', id: ++requestId, method: 'tools/call', params: { name: 'search_dates', arguments: params } });
    renderDateResults(res, params);
  } catch(e) {
    $('resultsArea').innerHTML = '<div class="msg"><div class="icon">&#9888;</div>Error: ' + e.message + '</div>';
  }
  $('searchDatesBtn').disabled = false;
  $('searchDatesBtn').textContent = 'Find Best Dates';
}

function renderFlightResults(res, params) {
  try {
    var sc = res && res.result ? res.result.structuredContent : null;
    var content = res && res.result ? res.result.content : null;
    var data = null;
    if (sc) { data = sc; }
    else if (content && content.length > 0) {
      var t = ''; for (var i = 0; i < content.length; i++) t += (content[i].text || '');
      data = JSON.parse(t);
    }
    if (!data) { $('resultsArea').innerHTML = '<div class="msg"><div class="icon">&#128269;</div>No results.</div>'; return; }
    if (data.success === false) { $('resultsArea').innerHTML = '<div class="msg"><div class="icon">&#9888;</div>' + (data.error || 'Error') + '</div>'; return; }
    var flights = data.flights;
    if (!flights || flights.length === 0) { $('resultsArea').innerHTML = '<div class="msg"><div class="icon">&#128269;</div>No flights found.</div>'; return; }

    var html = '<div class="results-header"><h2>' + params.origin + ' &rarr; ' + params.destination + '</h2>';
    html += '<span>' + flights.length + ' flights</span></div>';

    for (var i = 0; i < flights.length; i++) {
      var f = flights[i];
      var price = f.price != null ? f.price : '—';
      var legs = f.legs || [];
      var stops = Math.max(0, legs.length - 1);
      var totalMin = 0;
      for (var j = 0; j < legs.length; j++) totalMin += (legs[j].duration || 0);
      var stopsText = stops === 0 ? 'Non-stop' : stops + ' stop' + (stops > 1 ? 's' : '');
      var stopsClass = stops === 0 ? 'nonstop' : '';
      var firstLeg = legs[0] || {};
      var lastLeg = legs[legs.length - 1] || firstLeg;
      var depTime = firstLeg.departure_time ? firstLeg.departure_time.substring(11, 16) : '';
      var arrTime = lastLeg.arrival_time ? lastLeg.arrival_time.substring(11, 16) : '';

      html += '<div class="flight-card" style="animation-delay:' + (i * 0.05) + 's">';
      html += '<div class="fc-top"><div class="fc-price">$' + price + '</div><div class="fc-stops ' + stopsClass + '">' + stopsText + '</div></div>';
      html += '<div class="fc-route"><span class="fc-airport">' + params.origin + '</span><div class="fc-line"></div><span class="fc-airport">' + params.destination + '</span></div>';
      html += '<div class="fc-details"><div class="fc-detail">' + depTime + ' &rarr; ' + arrTime + '</div>';
      if (totalMin > 0) html += '<div class="fc-detail"><strong>' + fmtDur(totalMin) + '</strong></div>';
      if (firstLeg.airline) html += '<div class="fc-detail">' + firstLeg.airline + '</div>';
      html += '</div>';

      if (legs.length > 0) {
        html += '<div class="fc-legs">';
        for (var k = 0; k < legs.length; k++) {
          var l = legs[k];
          html += '<div class="fc-leg">';
          html += '<span class="fc-leg-airline">' + (l.airline || '') + '</span> ';
          html += '<span>' + (l.flight_number || '') + '</span> ';
          html += '<span>' + (l.departure_time ? l.departure_time.substring(11, 16) : '') + ' &rarr; ' + (l.arrival_time ? l.arrival_time.substring(11, 16) : '') + '</span> ';
          if (l.duration) html += '<span style="color:var(--text3);font-size:11px">' + fmtDur(l.duration) + '</span>';
          html += '</div>';
        }
        html += '</div>';
      }
      html += '</div>';
    }
    $('resultsArea').innerHTML = html;
  } catch(e) {
    $('resultsArea').innerHTML = '<div class="msg"><div class="icon">&#9888;</div>Render error: ' + e.message + '</div>';
  }
}

function renderDateResults(res, params) {
  try {
    var sc = res && res.result ? res.result.structuredContent : null;
    var content = res && res.result ? res.result.content : null;
    var data = null;
    if (sc) { data = sc; }
    else if (content && content.length > 0) {
      var t = ''; for (var i = 0; i < content.length; i++) t += (content[i].text || '');
      data = JSON.parse(t);
    }
    if (!data) { $('resultsArea').innerHTML = '<div class="msg"><div class="icon">&#128269;</div>No results.</div>'; return; }
    if (data.success === false) { $('resultsArea').innerHTML = '<div class="msg"><div class="icon">&#9888;</div>' + (data.error || 'Error') + '</div>'; return; }
    var dates = data.dates;
    if (!dates || dates.length === 0) { $('resultsArea').innerHTML = '<div class="msg"><div class="icon">&#128269;</div>No dates found.</div>'; return; }

    var minPrice = Infinity;
    for (var i = 0; i < dates.length; i++) { if (dates[i].price < minPrice) minPrice = dates[i].price; }

    var html = '<div class="results-header"><h2>' + params.origin + ' &rarr; ' + params.destination + '</h2>';
    html += '<span>' + dates.length + ' dates</span></div>';

    for (var i = 0; i < dates.length; i++) {
      var d = dates[i];
      var isCheap = d.price === minPrice;
      html += '<div class="date-card' + (isCheap ? ' dc-cheapest' : '') + '" style="animation-delay:' + (i * 0.04) + 's">';
      html += '<div><div class="dc-date">' + (d.date || '—') + '</div>';
      if (d.return_date) html += '<div style="font-size:12px;color:var(--text3)">Return: ' + d.return_date + '</div>';
      html += '</div>';
      html += '<div class="dc-price">' + (isCheap ? '&#9733; ' : '') + '$' + d.price + '</div>';
      html += '</div>';
    }
    $('resultsArea').innerHTML = html;
  } catch(e) {
    $('resultsArea').innerHTML = '<div class="msg"><div class="icon">&#9888;</div>Render error: ' + e.message + '</div>';
  }
}

function fmtDur(mins) {
  var h = Math.floor(mins / 60);
  var m = mins % 60;
  return h > 0 ? h + 'h ' + m + 'm' : m + 'm';
}

// Auto-connect on load
connect();
</script>
</body>
</html>'''


async def homepage(request):
    return HTMLResponse(HTML_PAGE)


# Create MCP app and add homepage
app = mcp.http_app(path="/mcp")
app.routes.insert(0, Route("/", homepage))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host=host, port=port)
