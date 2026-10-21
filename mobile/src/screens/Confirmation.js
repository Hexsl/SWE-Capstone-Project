import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { colors } from '../theme';
import { Button, Header } from '../ui';

export default function Confirmation({ go, params }) {
  const order = (params && params.order) || {};
  const when = order.created_at ? new Date(order.created_at).toLocaleString() : '';

  return (
    <ScrollView>
      <Header title="Purchase Complete" />
      <View style={{ padding: 14, paddingTop: 30 }}>
        <View style={s.box}>
          <Text style={s.title}>Demo receipt</Text>
          <Text style={s.line}>Ticket: {order.ticket}</Text>
          <Text style={s.line}>Order #: {order.receipt_number}</Text>
          <Text style={s.line}>Date: {when}</Text>
          <Text style={s.line}>Status: Demo, no payment taken</Text>
        </View>
        <Button title="Back to Home" wide onPress={() => go('home')} />
      </View>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  box: { backgroundColor: '#ffffff', borderWidth: 1, borderColor: colors.navy, padding: 16, marginBottom: 18 },
  title: { fontSize: 24, color: colors.text, marginBottom: 8 },
  line: { fontSize: 18, color: colors.text, marginVertical: 6 },
});