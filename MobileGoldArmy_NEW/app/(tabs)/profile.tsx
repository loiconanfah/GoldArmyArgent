import React from 'react';
import { View, Text, ScrollView } from 'react-native';
import { ScreenWrapper } from '../../src/components/layout/ScreenWrapper';
import { Header } from '../../src/components/layout/Header';
import { Card } from '../../src/components/ui/Card';
import { Avatar } from '../../src/components/ui/Avatar';
import { Button } from '../../src/components/ui/Button';
import { useTheme } from '../../src/hooks/useTheme';
import { useAuth } from '../../src/hooks/useAuth';
import { useAuthStore } from '../../src/stores/authStore';
import { formatFullName } from '../../src/utils/formatters';
import { styles } from './styles/profile.styles';

export default function ProfileScreen() {
  const { theme } = useTheme();
  const { logout } = useAuth();
  const { user } = useAuthStore();

  return (
    <ScreenWrapper>
      <Header title="Profil" />
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.profileHeader}>
          <Avatar
            uri={user?.avatar}
            firstName={user?.firstName}
            lastName={user?.lastName}
            size={80}
          />
          <Text style={[styles.name, { color: theme.colors.text }]}>
            {formatFullName(user?.firstName, user?.lastName)}
          </Text>
          <Text style={[styles.email, { color: theme.colors.textSecondary }]}>
            {user?.email}
          </Text>
        </View>

        <Card style={styles.card}>
          <Text style={[styles.cardTitle, { color: theme.colors.text }]}>
            Informations du compte
          </Text>
          <Text style={[styles.cardText, { color: theme.colors.textSecondary }]}>
            Membre depuis {user?.createdAt ? new Date(user.createdAt).getFullYear() : 'N/A'}
          </Text>
        </Card>

        <Button
          title="Se déconnecter"
          onPress={logout}
          variant="outline"
          fullWidth
          style={styles.logoutButton}
        />
      </ScrollView>
    </ScreenWrapper>
  );
}
