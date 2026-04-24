import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';

interface EndorsementBadgeProps {
  type: string;
  count: number;
}

const ENDORSEMENT_CONFIG: Record<string, { icon: string; label: string }> = {
  skill: { icon: 'trophy', label: 'Skilled' },
  sportsmanship: { icon: 'handshake-o', label: 'Sportsmanship' },
  punctuality: { icon: 'clock-o', label: 'Punctual' },
  friendliness: { icon: 'smile-o', label: 'Friendly' },
};

export default function EndorsementBadge({ type, count }: EndorsementBadgeProps) {
  const colorScheme = useColorScheme() ?? 'light';
  const colors = Colors[colorScheme];
  const config = ENDORSEMENT_CONFIG[type] ?? { icon: 'star', label: type };

  return (
    <View style={[styles.container, { backgroundColor: colors.backgroundSecondary, borderColor: colors.border }]}>
      <FontAwesome name={config.icon as any} size={14} color={colors.tint} />
      <Text style={[styles.label, { color: colors.text }]}>{config.label}</Text>
      <View style={[styles.countBadge, { backgroundColor: colors.tint }]}>
        <Text style={styles.countText}>{count}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
    gap: 6,
  },
  label: {
    fontSize: 12,
    fontWeight: '600',
  },
  countBadge: {
    width: 20,
    height: 20,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  countText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '700',
  },
});
