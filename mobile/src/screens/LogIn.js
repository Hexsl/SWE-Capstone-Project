import { useState } from 'react';
import { ScrollView, View } from 'react-native';
import { api } from '../api';
import { Button, Field, Header, LinkText, Notice } from '../ui';

export default function LogIn({ go, setSession }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit() {
    setError('');
    setBusy(true);
    try {
      const data = await api('/api/login/', { method: 'POST', body: { email, password } });
      setSession({ token: data.token, user: data.user });
      go('home');
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScrollView>
      <Header title="Log In" />
      <View style={{ padding: 14, paddingTop: 30 }}>
        {error ? <Notice kind="error">{error}</Notice> : null}
        <Field label="Email" placeholder="name@example.com" keyboardType="email-address" value={email} onChangeText={setEmail} />
        <Field label="Password" placeholder="Enter your password" secureTextEntry value={password} onChangeText={setPassword} />
        <Button title={busy ? 'Logging in...' : 'Log In'} wide disabled={busy} onPress={submit} />
        <LinkText onPress={() => {}}>Forgot password?</LinkText>
        <LinkText onPress={() => go('signup')}>New here? Create an account</LinkText>
      </View>
    </ScrollView>
  );
}