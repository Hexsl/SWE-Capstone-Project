import { useEffect, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { api } from '../api';
import BottomNav from '../BottomNav';
import { colors } from '../theme';
import { Button } from '../ui';

export default function Tickets({ go }) {
  const [fares, setFares] = useState(null);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api('/api/fares/')
      .then(setFares)
      .catch((e) => setError(e.message));
  }, []);

  return (
    <View style={{ flex: 1 }}>
      <ScrollView>
        <View style={s.header}>
          <Pressable onPress={() => go('home')}>
            <Text style={s.title}>{'\u2190'} Purchase Tickets</Text>
          </Pressable>
        </View>

        <View style={s.bar}>
          <Text style={s.barText}>Select Ticket Type</Text>
        </View>

        <View style={{ paddingHorizontal: 12 }}>
          {error ? <Text style={s.msg}>{error}</Text> : null}
          {!fares && !error ? <Text style={s.msg}>Loading...</Text> : null}
          {fares &&
            fares.map((f) => (
              <Pressable
                key={f.code}
                onPress={() => setSelected(f)}
                style={[s.card, selected && selected.code === f.code && s.cardOn]}
              >
                <Text style={s.cardName}>{f.name}</Text>
                <Text style={s.cardPrice}>${Number(f.price_usd).toFixed(2)}</Text>
              </Pressable>
            ))}
        </View>

        <View style={{ alignItems: 'center', marginVertical: 24 }}>
          <Button
            title="Purchase Ticket"
            disabled={!selected}
            onPress={() => go('payment', '', { fare: selected })}
          />
        </View>
      </ScrollView>
      <BottomNav active="tickets" go={go} />
    </View>
  );
}

const s = StyleSheet.create({
  header: { backgroundColor: '#d4f0c8', height: 123, justifyContent: 'flex-end', padding: 14 },
  title: { fontSize: 22, fontWeight: '700', color: colors.text },
  bar: { backgroundColor: '#e8dff2', marginHorizontal: 12, marginTop: 30, marginBottom: 18, padding: 10 },
  barText: { fontSize: 22, color: colors.text },
  card: {
    backgroundColor: '#ffffff', borderRadius: 32, borderWidth: 2, borderColor: '#dde3ea',
    paddingHorizontal: 20, height: 100, marginBottom: 28, justifyContent: 'center',
  },
  cardOn: { borderColor: colors.navy },
  cardName: { fontSize: 22, color: colors.text },
  cardPrice: { fontSize: 18, color: '#5f7388', marginTop: 4 },
  msg: { padding: 16, fontSize: 16, color: colors.text },
});