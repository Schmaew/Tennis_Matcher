import React from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  Image,
  StyleSheet,
  SafeAreaView,
} from 'react-native';
import { useRouter } from 'expo-router';
import { CONVERSATIONS, Conversation } from '@/data/messages';
import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';

function formatTime(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
  if (diffDays === 0) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) {
    return date.toLocaleDateString([], { weekday: 'short' });
  }
  return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
}

export default function MessagesScreen() {
  const router = useRouter();
  const colorScheme = useColorScheme();
  const colors = Colors[colorScheme ?? 'light'];

  const handleConversationPress = (conversation: Conversation) => {
    router.push(`/chat/${conversation.id}`);
  };

  const renderConversation = ({ item }: { item: Conversation }) => (
    <TouchableOpacity
      style={[styles.conversationRow, { borderBottomColor: colors.border }]}
      onPress={() => handleConversationPress(item)}
      activeOpacity={0.7}
    >
      <Image source={{ uri: item.playerPhoto }} style={styles.avatar} />
      <View style={styles.conversationContent}>
        <View style={styles.conversationHeader}>
          <Text
            style={[
              styles.playerName,
              { color: colors.text },
              item.unreadCount > 0 && styles.unreadName,
            ]}
          >
            {item.playerName}
          </Text>
          <Text style={[styles.timestamp, { color: colors.textSecondary }]}>
            {formatTime(item.lastMessageTime)}
          </Text>
        </View>
        <View style={styles.messageRow}>
          <Text
            style={[
              styles.lastMessage,
              { color: colors.textSecondary },
              item.unreadCount > 0 && { color: colors.text },
            ]}
            numberOfLines={1}
          >
            {item.lastMessage}
          </Text>
          {item.unreadCount > 0 && (
            <View style={[styles.unreadBadge, { backgroundColor: colors.tint }]}>
              <Text style={styles.unreadBadgeText}>{item.unreadCount}</Text>
            </View>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]}>
      <View style={styles.header}>
        <Text style={[styles.title, { color: colors.text }]}>Messages</Text>
      </View>
      <FlatList
        data={CONVERSATIONS}
        keyExtractor={(item) => item.id}
        renderItem={renderConversation}
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
    paddingHorizontal: 16,
    paddingTop: 8,
    paddingBottom: 12,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  conversationRow: {
    flexDirection: 'row',
    padding: 16,
    borderBottomWidth: StyleSheet.hairlineWidth,
    alignItems: 'center',
  },
  avatar: {
    width: 52,
    height: 52,
    borderRadius: 26,
    marginRight: 12,
  },
  conversationContent: {
    flex: 1,
  },
  conversationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  playerName: {
    fontSize: 16,
    fontWeight: '500',
  },
  unreadName: {
    fontWeight: '700',
  },
  timestamp: {
    fontSize: 12,
  },
  messageRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  lastMessage: {
    fontSize: 14,
    flex: 1,
    marginRight: 8,
  },
  unreadBadge: {
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 6,
  },
  unreadBadgeText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: 'bold',
  },
});
