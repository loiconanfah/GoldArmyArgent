/**
 * Toast Component
 * Notification toast with slide-in animation (using React Native Animated)
 */

import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Animated } from 'react-native';
import { BlurView } from 'expo-blur';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '@hooks/useTheme';
import { useUIStore, type ToastType } from '@stores/uiStore';
import { toastStyles as styles, toastContainerStyles } from './styles/Toast.styles';

interface ToastProps {
  id: string;
  message: string;
  type: ToastType;
  onDismiss: (id: string) => void;
}

export function Toast({ id, message, type, onDismiss }: ToastProps) {
  const { theme, colorScheme } = useTheme();
  const translateY = useRef(new Animated.Value(-100)).current;
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.spring(translateY, {
        toValue: 0,
        useNativeDriver: true,
        tension: 50,
        friction: 7,
      }),
      Animated.timing(opacity, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  const handleDismiss = () => {
    Animated.parallel([
      Animated.timing(translateY, {
        toValue: -100,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(opacity, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start(() => onDismiss(id));
  };

  const getIcon = () => {
    switch (type) {
      case 'success':
        return 'checkmark-circle';
      case 'error':
        return 'close-circle';
      case 'warning':
        return 'warning';
      case 'info':
        return 'information-circle';
      default:
        return 'information-circle';
    }
  };

  const getColor = () => {
    switch (type) {
      case 'success':
        return theme.colors.success;
      case 'error':
        return theme.colors.error;
      case 'warning':
        return theme.colors.warning;
      case 'info':
        return theme.colors.info;
      default:
        return theme.colors.primary;
    }
  };

  return (
    <Animated.View
      style={[
        styles.container,
        {
          transform: [{ translateY }],
          opacity,
        },
      ]}
    >
      <BlurView intensity={30} tint={colorScheme} style={styles.blur}>
        <View
          style={[
            styles.toast,
            {
              backgroundColor: theme.colors.surface,
              borderLeftColor: getColor(),
            },
          ]}
        >
          <Ionicons name={getIcon()} size={20} color={getColor()} style={styles.icon} />
          <Text style={[styles.message, { color: theme.colors.text }]}>{message}</Text>
          <TouchableOpacity onPress={handleDismiss} style={styles.closeButton}>
            <Ionicons name="close" size={18} color={theme.colors.textMuted} />
          </TouchableOpacity>
        </View>
      </BlurView>
    </Animated.View>
  );
}

/**
 * Toast Container
 * Renders all active toasts
 */
export function ToastContainer() {
  const { toasts, hideToast } = useUIStore();

  if (toasts.length === 0) return null;

  return (
    <View style={toastContainerStyles.container} pointerEvents="box-none">
      {toasts.map((toast) => (
        <Toast key={toast.id} {...toast} onDismiss={hideToast} />
      ))}
    </View>
  );
}
