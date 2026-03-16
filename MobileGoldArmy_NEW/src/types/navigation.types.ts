/**
 * Navigation Types
 * Type definitions for Expo Router navigation
 */

import type { NativeStackScreenProps } from '@react-navigation/native-stack';

export type RootStackParamList = {
  '(auth)': undefined;
  '(tabs)': undefined;
  index: undefined;
};

export type AuthStackParamList = {
  login: undefined;
  register: undefined;
  'forgot-password': undefined;
};

export type TabsStackParamList = {
  home: undefined;
  explore: undefined;
  profile: undefined;
  settings: undefined;
};

export type RootStackScreenProps<T extends keyof RootStackParamList> =
  NativeStackScreenProps<RootStackParamList, T>;

export type AuthStackScreenProps<T extends keyof AuthStackParamList> =
  NativeStackScreenProps<AuthStackParamList, T>;

export type TabsStackScreenProps<T extends keyof TabsStackParamList> =
  NativeStackScreenProps<TabsStackParamList, T>;
