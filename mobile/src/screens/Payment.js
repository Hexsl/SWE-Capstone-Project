import { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { api } from '../api';
import { colors } from '../theme';
import { Button, Header, Notice } from '../ui';

export default function Payment({ go, session, params }) {
  const fare = params && params.fare;
  // One key per visit to this screen, so a double tap can never charge twice.
  const [key] = useState(() => 'k' + Date.now() + Math.random().toString(36).slice(2));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  if (!fare) {
    return (
      <View>
        <Header title="Payment (Demo)" />
        <View style={{ padding: 14 }}>
          <Button title="Choose a ticket" wide onPress={() => go('tickets')} />
        </View>
      </View>
    );
  }

  async function pay() {
    setError('');
    setBusy(true);
    try {
      const order = await api('/api/purchase/', {
        method: 'POST',
        token: session.token,
        body: { fare_code: fare.code, idempotency_key: key },
      });
      go('confirmation', '', { order });
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScrollView>
      <Header title="Payment (Demo)" />
      <View style={{ padding: 14, paddingTop: 30 }}>
        <View style={s.banner}>
          <Text style={s.bannerText}>DEMO ONLY: no real payment is taken. Do not enter real card details.</Text>
        </View>

        {error ? <Notice kind="error">{error}</Notice> : null}

        <View style={s.box}>
          <Text style={s.small}>Order summary</Text>
          <Text style={s.big}>{fare.name}</Text>
          <Text style={s.small}>Price: ${Number(fare.price_usd).toFixed(2)}</Text>
        </View>

        <View style={s.box}>
          <Text style={s.small}>Payment method</Text>
          <Text style={s.mid}>Demo Card  {'\u2022\u2022\u2022\u2022'} 4242</Text>
        </View>

        <Button title={busy ? 'Processing...' : 'Pay (Demo)'} wide disabled={busy} onPress={pay} />
        <Pressable style={s.cancel} onPress={() => go('tickets')}>
          <Text style={s.cancelText}>Cancel</Text>
        </Pressable>
      </View>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  banner: { backgroundColor: '#cfdff7', borderWidth: 1, borderColor: colors.navy, padding: 16, marginBottom: 22 },
  bannerText: { fontSize: 16, color: colors.text },
  box: { backgroundColor: '#ffffff', borderWidth: 1, borderColor: colors.navy, padding: 16, marginBottom: 18 },
  small: { fontSize: 15, color: colors.text, marginTop: 4 },
  big: { fontSize: 22, color: colors.text, marginVertical: 4 },
  mid: { fontSize: 20, color: colors.text, marginTop: 4 },
  cancel: {
    height: 63, marginTop: 18, backgroundColor: '#ffffff', borderWidth: 1, borderColor: colors.navy,
    alignItems: 'center', justifyContent: 'center',
  },
  cancelText: { fontSize: 26, color: colors.navy },
});