import { useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { api } from '../api';
import BottomNav from '../BottomNav';
import Weather from '../Weather';
import { colors } from '../theme';

const tiles = [
  { label: 'Plan a Trip', bg: '#cfe0f7', to: 'plan' },
  { label: 'Nearby Stops', bg: '#d4f0c8', to: 'stops' },
  { label: 'Real-Time Updates', bg: '#f5dcee', to: 'updates' },
  { label: 'Buy Tickets', bg: '#e8dff2', to: 'tickets' },
];

export default function Home({ go, session, setSession }) {
  const [soon, setSoon] = useState('');

  async function logout() {
    try {
      await api('/api/logout/', { method: 'POST', token: session && session.token });
    } catch (e) {}
    setSession(null);
    go('welcome');
  }

  return (
    <View style={{ flex: 1 }}>
      <View style={s.header}>
        <View style={s.topRow}>
          <Text style={s.greeting}>Hi, {session && session.user.display_name}</Text>
          <Pressable onPress={() => go('more')} style={s.avatar}>
            <Text style={{ fontSize: 26 }}>{'\u{1F464}'}</Text>
          </Pressable>
        </View>
        <TextInput style={s.search} placeholder="Search for a route, stop, or location..." placeholderTextColor="#5f7388" />
      </View>

      <View style={s.map}>
        <Weather />
        <Text style={s.mapText}>MAP</Text>
      </View>

      {soon ? <Text style={s.soon}>{soon}</Text> : null}
      <View style={s.grid}>
        {tiles.map((t) => (
          <Pressable
            key={t.label}
            style={[s.tile, { backgroundColor: t.bg }]}
            onPress={() => (t.to ? go(t.to) : setSoon(t.label + ' is coming in the next sprint.'))}
          >
            <Text style={s.tileText}>{t.label}</Text>
          </Pressable>
        ))}
      </View>

      <BottomNav active="home" go={go} />
    </View>
  );
}

const s = StyleSheet.create({
  header: { backgroundColor: colors.navy, paddingTop: 20, paddingHorizontal: 22, paddingBottom: 16 },
  topRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 },
  greeting: { color: colors.white, fontSize: 18 },
  avatar: { width: 46, height: 46, borderRadius: 23, backgroundColor: '#6aaaf7', alignItems: 'center', justifyContent: 'center' },
  search: {
    height: 42, borderRadius: 21, borderWidth: 1, borderColor: '#0b1a2e',
    backgroundColor: colors.sky, paddingHorizontal: 14, fontSize: 16, color: colors.text,
  },
  map: { flex: 1, backgroundColor: colors.sky, alignItems: 'center', justifyContent: 'center' },
  mapText: { fontSize: 80, color: '#000000' },
  soon: { textAlign: 'center', color: colors.text, backgroundColor: '#ffffff', padding: 8 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', backgroundColor: '#ffffff', padding: 8 },
  tile: {
    width: '48%', margin: '1%', height: 102, borderRadius: 8, borderWidth: 1, borderColor: '#c9cfe6',
    alignItems: 'center', justifyContent: 'center',
  },
  tileText: { fontSize: 20, fontWeight: '700', color: colors.text, textAlign: 'center' },
});