/**
 * Register Form Component
 * Registration form with react-hook-form and zod validation
 */

import React, { useState } from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '@hooks/useAuth';
import { useTheme } from '@hooks/useTheme';
import { Button } from '@components/ui/Button';
import { Input } from '@components/ui/Input';
import { registerSchema, type RegisterFormData } from '@utils/validators';
import { spacing } from '@theme/spacing';
import { Ionicons } from '@expo/vector-icons';

export function RegisterForm() {
  const { theme } = useTheme();
  const { register, isLoading } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: '',
      password: '',
      confirmPassword: '',
      firstName: '',
      lastName: '',
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      await register(data.email, data.password, data.firstName, data.lastName);
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
        name="firstName"
        render={({ field: { onChange, onBlur, value } }) => (
          <Input
            label="First Name (Optional)"
            value={value}
            onChangeText={onChange}
            onBlur={onBlur}
            error={errors.firstName?.message}
            autoCapitalize="words"
            leftIcon={<Ionicons name="person-outline" size={20} color={theme.colors.textMuted} />}
          />
        )}
      />

      <Controller
        control={control}
        name="lastName"
        render={({ field: { onChange, onBlur, value } }) => (
          <Input
            label="Last Name (Optional)"
            value={value}
            onChangeText={onChange}
            onBlur={onBlur}
            error={errors.lastName?.message}
            autoCapitalize="words"
            leftIcon={<Ionicons name="person-outline" size={20} color={theme.colors.textMuted} />}
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
            autoComplete="password-new"
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

      <Controller
        control={control}
        name="confirmPassword"
        render={({ field: { onChange, onBlur, value } }) => (
          <Input
            label="Confirm Password"
            value={value}
            onChangeText={onChange}
            onBlur={onBlur}
            error={errors.confirmPassword?.message}
            secureTextEntry={!showConfirmPassword}
            autoCapitalize="none"
            autoComplete="password-new"
            leftIcon={<Ionicons name="lock-closed-outline" size={20} color={theme.colors.textMuted} />}
            rightIcon={
              <TouchableOpacity onPress={() => setShowConfirmPassword(!showConfirmPassword)}>
                <Ionicons
                  name={showConfirmPassword ? 'eye-off-outline' : 'eye-outline'}
                  size={20}
                  color={theme.colors.textMuted}
                />
              </TouchableOpacity>
            }
          />
        )}
      />

      <Button
        title="Créer mon compte"
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
