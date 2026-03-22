import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

import { getAccessToken } from '../../src/utils/storage';
import { API_BASE_URL } from '../../src/utils/constants';
import { styles } from './_styles/mentor-simulator-result.styles';

export default function MentorSimulatorResultScreen() {
  const { sessionId } = useLocalSearchParams<{ sessionId: string }>();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResult = async () => {
      try {
         if (!sessionId) return;
         const token = await getAccessToken();
         const res = await fetch(`${API_BASE_URL}/api/interview/history/${sessionId}`, {
           headers: { Authorization: `Bearer ${token}` }
         });
         const json = await res.json();
         if (res.ok) {
           setData(json);
         }
      } catch (err) {
         console.warn(err);
      } finally {
         setLoading(false);
      }
    };
    fetchResult();
  }, [sessionId]);

  if (loading) {
    return (
      <View style={styles.root}>
        <StatusBar style="light" />
        <View style={[styles.loaderContainer, { paddingTop: insets.top + 50 }]}>
           <ActivityIndicator size="large" color="#4F46E5" />
           <Text style={styles.loaderText}>Récupération de l'analyse...</Text>
        </View>
      </View>
    );
  }

  if (!data) {
    return (
      <View style={[styles.root, { alignItems: 'center', justifyContent: 'center' }]}>
         <Text style={{ color: '#FFF' }}>Analyse introuvable.</Text>
         <TouchableOpacity onPress={() => router.replace('/(tabs)/mentor')} style={styles.bottomBtn}>
           <Text style={styles.bottomBtnText}>Retour</Text>
         </TouchableOpacity>
      </View>
    );
  }

  const { scores, feedback, decision, job_title, company } = data;
  
  const getDecisionColor = (dec: string) => {
    if(dec?.toLowerCase().includes('favorable')) return { bg: 'rgba(16, 185, 129, 0.2)', txt: '#34D399' };
    if(dec?.toLowerCase().includes('défavorable')) return { bg: 'rgba(239, 68, 68, 0.2)', txt: '#F87171' };
    return { bg: 'rgba(245, 158, 11, 0.2)', txt: '#FBBF24' }; // Réservé
  };

  const decColor = getDecisionColor(decision);

  return (
    <View style={styles.root}>
      <StatusBar style="light" />
      <ScrollView 
        style={styles.scroll} 
        contentContainerStyle={[styles.content, { paddingTop: insets.top + 20 }]}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.headerRow}>
          <TouchableOpacity onPress={() => router.replace('/(tabs)/mentor')} style={styles.closeBtn}>
            <Ionicons name="close" size={20} color="#FFF" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Bilan de l'Entretien</Text>
        </View>

        {/* Global Summary */}
        <View style={styles.summaryCard}>
           <View style={[styles.decisionBadge, { backgroundColor: decColor.bg }]}>
             <Text style={[styles.decisionText, { color: decColor.txt }]}>{decision}</Text>
           </View>
           <View style={styles.scoreRow}>
             <Text style={styles.overallScore}>{scores?.overall || 0}</Text>
             <Text style={styles.scoreMax}>/10</Text>
           </View>
           <Text style={styles.rolesText}>{job_title} chez {company}</Text>
        </View>

        {/* Mini Scores */}
        <View style={styles.scoresGrid}>
           <View style={styles.miniScoreBox}>
             <Text style={styles.miniScoreVal}>{scores?.technical || 0}</Text>
             <Text style={styles.miniScoreLabel}>Technique</Text>
           </View>
           <View style={styles.miniScoreBox}>
             <Text style={styles.miniScoreVal}>{scores?.communication || 0}</Text>
             <Text style={styles.miniScoreLabel}>Communication</Text>
           </View>
           <View style={styles.miniScoreBox}>
             <Text style={styles.miniScoreVal}>{scores?.soft_skills || 0}</Text>
             <Text style={styles.miniScoreLabel}>Soft Skills</Text>
           </View>
        </View>

        {/* Points Forts */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
             <Ionicons name="trending-up" size={20} color="#10B981" />
             <Text style={styles.sectionTitle}>Points Forts</Text>
          </View>
          {feedback?.points_forts?.map((pf: string, i: number) => (
            <View key={i} style={styles.pointItemRow}>
               <View style={styles.pointDotContent}><Ionicons name="checkmark-circle" size={16} color="#10B981" /></View>
               <Text style={styles.pointText}>{pf}</Text>
            </View>
          ))}
        </View>

        {/* Points d'Amélioration */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
             <Ionicons name="trending-down" size={20} color="#F59E0B" />
             <Text style={styles.sectionTitle}>Axes d'Amélioration</Text>
          </View>
          {feedback?.points_amelioration?.map((pa: string, i: number) => (
            <View key={i} style={styles.pointItemRow}>
               <View style={styles.pointDotContent}><Ionicons name="alert-circle" size={16} color="#F59E0B" /></View>
               <Text style={styles.pointText}>{pa}</Text>
            </View>
          ))}
        </View>

        {/* Conseils */}
        {feedback?.conseils && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
               <Ionicons name="bulb-outline" size={20} color="#6366F1" />
               <Text style={styles.sectionTitle}>Conseils HR</Text>
            </View>
            <Text style={styles.adviceText}>"{feedback.conseils}"</Text>
          </View>
        )}

        {/* Action */}
        <TouchableOpacity style={styles.bottomBtn} onPress={() => router.replace('/(tabs)/mentor')}>
          <Text style={styles.bottomBtnText}>Terminer</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}
