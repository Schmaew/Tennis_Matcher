import React, { useState } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
} from 'react-native';
import { useRouter } from 'expo-router';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { COURTS, Court } from '@/data/courts';
import CourtCard from '@/components/CourtCard';
import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';

export default function CourtsScreen() {
  const router = useRouter();
  const colorScheme = useColorScheme();
  const colors = Colors[colorScheme ?? 'light'];
  const [viewMode, setViewMode] = useState<'list' | 'map'>('list');

  const handleCourtPress = (court: Court) => {
    router.push(`/court/${court.id}`);
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={[styles.title, { color: colors.text }]}>Tennis Courts</Text>
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

      {viewMode === 'list' ? (
        <FlatList
          data={COURTS}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <CourtCard court={item} onPress={() => handleCourtPress(item)} />
          )}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
        />
      ) : (
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
