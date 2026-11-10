import { useCallback, useEffect, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { api } from '../api';
import Top from '../Top';
import { Notice } from '../ui';
import { colors } from '../theme';

export const toF = (c) => Math.round((c * 9) / 5 + 32);
const toMph = (kph) => Math.round(kph * 0.621371);

// "2026-11-09T00:00:00-05:00" -> a Date for that calendar day, whatever timezone the phone is in
function dayOf(iso) {
  const [y, m, d] = iso.slice(0, 10).split('-').map(Number);
  return new Date(y, m - 1, d);
}

function whenText(iso) {
  return new Date(iso).toLocaleString([], { weekday: 'short', hour: 'numeric', minute: '2-digit' });
}

export default function WeatherScreen({ go }) {
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setError('');
    try {
      setReport(await api('/api/weather/'));
    } catch (e) {
      setError(e.message);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const cur = report && report.current;

  return (
    <ScrollView>
      <Top title="Weather" bg={colors.navy} color="#cbe9f5" height={136} onBack={() => go('more')} />
      <View style={{ padding: 16, paddingTop: 24 }}>
        {error ? (
          <View>
            <Notice kind="error">{error}</Notice>
            <Pressable style={s.retry} onPress={load} accessibilityRole="button">
              <Text style={s.retryText}>Try again</Text>
            </Pressable>
          </View>
        ) : null}
        {!report && !error ? <Text style={s.loading}>Loading weather...</Text> : null}

        {report ? (
          <View>
            {report.stale ? (
              <Notice kind="error">Couldn't refresh the weather. This is the last saved report and may be out of date.</Notice>
            ) : null}

            {report.alerts.map((a, i) => (
              <View key={i} style={s.alert} accessibilityRole="alert">
                <Text style={s.alertTitle}>{a.event} ({a.severity})</Text>
                <Text style={s.alertBody}>{a.headline}</Text>
              </View>
            ))}

            <View style={s.card}>
              <Text style={s.place}>New York City</Text>
              <Text style={s.temp} accessibilityLabel={`${toF(cur.temp_c)} degrees Fahrenheit, ${cur.conditions}`}>
                {toF(cur.temp_c)}{'°'}F
              </Text>
              <Text style={s.cond}>{cur.conditions}</Text>
              <View style={s.facts}>
                <Text style={s.fact}>Feels like {toF(cur.feels_like_c)}{'°'}F</Text>
                <Text style={s.fact}>
                  Rain chance {cur.precip_chance != null ? `${cur.precip_chance}%` : 'n/a'}
                  {cur.precip_mm ? `, ${cur.precip_mm} mm now` : ''}
                </Text>
                <Text style={s.fact}>Wind {toMph(cur.wind_kph)} mph{cur.wind_dir ? ` ${cur.wind_dir}` : ''}</Text>
              </View>
              {report.updated_at ? <Text style={s.updated}>Updated {whenText(report.updated_at)}</Text> : null}
            </View>

            {report.advice.length ? (
              <View style={s.advice}>
                {report.advice.map((t) => (
                  <Text key={t} style={s.adviceText}>{'•'} {t}</Text>
                ))}
              </View>
            ) : null}

            <Text style={s.heading} accessibilityRole="header">Next 48 hours</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 20 }}>
              {report.hourly.map((h) => (
                <View key={h.time} style={s.hour}>
                  <Text style={s.hourTime}>{new Date(h.time).toLocaleTimeString([], { hour: 'numeric' })}</Text>
                  <Text style={s.hourTemp}>{toF(h.temp_c)}{'°'}</Text>
                  <Text style={s.hourCond}>{h.conditions}</Text>
                  {h.precip_chance != null ? <Text style={s.hourCond}>{h.precip_chance}%</Text> : null}
                </View>
              ))}
            </ScrollView>

            <Text style={s.heading} accessibilityRole="header">Daily forecast</Text>
            {report.daily.map((d) => (
              <View key={d.date} style={s.day}>
                <Text style={s.dayName}>{dayOf(d.date).toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' })}</Text>
                <Text style={s.dayCond}>{d.conditions}{d.precip_chance != null ? `, ${d.precip_chance}%` : ''}</Text>
                <Text style={s.dayTemp}>{toF(d.high_c)}{'°'} / {toF(d.low_c)}{'°'}</Text>
              </View>
            ))}
            <Text style={s.credit}>Weather data by Open-Meteo.com. Alerts from the National Weather Service.</Text>
          </View>
        ) : null}
      </View>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  loading: { textAlign: 'center', fontSize: 16, color: colors.text, marginTop: 20 },
  retry: { alignSelf: 'center', backgroundColor: colors.navy, paddingVertical: 10, paddingHorizontal: 28, borderRadius: 4 },
  retryText: { color: '#ffffff', fontSize: 18 },
  card: { backgroundColor: '#ffffff', padding: 18, marginBottom: 16, alignItems: 'center' },
  place: { fontSize: 18, color: colors.text },
  temp: { fontSize: 64, color: colors.text, fontWeight: '300' },
  cond: { fontSize: 22, color: colors.text },
  facts: { marginTop: 12, alignItems: 'center' },
  fact: { fontSize: 16, color: colors.text, marginTop: 2 },
  updated: { fontSize: 13, color: colors.placeholder, marginTop: 12 },
  alert: { backgroundColor: '#fde8e6', borderLeftWidth: 5, borderLeftColor: '#c0392b', padding: 12, marginBottom: 12 },
  alertTitle: { fontSize: 17, fontWeight: '700', color: colors.errorText },
  alertBody: { fontSize: 14, color: colors.errorText, marginTop: 4 },
  advice: { backgroundColor: '#faf4c0', padding: 12, marginBottom: 20 },
  adviceText: { fontSize: 15, color: colors.text, marginVertical: 2 },
  heading: { fontSize: 22, fontWeight: '700', color: colors.text, marginBottom: 10 },
  hour: { backgroundColor: '#ffffff', width: 84, padding: 8, marginRight: 8, alignItems: 'center' },
  hourTime: { fontSize: 14, color: colors.text },
  hourTemp: { fontSize: 22, color: colors.text, marginVertical: 2 },
  hourCond: { fontSize: 11, color: colors.text, textAlign: 'center' },
  day: { backgroundColor: '#ffffff', padding: 12, marginBottom: 8, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  dayName: { fontSize: 16, color: colors.text, width: 110 },
  dayCond: { fontSize: 14, color: colors.text, flex: 1 },
  dayTemp: { fontSize: 16, color: colors.text },
  credit: { fontSize: 12, color: colors.placeholder, textAlign: 'center', marginTop: 16 },
});
