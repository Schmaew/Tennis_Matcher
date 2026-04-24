import React, { useState } from 'react';
import {
  View,
  Text,
  FlatList,
  ScrollView,
  Switch,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
} from 'react-native';
import { useRouter } from 'expo-router';
import { PLAYERS, Player } from '@/data/players';
import PlayerCard from '@/components/PlayerCard';
import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';

const FILTERS = ['All', '3.0-3.5', '4.0+', 'Nearby', 'Available Now'];

export default function HomeScreen() {
  const router = useRouter();
  const colorScheme = useColorScheme();
  const colors = Colors[colorScheme ?? 'light'];
  const [availableNow, setAvailableNow] = useState(false);
  const [activeFilter, setActiveFilter] = useState('All');

  const filteredPlayers = PLAYERS.filter((player) => {
    if (availableNow && !player.isAvailableNow) return false;
    if (activeFilter === '3.0-3.5') {
      const level = parseFloat(player.skillLevel);
      return level >= 3.0 && level <= 3.5;
    }
    if (activeFilter === '4.0+') {
      return parseFloat(player.skillLevel) >= 4.0;
    }
    if (activeFilter === 'Nearby') {
      return player.distance <= 2.0;
    }
    if (activeFilter === 'Available Now') {
      return player.isAvailableNow;
    }
    return true;
  });

  const handlePlayerPress = (player: Player) => {
    router.push(`/player/${player.id}`);
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={[styles.appName, { color: colors.tint }]}>Tennis Matcher</Text>
        <View style={styles.toggleRow}>
          <Text style={[styles.toggleLabel, { color: colors.textSecondary }]}>Available Now</Text>
          <Switch
            value={availableNow}
            onValueChange={setAvailableNow}
            trackColor={{ false: colors.border, true: colors.tint }}
            thumbColor="#fff"
          />
        </View>
      </View>

      {/* Filter Chips */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.filterRow}
        contentContainerStyle={styles.filterContent}
      >
        {FILTERS.map((filter) => (
          <TouchableOpacity
            key={filter}
            style={[
              styles.filterChip,
              {
                backgroundColor: activeFilter === filter ? colors.tint : colors.backgroundSecondary,
                borderColor: activeFilter === filter ? colors.tint : colors.border,
              },
            ]}
            onPress={() => setActiveFilter(filter)}
          >
            <Text
              style={[
                styles.filterChipText,
                { color: activeFilter === filter ? '#fff' : colors.text },
              ]}
            >
              {filter}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Player List */}
      <FlatList
        data={filteredPlayers}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <PlayerCard player={item} onPress={() => handlePlayerPress(item)} />
        )}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
      />
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
    paddingBottom: 8,
  },
  appName: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  toggleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  toggleLabel: {
    fontSize: 13,
  },
  filterRow: {
    maxHeight: 44,
  },
  filterContent: {
    paddingHorizontal: 16,
    gap: 8,
  },
  filterChip: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
  },
  filterChipText: {
    fontSize: 13,
    fontWeight: '500',
  },
  listContent: {
    padding: 16,
    gap: 12,
  },
});
