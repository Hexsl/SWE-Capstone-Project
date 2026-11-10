import { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { api } from '../api';
import BottomNav from '../BottomNav';
import Top from '../Top';
import { colors } from '../theme';

export default function More({ go, session, setSession }) {
  const [soon, setSoon] = useState('');
  const rows = [
    ['Bike Locations', null],
    ['Weather', null],
    ['Carbon Footprint', null],
    ['Emergency Contacts', 'emergency'],
    ['Tutorial & Guide', null],
    ['Trip History', 'history'],
    ['Accessibility', 'accessibility'],
  ];
  if (session && session.user.role === 'admin') rows.push(['Admin Dashboard', 'admin']);

  async function logout() {
    try {
      await api('/api/logout/', { method: 'POST', token: session && session.token });
    } catch (e) {}
    setSession(null);
    go('welcome');
  }

  return (
    <View style={{ flex: 1 }}>
      <ScrollView>
        <Top title="More" bg={colors.navy} color="#cbe9f5" height={131} onBack={() => go('home')} />
        <View style={{ padding: 16, paddingTop: 30 }}>
          {session ? <Text style={s.who}>Signed in as {session.user.display_name}</Text> : null}
          {soon ? <Text style={s.soon}>{soon}</Text> : null}
          {rows.map(([label, to]) => (
            <Pressable
              key={label}
              style={s.row}
              onPress={() => (to ? go(to) : setSoon(label + ' is coming in a later sprint.'))}
            >
              <Text style={s.text}>{label}</Text>
            </Pressable>
          ))}
          <Pressable style={[s.row, s.logout]} onPress={logout}>
            <Text style={[s.text, { color: '#ffffff' }]}>Log out</Text>
          </Pressable>
        </View>
      </ScrollView>
      <BottomNav active="more" go={go} />
    </View>
  );
}

const s = StyleSheet.create({
  row: { backgroundColor: '#ffffff', height: 60, justifyContent: 'center', paddingHorizontal: 14, marginBottom: 32 },
  logout: { backgroundColor: colors.navy, marginTop: 8 },
  text: { fontSize: 22, color: colors.text },
  who: { textAlign: 'center', fontSize: 16, color: colors.text, marginBottom: 18 },
  soon: { textAlign: 'center', color: colors.text, backgroundColor: '#faf4c0', padding: 8, marginBottom: 20 },
});