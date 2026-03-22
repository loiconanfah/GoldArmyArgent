import React from 'react';
import { Modal, View, Text, TouchableOpacity, StyleSheet, Linking } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { BlurView } from 'expo-blur';
import { spacing } from '../../theme/spacing';

interface PaywallModalProps {
  visible: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  url?: string;
}

export function PaywallModal({ 
  visible, 
  onClose, 
  title = "Limite Atteinte", 
  description = "Vous avez utilisé toutes vos recherches Sniper pour aujourd'hui. Revenez dans 24h ou débloquez l'intelligence artificielle en illimité.",
  url = "https://goldarmyai.com"
}: PaywallModalProps) {
  return (
    <Modal visible={visible} transparent animationType="fade">
      <View style={styles.overlay}>
        <BlurView intensity={30} tint="dark" style={StyleSheet.absoluteFillObject} />
        
        <View style={styles.content}>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Ionicons name="close" size={24} color="#999" />
          </TouchableOpacity>
          
          <View style={styles.iconContainer}>
            <Ionicons name="rocket-outline" size={32} color="#F5D061" />
          </View>
          
          <Text style={styles.title}>{title}</Text>
          <Text style={styles.description}>{description}</Text>
          
          <TouchableOpacity 
            style={styles.premiumButton} 
            activeOpacity={0.8}
            onPress={() => {
              Linking.openURL(url).catch(console.error);
              onClose();
            }}
          >
            <Text style={styles.premiumButtonText}>Découvrir Premium</Text>
            <Ionicons name="sparkles" size={16} color="#1A1A1A" style={{ marginLeft: 6 }} />
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: { 
    flex: 1, 
    backgroundColor: 'rgba(0,0,0,0.6)', 
    justifyContent: 'center', 
    alignItems: 'center' 
  },
  content: { 
    width: '85%', 
    backgroundColor: '#1E293B', 
    borderRadius: 24, 
    padding: spacing.xl, 
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)'
  },
  closeButton: { 
    position: 'absolute', 
    top: 16, 
    right: 16,
    zIndex: 10
  },
  iconContainer: { 
    width: 64, 
    height: 64, 
    borderRadius: 32, 
    backgroundColor: 'rgba(245, 208, 97, 0.1)', 
    justifyContent: 'center', 
    alignItems: 'center', 
    marginBottom: spacing.lg 
  },
  title: { 
    fontSize: 22, 
    fontFamily: 'Inter-Black', 
    color: '#FFF', 
    textAlign: 'center', 
    marginBottom: spacing.sm 
  },
  description: { 
    fontSize: 14, 
    fontFamily: 'Inter-Regular', 
    color: '#94A3B8', 
    textAlign: 'center', 
    lineHeight: 22, 
    marginBottom: spacing.xl 
  },
  premiumButton: { 
    width: '100%', 
    flexDirection: 'row',
    backgroundColor: '#F5D061', 
    paddingVertical: 16, 
    borderRadius: 16, 
    alignItems: 'center',
    justifyContent: 'center'
  },
  premiumButtonText: { 
    color: '#1A1A1A', 
    fontFamily: 'Inter-Bold', 
    fontSize: 16 
  },
});
