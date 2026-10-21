import { Platform } from 'react-native';

// In the browser preview the app talks to Django on this computer.
// On a real phone this must be your computer's Wi-Fi address, e.g. http://192.168.1.20:8080
const API_URL = Platform.OS === 'web' ? 'http://127.0.0.1:8080' : 'http://192.168.0.10:8080';

export async function api(path, { method = 'GET', body, token } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers.Authorization = `Bearer ${token}`;
  let res;
  try {
    res = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (e) {
    throw new Error('Cannot reach the server. Is Django running?');
  }
  let data = null;
  try {
    data = await res.json();
  } catch (e) {}
  if (!res.ok) {
    throw new Error((data && (data.error || data.detail)) || 'Something went wrong.');
  }
  return data;
}