import React from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet } from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';
import { AMENITIES } from '@/constants/amenities';
import { Court } from '@/data/courts';

interface CourtCardProps {
  court: Court;
  onPress: () => void;
}

export default function CourtCard({ court, onPress }: CourtCardProps) {
  const colorScheme = useColorScheme() ?? 'light';
  const colors = Colors[colorScheme];
  const isFree = court.courtFee === 0;

  return (
    <TouchableOpacity
      style={[styles.card, { backgroundColor: colors.card, borderColor: colors.border }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <Image source={{ uri: court.photo }} style={styles.photo} />

      <View style={styles.content}>
        <Text style={[styles.name, { color: colors.text }]}>{court.name}</Text>

        <View style={styles.row}>
          <FontAwesome name="map-marker" size={12} color={colors.textSecondary} />
          <Text style={[styles.address, { color: colors.textSecondary }]}>{court.address}</Text>
        </View>

        <View style={styles.row}>
          <Text style={isFree ? [styles.fee, { color: colors.success }] : [styles.fee, { color: colors.text }]}>
            {isFree ? 'FREE' : `$${court.courtFee} ${court.feeUnit}`}
          </Text>
          <View style={[styles.dot, { backgroundColor: colors.border }]} />
          <Text style={[styles.surface, { color: colors.textSecondary }]}>{court.surface}</Text>
          <View style={[styles.dot, { backgroundColor: colors.border }]} />
          <FontAwesome name="star" size={12} color={colors.warning} />
          <Text style={[styles.rating, { color: colors.text }]}>
            {court.rating} ({court.reviewCount})
          </Text>
        </View>

        <View style={styles.amenitiesRow}>
          {court.amenities.slice(0, 6).map((key) => {
            const amenity = AMENITIES[key as keyof typeof AMENITIES];
            if (!amenity) return null;
            return (
              <View key={key} style={[styles.amenityIcon, { backgroundColor: colors.backgroundSecondary }]}>
                <FontAwesome name={amenity.icon as any} size={12} color={colors.textSecondary} />
              </View>
            );
          })}
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 12,
    borderWidth: 1,
    overflow: 'hidden',
  },
  photo: {
    width: '100%',
    height: 150,
  },
  content: {
    padding: 14,
    gap: 6,
  },
  name: {
    fontSize: 17,
    fontWeight: '700',
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    flexWrap: 'wrap',
  },
  address: {
    fontSize: 12,
    flex: 1,
  },
  fee: {
    fontSize: 13,
    fontWeight: '700',
  },
  dot: {
    width: 3,
    height: 3,
    borderRadius: 1.5,
  },
  surface: {
    fontSize: 12,
  },
  rating: {
    fontSize: 12,
    fontWeight: '600',
  },
  amenitiesRow: {
    flexDirection: 'row',
    gap: 6,
    marginTop: 4,
  },
  amenityIcon: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
