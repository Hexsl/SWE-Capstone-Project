import { useEffect, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { api } from '../api';
import BottomNav from '../BottomNav';
import Top from '../Top';
import { colors } from '../theme';

const tabs = [['View Reports', ''], ['Received', 'received'], ['In-Progress', 'in_progress']];

export default function Reports({ go, session }) {
  const [status, setStatus] = useState('');
  const [rows, setRows] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    setRows(null);
    setError('');
    api('/api/admin/reports/' + (status ? '?status=' + status : ''), { token: session.token })
      .then(setRows)
      .catch((e) => setError(e.message));
  }, [status]);

  return (
    <View style={{ flex: 1 }}>
      <ScrollView>
        <Top title="User Reports" bg={colors.navy} color="#ffffff" height={120} onBack={() => go('admin')} />
        <View style={{ padding: 18 }}>
          <View style={{ flexDirection: 'row', marginBottom: 8 }}>
            {tabs.map(([label, value]) => (
              <Pressable key={label} onPress={() => setStatus(value)} style={[s.tab, status === value && s.tabOn]}>
                <Text style={s.tabText}>{label}</Text>
              </Pressable>
            ))}
          </View>
          <View style={{ backgroundColor: '#ffffff', minHeight: 300 }}>
            {error ? <Text style={s.msg}>{error}</Text> : null}
            {!rows && !error ? <Text style={s.msg}>Loading...</Text> : null}
            {rows && rows.length === 0 ? <Text style={s.msg}>No reports here.</Text> : null}
            {rows &&
              rows.map((r) => (
                <View key={r.id} style={s.row}>
                  <Text style={{ fontSize: 28 }}>{r.kind === 'problem' ? '\u26A0\uFE0F' : '\u{1F527}'}</Text>
                  <View style={{ flex: 1, marginHorizontal: 12 }}>
                    <Text style={s.title}>{r.subject || r.message}</Text>
                    <Text style={s.meta}>{r.status}</Text>
                  </View>
                  <Text style={s.title}>{'>'}</Text>
                </View>
              ))}
          </View>
        </View>
      </ScrollView>
      <BottomNav active="more" go={go} />
    </View>
  );
}

const s = StyleSheet.create({
  tab: { paddingHorizontal: 10, paddingVertical: 6, backgroundColor: '#dfe6df', marginRight: 6, borderWidth: 1, borderColor: '#c8d0c8' },
  tabOn: { backgroundColor: '#cfdff7' },
  tabText: { fontSize: 15, color: colors.text },
  row: { flexDirection: 'row', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderColor: colors.navy },
  title: { fontSize: 19, color: colors.text },
  meta: { fontSize: 14, color: '#5f7388', marginTop: 2 },
  msg: { padding: 16, fontSize: 17, color: colors.text },
});