import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { colors } from './theme';

export function Header({ title }) {
  return (
    <View style={s.header}>
      <Text style={s.headerText}>{title}</Text>
    </View>
  );
}

export function Field({ label, ...props }) {
  return (
    <View style={{ marginBottom: 17 }}>
      <Text style={s.label}>{label}</Text>
      <TextInput
        placeholderTextColor={colors.placeholder}
        autoCapitalize="none"
        style={s.input}
        {...props}
      />
    </View>
  );
}

export function Button({ title, onPress, light, wide, disabled }) {
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled}
      style={[
        s.btn,
        wide && s.btnWide,
        light && s.btnLight,
        disabled && { opacity: 0.6 },
      ]}
    >
      <Text style={[s.btnText, light && { color: colors.navy }, wide && { fontSize: 26 }]}>{title}</Text>
    </Pressable>
  );
}

export function Notice({ kind = 'ok', children }) {
  const error = kind === 'error';
  return (
    <View style={[s.notice, { backgroundColor: error ? colors.errorBg : colors.okBg }]}>
      <Text style={{ color: error ? colors.errorText : colors.okText, fontSize: 16 }}>{children}</Text>
    </View>
  );
}

export function LinkText({ children, onPress }) {
  return (
    <Pressable onPress={onPress}>
      <Text style={s.link}>{children}</Text>
    </Pressable>
  );
}

const s = StyleSheet.create({
  header: { backgroundColor: colors.navy, height: 174, paddingTop: 52, paddingLeft: 56 },
  headerText: { color: colors.white, fontSize: 24 },
  label: { fontSize: 15, color: colors.text, marginBottom: 6 },
  input: {
    height: 52,
    paddingHorizontal: 15,
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: colors.navy,
    borderRadius: 2,
    fontSize: 20,
    color: colors.text,
  },
  btn: {
    width: 241,
    paddingVertical: 16,
    alignItems: 'center',
    backgroundColor: colors.navy,
    borderRadius: 4,
  },
  btnWide: { width: '100%', height: 63, justifyContent: 'center', paddingVertical: 0, borderRadius: 2 },
  btnLight: { width: 201, paddingVertical: 10, backgroundColor: colors.white },
  btnText: { color: colors.white, fontSize: 22 },
  notice: { padding: 12, borderRadius: 2, marginBottom: 20 },
  link: { color: colors.text, fontSize: 18, textAlign: 'center', marginTop: 22 },
});