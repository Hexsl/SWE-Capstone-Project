import { createElement, useMemo } from 'react';
import { View } from 'react-native';
import { mapHtml } from './mapHtml';

// Browser: react-native-webview doesn't run on web, so the same Leaflet page goes in an iframe.
export default function LeafletMap({ stops, routes, style }) {
  const html = useMemo(() => mapHtml({ stops, routes }), [stops, routes]);
  return (
    <View style={style}>
      {createElement('iframe', {
        srcDoc: html,
        title: 'Long Island Rail Road map',
        style: { border: 0, width: '100%', height: '100%' },
      })}
    </View>
  );
}
