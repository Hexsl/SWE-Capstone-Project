import { useMemo } from 'react';
import { WebView } from 'react-native-webview';
import { mapHtml } from './mapHtml';

// Phones: the Leaflet page runs inside a WebView. The browser build uses LeafletMap.web.js instead.
export default function LeafletMap({ stops, routes, style }) {
  const html = useMemo(() => mapHtml({ stops, routes }), [stops, routes]);
  // baseUrl gives the page an origin, so tile requests carry a Referer (OpenStreetMap blocks them otherwise)
  return <WebView originWhitelist={['*']} source={{ html, baseUrl: 'https://transithub.nyc/' }} style={style} />;
}
