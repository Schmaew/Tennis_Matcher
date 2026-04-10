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
import { MATCHES } from '@/data/matches';
import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';

export default function MatchDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const colorScheme = useColorScheme() ?? 'light';
  const colors = Colors[colorScheme];

  const match = MATCHES.find((m) => m.id === id);

  if (!match) {
    return (
      <View style={[styles.center, { backgroundColor: colors.background }]}>
        <Text style={{ color: colors.text }}>Match not found</Text>
      </View>
    );
  }

  const isFull = match.spotsFilled >= match.spotsTotal;
  const isOpen = match.status === 'open' && !isFull;

  const typeBadgeColor = () => {
    switch (match.type) {
      case 'singles': return '#1565C0';
      case 'doubles': return '#7B1FA2';
      case 'group': return '#E65100';
      default: return '#666';
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Match Type Badge */}
        <View style={styles.section}>
          <View style={[styles.typeBadge, { backgroundColor: typeBadgeColor() }]}>
            <Text style={styles.typeBadgeText}>
              {match.type.charAt(0).toUpperCase() + match.type.slice(1)}
            </Text>
          </View>
        </View>

        {/* Court */}
        <View style={styles.section}>
          <Text style={[styles.label, { color: colors.textSecondary }]}>Court</Text>
          <TouchableOpacity onPress={() => router.push(`/court/${match.courtId}`)}>
            <Text style={[styles.courtName, { color: colors.tint }]}>{match.courtName}</Text>
          </TouchableOpacity>
        </View>

        {/* Date, Time, Duration */}
        <View style={styles.section}>
          <View style={styles.infoGrid}>
            <View style={styles.infoItem}>
              <FontAwesome name="calendar" size={14} color={colors.tint} />
              <Text style={[styles.infoText, { color: colors.text }]}>{match.date}</Text>
            </View>
            <View style={styles.infoItem}>
              <FontAwesome name="clock-o" size={14} color={colors.tint} />
              <Text style={[styles.infoText, { color: colors.text }]}>{match.time}</Text>
            </View>
            <View style={styles.infoItem}>
              <FontAwesome name="hourglass-half" size={14} color={colors.tint} />
              <Text style={[styles.infoText, { color: colors.text }]}>
                {match.duration} {match.duration === 1 ? 'hour' : 'hours'}
              </Text>
            </View>
          </View>
        </View>

        {/* Skill Range */}
        <View style={styles.section}>
          <Text style={[styles.label, { color: colors.textSecondary }]}>Skill Range</Text>
          <Text style={[styles.skillRange, { color: colors.text }]}>NTRP {match.skillRange}</Text>
        </View>

        {/* Description */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Description</Text>
          <Text style={[styles.bodyText, { color: colors.textSecondary }]}>
            {match.description}
          </Text>
        </View>

        {/* Organizer */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Organizer</Text>
          <TouchableOpacity
            style={styles.organizerRow}
            onPress={() => router.push(`/player/${match.organizerId}`)}
          >
            <Image source={{ uri: match.organizerPhoto }} style={styles.organizerPhoto} />
            <Text style={[styles.organizerName, { color: colors.text }]}>
              {match.organizerName}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Players */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>
            Players ({match.spotsFilled} of {match.spotsTotal} spots filled)
          </Text>
          <View style={styles.playersGrid}>
            {match.players.map((p) => (
              <TouchableOpacity
                key={p.id}
                style={styles.playerItem}
                onPress={() => router.push(`/player/${p.id}`)}
              >
                <Image source={{ uri: p.photo }} style={styles.playerPhoto} />
                <Text style={[styles.playerName, { color: colors.text }]} numberOfLines={1}>
                  {p.name}
                </Text>
              </TouchableOpacity>
            ))}
            {/* Empty spots */}
            {Array.from({ length: match.spotsTotal - match.spotsFilled }).map((_, i) => (
              <View key={`empty-${i}`} style={styles.playerItem}>
                <View style={[styles.emptySpot, { backgroundColor: colors.backgroundSecondary, borderColor: colors.border }]}>
                  <FontAwesome name="user-plus" size={18} color={colors.textSecondary} />
                </View>
                <Text style={[styles.playerName, { color: colors.textSecondary }]}>Open</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Cost Breakdown */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Cost</Text>
          {match.totalCost === 0 ? (
            <Text style={[styles.freeText, { color: colors.tint }]}>FREE</Text>
          ) : (
            <View style={[styles.costCard, { backgroundColor: colors.backgroundSecondary, borderColor: colors.border }]}>
              <View style={styles.costRow}>
                <Text style={[styles.costLabel, { color: colors.textSecondary }]}>Total Cost</Text>
                <Text style={[styles.costValue, { color: colors.text }]}>
                  ${match.totalCost.toFixed(2)}
                </Text>
              </View>
              <View style={[styles.costDivider, { backgroundColor: colors.border }]} />
              <View style={styles.costRow}>
                <Text style={[styles.costLabel, { color: colors.textSecondary }]}>Per Person</Text>
                <Text style={[styles.costPerPerson, { color: colors.tint }]}>
                  ${match.costPerPerson.toFixed(2)}
                </Text>
              </View>
            </View>
          )}
        </View>

        {/* Bottom spacer */}
        <View style={{ height: 80 }} />
      </ScrollView>

      {/* Fixed Bottom Button */}
      <View style={[styles.bottomBar, { backgroundColor: colors.background, borderTopColor: colors.border }]}>
        {isOpen ? (
          <TouchableOpacity
            style={[styles.joinButton, { backgroundColor: colors.tint }]}
            onPress={() => Alert.alert('Success', "You've joined this match!")}
          >
            <FontAwesome name="check" size={16} color="#fff" />
            <Text style={styles.joinButtonText}>Join Match</Text>
          </TouchableOpacity>
        ) : (
          <View style={[styles.joinButton, { backgroundColor: colors.textSecondary, opacity: 0.6 }]}>
            <Text style={styles.joinButtonText}>Match Full</Text>
          </View>
        )}
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
  section: {
    paddingHorizontal: 16,
    paddingTop: 16,
  },
  typeBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 14,
  },
  typeBadgeText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '700',
  },
  label: {
    fontSize: 12,
    marginBottom: 2,
  },
  courtName: {
    fontSize: 17,
    fontWeight: '600',
  },
  infoGrid: {
    flexDirection: 'row',
    gap: 20,
  },
  infoItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  infoText: {
    fontSize: 14,
  },
  skillRange: {
    fontSize: 15,
    fontWeight: '600',
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
  organizerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  organizerPhoto: {
    width: 40,
    height: 40,
    borderRadius: 20,
  },
  organizerName: {
    fontSize: 15,
    fontWeight: '600',
  },
  playersGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  playerItem: {
    alignItems: 'center',
    width: 70,
  },
  playerPhoto: {
    width: 50,
    height: 50,
    borderRadius: 25,
    marginBottom: 4,
  },
  playerName: {
    fontSize: 11,
    textAlign: 'center',
  },
  emptySpot: {
    width: 50,
    height: 50,
    borderRadius: 25,
    borderWidth: 2,
    borderStyle: 'dashed',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 4,
  },
  freeText: {
    fontSize: 20,
    fontWeight: '800',
  },
  costCard: {
    borderRadius: 10,
    borderWidth: 1,
    padding: 14,
  },
  costRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  costLabel: {
    fontSize: 14,
  },
  costValue: {
    fontSize: 15,
    fontWeight: '600',
  },
  costDivider: {
    height: 1,
    marginVertical: 8,
  },
  costPerPerson: {
    fontSize: 20,
    fontWeight: '800',
  },
  bottomBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: 16,
    borderTopWidth: 1,
  },
  joinButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 14,
    borderRadius: 10,
  },
  joinButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },
});
