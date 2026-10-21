import { ScrollView, StyleSheet, Text, View } from 'react-native';
import BottomNav from '../BottomNav';
import Top from '../Top';
import { colors } from '../theme';

const cards = [
  ['Train', '1 train \u00B7 about 18 min'],
  ['Bus', 'M15 \u00B7 about 35 min'],
  ['Bike', 'Citi Bike \u00B7 about 22 min'],
  ['Walking', 'About 45 min'],
];

export default function Results({ go, params }) {
  const from = (params && params.from) || 'Current Location';
  const to = (params && params.to) || 'Times Square, Manhattan';
  return (
    <View style={{ flex: 1 }}>
      <ScrollView>
        <Top title="Trip Results" bg="#d0e0f8" height={165} onBack={() => go('plan')}>
          <Text style={s.sub}>From: {from}</Text>
          <Text style={s.sub}>To: {to}</Text>
        </Top>
        <Text style={s.note}>Sample results. The route planner engine comes in a later sprint.</Text>
        <View style={{ paddingHorizontal: 26 }}>
          {cards.map(([name, detail]) => (
            <View key={name} style={s.card}>
              <Text style={s.name}>{name}</Text>
              <Text style={s.detail}>{detail}</Text>
            </View>
          ))}
        </View>
      </ScrollView>
      <BottomNav active="home" go={go} />
    </View>
  );
}

const s = StyleSheet.create({
  sub: { color: colors.text, fontSize: 16, fontWeight: '700', marginLeft: 26 },
  note: { textAlign: 'center', color: '#5f7388', fontSize: 14, marginVertical: 14 },
  card: {
    backgroundColor: '#ffffff', borderRadius: 30, borderWidth: 1, borderColor: '#dde3ea',
    height: 110, marginBottom: 20, alignItems: 'center', justifyContent: 'center',
  },
  name: { fontSize: 22, color: '#000000' },
  detail: { fontSize: 16, color: '#5f7388', marginTop: 4 },
});