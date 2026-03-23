import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, ActivityIndicator, RefreshControl } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import * as Notifications from 'expo-notifications';
import { notificationService, Notification as AppNotification } from '../src/services/notificationService';
import { styles } from './_styles/notifications.styles';

export default function NotificationsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
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

  const handlePressNotif = async (notif: AppNotification) => {
    if (!notif.is_read) {
      await notificationService.markAsRead(notif.id);
      
      const newNotifs = notifications.map(n => n.id === notif.id ? { ...n, is_read: true } : n);
      setNotifications(newNotifs);
      
      const unread = newNotifs.filter(n => !n.is_read).length;
      Notifications.setBadgeCountAsync(unread).catch(console.error);
    }
    // Si besoin d'action_url (ex: /analytics)
  };

  const renderItem = ({ item }: { item: AppNotification }) => {
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
