import React from 'react';
import {
  View,
  Text,
  Image,
  ScrollView,
  TouchableOpacity,
  Alert,
  StyleSheet,
  SafeAreaView,
} from 'react-native';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { useAuth } from '@/contexts/AuthContext';
import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';

export default function ProfileScreen() {
  const { user, logout } = useAuth();
  const colorScheme = useColorScheme();
  const colors = Colors[colorScheme ?? 'light'];

  if (!user) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
        <View style={styles.centered}>
          <Text style={[styles.emptyText, { color: colors.textSecondary }]}>
            Please log in to view your profile.
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  const handleEditProfile = () => {
    Alert.alert('Coming soon!', 'Profile editing will be available in a future update.');
  };

  const handleLogout = () => {
    Alert.alert('Logout', 'Are you sure you want to logout?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Logout', style: 'destructive', onPress: logout },
    ]);
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={[styles.title, { color: colors.text }]}>Profile</Text>
        </View>

        {/* Photo & Name */}
        <View style={styles.profileTop}>
          <Image source={{ uri: user.photo }} style={styles.photo} />
          <Text style={[styles.name, { color: colors.text }]}>{user.name}</Text>
          <View style={[styles.skillBadge, { backgroundColor: colors.tint }]}>
            <Text style={styles.skillBadgeText}>NTRP {user.skillLevel}</Text>
          </View>
        </View>

        {/* Bio */}
        <View style={[styles.section, { borderBottomColor: colors.border }]}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>About</Text>
          <Text style={[styles.bioText, { color: colors.textSecondary }]}>{user.bio}</Text>
        </View>

        {/* Looking For */}
        <View style={[styles.section, { borderBottomColor: colors.border }]}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Looking for</Text>
          <View style={styles.tagsRow}>
            {user.lookingFor.map((item) => (
              <View key={item} style={[styles.tag, { backgroundColor: colors.backgroundSecondary, borderColor: colors.border }]}>
                <Text style={[styles.tagText, { color: colors.text }]}>{item}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Play Style */}
        <View style={[styles.section, { borderBottomColor: colors.border }]}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Play Style</Text>
          <View style={styles.tagsRow}>
            {user.playStyle.map((item) => (
              <View key={item} style={[styles.tag, { backgroundColor: colors.backgroundSecondary, borderColor: colors.border }]}>
                <Text style={[styles.tagText, { color: colors.text }]}>{item}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Availability */}
        <View style={[styles.section, { borderBottomColor: colors.border }]}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Availability</Text>
          {user.availability.map((slot, index) => (
            <Text key={index} style={[styles.availabilityText, { color: colors.textSecondary }]}>
              {slot.day} - {slot.timeSlot}
            </Text>
          ))}
        </View>

        {/* Stats */}
        <View style={[styles.section, { borderBottomColor: colors.border }]}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Stats</Text>
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Text style={[styles.statNumber, { color: colors.tint }]}>{user.matchesPlayed}</Text>
              <Text style={[styles.statLabel, { color: colors.textSecondary }]}>Matches</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={[styles.statNumber, { color: colors.tint }]}>{user.endorsements.length}</Text>
              <Text style={[styles.statLabel, { color: colors.textSecondary }]}>Endorsements</Text>
            </View>
          </View>
        </View>

        {/* Buttons */}
        <View style={styles.buttonsSection}>
          <TouchableOpacity
            style={[styles.button, { backgroundColor: colors.tint }]}
            onPress={handleEditProfile}
          >
            <FontAwesome name="pencil" size={16} color="#fff" />
            <Text style={styles.buttonText}>Edit Profile</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.button, styles.logoutButton, { borderColor: colors.error }]}
            onPress={handleLogout}
          >
            <FontAwesome name="sign-out" size={16} color={colors.error} />
            <Text style={[styles.buttonText, { color: colors.error }]}>Logout</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  centered: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyText: {
    fontSize: 16,
  },
  header: {
    paddingHorizontal: 16,
    paddingTop: 8,
    paddingBottom: 4,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  profileTop: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  photo: {
    width: 100,
    height: 100,
    borderRadius: 50,
    marginBottom: 12,
  },
  name: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  skillBadge: {
    paddingHorizontal: 14,
    paddingVertical: 4,
    borderRadius: 12,
  },
  skillBadgeText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: '600',
  },
  section: {
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  bioText: {
    fontSize: 14,
    lineHeight: 20,
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
  availabilityText: {
    fontSize: 14,
    marginBottom: 4,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 32,
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  statLabel: {
    fontSize: 13,
    marginTop: 2,
  },
  buttonsSection: {
    padding: 16,
    gap: 12,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 12,
    gap: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  logoutButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
  },
});
