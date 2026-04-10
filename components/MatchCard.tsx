import React from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet } from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';
import SkillBadge from '@/components/SkillBadge';
import { Match } from '@/data/matches';

interface MatchCardProps {
  match: Match;
  onPress: () => void;
}

const TYPE_COLORS: Record<string, string> = {
  singles: '#1565C0',
  doubles: '#7B1FA2',
  group: '#E65100',
};

export default function MatchCard({ match, onPress }: MatchCardProps) {
  const colorScheme = useColorScheme() ?? 'light';
  const colors = Colors[colorScheme];

  return (
    <TouchableOpacity
      style={[styles.card, { backgroundColor: colors.card, borderColor: colors.border }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      {/* Court name and date */}
      <View style={styles.header}>
        <View style={{ flex: 1 }}>
          <Text style={[styles.courtName, { color: colors.text }]}>{match.courtName}</Text>
          <View style={styles.row}>
            <FontAwesome name="calendar" size={11} color={colors.textSecondary} />
            <Text style={[styles.dateText, { color: colors.textSecondary }]}>
              {match.date} · {match.time} · {match.duration}hr
            </Text>
          </View>
        </View>
        <View style={[styles.typeBadge, { backgroundColor: TYPE_COLORS[match.type] ?? '#666' }]}>
          <Text style={styles.typeText}>{match.type.charAt(0).toUpperCase() + match.type.slice(1)}</Text>
        </View>
      </View>

      {/* Skill range and spots */}
      <View style={styles.detailsRow}>
        <View style={styles.row}>
          <FontAwesome name="signal" size={11} color={colors.textSecondary} />
          <Text style={[styles.detailText, { color: colors.textSecondary }]}>{match.skillRange}</Text>
        </View>
        <View style={styles.row}>
          <FontAwesome name="users" size={11} color={colors.textSecondary} />
          <Text style={[styles.detailText, { color: colors.textSecondary }]}>
            {match.spotsFilled}/{match.spotsTotal} spots filled
          </Text>
        </View>
        <Text style={[styles.cost, { color: colors.tint }]}>
          {match.costPerPerson === 0 ? 'FREE' : `$${match.costPerPerson.toFixed(2)}/person`}
        </Text>
      </View>

      {/* Organizer and player avatars */}
      <View style={styles.footer}>
        <View style={styles.organizer}>
          <Image source={{ uri: match.organizerPhoto }} style={styles.organizerPhoto} />
          <Text style={[styles.organizerName, { color: colors.textSecondary }]}>
            {match.organizerName}
          </Text>
        </View>
        <View style={styles.avatarRow}>
          {match.players.slice(0, 5).map((p, i) => (
            <Image
              key={p.id}
              source={{ uri: p.photo }}
              style={[styles.avatar, { marginLeft: i > 0 ? -8 : 0, borderColor: colors.card }]}
            />
          ))}
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 12,
    borderWidth: 1,
    padding: 14,
    gap: 10,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  courtName: {
    fontSize: 16,
    fontWeight: '700',
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  dateText: {
    fontSize: 12,
  },
  typeBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 10,
  },
  typeText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '700',
  },
  detailsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: 12,
  },
  detailText: {
    fontSize: 12,
  },
  cost: {
    fontSize: 13,
    fontWeight: '700',
    marginLeft: 'auto',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  organizer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  organizerPhoto: {
    width: 24,
    height: 24,
    borderRadius: 12,
  },
  organizerName: {
    fontSize: 12,
    fontWeight: '500',
  },
  avatarRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 28,
    height: 28,
    borderRadius: 14,
    borderWidth: 2,
  },
});
