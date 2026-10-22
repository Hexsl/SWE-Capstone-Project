import { useEffect, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { api } from '../api';
import BottomNav from '../BottomNav';
import { colors } from '../theme';
import Top from '../Top';

const filters = [['All', ''], ['Subway', 'subway'], ['Bus', 'bus'], ['Rail', 'rail']];
const cap = (m) => (m ? m.charAt(0).toUpperCase() + m.slice(1) : '');
const fmt = (d) =>
  d ? new Date(d).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) : '';

export default function History({ go, session }) {
  const [mode, setMode] = useState('');
  const [trips, setTrips] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    setTrips(null);
    api('/api/trips/' + (mode ? '?mode=' + mode : ''), { token: session.token })
      .then(setTrips)
      .catch((e) => setError(e.message));
  }, [mode]);

  return (
    <View style={{ flex: 1 }}>
      <ScrollView>
        <Top title="Trip History" bg={colors.navy} color="#ffffff" height={124} onBack={() => go('more')} />
        <View style={{ padding: 14, paddingTop: 30 }}>
          <View style={{ flexDirection: 'row', marginBottom: 18 }}>
            {filters.map(([label, value]) => (
              <Pressable key={label} onPress={() => setMode(value)} style={[s.chip, mode === value && s.chipOn]}>
                <Text style={[s.chipText, mode === value && { color: '#ffffff' }]}>{label}</Text>
              </Pressable>
            ))}
          </View>
          {error ? <Text style={s.msg}>{error}</Text> : null}
          {!trips && !error ? <Text style={s.msg}>Loading...</Text> : null}
          {trips && trips.length === 0 ? <Text style={s.msg}>No trips yet.</Text> : null}
          {trips &&
            trips.map((t) => (
              <View key={t.id} style={s.card}>
                <Text style={s.title}>
                  {t.origin} {'\u2192'} {t.destination}
                </Text>
                <Text style={s.meta}>
                  {cap(t.mode)} {'\u00B7'} {t.line} {'\u00B7'} {fmt(t.depart_at)}
                </Text>
              </View>
            ))}
        </View>
      </ScrollView>
      <BottomNav active="more" go={go} />
    </View>
  );
}

const s = StyleSheet.create({
  chip: { paddingHorizontal: 16, height: 37, justifyContent: 'center', backgroundColor: '#ffffff', borderWidth: 1, borderColor: colors.navy, marginRight: 8 },
  chipOn: { backgroundColor: colors.navy },
  chipText: { fontSize: 16, color: colors.navy },
  card: { backgroundColor: '#ffffff', borderWidth: 1, borderColor: colors.navy, padding: 16, marginBottom: 18 },
  title: { fontSize: 22, color: colors.text },
  meta: { fontSize: 15, color: colors.text, marginTop: 4 },
  msg: { fontSize: 18, color: colors.text },
});