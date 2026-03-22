import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, ActivityIndicator, RefreshControl } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { notificationService, Notification } from '../src/services/notificationService';
import { spacing } from '../src/theme/spacing';
import * as Notifications from 'expo-notifications';

export default function NotificationsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadNotifications = async () => {
    try {
      const data = await notificationService.getNotifications();
      setNotifications(data);
      const unread = data.filter(n => !n.is_read).length;
      Notifications.setBadgeCountAsync(unread).catch(console.error);
    } catch(e) {
      console.error(e);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    loadNotifications();
  }, []);

  const handleMarkAllRead = async () => {
    await notificationService.markAllAsRead();
    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    Notifications.setBadgeCountAsync(0).catch(console.error);
  };

  const handlePressNotif = async (notif: Notification) => {
    if (!notif.is_read) {
      await notificationService.markAsRead(notif.id);
      
      const newNotifs = notifications.map(n => n.id === notif.id ? { ...n, is_read: true } : n);
      setNotifications(newNotifs);
      
      const unread = newNotifs.filter(n => !n.is_read).length;
      Notifications.setBadgeCountAsync(unread).catch(console.error);
    }
    // Si besoin d'action_url (ex: /analytics)
  };

  const renderItem = ({ item }: { item: Notification }) => {
    let iconName: any = "information-circle";
    let iconColor = "#60A5FA";
    if (item.type === 'success') { iconName = "checkmark-circle"; iconColor = "#10B981"; }
    else if (item.type === 'warning') { iconName = "warning"; iconColor = "#F5D061"; }
    else if (item.type === 'error') { iconName = "alert-circle"; iconColor = "#EF4444"; }

    return (
      <TouchableOpacity 
        style={[styles.notifCard, !item.is_read && styles.notifCardUnread]} 
        activeOpacity={0.7}
        onPress={() => handlePressNotif(item)}
      >
        <View style={styles.notifIcon}>
          <Ionicons name={iconName} size={24} color={iconColor} />
        </View>
        <View style={styles.notifContent}>
          <Text style={styles.notifTitle}>{item.title}</Text>
          <Text style={styles.notifMessage}>{item.message}</Text>
          <Text style={styles.notifTime}>{new Date(item.created_at).toLocaleString('fr-FR', { day:'2-digit', month:'short', hour:'2-digit', minute:'2-digit' })}</Text>
        </View>
        {!item.is_read && <View style={styles.unreadDot} />}
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.root}>
      <StatusBar style="dark" />
      <View style={[styles.header, { paddingTop: insets.top }]}>
        <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
          <Ionicons name="chevron-back" size={24} color="#1A1A1A" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Notifications</Text>
        <TouchableOpacity style={styles.markReadBtn} onPress={handleMarkAllRead}>
          <Ionicons name="checkmark-done-outline" size={24} color="#1A1A1A" />
        </TouchableOpacity>
      </View>

      {loading && !refreshing ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color="#F5D061" />
        </View>
      ) : (
        <FlatList
          data={notifications}
          keyExtractor={item => item.id}
          renderItem={renderItem}
          contentContainerStyle={styles.listContent}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#F5D061" />}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Ionicons name="notifications-off-outline" size={48} color="#D1D5DB" />
              <Text style={styles.emptyText}>Aucune notification récente.</Text>
            </View>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#FAFAFA' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.xl,
    paddingBottom: spacing.md,
    backgroundColor: '#FFF',
    borderBottomWidth: 1,
    borderBottomColor: '#F5F5F0',
  },
  backBtn: { padding: spacing.xs },
  markReadBtn: { padding: spacing.xs },
  headerTitle: { fontSize: 18, fontFamily: 'Inter-Bold', color: '#1A1A1A' },
  listContent: { padding: spacing.lg, paddingBottom: 100 },
  notifCard: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    padding: spacing.md,
    borderRadius: 16,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: '#EFEFEF',
  },
  notifCardUnread: {
    backgroundColor: '#F8FAFC',
    borderColor: '#E2E8F0',
  },
  notifIcon: { marginRight: spacing.md, paddingTop: 2 },
  notifContent: { flex: 1 },
  notifTitle: { fontSize: 15, fontFamily: 'Inter-SemiBold', color: '#1A1A1A', marginBottom: 2 },
  notifMessage: { fontSize: 13, fontFamily: 'Inter-Regular', color: '#4B5563', lineHeight: 18 },
  notifTime: { fontSize: 11, fontFamily: 'Inter-Medium', color: '#9CA3AF', marginTop: 6 },
  unreadDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#3B82F6', alignSelf: 'center', marginLeft: 8 },
  emptyContainer: { alignItems: 'center', marginTop: 100 },
  emptyText: { marginTop: spacing.md, fontSize: 15, color: '#9CA3AF', fontFamily: 'Inter-Medium' }
});
