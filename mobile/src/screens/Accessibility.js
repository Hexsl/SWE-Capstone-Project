import { useState } from 'react';
import { ScrollView, StyleSheet, Switch, Text, View } from 'react-native';
import Top from '../Top';
import { colors } from '../theme';

const options = ['Larger Text', 'High Contrast', 'Screen reader', 'Voice Navigation', 'Accessible Routes Only'];

export default function Accessibility({ go }) {
  const [on, setOn] = useState({});
  return (
    <ScrollView>
      <Top title="Accessibility" bg={colors.navy} color="#cbe9f5" height={136} onBack={() => go('more')} />
      <View style={{ padding: 16, paddingTop: 40 }}>
        {options.map((label) => (
          <View key={label} style={s.row}>
            <Text style={s.text}>{label}</Text>
            <Switch value={!!on[label]} onValueChange={(v) => setOn({ ...on, [label]: v })} />
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  row: {
    backgroundColor: '#ffffff', height: 60, paddingHorizontal: 14, marginBottom: 27,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
  },
  text: { fontSize: 22, color: colors.text },
});