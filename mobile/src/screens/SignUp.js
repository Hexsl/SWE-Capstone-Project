import { useState } from 'react';
import { ScrollView, View } from 'react-native';
import { api } from '../api';
import { Button, Field, Header, LinkText, Notice } from '../ui';

export default function SignUp({ go }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit() {
    setError('');
    setBusy(true);
    try {
      await api('/api/signup/', { method: 'POST', body: { name, email, password, confirm } });
      go('welcome', 'Account created! Tap Log In to continue.');
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <ScrollView>
      <Header title="Create Account" />
      <View style={{ padding: 14, paddingTop: 30 }}>
        {error ? <Notice kind="error">{error}</Notice> : null}
        <Field label="Full name" placeholder="Jane Rider" autoCapitalize="words" value={name} onChangeText={setName} />
        <Field label="Email" placeholder="name@example.com" keyboardType="email-address" value={email} onChangeText={setEmail} />
        <Field label="Password" placeholder="At least 10 characters" secureTextEntry value={password} onChangeText={setPassword} />
        <Field label="Confirm password" placeholder="Re-enter password" secureTextEntry value={confirm} onChangeText={setConfirm} />
        <Button title={busy ? 'Creating...' : 'Sign Up'} wide disabled={busy} onPress={submit} />
        <LinkText onPress={() => go('login')}>Already have an account? Log in</LinkText>
      </View>
    </ScrollView>
  );
}