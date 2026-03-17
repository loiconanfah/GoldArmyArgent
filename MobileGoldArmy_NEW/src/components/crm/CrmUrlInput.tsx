import React from 'react';
import { View, TextInput, StyleSheet, TouchableOpacity, Text, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { spacing } from '../../theme/spacing';

interface Props {
  url: string;
  onChangeUrl: (value: string) => void;
  onSubmit: () => void;
  loading?: boolean;
}

export const CrmUrlInput: React.FC<Props> = ({ url, onChangeUrl, onSubmit, loading }) => {
  const handlePress = () => {
    if (!loading) {
      onSubmit();
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.inputWrapper}>
        <Ionicons name="link-outline" size={16} color="#9A9A94" />
        <TextInput
          style={styles.input}
          placeholder="Colle l'URL LinkedIn, Indeed..."
          placeholderTextColor="#9A9A94"
          value={url}
          onChangeText={onChangeUrl}
          keyboardType="url"
          autoCapitalize="none"
          returnKeyType="done"
        />
      </View>
      <TouchableOpacity activeOpacity={0.9} onPress={handlePress} style={styles.buttonWrapper}>
        <LinearGradient
          colors={['#FF6B35', '#E8521A']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={styles.button}
        >
          {loading ? (
            <ActivityIndicator color="#FFFFFF" size="small" />
          ) : (
            <>
              <Ionicons name="add-outline" size={18} color="#FFFFFF" />
              <Text style={styles.buttonText}>Ajouter</Text>
            </>
          )}
        </LinearGradient>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    marginBottom: spacing.sm,
    marginTop: spacing.xs,
  },
  inputWrapper: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#E2E0DA',
    paddingHorizontal: spacing.md,
    height: 48,
  },
  input: {
    flex: 1,
    marginLeft: spacing.sm,
    fontSize: 13,
    color: '#1A1A18',
  },
  buttonWrapper: {
    marginLeft: spacing.sm,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 48,
    paddingHorizontal: spacing.md,
    borderRadius: 999,
    shadowColor: 'rgba(255,107,53,0.4)',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 1,
    shadowRadius: 10,
    elevation: 3,
  },
  buttonText: {
    marginLeft: 6,
    fontSize: 13,
    fontWeight: '700',
    color: '#FFFFFF',
  },
});

