import { useEffect, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { api } from '../api';
import BottomNav from '../BottomNav';
import Top from '../Top';
import { colors } from '../theme';
import { Button } from '../ui';

export default function PlanTrip({ go, session }) {
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('Times Square, Manhattan');
  const [recent, setRecent] = useState(null);

  useEffect(() => {
    api('/api/trips/', { token: session.token })
      .then((t) => setRecent(t.slice(0, 5)))
      .catch(() => setRecent([]));
  }, []);

  const search = (f, t) => go('results', '', { from: f || 'Current Location', to: t });

  return (
    <View style={{ flex: 1 }}>
      <ScrollView>
        <Top title="Plan a Trip" bg={colors.sky} height={110} onBack={() => go('home')} />
        <View style={{ paddingHorizontal: 28 }}>
          <Text style={s.label}>From:</Text>
          <TextInput style={s.input} value={from} onChangeText={setFrom} placeholder="Current Location" placeholderTextColor="#8a97a8" />
          <Text style={s.label}>To:</Text>
          <TextInput style={s.input} value={to} onChangeText={setTo} />
          <View style={{ alignItems: 'center', marginTop: 24, marginBottom: 40 }}>
            <Button title="Search" onPress={() => search(from, to)} />
          </View>
        </View>

        <View style={s.bar}>
          <Text style={s.barText}>Recent Searches</Text>
        </View>
        <View style={{ backgroundColor: '#ffffff', minHeight: 220 }}>
          {recent && recent.length === 0 ? <Text style={s.msg}>No past trips yet.</Text> : null}
          {recent &&
            recent.map((t) => (
              <Pressable key={t.id} style={s.row} onPress={() => search(t.origin, t.destination)}>
                <Text style={s.rowText}>
                  {t.origin} {'\u2192'} {t.destination}
                </Text>
              </Pressable>
            ))}
        </View>
      </ScrollView>
      <BottomNav active="home" go={go} />
    </View>
  );
}

const s = StyleSheet.create({
  label: { fontSize: 20, color: colors.text, marginBottom: 8, marginTop: 14 },
  input: { height: 46, backgroundColor: '#ffffff', paddingHorizontal: 14, fontSize: 18, color: colors.text },
  bar: { backgroundColor: '#faf4c0', paddingVertical: 10, alignItems: 'center', borderWidth: 1, borderColor: '#e8de9a' },
  barText: { fontSize: 24, color: colors.text },
  row: { padding: 16, borderBottomWidth: 1, borderColor: '#e3e8ee' },
  rowText: { fontSize: 18, color: colors.text },
  msg: { padding: 20, fontSize: 18, color: colors.text },
});