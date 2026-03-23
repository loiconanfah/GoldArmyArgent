import { Modal, View, Text, TouchableOpacity, Linking, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { BlurView } from 'expo-blur';
import { styles } from './styles/PaywallModal.styles';

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
