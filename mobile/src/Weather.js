import { StyleSheet, Text, View } from 'react-native';

export default function Weather() {
  return (
    <View style={s.badge}>
      <Text style={s.temp}>{'76\u00B0'}</Text>
      <Text style={s.cond}>Cloudy</Text>
    </View>
  );
}

const s = StyleSheet.create({
  badge: {
    position: 'absolute', top: 10, left: 10, width: 56, height: 56, borderRadius: 28,
    backgroundColor: '#ffffff', alignItems: 'center', justifyContent: 'center',
  },
  temp: { fontSize: 20 },
  cond: { fontSize: 8 },
});