import React, { useState, useRef, useEffect } from 'react';
import { StyleSheet, View, Text, TouchableOpacity, TextInput, ActivityIndicator, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { authService } from '../../src/services/authService';
import { spacing } from '@theme/spacing';

export default function VerifyOtpScreen() {
  const router = useRouter();
  const { email } = useLocalSearchParams<{ email: string }>();
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [timer, setTimer] = useState(60);
  const inputs = useRef<TextInput[]>([]);

  useEffect(() => {
    let interval = setInterval(() => { if (timer > 0) setTimer(t => t - 1); }, 1000);
    return () => clearInterval(interval);
  }, [timer]);

  const handleTextChange = (text: string, index: number) => {
    const newCode = [...code];
    newCode[index] = text;
    setCode(newCode);
    if (text !== '' && index < 5) inputs.current[index + 1]?.focus();
  };

  const handleVerify = async () => {
    setLoading(true);
    try {
      await authService.verifyOtp(email, code.join(''));
      router.replace('/(tabs)/home');
    } catch (e: any) {
      Alert.alert('Erreur', e.response?.data?.detail || 'Code invalide');
    } finally { setLoading(false); }
  };

  return (
    <LinearGradient colors={['#0F172A', '#1E293B']} style={{flex:1}}>
      <View style={{flex:1, padding: spacing.xl, paddingTop: 60}}>
        <Text style={{fontSize: 28, fontWeight: '800', color: '#FFF', textAlign: 'center'}}>Vérification</Text>
        <Text style={{color: '#94A3B8', textAlign: 'center', marginTop: 10}}>Code envoyé à {email}</Text>
        <View style={{flexDirection: 'row', justifyContent: 'space-between', marginVertical: 40}}>
          {code.map((d, i) => (
            <TextInput key={i} style={styles.input} keyboardType="number-pad" maxLength={1} value={d}
              onChangeText={t => handleTextChange(t, i)} ref={r => { if(r) inputs.current[i]=r; }} />
          ))}
        </View>
        <TouchableOpacity style={styles.btn} onPress={handleVerify} disabled={loading}>
          {loading ? <ActivityIndicator color="#FFF" /> : <Text style={{color:'#FFF', fontWeight:'700'}}>Vérifier</Text>}
        </TouchableOpacity>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  input: { width: 48, height: 56, backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 12, color: '#FFF', textAlign: 'center', fontSize: 24, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  btn: { height: 56, backgroundColor: '#4F46E5', borderRadius: 16, justifyContent: 'center', alignItems: 'center' }
});
