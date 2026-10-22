import { useEffect, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { api } from '../api';
import BottomNav from '../BottomNav';
import Weather from '../Weather';
import LeafletMap from '../LeafletMap';
import { colors } from '../theme';

export default function Stops({ go }) {
  const [stops, setStops] = useState(null);
  const [error, setError] = useState('');
  const [layer, setLayer] = useState(null);
  const [mapError, setMapError] = useState('');

  useEffect(() => {
    api('/api/stops/nearby/')
      .then(setStops)
      .catch((e) => setError(e.message));
  }, []);

  const loadMap = () => {
    setMapError('');
    api('/api/map/?agency=LIRR')
      .then((d) => (d.stops.length ? setLayer(d) : setMapError('No LIRR stations yet. Run: python -m database.mta_lirr')))
      .catch((e) => setMapError(e.message));
  };
  useEffect(loadMap, []);

  // LIRR ids ("lirr-4") mean nothing to riders: show branch names ("Ronkonkoma") from the map data
  const branchName = {};
  (layer ? layer.routes : []).forEach((r) => { branchName[r.route_id] = r.name.replace(' Branch', ''); });
  const lines = (ids = []) => ids.map((id) => branchName[id] || (id.startsWith('lirr-') ? 'LIRR' : id)).join(', ');

  return (
    <View style={{ flex: 1 }}>
      <ScrollView>
        <View style={s.header}>
          <Pressable onPress={() => go('home')}>
            <Text style={s.title}>{'\u2190'}  Nearby Stops</Text>
          </Pressable>
          <Text style={s.sub}>From: Current Location</Text>
          <Text style={s.sub}>To: Times Square, Manhattan</Text>
          <TextInput style={s.search} placeholder="Search for a route, stop, or location..." placeholderTextColor="#5f7388" />
        </View>

        <View style={s.map}>
          {layer ? (
            <LeafletMap stops={layer.stops} routes={layer.routes} style={{ flex: 1, alignSelf: 'stretch' }} />
          ) : (
            <View style={s.mapMsg}>
              <Text style={s.msg}>{mapError || 'Loading map...'}</Text>
              {mapError ? (
                <Pressable onPress={loadMap}>
                  <Text style={[s.msg, { fontWeight: '700' }]}>Try again</Text>
                </Pressable>
              ) : null}
            </View>
          )}
          <Weather />
        </View>

        <View style={s.bar}>
          <Text style={s.barText}>Nearby Stops</Text>
        </View>

        <View style={{ backgroundColor: '#ffffff', minHeight: 260 }}>
          {error ? <Text style={s.msg}>{error}</Text> : null}
          {!stops && !error ? <Text style={s.msg}>Loading...</Text> : null}
          {stops && stops.length === 0 ? <Text style={s.msg}>No stops nearby.</Text> : null}
          {stops &&
            stops.map((st) => (
              <View key={st.stop_id} style={s.row}>
                <Text style={s.name}>{st.name}</Text>
                <Text style={s.meta}>
                  {st.mode} {'\u00B7'} {lines(st.route_ids)} {'\u00B7'} {st.walk_minutes} min walk
                </Text>
              </View>
            ))}
        </View>
      </ScrollView>
      <BottomNav active="stops" go={go} />
    </View>
  );
}

const s = StyleSheet.create({
  header: { backgroundColor: colors.navy, paddingTop: 28, paddingHorizontal: 18, paddingBottom: 18 },
  title: { color: '#cbe9f5', fontSize: 24 },
  sub: { color: '#cbe9f5', fontSize: 18, marginLeft: 6, marginTop: 2 },
  search: {
    height: 42, borderRadius: 21, borderWidth: 1, borderColor: '#0b1a2e', marginTop: 14,
    backgroundColor: colors.sky, paddingHorizontal: 14, fontSize: 16, color: colors.text,
  },
  map: { height: 340, backgroundColor: colors.sky },
  mapMsg: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 20 },
  bar: { backgroundColor: '#d4f0c8', paddingVertical: 10, alignItems: 'center', borderWidth: 1, borderColor: '#bcd9b3' },
  barText: { fontSize: 24, color: colors.text },
  row: { padding: 14, borderBottomWidth: 1, borderColor: '#e3e8ee' },
  name: { fontSize: 19, fontWeight: '700', color: colors.text },
  meta: { fontSize: 15, color: '#5f7388', marginTop: 3 },
  msg: { padding: 16, fontSize: 16, color: colors.text },
});