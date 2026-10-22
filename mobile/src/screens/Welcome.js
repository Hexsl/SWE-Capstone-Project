import { StyleSheet, Text, View } from 'react-native';
import Svg, { Circle, Path, Rect } from 'react-native-svg';
import { colors } from '../theme';
import { Button, Notice } from '../ui';

export default function Welcome({ go, notice }) {
  return (
    <View style={s.screen}>
      <Svg width={180} height={180} viewBox="0 0 180 180">
        <Rect width={180} height={180} rx={44} fill="#233b5d" />
        <Path d="M62 112 H92 Q108 112 108 96 V84 Q108 68 124 68 H138" fill="none" stroke="#cbe9f5" strokeWidth={9} strokeLinecap="round" />
        <Path d="M108 100 V120 Q108 126 114 126 H128" fill="none" stroke="#cbe9f5" strokeWidth={9} strokeLinecap="round" />
        <Circle cx={52} cy={112} r={11} fill="#233b5d" stroke="#cbe9f5" strokeWidth={8} />
        <Circle cx={146} cy={68} r={11} fill="#233b5d" stroke="#cbe9f5" strokeWidth={8} />
        <Circle cx={136} cy={126} r={11} fill="#233b5d" stroke="#cbe9f5" strokeWidth={8} />
        <Path d="M60 30 a22 22 0 0 1 22 22 c0 16 -22 38 -22 38 s-22 -22 -22 -38 a22 22 0 0 1 22 -22z" fill="#cbe9f5" />
        <Circle cx={60} cy={52} r={8} fill="#233b5d" />
      </Svg>

      <Text style={s.title}>TransitHub NY</Text>
      <Text style={s.tagline}>Plan. Ride. Explore.</Text>

      {notice ? (
        <View style={{ width: '100%', marginTop: 24 }}>
          <Notice>{notice}</Notice>
        </View>
      ) : null}

      <View style={s.actions}>
        <Button title="Get Started" onPress={() => go('signup')} />
        <View style={{ height: 18 }} />
        <Button title="Log In" light onPress={() => go('login')} />
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  screen: { flex: 1, alignItems: 'center', paddingTop: 120, paddingHorizontal: 24 },
  title: { marginTop: 20, fontSize: 36, fontWeight: '800', color: colors.navyDeep },
  tagline: { fontSize: 22, color: colors.text },
  actions: { marginTop: 'auto', alignItems: 'center', paddingBottom: 90 },
});