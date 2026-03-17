import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { spacing } from '../../theme/spacing';
import { useTheme } from '../../hooks/useTheme';

interface Props {
  onRefresh: () => void;
}

export const CrmHeader: React.FC<Props> = ({ onRefresh }) => {
  const { theme } = useTheme();
  const rotate = React.useRef(new Animated.Value(0)).current;

  const handlePress = () => {
    Animated.timing(rotate, {
      toValue: 1,
      duration: 600,
      useNativeDriver: true,
    }).start(() => {
      rotate.setValue(0);
    });
    onRefresh();
  };

  const spin = rotate.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  return (
    <View style={styles.container}>
      <View>
        <View style={styles.badgeRow}>
          <View style={styles.pillDot} />
          <Text style={styles.badgeText}>KANBAN BOARD</Text>
        </View>
        <View style={styles.titleRow}>
          <Text style={[styles.titleBase, { color: theme.colors.text }]}>
            Central CRM{' '}
          </Text>
          <Text style={styles.titleAccent}>Candidatures</Text>
        </View>
        <Text style={styles.subtitle}>Swipe une card pour changer son statut.</Text>
      </View>
      <TouchableOpacity style={styles.refreshButton} activeOpacity={0.9} onPress={handlePress}>
        <Animated.View style={{ transform: [{ rotate: spin }] }}>
          <Ionicons name="refresh-outline" size={16} color="#4A4A46" />
        </Animated.View>
        <Text style={styles.refreshText}>Actualiser</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
    paddingBottom: spacing.sm,
  },
  badgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 999,
    backgroundColor: '#FFFBEB',
    marginBottom: spacing.xs,
  },
  pillDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#F59E0B',
    marginRight: 6,
  },
  badgeText: {
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 1,
    textTransform: 'uppercase',
    color: '#92400E',
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  titleBase: {
    fontSize: 26,
    fontWeight: '800',
  },
  titleAccent: {
    fontSize: 26,
    fontWeight: '800',
    color: '#FF6B35',
  },
  subtitle: {
    marginTop: 4,
    fontSize: 12,
    color: '#9A9A94',
  },
  refreshButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: 999,
    backgroundColor: '#F5F4F0',
    borderWidth: 1,
    borderColor: '#E2E0DA',
    marginTop: spacing.xs,
  },
  refreshText: {
    marginLeft: 6,
    fontSize: 13,
    color: '#4A4A46',
    fontWeight: '500',
  },
});

