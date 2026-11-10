import { useCallback, useEffect, useState } from 'react';
import { Linking, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { api } from '../api';
import Top from '../Top';
import { Notice } from '../ui';
import { colors } from '../theme';

// Order and titles of the groups on screen. Anything with another category goes under "More help".
const GROUPS = [
  ['emergency', 'Emergency'],
  ['police', 'Police'],
  ['transit', 'Transit help'],
  ['city_services', 'City services'],
  ['crisis', 'Crisis support'],
  ['accessibility', 'Accessibility'],
];

const digits = (phone) => phone.replace(/[^\d+]/g, '');

export default function Emergency({ go }) {
  const [items, setItems] = useState(null);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const load = useCallback(async () => {
    setError('');
    setItems(null);
    try {
      const data = await api('/api/emergency/');
      setItems(data.items);
    } catch (e) {
      setError(e.message);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function open(url, fallback) {
    setMessage('');
    try {
      await Linking.openURL(url);
    } catch (e) {
      setMessage(fallback);
    }
  }

  const disclaimer = (items || []).find((i) => i.category === 'instructions');
  const contacts = (items || []).filter((i) => i.category !== 'instructions');
  const known = GROUPS.map(([key]) => key);
  const groups = [
    ...GROUPS.map(([key, title]) => [title, contacts.filter((i) => i.category === key)]),
    ['More help', contacts.filter((i) => !known.includes(i.category))],
  ].filter(([, list]) => list.length > 0);

  return (
    <ScrollView>
      <Top title="Emergency Contacts" bg={colors.navy} color="#cbe9f5" height={136} onBack={() => go('more')} />
      <View style={{ padding: 16, paddingTop: 24 }}>
        {disclaimer ? (
          <View style={s.disclaimer} accessibilityRole="alert">
            <Text style={s.disclaimerTitle}>{disclaimer.name}</Text>
            <Text style={s.disclaimerBody}>{disclaimer.when_to_use}</Text>
          </View>
        ) : null}
        {message ? <Notice kind="error">{message}</Notice> : null}
        {error ? (
          <View>
            <Notice kind="error">{error}</Notice>
            <Pressable style={s.retry} onPress={load} accessibilityRole="button">
              <Text style={s.retryText}>Try again</Text>
            </Pressable>
          </View>
        ) : null}
        {!items && !error ? <Text style={s.loading}>Loading help numbers...</Text> : null}

        {groups.map(([title, list]) => (
          <View key={title}>
            <Text style={s.groupTitle} accessibilityRole="header">{title}</Text>
            {list.map((c) => (
              <View key={c.key} style={s.card}>
                <Text style={s.name}>{c.name}</Text>
                <Text style={s.when}>{c.when_to_use}</Text>
                {c.phone ? <Text style={s.number}>{c.phone}</Text> : null}
                <View style={s.actions}>
                  {c.phone ? (
                    <Pressable
                      style={s.action}
                      accessibilityRole="button"
                      accessibilityLabel={`Call ${c.name}`}
                      onPress={() => open(`tel:${digits(c.phone)}`, `Can't place calls from this device. Dial ${c.phone}.`)}
                    >
                      <Text style={s.actionText}>Call</Text>
                    </Pressable>
                  ) : null}
                  {c.sms ? (
                    <Pressable
                      style={[s.action, s.actionLight]}
                      accessibilityRole="button"
                      accessibilityLabel={`Text ${c.name}`}
                      onPress={() => open(`sms:${digits(c.sms)}`, `Can't send texts from this device. Text ${c.sms}.`)}
                    >
                      <Text style={[s.actionText, { color: colors.navy }]}>Text</Text>
                    </Pressable>
                  ) : null}
                  {c.url ? (
                    <Pressable
                      style={[s.action, s.actionLight]}
                      accessibilityRole="link"
                      accessibilityLabel={`${c.url.startsWith('mailto:') ? 'Email' : 'Website for'} ${c.name}`}
                      onPress={() => open(c.url, `Can't open ${c.url} from this device.`)}
                    >
                      <Text style={[s.actionText, { color: colors.navy }]}>
                        {c.url.startsWith('mailto:') ? 'Email' : 'Website'}
                      </Text>
                    </Pressable>
                  ) : null}
                </View>
              </View>
            ))}
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  disclaimer: { backgroundColor: '#fde8e6', borderLeftWidth: 5, borderLeftColor: '#c0392b', padding: 12, marginBottom: 20 },
  disclaimerTitle: { fontSize: 17, fontWeight: '700', color: colors.errorText },
  disclaimerBody: { fontSize: 15, color: colors.errorText, marginTop: 4 },
  groupTitle: { fontSize: 22, fontWeight: '700', color: colors.text, marginTop: 8, marginBottom: 12 },
  card: { backgroundColor: '#ffffff', padding: 14, marginBottom: 16 },
  name: { fontSize: 19, fontWeight: '700', color: colors.text },
  when: { fontSize: 15, color: colors.text, marginTop: 4 },
  number: { fontSize: 22, color: colors.text, marginTop: 8 },
  actions: { flexDirection: 'row', flexWrap: 'wrap', marginTop: 10 },
  action: { backgroundColor: colors.navy, paddingVertical: 10, paddingHorizontal: 22, borderRadius: 4, marginRight: 10, marginTop: 4, borderWidth: 1, borderColor: colors.navy },
  actionLight: { backgroundColor: '#ffffff' },
  actionText: { color: '#ffffff', fontSize: 17 },
  loading: { textAlign: 'center', fontSize: 16, color: colors.text, marginTop: 20 },
  retry: { alignSelf: 'center', backgroundColor: colors.navy, paddingVertical: 10, paddingHorizontal: 28, borderRadius: 4 },
  retryText: { color: '#ffffff', fontSize: 18 },
});
