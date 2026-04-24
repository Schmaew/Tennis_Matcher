import React, { useState } from 'react';
import {
  View,
  Text,
  Image,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Linking,
} from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { FontAwesome } from '@expo/vector-icons';
import { COURTS } from '@/data/courts';
import { AMENITIES } from '@/constants/amenities';
import CostSplitter from '@/components/CostSplitter';
import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';

export default function CourtDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const colorScheme = useColorScheme() ?? 'light';
  const colors = Colors[colorScheme];

  const court = COURTS.find((c) => c.id === id);
  const [isFavorite, setIsFavorite] = useState(court?.isFavorite ?? false);

  if (!court) {
    return (
      <View style={[styles.center, { backgroundColor: colors.background }]}>
        <Text style={{ color: colors.text }}>Court not found</Text>
      </View>
    );
  }

  const renderStars = (rating: number) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      if (i <= Math.floor(rating)) {
        stars.push(<FontAwesome key={i} name="star" size={16} color={colors.warning} />);
      } else if (i - 0.5 <= rating) {
        stars.push(<FontAwesome key={i} name="star-half-o" size={16} color={colors.warning} />);
      } else {
        stars.push(<FontAwesome key={i} name="star-o" size={16} color={colors.warning} />);
      }
    }
    return stars;
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Photo */}
        <View>
          <Image source={{ uri: court.photo }} style={styles.photo} />
          <TouchableOpacity
            style={[styles.favoriteButton, { backgroundColor: colors.background }]}
            onPress={() => setIsFavorite(!isFavorite)}
          >
            <FontAwesome
              name={isFavorite ? 'heart' : 'heart-o'}
              size={22}
              color={isFavorite ? colors.error : colors.textSecondary}
            />
          </TouchableOpacity>
        </View>

        {/* Name & Address */}
        <View style={styles.section}>
          <Text style={[styles.name, { color: colors.text }]}>{court.name}</Text>
          <View style={styles.addressRow}>
            <FontAwesome name="map-marker" size={14} color={colors.textSecondary} />
            <Text style={[styles.addressText, { color: colors.textSecondary }]}>
              {court.address}
            </Text>
          </View>

          {/* Rating */}
          <View style={styles.ratingRow}>
            {renderStars(court.rating)}
            <Text style={[styles.ratingText, { color: colors.text }]}>{court.rating}</Text>
            <Text style={[styles.reviewCount, { color: colors.textSecondary }]}>
              ({court.reviewCount} reviews)
            </Text>
          </View>
        </View>

        {/* Fee */}
        <View style={styles.section}>
          <View style={[styles.feeCard, { backgroundColor: colors.backgroundSecondary, borderColor: colors.border }]}>
            <FontAwesome name="dollar" size={18} color={colors.tint} />
            <Text style={[styles.feeText, { color: colors.text }]}>
              {court.courtFee === 0 ? 'FREE' : `$${court.courtFee} ${court.feeUnit}`}
            </Text>
          </View>
        </View>

        {/* Cost Splitter */}
        {court.courtFee > 0 && (
          <View style={styles.section}>
            <CostSplitter courtFee={court.courtFee} feeUnit={court.feeUnit} />
          </View>
        )}

        {/* Surface & Courts */}
        <View style={styles.section}>
          <View style={styles.infoRow}>
            <View style={styles.infoItem}>
              <Text style={[styles.infoLabel, { color: colors.textSecondary }]}>Surface</Text>
              <Text style={[styles.infoValue, { color: colors.text }]}>{court.surface}</Text>
            </View>
            <View style={styles.infoItem}>
              <Text style={[styles.infoLabel, { color: colors.textSecondary }]}>Courts</Text>
              <Text style={[styles.infoValue, { color: colors.text }]}>{court.numberOfCourts}</Text>
            </View>
          </View>
        </View>

        {/* Opening Hours */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Opening Hours</Text>
          {court.openingHours.map((h, i) => (
            <View key={i} style={styles.hoursRow}>
              <Text style={[styles.hoursDay, { color: colors.text }]}>{h.day}</Text>
              <Text style={[styles.hoursTime, { color: colors.textSecondary }]}>
                {h.open} - {h.close}
              </Text>
            </View>
          ))}
        </View>

        {/* Amenities */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Amenities</Text>
          <View style={styles.amenitiesGrid}>
            {court.amenities.map((key) => {
              const amenity = AMENITIES[key as keyof typeof AMENITIES];
              if (!amenity) return null;
              return (
                <View key={key} style={styles.amenityItem}>
                  <FontAwesome name={amenity.icon as any} size={18} color={colors.tint} />
                  <Text style={[styles.amenityLabel, { color: colors.text }]}>{amenity.label}</Text>
                </View>
              );
            })}
          </View>
        </View>

        {/* Rules */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Rules & Regulations</Text>
          {court.rules.map((rule, i) => (
            <View key={i} style={styles.ruleRow}>
              <FontAwesome name="circle" size={6} color={colors.textSecondary} style={{ marginTop: 6 }} />
              <Text style={[styles.ruleText, { color: colors.textSecondary }]}>{rule}</Text>
            </View>
          ))}
        </View>

        {/* Contact */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Contact</Text>
          {court.phone ? (
            <TouchableOpacity
              style={styles.contactRow}
              onPress={() => Linking.openURL(`tel:${court.phone}`)}
            >
              <FontAwesome name="phone" size={16} color={colors.tint} />
              <Text style={[styles.contactText, { color: colors.tint }]}>{court.phone}</Text>
            </TouchableOpacity>
          ) : null}
          {court.website ? (
            <TouchableOpacity
              style={styles.contactRow}
              onPress={() => Linking.openURL(court.website)}
            >
              <FontAwesome name="globe" size={16} color={colors.tint} />
              <Text style={[styles.contactText, { color: colors.tint }]}>{court.website}</Text>
            </TouchableOpacity>
          ) : null}
        </View>

        {/* Description */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>About</Text>
          <Text style={[styles.bodyText, { color: colors.textSecondary }]}>
            {court.description}
          </Text>
        </View>

        <View style={{ height: 30 }} />
      </ScrollView>
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
    height: 200,
  },
  favoriteButton: {
    position: 'absolute',
    top: 12,
    right: 12,
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
    elevation: 3,
  },
  section: {
    paddingHorizontal: 16,
    paddingTop: 16,
  },
  name: {
    fontSize: 22,
    fontWeight: '700',
    marginBottom: 4,
  },
  addressRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 8,
  },
  addressText: {
    fontSize: 14,
  },
  ratingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  ratingText: {
    fontSize: 14,
    fontWeight: '700',
    marginLeft: 4,
  },
  reviewCount: {
    fontSize: 13,
  },
  feeCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    padding: 14,
    borderRadius: 10,
    borderWidth: 1,
  },
  feeText: {
    fontSize: 18,
    fontWeight: '700',
  },
  infoRow: {
    flexDirection: 'row',
    gap: 24,
  },
  infoItem: {},
  infoLabel: {
    fontSize: 12,
    marginBottom: 2,
  },
  infoValue: {
    fontSize: 15,
    fontWeight: '600',
  },
  sectionTitle: {
    fontSize: 17,
    fontWeight: '700',
    marginBottom: 8,
  },
  hoursRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  hoursDay: {
    fontSize: 14,
    fontWeight: '500',
  },
  hoursTime: {
    fontSize: 14,
  },
  amenitiesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
  },
  amenityItem: {
    alignItems: 'center',
    width: 70,
    gap: 4,
  },
  amenityLabel: {
    fontSize: 11,
    textAlign: 'center',
  },
  ruleRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 6,
  },
  ruleText: {
    fontSize: 14,
    flex: 1,
    lineHeight: 20,
  },
  contactRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  contactText: {
    fontSize: 14,
  },
  bodyText: {
    fontSize: 15,
    lineHeight: 22,
  },
});
