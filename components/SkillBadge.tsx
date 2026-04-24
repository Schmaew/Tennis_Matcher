import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface SkillBadgeProps {
  level: string;
  size?: 'small' | 'large';
}

function getBadgeColor(level: string): string {
  const num = parseFloat(level);
  if (num >= 5.0) return '#D32F2F';
  if (num >= 4.0) return '#7B1FA2';
  if (num >= 3.0) return '#1565C0';
  return '#2E7D32';
}

export default function SkillBadge({ level, size = 'small' }: SkillBadgeProps) {
  const color = getBadgeColor(level);
  const isLarge = size === 'large';

  return (
    <View style={[styles.badge, { backgroundColor: color }, isLarge && styles.badgeLarge]}>
      <Text style={[styles.text, isLarge && styles.textLarge]}>NTRP {level}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10,
    alignSelf: 'flex-start',
  },
  badgeLarge: {
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 14,
  },
  text: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '700',
  },
  textLarge: {
    fontSize: 14,
  },
});
