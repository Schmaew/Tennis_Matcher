import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';

interface CostSplitterProps {
  courtFee: number;
  feeUnit: string;
}

export default function CostSplitter({ courtFee, feeUnit }: CostSplitterProps) {
  const colorScheme = useColorScheme() ?? 'light';
  const colors = Colors[colorScheme];
  const [players, setPlayers] = useState(2);

  const perPerson = courtFee / players;

  return (
    <View style={[styles.container, { backgroundColor: colors.backgroundSecondary, borderColor: colors.border }]}>
      <Text style={[styles.title, { color: colors.text }]}>Cost Splitter</Text>

      <View style={styles.row}>
        <Text style={[styles.label, { color: colors.textSecondary }]}>Court Fee</Text>
        <Text style={[styles.value, { color: colors.text }]}>
          ${courtFee.toFixed(2)} {feeUnit}
        </Text>
      </View>

      <View style={styles.row}>
        <Text style={[styles.label, { color: colors.textSecondary }]}>Players</Text>
        <View style={styles.stepper}>
          <TouchableOpacity
            style={[styles.stepperButton, { backgroundColor: colors.border }]}
            onPress={() => setPlayers((p) => Math.max(1, p - 1))}
          >
            <FontAwesome name="minus" size={12} color={colors.text} />
          </TouchableOpacity>
          <Text style={[styles.stepperValue, { color: colors.text }]}>{players}</Text>
          <TouchableOpacity
            style={[styles.stepperButton, { backgroundColor: colors.border }]}
            onPress={() => setPlayers((p) => Math.min(8, p + 1))}
          >
            <FontAwesome name="plus" size={12} color={colors.text} />
          </TouchableOpacity>
        </View>
      </View>

      <View style={[styles.divider, { backgroundColor: colors.border }]} />

      <View style={styles.row}>
        <Text style={[styles.perPersonLabel, { color: colors.text }]}>Per Person</Text>
        <Text style={[styles.perPersonValue, { color: colors.tint }]}>
          ${perPerson.toFixed(2)}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 12,
    borderWidth: 1,
    padding: 16,
    gap: 12,
  },
  title: {
    fontSize: 16,
    fontWeight: '700',
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  label: {
    fontSize: 14,
  },
  value: {
    fontSize: 14,
    fontWeight: '600',
  },
  stepper: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  stepperButton: {
    width: 30,
    height: 30,
    borderRadius: 15,
    alignItems: 'center',
    justifyContent: 'center',
  },
  stepperValue: {
    fontSize: 16,
    fontWeight: '700',
    minWidth: 20,
    textAlign: 'center',
  },
  divider: {
    height: 1,
  },
  perPersonLabel: {
    fontSize: 15,
    fontWeight: '600',
  },
  perPersonValue: {
    fontSize: 20,
    fontWeight: '800',
  },
});
