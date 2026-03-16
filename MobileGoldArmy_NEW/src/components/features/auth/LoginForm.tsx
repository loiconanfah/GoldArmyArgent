/**
 * Login Form Component
 * Login form with react-hook-form and zod validation
 */

import React, { useState } from 'react';
import { View, StyleSheet, TouchableOpacity, Text } from 'react-native';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '@hooks/useAuth';
import { useTheme } from '@hooks/useTheme';
import { Button } from '@components/ui/Button';
import { Input } from '@components/ui/Input';
import { loginSchema, type LoginFormData } from '@utils/validators';
import { spacing } from '@theme/spacing';
import { Ionicons } from '@expo/vector-icons';

export function LoginForm() {
  const { theme } = useTheme();
  const { login, isLoading } = useAuth();
  const [showPassword, setShowPassword] = useState(false);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      await login(data.email, data.password);
    } catch (error) {
      // Error handled by useAuth hook
    }
  };

  return (
    <View style={styles.container}>
      <Controller
        control={control}
        name="email"
        render={({ field: { onChange, onBlur, value } }) => (
          <Input
            label="Email"
            value={value}
            onChangeText={onChange}
            onBlur={onBlur}
            error={errors.email?.message}
            keyboardType="email-address"
            autoCapitalize="none"
            autoComplete="email"
            leftIcon={<Ionicons name="mail-outline" size={20} color={theme.colors.textMuted} />}
          />
        )}
      />

      <Controller
        control={control}
        name="password"
        render={({ field: { onChange, onBlur, value } }) => (
          <Input
            label="Password"
            value={value}
            onChangeText={onChange}
            onBlur={onBlur}
            error={errors.password?.message}
            secureTextEntry={!showPassword}
            autoCapitalize="none"
            autoComplete="password"
            leftIcon={<Ionicons name="lock-closed-outline" size={20} color={theme.colors.textMuted} />}
            rightIcon={
              <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                <Ionicons
                  name={showPassword ? 'eye-off-outline' : 'eye-outline'}
                  size={20}
                  color={theme.colors.textMuted}
                />
              </TouchableOpacity>
            }
          />
        )}
      />

      <Button
        title="Se connecter"
        onPress={handleSubmit(onSubmit)}
        loading={isLoading}
        fullWidth
        style={styles.button}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: '100%',
  },
  button: {
    marginTop: spacing.lg,
  },
});
