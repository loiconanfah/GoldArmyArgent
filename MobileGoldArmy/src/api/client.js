/**
 * Client API pour GoldArmy - réutilise les mêmes endpoints que le frontend web
 */
import { getApiUrl } from '../config';
import * as SecureStore from 'expo-secure-store';

const TOKEN_KEY = 'goldarmy_token';

export async function getStoredToken() {
  try {
    return await SecureStore.getItemAsync(TOKEN_KEY);
  } catch {
    return null;
  }
}

export async function setStoredToken(token) {
  try {
    if (token) await SecureStore.setItemAsync(TOKEN_KEY, token);
    else await SecureStore.deleteItemAsync(TOKEN_KEY);
  } catch (e) {
    console.warn('SecureStore set/delete failed', e);
  }
}

async function authFetch(path, options = {}) {
  const token = await getStoredToken();
  const url = getApiUrl(path);
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };
  const res = await fetch(url, { ...options, headers });
  if (res.status === 401) {
    await setStoredToken(null);
    throw new Error('Unauthorized');
  }
  return res;
}

// —— Auth ——
export async function login(email, password) {
  const body = new URLSearchParams();
  body.append('username', email);
  body.append('password', password);
  const url = getApiUrl('/api/auth/login');
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Accept: 'application/json',
    },
    body: body.toString(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Login failed');
  }
  const data = await res.json();
  await setStoredToken(data.access_token);
  return data;
}

export async function register(email, password) {
  const res = await authFetch('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Register failed');
  }
  return res.json();
}

export async function getMe() {
  const res = await authFetch('/api/auth/me');
  if (!res.ok) throw new Error('Not authenticated');
  return res.json();
}

export async function logout() {
  await setStoredToken(null);
}

// —— Chat / Agent (exemple) ——
export async function chat(message, options = {}) {
  const res = await authFetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      session_id: options.session_id || 'mobile',
      ...options,
    }),
  });
  if (!res.ok) throw new Error('Chat request failed');
  return res.json();
}
