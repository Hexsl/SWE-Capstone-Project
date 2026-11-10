import { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { api } from './api';

// Small temperature badge shown on the map screens. Fetches live weather from the backend.
export default function Weather() {
  const [now, setNow] = useState(null); // { temp, cond }, or 'error'

  useEffect(() => {
    let alive = true;
    api('/api/weather/')
      .then((r) => alive && setNow({ temp: Math.round((r.current.temp_c * 9) / 5 + 32), cond: r.current.conditions }))
      .catch(() => alive && setNow('error'));
    return () => {
      alive = false;
    };
  }, []);

  const failed = now === 'error';
  return (
    <View
      style={s.badge}
      accessibilityLabel={now && !failed ? `${now.temp} degrees, ${now.cond}` : 'Weather unavailable'}
    >
      <Text style={s.temp}>{now && !failed ? `${now.temp}°` : '--'}</Text>
      <Text style={s.cond} numberOfLines={1}>{now && !failed ? now.cond : ''}</Text>
    </View>
  );
}

const s = StyleSheet.create({
  badge: {
    position: 'absolute', top: 10, left: 10, width: 56, height: 56, borderRadius: 28,
    backgroundColor: '#ffffff', alignItems: 'center', justifyContent: 'center',
  },
  temp: { fontSize: 20 },
  cond: { fontSize: 8, maxWidth: 50 },
});
