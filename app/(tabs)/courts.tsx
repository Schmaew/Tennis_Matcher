import CourtCard from '@/components/CourtCard';
import { useColorScheme } from '@/components/useColorScheme';
import Colors from '@/constants/Colors';
import { Court } from '@/data/courts';
import { useCourts } from '@/hooks/useCourts';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import {
    ActivityIndicator,
    FlatList,
    SafeAreaView,
    StyleSheet,
    Text,
    TouchableOpacity,
    View,
} from 'react-native';

export default function CourtsScreen() {
  const router = useRouter();
  const colorScheme = useColorScheme();
  const colors = Colors[colorScheme ?? 'light'];
  const [viewMode, setViewMode] = useState<'list' | 'map'>('list');

  const { courts, loading, error, isRealData, reload } = useCourts();

  const handleCourtPress = (court: Court) => {
    router.push(`/court/${court.id}`);
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={[styles.title, { color: colors.text }]}>Tennis Courts</Text>
          {isRealData && (
            <Text style={[styles.subtitle, { color: colors.tint }]}>
              📍 Nearby real courts
            </Text>
          )}
        </View>
        <View style={styles.headerRight}>
          <TouchableOpacity onPress={reload} style={styles.reloadButton}>
            <FontAwesome name="refresh" size={16} color={colors.textSecondary} />
          </TouchableOpacity>
          <View style={styles.viewToggle}>
            <TouchableOpacity
              style={[
                styles.viewButton,
                viewMode === 'list' && { backgroundColor: colors.tint },
              ]}
              onPress={() => setViewMode('list')}
            >
              <FontAwesome
                name="list"
                size={16}
                color={viewMode === 'list' ? '#fff' : colors.textSecondary}
              />
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.viewButton,
                viewMode === 'map' && { backgroundColor: colors.tint },
              ]}
              onPress={() => setViewMode('map')}
            >
              <FontAwesome
                name="map"
                size={16}
                color={viewMode === 'map' ? '#fff' : colors.textSecondary}
              />
            </TouchableOpacity>
          </View>
        </View>
      </View>

      {/* Error banner */}
      {error !== null && (
        <View style={[styles.errorBanner, { backgroundColor: colors.backgroundSecondary }]}>
          <FontAwesome name="info-circle" size={14} color={colors.textSecondary} />
          <Text style={[styles.errorText, { color: colors.textSecondary }]}>{error}</Text>
        </View>
      )}

      {/* Loading spinner */}
      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.tint} />
          <Text style={[styles.loadingText, { color: colors.textSecondary }]}>
            Finding courts near you...
          </Text>
        </View>
      )}

      {!loading && viewMode === 'list' && (
        <FlatList
          data={courts}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <CourtCard court={item} onPress={() => handleCourtPress(item)} />
          )}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
        />
      )}

      {!loading && viewMode === 'map' && (
        <View style={[styles.mapPlaceholder, { backgroundColor: colors.backgroundSecondary }]}>
          <FontAwesome name="map" size={48} color={colors.textSecondary} />
          <Text style={[styles.mapPlaceholderText, { color: colors.textSecondary }]}>
            Map view coming soon
          </Text>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingTop: 8,
    paddingBottom: 12,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  subtitle: {
    fontSize: 12,
    fontWeight: '500',
    marginTop: 2,
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  reloadButton: {
    padding: 8,
  },
  viewToggle: {
    flexDirection: 'row',
    borderRadius: 8,
    overflow: 'hidden',
  },
  viewButton: {
    padding: 8,
    paddingHorizontal: 12,
  },
  listContent: {
    padding: 16,
    gap: 12,
  },
  errorBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginHorizontal: 16,
    marginBottom: 8,
    padding: 10,
    borderRadius: 8,
  },
  errorText: {
    fontSize: 12,
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
  },
  loadingText: {
    fontSize: 14,
  },
  mapPlaceholder: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    margin: 16,
    borderRadius: 12,
  },
  mapPlaceholderText: {
    marginTop: 12,
    fontSize: 16,
  },
});
