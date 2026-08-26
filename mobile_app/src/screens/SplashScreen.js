import React, { useEffect } from 'react';
import { Image, StyleSheet, Text, View } from 'react-native';

const SPLASH_DURATION_MS = 2000;

/**
 * YOUNG STAR ITC — Splash Screen 1
 *
 * Visual source of truth: Figma frame "Splash Screen 1" (350:11), 392x800.
 * Do not add trading logic here. The screen only presents the approved brand
 * splash and transitions after the approved 2-second duration.
 */
export default function SplashScreen({ onFinish }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      if (typeof onFinish === 'function') onFinish();
    }, SPLASH_DURATION_MS);

    return () => clearTimeout(timer);
  }, [onFinish]);

  return (
    <View style={styles.screen}>
      <Image
        source={{ uri: 'https://www.figma.com/api/mcp/asset/862f07d5-c57d-4c3b-9a05-dd5e73756eb5.png' }}
        style={styles.theme}
        resizeMode="cover"
      />
      <Image
        source={{ uri: 'https://www.figma.com/api/mcp/asset/73b3b558-1786-4d74-826b-1bdb90cf8100.png' }}
        style={styles.logo}
        resizeMode="cover"
      />

      <Text style={styles.youngStar}>Y O U N G   S T A R</Text>
      <Text style={styles.divider}>══════════ ✦ ══════════</Text>
      <Text style={styles.itc}>I   T   C</Text>
      <Text style={styles.subtitle}>Trading Operating System</Text>

      <Text style={styles.loading}>Loading</Text>
      <Text style={styles.dots}>●  ●  ●</Text>

      <Text style={styles.version}>──────── Version 1.0.0 ────────</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    width: '100%',
    height: '100%',
    backgroundColor: '#000000',
    alignItems: 'center',
    position: 'relative',
    overflow: 'hidden',
  },
  theme: {
    ...StyleSheet.absoluteFillObject,
    width: '100%',
    height: '100%',
    opacity: 0.52,
  },
  logo: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '49%',
    opacity: 0.85,
  },
  youngStar: {
    position: 'absolute',
    top: 270,
    width: '100%',
    color: '#FFFFFF',
    fontFamily: 'Inter',
    fontSize: 34,
    fontWeight: '700',
    textAlign: 'center',
    opacity: 0.89,
  },
  divider: {
    position: 'absolute',
    top: 301,
    width: '100%',
    color: '#FFD54A',
    fontFamily: 'Inter',
    fontSize: 12,
    textAlign: 'center',
    opacity: 0.70,
  },
  itc: {
    position: 'absolute',
    top: 330,
    width: '100%',
    color: '#F4B400',
    fontFamily: 'Inter',
    fontSize: 24,
    fontWeight: '700',
    textAlign: 'center',
  },
  subtitle: {
    position: 'absolute',
    top: 360,
    width: '100%',
    color: '#B8BDC7',
    fontFamily: 'Inter',
    fontSize: 20,
    fontWeight: '700',
    textAlign: 'center',
    opacity: 0.74,
  },
  loading: {
    position: 'absolute',
    top: 500,
    width: '100%',
    color: '#D0D5DD',
    fontFamily: 'Inter',
    fontSize: 13,
    textAlign: 'center',
    opacity: 0.80,
  },
  dots: {
    position: 'absolute',
    top: 525,
    width: '100%',
    color: '#F4C542',
    fontFamily: 'Inter',
    fontSize: 10,
    textAlign: 'center',
    opacity: 0.70,
  },
  version: {
    position: 'absolute',
    bottom: 14,
    width: '100%',
    color: '#FFFFFF',
    fontFamily: 'Inter',
    fontSize: 13,
    textAlign: 'center',
    opacity: 0.80,
  },
});
