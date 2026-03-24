import { StyleSheet } from 'react-native';
import { spacing } from '../../../theme/spacing';

export const styles = StyleSheet.create({
  overlay: { 
    flex: 1, 
    backgroundColor: 'rgba(0,0,0,0.6)', 
    justifyContent: 'center', 
    alignItems: 'center' 
  },
  content: { 
    width: '85%', 
    backgroundColor: '#1E293B', 
    borderRadius: 24, 
    padding: spacing.xl, 
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)'
  },
  closeButton: { 
    position: 'absolute', 
    top: 16, 
    right: 16,
    zIndex: 10
  },
  iconContainer: { 
    width: 64, 
    height: 64, 
    borderRadius: 32, 
    backgroundColor: 'rgba(245, 208, 97, 0.1)', 
    justifyContent: 'center', 
    alignItems: 'center', 
    marginBottom: spacing.lg 
  },
  title: { 
    fontSize: 22, 
    fontWeight: '900',
    color: '#FFF', 
    textAlign: 'center', 
    marginBottom: spacing.sm 
  },
  description: { 
    fontSize: 14, 
    color: '#94A3B8', 
    textAlign: 'center', 
    lineHeight: 22, 
    marginBottom: spacing.xl 
  },
  premiumButton: { 
    width: '100%', 
    flexDirection: 'row',
    backgroundColor: '#F5D061', 
    paddingVertical: 16, 
    borderRadius: 16, 
    alignItems: 'center',
    justifyContent: 'center'
  },
  premiumButtonText: { 
    color: '#1A1A1A', 
    fontWeight: '700',
    fontSize: 16 
  },
});
