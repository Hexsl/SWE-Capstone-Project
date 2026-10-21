import { Pressable, Text, View } from 'react-native';

export default function Top({ title, onBack, bg, color = '#2b4062', height = 124, children }) {
  return (
    <View style={{ backgroundColor: bg, height, justifyContent: 'flex-end', paddingHorizontal: 14, paddingBottom: 14 }}>
      <Pressable onPress={onBack}>
        <Text style={{ color, fontSize: 22, fontWeight: '700' }}>{'\u2190'}  {title}</Text>
      </Pressable>
      {children}
    </View>
  );
}