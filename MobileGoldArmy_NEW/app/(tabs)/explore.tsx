/**
 * Explore Screen
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { ScreenWrapper } from '../../src/components/layout/ScreenWrapper';
import { Header } from '../../src/components/layout/Header';
import { useTheme } from '../../src/hooks/useTheme';
import { spacing } from '../../src/theme/spacing';
import { typography } from '../../src/theme';

export default function ExploreScreen() {
  const { theme } = useTheme();

  return (
    <ScreenWrapper>
      <Header title="Explorer" />
      <View style={styles.container}>
        <Text style={[styles.text, { color: theme.colors.text }]}>
          Explore Screen
        </Text>
      </View>
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
  },
  text: {
    ...typography.h2,
  },
});
