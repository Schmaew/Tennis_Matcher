import React from 'react';
import {
  View,
  Text,
  Image,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { FontAwesome } from '@expo/vector-icons';
import { PLAYERS } from '@/data/players';
import SkillBadge from '@/components/SkillBadge';
import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';

export default function PlayerDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const colorScheme = useColorScheme() ?? 'light';
  const colors = Colors[colorScheme];

  const player = PLAYERS.find((p) => p.id === id);

  if (!player) {
    return (
      <View style={[styles.center, { backgroundColor: colors.background }]}>
        <Text style={{ color: colors.text }}>Player not found</Text>
      </View>
    );
  }

  const endorsementIcon = (type: string) => {
    switch (type) {
      case 'skill': return 'star';
      case 'sportsmanship': return 'handshake-o';
      case 'punctuality': return 'clock-o';
      case 'friendliness': return 'smile-o';
      default: return 'star';
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Photo */}
        <Image source={{ uri: player.photo }} style={styles.photo} />

        {/* Name, Age, Location */}
        <View style={styles.section}>
          <Text style={[styles.name, { color: colors.text }]}>
            {player.name}, {player.age}
          </Text>
          <View style={styles.locationRow}>
            <FontAwesome name="map-marker" size={14} color={colors.textSecondary} />
            <Text style={[styles.locationText, { color: colors.textSecondary }]}>
              {player.location} - {player.distance} mi away
            </Text>
          </View>
          <SkillBadge level={player.skillLevel} size="large" />
        </View>

        {/* Bio */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>About</Text>
          <Text style={[styles.bodyText, { color: colors.textSecondary }]}>
            {player.bio}
          </Text>
        </View>

        {/* Looking For */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Looking For</Text>
          <View style={styles.tagsRow}>
            {player.lookingFor.map((item) => (
              <View key={item} style={[styles.tag, { backgroundColor: colors.backgroundSecondary, borderColor: colors.border }]}>
                <Text style={[styles.tagText, { color: colors.text }]}>{item}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Play Style */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Play Style</Text>
          <View style={styles.tagsRow}>
            {player.playStyle.map((item) => (
              <View key={item} style={[styles.tag, { backgroundColor: colors.backgroundSecondary, borderColor: colors.border }]}>
                <Text style={[styles.tagText, { color: colors.text }]}>{item}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Availability */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Availability</Text>
          {player.availability.map((slot, i) => (
            <View key={i} style={styles.availRow}>
              <FontAwesome name="calendar" size={13} color={colors.tint} />
              <Text style={[styles.availText, { color: colors.text }]}>
                {slot.day} - {slot.timeSlot}
              </Text>
            </View>
          ))}
        </View>

        {/* Group Size */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Group Size</Text>
          <Text style={[styles.bodyText, { color: colors.textSecondary }]}>
            {player.groupSize === 1
              ? 'Playing solo - looking for partners'
              : `Has a group of ${player.groupSize} players`}
          </Text>
        </View>

        {/* Endorsements */}
        {player.endorsements.length > 0 && (
          <View style={styles.section}>
            <Text style={[styles.sectionTitle, { color: colors.text }]}>
              Endorsements ({player.endorsements.length})
            </Text>
            {player.endorsements.map((e) => (
              <View key={e.id} style={[styles.endorsementCard, { backgroundColor: colors.backgroundSecondary, borderColor: colors.border }]}>
                <View style={styles.endorsementHeader}>
                  <Image source={{ uri: e.fromPlayerPhoto }} style={styles.endorsementPhoto} />
                  <View style={{ flex: 1 }}>
                    <Text style={[styles.endorsementName, { color: colors.text }]}>
                      {e.fromPlayerName}
                    </Text>
                    <View style={styles.endorsementTypeRow}>
                      <FontAwesome name={endorsementIcon(e.type)} size={12} color={colors.tint} />
                      <Text style={[styles.endorsementType, { color: colors.tint }]}>
                        {e.type.charAt(0).toUpperCase() + e.type.slice(1)}
                      </Text>
                    </View>
                  </View>
                </View>
                <Text style={[styles.endorsementComment, { color: colors.textSecondary }]}>
                  "{e.comment}"
                </Text>
              </View>
            ))}
          </View>
        )}

        {/* Stats */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Stats</Text>
          <View style={styles.statRow}>
            <FontAwesome name="trophy" size={14} color={colors.accent} />
            <Text style={[styles.statText, { color: colors.text }]}>
              {player.matchesPlayed} matches played
            </Text>
          </View>
        </View>

        {/* Bottom spacer for fixed button */}
        <View style={{ height: 80 }} />
      </ScrollView>

      {/* Fixed Send Message Button */}
      <View style={[styles.bottomBar, { backgroundColor: colors.background, borderTopColor: colors.border }]}>
        <TouchableOpacity
          style={[styles.sendButton, { backgroundColor: colors.tint }]}
          onPress={() => {
            // Try to find existing conversation with this player
            const { CONVERSATIONS } = require('@/data/messages');
            const convo = CONVERSATIONS.find((c: any) => c.playerId === player.id);
            if (convo) {
              router.push(`/chat/${convo.id}`);
            } else {
              Alert.alert('Message Sent', `Starting a conversation with ${player.name}!`);
            }
          }}
        >
          <FontAwesome name="comment" size={16} color="#fff" />
          <Text style={styles.sendButtonText}>Send Message</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  center: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  scrollContent: {
    paddingBottom: 20,
  },
  photo: {
    width: '100%',
    height: 300,
  },
  section: {
    paddingHorizontal: 16,
    paddingTop: 16,
  },
  name: {
    fontSize: 24,
    fontWeight: '700',
    marginBottom: 4,
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 10,
  },
  locationText: {
    fontSize: 14,
  },
  sectionTitle: {
    fontSize: 17,
    fontWeight: '700',
    marginBottom: 8,
  },
  bodyText: {
    fontSize: 15,
    lineHeight: 22,
  },
  tagsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  tag: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
  },
  tagText: {
    fontSize: 13,
  },
  availRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 6,
  },
  availText: {
    fontSize: 14,
  },
  endorsementCard: {
    borderRadius: 10,
    borderWidth: 1,
    padding: 12,
    marginBottom: 8,
  },
  endorsementHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 6,
  },
  endorsementPhoto: {
    width: 36,
    height: 36,
    borderRadius: 18,
  },
  endorsementName: {
    fontSize: 14,
    fontWeight: '600',
  },
  endorsementTypeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 2,
  },
  endorsementType: {
    fontSize: 12,
    fontWeight: '600',
  },
  endorsementComment: {
    fontSize: 13,
    fontStyle: 'italic',
  },
  statRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  statText: {
    fontSize: 15,
  },
  bottomBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: 16,
    borderTopWidth: 1,
  },
  sendButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 14,
    borderRadius: 10,
  },
  sendButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },
});
