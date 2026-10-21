import { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { api } from '../api';
import BottomNav from '../BottomNav';
import Top from '../Top';
import { colors } from '../theme';
import { Button } from '../ui';

const WRENCH = ['reroute', 'planned_work', 'elevator_outage', 'escalator_outage', 'skipped_stops'];

function look(a) {
  if (a.is_planned) return { bg: '#d4f0c8', border: '#b8dfae', icon: '\u{1F552}' };
  if (WRENCH.includes(a.effect)) return { bg: '#faf4c0', border: '#e8de9a', icon: '\u{1F527}' };
  return { bg: '#ffd5d5', border: '#f0b0b0', icon: '\u26A0\uFE0F' };
}

export default function Updates({ go }) {
  const [data, setData] = useState(null);
  const [all, setAll] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    api('/api/alerts/')
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  const items = data ? [...data.current, ...data.planned] : [];
  const shown = all ? items : items.slice(0, 3);

  return (
    <View style={{ flex: 1 }}>
      <ScrollView>
        <Top title="Service Alerts" bg="#f5dcee" onBack={() => go('home')} />
        <View style={{ padding: 22 }}>
          {error ? <Text style={s.msg}>{error}</Text> : null}
          {!data && !error ? <Text style={s.msg}>Loading...</Text> : null}
          {data && items.length === 0 ? <Text style={s.msg}>No alerts right now.</Text> : null}
          {shown.map((a) => {
            const l = look(a);
            return (
              <View key={a.alert_id} style={[s.card, { backgroundColor: l.bg, borderColor: l.border }]}>
                <Text style={{ fontSize: 30 }}>{l.icon}</Text>
                <Text style={s.header}>{a.header}</Text>
                {a.description ? <Text style={s.desc}>{a.description}</Text> : null}
                {a.route_ids && a.route_ids.length > 0 ? <Text style={s.desc}>Lines: {a.route_ids.join(', ')}</Text> : null}
                {a.is_planned ? <Text style={s.desc}>Planned work</Text> : null}
              </View>
            );
          })}
          {items.length > 3 ? (
            <View style={{ alignItems: 'center', marginTop: 10 }}>
              <Button title={all ? 'Show Fewer' : 'View All Alerts'} onPress={() => setAll(!all)} />
            </View>
          ) : null}
        </View>
      </ScrollView>
      <BottomNav active="home" go={go} />
    </View>
  );
}

const s = StyleSheet.create({
  card: { borderWidth: 1, padding: 14, marginBottom: 18 },
  header: { fontSize: 22, color: colors.text, marginTop: 6 },
  desc: { fontSize: 15, color: colors.text, marginTop: 6 },
  msg: { fontSize: 18, color: colors.text },
});