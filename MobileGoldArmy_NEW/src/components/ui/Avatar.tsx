/**
 * Avatar Component
 * User avatar with fallback initials
 */

import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { Image } from 'expo-image';
import { useTheme } from '@hooks/useTheme';
import { formatInitials } from '@utils/formatters';

interface AvatarProps {
  uri?: string;
  firstName?: string;
  lastName?: string;
  size?: number;
  style?: ViewStyle;
}

const BLURHASH = 'L6PZfSi_.AyE_3t7t7R**0o#DgR4';

export function Avatar({ uri, firstName, lastName, size = 48, style }: AvatarProps) {
  const { theme } = useTheme();
  const initials = formatInitials(firstName, lastName);

  return (
    <View
      style={[
        styles.container,
        {
          width: size,
          height: size,
          borderRadius: size / 2,
          backgroundColor: theme.colors.primary,
        },
        style,
      ]}
    >
      {uri ? (
        <Image
          source={{ uri }}
          placeholder={{ blurhash: BLURHASH }}
          contentFit="cover"
          transition={300}
          style={[
            styles.image,
            {
              width: size,
              height: size,
              borderRadius: size / 2,
            },
          ]}
        />
      ) : (
        <Text
          style={[
            styles.initials,
            {
              fontSize: size * 0.4,
              color: theme.colors.textInverse,
            },
          ]}
        >
          {initials}
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    overflow: 'hidden',
    alignItems: 'center',
    justifyContent: 'center',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  initials: {
    fontWeight: '700',
  },
});
