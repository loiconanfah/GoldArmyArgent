import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, ActivityIndicator, Alert, StyleSheet, Platform, Animated } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useAuth } from '../src/hooks/useAuth';
import { profileService, UserProfile } from '../src/services/profileService';

const tiers = [
  {
    name: 'Gratuit',
    id: 'tier-free',
    price: '0€',
    description: 'Pour débuter votre conquête du marché.',
    features: [
      '2 recherches Sniper / jour',
      '2 audits de CV (Mentor IA)',
      '1 entretien RH vocal',
      '5 relances automatiques',
      '3 adaptations de CV par IA',
      'Accès communautaire',
    ],
    unavailable: [
      'Usage Headhunter',
      'Carnet d\'adresses privé',
      'Portfolio personnalisé'
    ],
    buttonText: 'Plan Actuel',
    highlighted: false,
    icon: 'shield-checkmark',
    gradientColors: ['#1E293B', '#0F172A'],
    iconColor: '#94A3B8'
  },
  {
    name: 'Essentiel',
    id: 'tier-essential',
    price: '9.99€',
    description: 'Le choix des vainqueurs (Conseillé).',
    features: [
      '25 recherches Sniper / mois',
      '10 audits de CV ATS',
      '10 entretiens RH vocaux',
      '10 usages Headhunter',
      '25 places au carnet d\'adresses',
      'Relances illimitées',
      'Adaptations CV illimitées',
    ],
    unavailable: [],
    buttonText: 'Choisir Essentiel',
    highlighted: true,
    icon: 'star',
    gradientColors: ['rgba(245, 158, 11, 0.1)', 'rgba(245, 158, 11, 0.02)'], 
    iconColor: '#F59E0B'
  },
  {
    name: 'Pro',
    id: 'tier-pro',
    price: '19.99€',
    description: 'Puissance de feu maximale pour l\'élite.',
    features: [
      'Recherches Sniper illimitées',
      '20 audits de CV approfondis',
      '15 entretiens RH IA',
      'Headhunter illimité (Automation)',
      'Carnet d\'adresses illimité',
      'Portfolio personnalisé IA',
      'Support Prioritaire 24/7',
    ],
    unavailable: [],
    buttonText: 'Devenir Pro',
    highlighted: false,
    icon: 'rocket',
    gradientColors: ['rgba(99, 102, 241, 0.15)', 'rgba(99, 102, 241, 0.05)'],
    iconColor: '#818CF8'
  }
];

export default function SettingsScreen() {
  const router = useRouter();
  const { user, deleteAccount } = useAuth();
  const [isSubscribing, setIsSubscribing] = useState<string | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  React.useEffect(() => {
    profileService.getProfile()
      .then(data => setProfile(data))
      .catch(err => console.log('Err fetching profile', err))
      .finally(() => setLoading(false));
  }, []);

  // Fallback to FREE if user tier is empty
  const userTier = profile?.subscription_tier || 'FREE';
  const userName = profile?.full_name || 'Utilisateur';

  const handleSubscribe = async (tierId: string) => {
    if (isSubscribing) return;
    
    const tierMap: Record<string, string> = {
      'tier-free': 'FREE',
      'tier-essential': 'ESSENTIAL',
      'tier-pro': 'PRO'
    };
    const tier = tierMap[tierId];
    
    if (tier === 'FREE') {
       router.push('/(tabs)/home');
       return;
    }
    
    if (tier === userTier) {
      Alert.alert("Info", "Vous êtes déjà sur ce forfait.");
      return;
    }

    setIsSubscribing(tierId);
    try {
      // Fake delay to simulate backend request
      await new Promise(resolve => setTimeout(resolve, 1500));
      Alert.alert("Succès", "Redirection vers la page de paiement Stripe (Simulation).");
    } catch (err) {
      Alert.alert("Erreur", "Erreur de connexion au service de paiement.");
    } finally {
      setIsSubscribing(null);
    }
  };

  const handleAlertChange = (title: string) => {
    Alert.alert(title, "Cette fonctionnalité sera bientôt connectée au backend Gemini 3.1.", [{ text: "OK", style: "default" }]);
  };

  const handleDeleteAccount = () => {
    Alert.alert(
      "Suppression du compte", 
      "Attention, cette action est irréversible. Toutes vos données seront effacées.", 
      [
        { text: "Annuler", style: "cancel" },
        { 
          text: "Confirmer la suppression", 
          style: "destructive", 
          onPress: async () => {
            try {
              await deleteAccount();
            } catch (err) {
              Alert.alert("Erreur", "La suppression a échoué. Veuillez réessayer.");
            }
          } 
        }
      ]
    );
  };

  const getTiers = () => {
    return tiers.map(t => {
      let isActive = (t.id === 'tier-free' && userTier === 'FREE') || 
                     (t.id === 'tier-essential' && userTier === 'ESSENTIAL') ||
                     (t.id === 'tier-pro' && userTier === 'PRO');
      
      let buttonText = isActive ? 'Plan Actuel' : t.buttonText;
      let tierName = t.name;

      if (t.id === 'tier-pro' && userTier === 'ADMIN') {
        isActive = true;
        buttonText = 'Plan Admin GoldArmy';
        tierName = 'Admin';
      }

      return {
        ...t,
        name: tierName,
        buttonText,
        highlighted: t.id === 'tier-essential' || isActive,
        isActive
      };
    });
  };

  return (
    <SafeAreaView style={styles.root}>
      <StatusBar style="light" />
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color="#94A3B8" />
        </TouchableOpacity>
        <View style={styles.headerTitleContainer}>
          <Text style={styles.title}>Paramètres <Text style={styles.titleHighlight}>&</Text> Abonnements</Text>
          <Text style={styles.subtitle}>Optimisez votre arsenal et gérez vos privilèges GoldArmy.</Text>
        </View>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
        
        {/* Pricing Grid */}
        {Platform.OS !== 'ios' && (
          <View style={styles.pricingGrid}>
          {getTiers().map(tier => (
            <View 
              key={tier.id} 
              style={[
                styles.tierCard, 
                tier.highlighted && styles.tierCardHighlighted
              ]}
            >
              {tier.highlighted && (
                <LinearGradient
                   colors={['rgba(245, 158, 11, 0.15)', 'transparent']}
                   style={[StyleSheet.absoluteFillObject, { borderRadius: 24 }]}
                   start={{ x: 0.5, y: 0 }}
                   end={{ x: 0.5, y: 1 }}
                />
              )}
              {tier.highlighted && (
                <View style={styles.popularBadge}>
                  <LinearGradient
                    colors={['#F5D061', '#F59E0B']}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 0 }}
                    style={styles.popularBadgeGradient}
                  >
                    <Text style={styles.popularBadgeText}>LE PLUS POPULAIRE</Text>
                  </LinearGradient>
                </View>
              )}
              
              <View style={styles.tierHeader}>
                <View style={[styles.iconContainer, { backgroundColor: tier.gradientColors[0] }]}>
                  <Ionicons name={tier.icon as any} size={26} color={tier.iconColor} />
                </View>
                <Text style={styles.tierName}>{tier.name}</Text>
                <View style={styles.priceRow}>
                  <Text style={styles.tierPrice}>{tier.price}</Text>
                  <Text style={styles.tierPriceSub}>/ mois</Text>
                </View>
                <Text style={styles.tierDesc}>{tier.description}</Text>
              </View>

              <View style={styles.featuresContainer}>
                {tier.features.map((feat, idx) => (
                  <View key={`feat-${idx}`} style={styles.featureRow}>
                    <View style={styles.checkIconWrapper}>
                      <Ionicons name="checkmark" size={14} color="#10B981" />
                    </View>
                    <Text style={styles.featureText}>{feat}</Text>
                  </View>
                ))}
                {tier.unavailable.map((unfeat, idx) => (
                  <View key={`unfeat-${idx}`} style={[styles.featureRow, { opacity: 0.4 }]}>
                    <View style={styles.crossIconWrapper}>
                      <View style={styles.horizontalLine} />
                    </View>
                    <Text style={[styles.featureText, { textDecorationLine: 'line-through' }]}>{unfeat}</Text>
                  </View>
                ))}
              </View>

              <TouchableOpacity 
                style={[styles.subscribeBtnWrapper, isSubscribing === tier.id && { opacity: 0.7 }]}
                onPress={() => handleSubscribe(tier.id)}
                disabled={isSubscribing !== null}
                activeOpacity={0.8}
              >
                <LinearGradient
                  colors={tier.highlighted ? ['#F5D061', '#F59E0B'] : ['#334155', '#1E293B']}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                  style={[styles.subscribeBtn, tier.highlighted ? styles.subscribeBtnHighlighted : styles.subscribeBtnNormal]}
                >
                  {isSubscribing === tier.id ? (
                    <ActivityIndicator color={tier.highlighted ? '#1E293B' : '#FFF'} />
                  ) : (
                    <Text style={[
                        styles.subscribeBtnText, 
                        tier.highlighted ? styles.subscribeBtnTextHighlighted : styles.subscribeBtnTextNormal
                      ]}
                    >
                      {tier.buttonText}
                    </Text>
                  )}
                </LinearGradient>
              </TouchableOpacity>
            </View>
          ))}
        </View>
        )}

        {/* Extra Settings Section */}
        <View style={styles.extraSettings}>
          {/* AI Settings - Hidden on iOS for review if not implemented */}
          {Platform.OS !== 'ios' && (
            <View style={styles.settingSection}>
              <View style={styles.settingSectionHeader}>
                <View style={[styles.sectionIconBg, { backgroundColor: 'rgba(99, 102, 241, 0.1)' }]}>
                  <Ionicons name="sparkles" size={20} color="#6366F1" />
                </View>
                <Text style={styles.settingSectionTitle}>Préférences IA</Text>
              </View>
              
              <TouchableOpacity style={styles.settingItem} onPress={() => handleAlertChange("Précision Sniper")}>
                <View>
                  <Text style={styles.settingLabel}>Précision de filtrage Sniper</Text>
                  <Text style={styles.settingSubLabel}>Définit le niveau de sévérité de Gemini 3.1</Text>
                </View>
                <Text style={styles.settingValueText}>Standard (Auto)</Text>
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.settingItem} onPress={() => handleAlertChange("Voix de l'entretien")}>
                <View>
                  <Text style={styles.settingLabel}>Voix de l'entretien</Text>
                  <Text style={styles.settingSubLabel}>Sélectionnez le profil vocal du recruteur IA</Text>
                </View>
                <Text style={styles.settingValueText}>Recruteur Standard</Text>
              </TouchableOpacity>
            </View>
          )}

          {/* Profile & Privacy */}
          <View style={styles.settingSection}>
            <View style={styles.settingSectionHeader}>
              <View style={[styles.sectionIconBg, { backgroundColor: 'rgba(16, 185, 129, 0.1)' }]}>
                <Ionicons name="people" size={20} color="#10B981" />
              </View>
              <Text style={styles.settingSectionTitle}>Profil & Confidentialité</Text>
            </View>

            <View style={styles.profileBadge}>
              <View style={styles.profileBadgeAvatar}>
                <Text style={styles.profileBadgeAvatarText}>{userName.charAt(0).toUpperCase()}</Text>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.profileBadgeName}>{userName}</Text>
                <Text style={styles.profileBadgeTier}>
                  {userTier === 'ADMIN' ? 'Administrateur GoldArmy' : 
                   userTier === 'PRO' ? 'Membre GoldArmy Pro' : 'Utilisateur GoldArmy'}
                </Text>
              </View>
            </View>

             <TouchableOpacity style={styles.deleteAccountBtn} onPress={handleDeleteAccount}>
                <Text style={styles.deleteAccountBtnText}>Supprimer mon compte et mes données</Text>
             </TouchableOpacity>

          </View>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#0F172A', // Dark mode by default for premium feel
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: Platform.OS === 'android' ? 40 : 10,
    paddingBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#1E293B',
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: '#1E293B',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  headerTitleContainer: {
    flex: 1,
  },
  title: {
    fontSize: 22,
    fontWeight: '900',
    color: '#FFF',
  },
  titleHighlight: {
    color: '#F59E0B',
  },
  subtitle: {
    fontSize: 12,
    color: '#94A3B8',
    marginTop: 2,
  },
  scroll: {
    flex: 1,
  },
  content: {
    padding: 20,
    paddingBottom: 40,
  },
  pricingGrid: {
    gap: 24,
    marginBottom: 40,
  },
  tierCard: {
    backgroundColor: '#1E293B',
    borderRadius: 32,
    padding: 24,
    borderWidth: 1,
    borderColor: '#334155',
    position: 'relative',
    overflow: 'hidden',
  },
  tierCardHighlighted: {
    borderColor: '#F59E0B',
    backgroundColor: '#1E293B',
    shadowColor: '#F59E0B',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.15,
    shadowRadius: 20,
    elevation: 8,
  },
  popularBadge: {
    position: 'absolute',
    top: -1,
    alignSelf: 'center',
  },
  popularBadgeGradient: {
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderBottomLeftRadius: 16,
    borderBottomRightRadius: 16,
  },
  popularBadgeText: {
    fontSize: 10,
    fontWeight: '900',
    color: '#0F172A',
    letterSpacing: 1.5,
  },
  tierHeader: {
    marginBottom: 24,
    marginTop: 8,
  },
  iconContainer: {
    width: 60,
    height: 60,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    borderWidth: 1,
    borderColor: 'rgba(245, 158, 11, 0.1)',
  },
  tierName: {
    fontSize: 24,
    fontWeight: '900',
    color: '#FFF',
    marginBottom: 4,
    letterSpacing: -0.5,
  },
  priceRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: 12,
  },
  tierPrice: {
    fontSize: 42,
    fontWeight: '900',
    color: '#FFF',
    letterSpacing: -1,
  },
  tierPriceSub: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#94A3B8',
    marginLeft: 6,
    textTransform: 'uppercase',
  },
  tierDesc: {
    fontSize: 14,
    color: '#94A3B8',
    lineHeight: 20,
    fontWeight: '500',
  },
  featuresContainer: {
    gap: 16,
    marginBottom: 32,
  },
  featureRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  checkIconWrapper: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: 'rgba(16, 185, 129, 0.15)',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(16, 185, 129, 0.3)',
  },
  crossIconWrapper: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#334155',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#475569',
  },
  horizontalLine: {
    width: 6,
    height: 2,
    backgroundColor: '#64748B',
    borderRadius: 1,
  },
  featureText: {
    fontSize: 14,
    color: '#E2E8F0',
    flex: 1,
    fontWeight: '600',
  },
  subscribeBtnWrapper: {
    width: '100%',
    borderRadius: 20,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
  },
  subscribeBtn: {
    width: '100%',
    paddingVertical: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  subscribeBtnNormal: {
    borderWidth: 1,
    borderColor: '#475569',
  },
  subscribeBtnHighlighted: {
    // Gradient handles background
  },
  subscribeBtnText: {
    fontSize: 14,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  subscribeBtnTextNormal: {
    color: '#FFF',
  },
  subscribeBtnTextHighlighted: {
    color: '#0F172A',
  },
  extraSettings: {
    gap: 20,
  },
  settingSection: {
    backgroundColor: '#1E293B',
    borderRadius: 24,
    padding: 24,
    borderWidth: 1,
    borderColor: '#334155',
  },
  settingSectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 20,
  },
  sectionIconBg: {
    width: 40,
    height: 40,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  settingSectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFF',
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  settingLabel: {
    color: '#F8FAFC',
    fontSize: 14,
    fontWeight: '600',
  },
  settingSubLabel: {
    color: '#64748B',
    fontSize: 11,
    marginTop: 2,
    maxWidth: 200,
  },
  settingValueText: {
    color: '#CBD5E1',
    fontSize: 12,
    fontWeight: 'bold',
    backgroundColor: '#334155',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 8,
  },
  profileBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0F172A',
    padding: 15,
    borderRadius: 16,
    gap: 15,
    marginBottom: 15,
  },
  profileBadgeAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(245, 158, 11, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  profileBadgeAvatarText: {
    color: '#F59E0B',
    fontSize: 18,
    fontWeight: 'bold',
  },
  profileBadgeName: {
    color: '#F8FAFC',
    fontSize: 14,
    fontWeight: 'bold',
  },
  profileBadgeTier: {
    color: '#64748B',
    fontSize: 10,
    fontWeight: '900',
    textTransform: 'uppercase',
    marginTop: 2,
  },
  deleteAccountBtn: {
    paddingVertical: 15,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(239, 68, 68, 0.2)',
    borderRadius: 16,
    backgroundColor: 'rgba(239, 68, 68, 0.05)',
  },
  deleteAccountBtnText: {
    color: '#F87171',
    fontSize: 12,
    fontWeight: 'bold',
  }
});
