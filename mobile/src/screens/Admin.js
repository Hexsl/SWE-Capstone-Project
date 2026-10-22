import { useEffect, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { api } from '../api';
import BottomNav from '../BottomNav';
import Top from '../Top';
import { colors } from '../theme';

export default function Admin({ go, session }) {
  const [sum, setSum] = useState(null);
  const [error, setError] = useState('');
  const [soon, setSoon] = useState('');

  useEffect(() => {
    api('/api/admin/summary/', { token: session.token })
      .then(setSum)
      .catch((e) => setError(e.message));
  }, []);

  const tiles = [
    { label: 'Reports', extra: sum ? sum.reports_open + ' New' : '', bg: '#ffd5d5', to: 'reports' },
    { label: 'Create Alert', extra: '', bg: '#faf4c0', to: 'createalert' },
    { label: 'All Map Routes', extra: '', bg: '#d4f0c8', to: null },
    { label: 'All Schedules', extra: '', bg: '#e8dff2', to: null },
  ];

  return (
    <View style={{ flex: 1 }}>
      <ScrollView>
        <Top title="Dashboard" bg={colors.navy} color="#ffffff" height={120} onBack={() => go('more')} />
        <View style={{ padding: 18 }}>
          {error ? <Text style={s.msg}>{error}</Text> : null}
          <View style={s.card}>
            <Text style={s.cardTitle}>Transport</Text>
            <View style={{ flexDirection: 'row', marginTop: 18 }}>
              <Text style={[s.pill, { backgroundColor: '#d4f0c8' }]}>{sum ? sum.stops : '-'}</Text>
              <Text style={s.pillLabel}>Stops</Text>
              <Text style={[s.pill, { backgroundColor: '#c8d0c8' }]}>{sum ? sum.active_alerts : '-'}</Text>
              <Text style={s.pillLabel}>Active alerts</Text>
            </View>
          </View>
          {soon ? <Text style={s.soon}>{soon}</Text> : null}
          <View style={[s.card, { flexDirection: 'row', flexWrap: 'wrap', marginTop: 24 }]}>
            {tiles.map((t) => (
              <Pressable
                key={t.label}
                style={[s.tile, { backgroundColor: t.bg }]}
                onPress={() => (t.to ? go(t.to) : setSoon(t.label + ' is coming in a later sprint.'))}
              >
                <Text style={s.tileText}>{t.label}</Text>
                {t.extra ? <Text style={s.tileText}>{t.extra}</Text> : null}
              </Pressable>
            ))}
          </View>
        </View>
      </ScrollView>
      <BottomNav active="more" go={go} />
    </View>
  );
}

const s = StyleSheet.create({
  card: { backgroundColor: '#ffffff', padding: 16 },
  cardTitle: { fontSize: 22, color: colors.text },
  pill: { fontSize: 22, color: colors.text, paddingHorizontal: 12, paddingVertical: 4, marginRight: 8 },
  pillLabel: { fontSize: 20, color: colors.text, marginRight: 14, alignSelf: 'center' },
  tile: { width: '47%', margin: '1.5%', height: 100, alignItems: 'center', justifyContent: 'center', borderWidth: 1, borderColor: '#d5d5e5' },
  tileText: { fontSize: 20, color: colors.text, textAlign: 'center' },
  msg: { fontSize: 18, color: colors.errorText, marginBottom: 12 },
  soon: { textAlign: 'center', color: colors.text, backgroundColor: '#faf4c0', padding: 8, marginTop: 16 },
});