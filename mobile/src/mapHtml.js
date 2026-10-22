// Builds a small Leaflet page that draws branch lines and stations on OpenStreetMap tiles.
// LeafletMap.js (phones, WebView) and LeafletMap.web.js (browser, iframe) both show this page.

const LEAFLET = 'https://unpkg.com/leaflet@1.9.4/dist';

export function mapHtml({ stops, routes }) {
  // "<" escaped so a station name can never close the <script> tag
  const data = JSON.stringify({ stops, routes }).replace(/</g, '\\u003c');
  return `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<link rel="stylesheet" href="${LEAFLET}/leaflet.css"
  integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
<script src="${LEAFLET}/leaflet.js"
  integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<style>
  html, body, #map { height: 100%; margin: 0; }
  body { font-family: -apple-system, system-ui, sans-serif; color: #2b4062; }
  .leaflet-popup-content { margin: 10px 12px; font-size: 14px; }
  .name { font-weight: 700; font-size: 16px; margin-bottom: 6px; }
  .chip { display: inline-block; padding: 2px 7px; margin: 0 4px 4px 0; border-radius: 10px; font-size: 12px; }
  .legend { background: #fff; padding: 6px 10px; border-radius: 4px; box-shadow: 0 1px 4px rgba(0,0,0,.3);
            font-size: 13px; max-height: 180px; overflow-y: auto; }
  .legend button { border: 0; background: none; font: inherit; font-weight: 700; color: #2b4062; padding: 0; cursor: pointer; }
  .legend .row { display: flex; align-items: center; margin-top: 4px; }
  .legend .swatch { width: 18px; height: 4px; margin-right: 6px; border-radius: 2px; }
  .legend .dot { width: 9px; height: 9px; margin: 0 10px 0 4px; border-radius: 50%; border: 2px solid #2b4062; background: #fff; }
</style>
</head>
<body>
<div id="map"></div>
<script>
  var data = ${data};
  // Zoom buttons on the right: the app's weather badge sits over the top-left corner
  var map = L.map('map', { zoomControl: false, preferCanvas: true });
  L.control.zoom({ position: 'topright' }).addTo(map);
  // OpenStreetMap's tile servers want a Referer; LeafletMap.js gives the WebView page a base URL for that
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> | MTA'
  }).addTo(map);

  function esc(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

  var routeById = {};
  data.routes.forEach(function (r) {
    routeById[r.route_id] = r;
    r.lines.forEach(function (line) {
      L.polyline(line.map(function (p) { return [p[1], p[0]]; }), { color: r.color, weight: 4, opacity: 0.85 })
        .bindTooltip(esc(r.name), { sticky: true })
        .addTo(map);
    });
  });

  // Small dots when zoomed out so stations don't hide the lines, bigger (easier to tap) when zoomed in
  function radius() { return map.getZoom() <= 9 ? 3 : map.getZoom() <= 11 ? 4.5 : 7; }
  var markers = [];
  map.on('zoomend', function () { markers.forEach(function (m) { m.setRadius(radius()); }); });

  var bounds = [];
  data.stops.forEach(function (s) {
    var chips = s.route_ids.map(function (id) {
      var r = routeById[id];
      return r ? '<span class="chip" style="background:' + r.color + ';color:' + (r.text_color || '#fff') + '">' + esc(r.name.replace(' Branch', '')) + '</span>' : '';
    }).join('');
    markers.push(L.circleMarker([s.lat, s.lon], { radius: 3, color: '#2b4062', weight: 2, fillColor: '#fff', fillOpacity: 1 })
      .bindPopup('<div class="name">' + esc(s.name) + '</div>' + chips +
                 '<div>' + (s.accessible ? '&#9855; Accessible station' : 'Not accessible') + '</div>')
      .bindTooltip(esc(s.name), { direction: 'top', offset: [0, -4] })
      .addTo(map));
    bounds.push([s.lat, s.lon]);
  });

  if (bounds.length) map.fitBounds(bounds, { padding: [12, 12] });
  else map.setView([40.75, -73.4], 9);
  markers.forEach(function (m) { m.setRadius(radius()); });

  // Map S3: an explanation of the line colors and markers, collapsed so it doesn't hide the map
  var legend = L.control({ position: 'bottomleft' });
  legend.onAdd = function () {
    var div = L.DomUtil.create('div', 'legend');
    var rows = data.routes.filter(function (r) { return r.lines.length; }).map(function (r) {
      return '<div class="row"><span class="swatch" style="background:' + r.color + '"></span>' + esc(r.name) + '</div>';
    }).join('') + '<div class="row"><span class="dot"></span>Station</div>';
    div.innerHTML = '<button aria-expanded="false">Legend &#9662;</button><div hidden>' + rows + '</div>';
    var btn = div.querySelector('button'), body = div.querySelector('div');
    btn.onclick = function () {
      body.hidden = !body.hidden;
      btn.setAttribute('aria-expanded', String(!body.hidden));
    };
    L.DomEvent.disableClickPropagation(div);
    L.DomEvent.disableScrollPropagation(div);
    return div;
  };
  legend.addTo(map);
</script>
</body>
</html>`;
}
