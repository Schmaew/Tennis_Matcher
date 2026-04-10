import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  FlatList,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
} from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { FontAwesome } from '@expo/vector-icons';
import { CONVERSATIONS, Message } from '@/data/messages';
import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';

export default function ChatScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const colorScheme = useColorScheme() ?? 'light';
  const colors = Colors[colorScheme];

  const conversation = CONVERSATIONS.find((c) => c.id === id);
  const [messages, setMessages] = useState<Message[]>(conversation?.messages ?? []);
  const [inputText, setInputText] = useState('');
  const flatListRef = useRef<FlatList>(null);

  if (!conversation) {
    return (
      <View style={[styles.center, { backgroundColor: colors.background }]}>
        <Text style={{ color: colors.text }}>Conversation not found</Text>
      </View>
    );
  }

  const sendMessage = () => {
    const text = inputText.trim();
    if (!text) return;

    const newMsg: Message = {
      id: `local-${Date.now()}`,
      senderId: 'current',
      text,
      timestamp: new Date().toISOString(),
      read: true,
    };

    setMessages((prev) => [...prev, newMsg]);
    setInputText('');
  };

  const fillTemplate = () => {
    setInputText('Want to play at Greenwood Tennis Center on Saturday?');
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const renderMessage = ({ item }: { item: Message }) => {
    const isSent = item.senderId === 'current';
    return (
      <View style={[styles.bubbleWrapper, isSent ? styles.sentWrapper : styles.receivedWrapper]}>
        <View
          style={[
            styles.bubble,
            isSent
              ? [styles.sentBubble, { backgroundColor: colors.tint }]
              : [styles.receivedBubble, { backgroundColor: colors.backgroundSecondary }],
          ]}
        >
          <Text style={[styles.bubbleText, { color: isSent ? '#fff' : colors.text }]}>
            {item.text}
          </Text>
        </View>
        <Text style={[styles.timestamp, { color: colors.textSecondary }, isSent && styles.timestampSent]}>
          {formatTime(item.timestamp)}
        </Text>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView
      style={[styles.container, { backgroundColor: colors.background }]}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={90}
    >
      {/* Messages */}
      <FlatList
        ref={flatListRef}
        data={[...messages].reverse()}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        inverted
        contentContainerStyle={styles.messagesList}
      />

      {/* Quick Template */}
      <View style={[styles.templateBar, { borderTopColor: colors.border }]}>
        <TouchableOpacity
          style={[styles.templateButton, { backgroundColor: colors.backgroundSecondary, borderColor: colors.border }]}
          onPress={fillTemplate}
        >
          <FontAwesome name="bolt" size={12} color={colors.tint} />
          <Text style={[styles.templateText, { color: colors.tint }]} numberOfLines={1}>
            Quick invite
          </Text>
        </TouchableOpacity>
      </View>

      {/* Input Bar */}
      <View style={[styles.inputBar, { borderTopColor: colors.border, backgroundColor: colors.background }]}>
        <TextInput
          style={[styles.input, { backgroundColor: colors.backgroundSecondary, color: colors.text, borderColor: colors.border }]}
          placeholder="Type a message..."
          placeholderTextColor={colors.textSecondary}
          value={inputText}
          onChangeText={setInputText}
          multiline
        />
        <TouchableOpacity
          style={[styles.sendButton, { backgroundColor: colors.tint, opacity: inputText.trim() ? 1 : 0.5 }]}
          onPress={sendMessage}
          disabled={!inputText.trim()}
        >
          <FontAwesome name="send" size={16} color="#fff" />
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
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
  messagesList: {
    padding: 12,
  },
  bubbleWrapper: {
    marginBottom: 10,
    maxWidth: '80%',
  },
  sentWrapper: {
    alignSelf: 'flex-end',
  },
  receivedWrapper: {
    alignSelf: 'flex-start',
  },
  bubble: {
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 16,
  },
  sentBubble: {
    borderBottomRightRadius: 4,
  },
  receivedBubble: {
    borderBottomLeftRadius: 4,
  },
  bubbleText: {
    fontSize: 15,
    lineHeight: 20,
  },
  timestamp: {
    fontSize: 11,
    marginTop: 3,
  },
  timestampSent: {
    textAlign: 'right',
  },
  templateBar: {
    borderTopWidth: 1,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  templateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    gap: 6,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 14,
    borderWidth: 1,
  },
  templateText: {
    fontSize: 13,
    fontWeight: '500',
  },
  inputBar: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderTopWidth: 1,
    gap: 8,
  },
  input: {
    flex: 1,
    borderRadius: 20,
    borderWidth: 1,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 15,
    maxHeight: 100,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
