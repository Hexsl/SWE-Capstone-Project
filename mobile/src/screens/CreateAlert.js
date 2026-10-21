import { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { api } from '../api';
import BottomNav from '../BottomNav';
import Top from '../Top';
import { colors } from '../theme';
import { Button, Notice } from '../ui';

const types = ['Service Change', 'Delay', 'Planned Work', 'Elevator Outage'];
const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

export default function CreateAlert({ go, session }) {
  const [type, setType] = useState(types[0]);
  const [days, setDays] = useState([]);
  const [start, setStart] = useState('06:00');
  const [end, setEnd] = useState('17:00');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const toggle = (d) => setDays(days.includes(d) ? days.filter((x) => x !== d) : [...days, d]);
  const nextType = () => setType(types[(types.indexOf(type) + 1) % types.length]);

  async function submit() {
    setBusy(true);
    setError('');
    setMessage('');
    try {
      await api('/api/admin/alerts/', {
        method: 'POST',
        token: session.token,
        body: { type, days, start_time: start, end_time: end },
      });
      setMessage('Alert created. It now shows in Real-Time Updates.');
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <View style={{ flex: 1 }}>
      <ScrollView>
        <Top title="Create an Alert" bg={colors.navy} color="#ffffff" height={120} onBack={() => go('admin')} />
        <View style={{ padding: 18 }}>
          {error ? <Notice kind="error">{error}</Notice> : null}
          {message ? <Notice>{message}</Notice> : null}

          <View style={s.card}>
            <Text style={s.label}>Type of Alert:</Text>
            <Pressable style={s.select} onPress={nextType}>
              <Text style={s.selectText}>{type}   v</Text>
            </Pressable>
            <Text style={s.hint}>Tap to change the type</Text>
          </View>

          <View style={[s.card, { marginTop: 18 }]}>
            <View style={{ flexDirection: 'row' }}>
              <View style={{ flex: 1 }}>
                {dayNames.map((d) => (
                  <Pressable key={d} onPress={() => toggle(d)} style={[s.day, days.includes(d) && s.dayOn]}>
                    <Text style={s.dayText}>{d}</Text>
                  </Pressable>
                ))}
              </View>
              <View style={{ flex: 1, alignItems: 'center', paddingLeft: 12 }}>
                <Text style={s.label}>Start Time:</Text>
                <TextInput style={s.time} value={start} onChangeText={setStart} />
                <Text style={[s.label, { marginTop: 18 }]}>End Time:</Text>
                <TextInput style={s.time} value={end} onChangeText={setEnd} />
              </View>
            </View>
          </View>

          <View style={{ alignItems: 'center', marginTop: 24 }}>
            <Button title={busy ? 'Creating...' : 'Create Alert'} disabled={busy} onPress={submit} />
          </View>
        </View>
      </ScrollView>
      <BottomNav active="more" go={go} />
    </View>
  );
}

const s = StyleSheet.create({
  card: { backgroundColor: '#ffffff', padding: 14 },
  label: { fontSize: 20, color: colors.text },
  select: { marginTop: 14, backgroundColor: '#dfe6df', borderWidth: 1, borderColor: '#c8d0c8', padding: 10 },
  selectText: { fontSize: 22, color: colors.text },
  hint: { fontSize: 13, color: '#5f7388', marginTop: 6 },
  day: { backgroundColor: '#cfdff7', borderWidth: 1, borderColor: '#b8c9e8', height: 46, justifyContent: 'center', paddingHorizontal: 14, marginBottom: 10 },
  dayOn: { backgroundColor: colors.navy },
  dayText: { fontSize: 18, color: colors.text },
  time: { width: 110, height: 46, backgroundColor: '#cfdff7', borderWidth: 1, borderColor: '#b8c9e8', textAlign: 'center', fontSize: 20, color: colors.text, marginTop: 6 },
});