/**
 * Formatting utilities
 * Functions for formatting dates, prices, text, etc.
 */

import { format, formatDistanceToNow, isToday, isYesterday, parseISO } from 'date-fns';

/**
 * Format date to readable string
 */
export const formatDate = (date: string | Date, formatStr = 'PPP'): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, formatStr);
  } catch (error) {
    console.error('[Formatters][formatDate]', error);
    return '';
  }
};

/**
 * Format date to relative time (e.g., "2 hours ago")
 */
export const formatRelativeTime = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return formatDistanceToNow(dateObj, { addSuffix: true });
  } catch (error) {
    console.error('[Formatters][formatRelativeTime]', error);
    return '';
  }
};

/**
 * Format date to smart format (Today, Yesterday, or date)
 */
export const formatSmartDate = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    
    if (isToday(dateObj)) {
      return 'Today';
    }
    
    if (isYesterday(dateObj)) {
      return 'Yesterday';
    }
    
    return formatDate(dateObj);
  } catch (error) {
    console.error('[Formatters][formatSmartDate]', error);
    return '';
  }
};

/**
 * Format currency amount
 */
export const formatCurrency = (
  amount: number,
  currency = 'USD',
  locale = 'en-US'
): string => {
  try {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency,
    }).format(amount);
  } catch (error) {
    console.error('[Formatters][formatCurrency]', error);
    return `${currency} ${amount.toFixed(2)}`;
  }
};

/**
 * Format number with thousand separators
 */
export const formatNumber = (value: number, locale = 'en-US'): string => {
  try {
    return new Intl.NumberFormat(locale).format(value);
  } catch (error) {
    console.error('[Formatters][formatNumber]', error);
    return value.toString();
  }
};

/**
 * Truncate text to specified length
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}...`;
};

/**
 * Capitalize first letter of string
 */
export const capitalize = (text: string): string => {
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
};

/**
 * Format user full name
 */
export const formatFullName = (firstName?: string, lastName?: string): string => {
  const parts = [firstName, lastName].filter(Boolean);
  return parts.length > 0 ? parts.join(' ') : 'User';
};

/**
 * Format initials from name
 */
export const formatInitials = (firstName?: string, lastName?: string): string => {
  const first = firstName?.charAt(0).toUpperCase() || '';
  const last = lastName?.charAt(0).toUpperCase() || '';
  return first + last || 'U';
};
