import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import { chat, logout } from '../api/client';

export default function HomeScreen({ navigation }) {
  const { user, refreshUser } = useAuth();
  const [message, setMessage] = useState('');
  const [reply, setReply] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!message.trim()) return;
    setLoading(true);
    setReply('');
    try {
      const data = await chat(message.trim());
      const payload = data?.data;
      const text = typeof payload?.content === 'string'
        ? payload.content
        : payload?.message ?? (payload?.content ? JSON.stringify(payload.content) : JSON.stringify(payload));
      setReply(text || 'Réponse reçue.');
    } catch (e) {
      Alert.alert('Erreur', e.message || 'Impossible de contacter l’agent.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    await refreshUser();
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.greeting}>Bonjour, {user?.email ?? 'GoldArmy'}</Text>
        <TouchableOpacity onPress={handleLogout} style={styles.logoutBtn}>
          <Text style={styles.logoutText}>Déconnexion</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Agent GoldArmy</Text>
        <Text style={styles.cardSubtitle}>Pose une question à l’agent (API chat)</Text>
        <TextInput
          style={styles.input}
          placeholder="Votre message..."
          placeholderTextColor="#64748b"
          value={message}
          onChangeText={setMessage}
          multiline
          editable={!loading}
        />
        <TouchableOpacity
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={handleSend}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>Envoyer</Text>
          )}
        </TouchableOpacity>
        {reply ? (
          <View style={styles.replyBox}>
            <Text style={styles.replyLabel}>Réponse</Text>
            <Text style={styles.replyText}>{reply}</Text>
          </View>
        ) : null}
      </View>

      <Text style={styles.hint}>
        L’API backend (auth, chat, opportunités, CRM, etc.) est la même que le site web.
        Tu peux ajouter les écrans Opportunités, CRM, Interview, Profil depuis ici.
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  content: {
    padding: 20,
    paddingBottom: 40,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  greeting: {
    fontSize: 20,
    fontWeight: '600',
    color: '#f8fafc',
  },
  logoutBtn: {
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  logoutText: {
    color: '#94a3b8',
    fontSize: 14,
  },
  card: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#f8fafc',
    marginBottom: 4,
  },
  cardSubtitle: {
    fontSize: 14,
    color: '#94a3b8',
    marginBottom: 16,
  },
  input: {
    backgroundColor: '#334155',
    borderRadius: 12,
    padding: 14,
    fontSize: 16,
    color: '#f8fafc',
    minHeight: 80,
    textAlignVertical: 'top',
    marginBottom: 12,
  },
  button: {
    backgroundColor: '#f59e0b',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  replyBox: {
    marginTop: 16,
    padding: 12,
    backgroundColor: '#334155',
    borderRadius: 12,
  },
  replyLabel: {
    fontSize: 12,
    color: '#94a3b8',
    marginBottom: 6,
  },
  replyText: {
    fontSize: 14,
    color: '#e2e8f0',
  },
  hint: {
    fontSize: 12,
    color: '#64748b',
    textAlign: 'center',
  },
});
