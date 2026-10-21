import { Pressable, StyleSheet, Text, View } from 'react-native';
import { colors } from './theme';

const items = [
  { key: 'home', icon: '\u{1F3E0}', label: 'Home' },
  { key: 'stops', icon: '\u{1F5FA}\uFE0F', label: 'Map' },
  { key: 'tickets', icon: '\u{1F3AB}', label: 'Tickets' },
  { key: 'more', icon: '\u2630', label: 'More' },
];

export default function BottomNav({ active, go }) {
  return (
    <View style={s.bar}>
      {items.map((it) => (
        <Pressable key={it.key} style={s.item} onPress={() => go(it.key)}>
          <Text style={s.icon}>{it.icon}</Text>
          <Text style={[s.label, active === it.key && s.active]}>{it.label}</Text>
        </Pressable>
      ))}
    </View>
  );
}

const s = StyleSheet.create({
  bar: { flexDirection: 'row', backgroundColor: '#ffffff', borderTopWidth: 1, borderColor: '#d5dde6', paddingVertical: 8 },
  item: { flex: 1, alignItems: 'center' },
  icon: { fontSize: 26 },
  label: { fontSize: 16, color: colors.navy },
  active: { fontWeight: '700' },
});