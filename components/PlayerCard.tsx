import React from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet } from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';
import SkillBadge from '@/components/SkillBadge';
import { Player } from '@/data/players';

interface PlayerCardProps {
  player: Player;
  onPress: () => void;
}

export default function PlayerCard({ player, onPress }: PlayerCardProps) {
  const colorScheme = useColorScheme() ?? 'light';
  const colors = Colors[colorScheme];

  return (
    <TouchableOpacity
      style={[styles.card, { backgroundColor: colors.card, borderColor: colors.border }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.topRow}>
        <Image source={{ uri: player.photo }} style={styles.photo} />
        <View style={styles.info}>
          <Text style={[styles.name, { color: colors.text }]}>{player.name}</Text>
          <SkillBadge level={player.skillLevel} />
          <View style={styles.locationRow}>
            <FontAwesome name="map-marker" size={12} color={colors.textSecondary} />
            <Text style={[styles.locationText, { color: colors.textSecondary }]}>
              {player.location} · {player.distance} mi
            </Text>
          </View>
        </View>
      </View>

      <View style={styles.tagsRow}>
        {player.availability.slice(0, 3).map((a, i) => (
          <View key={i} style={[styles.tag, { backgroundColor: colors.backgroundSecondary }]}>
            <Text style={[styles.tagText, { color: colors.textSecondary }]}>
              {a.day.slice(0, 3)} {a.timeSlot}
            </Text>
          </View>
        ))}
      </View>

      <View style={styles.tagsRow}>
        {player.playStyle.map((style, i) => (
          <View key={i} style={[styles.tag, { backgroundColor: colors.tint + '18' }]}>
            <Text style={[styles.tagText, { color: colors.tint }]}>{style}</Text>
          </View>
        ))}
      </View>

      <TouchableOpacity style={[styles.messageButton, { backgroundColor: colors.tint }]}>
        <FontAwesome name="envelope" size={14} color="#fff" />
        <Text style={styles.messageText}>Message</Text>
      </TouchableOpacity>
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
  topRow: {
    flexDirection: 'row',
    gap: 12,
  },
  photo: {
    width: 80,
    height: 80,
    borderRadius: 40,
  },
  info: {
    flex: 1,
    gap: 4,
    justifyContent: 'center',
  },
  name: {
    fontSize: 17,
    fontWeight: '700',
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 2,
  },
  locationText: {
    fontSize: 12,
  },
  tagsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  tag: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  tagText: {
    fontSize: 11,
    fontWeight: '500',
  },
  messageButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    borderRadius: 10,
    gap: 6,
  },
  messageText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
});
