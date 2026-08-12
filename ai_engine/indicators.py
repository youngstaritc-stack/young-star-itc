import pandas as pd
import numpy as np

class TechnicalAnalysis:
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
        return prices.ewm(span=period, adjust=False).mean()

    @classmethod
    def generate_signal(cls, df: pd.DataFrame) -> dict:
        if len(df) < 50:
            return {"signal": "HOLD", "reason": "Insufficient data"}

        df['rsi'] = cls.calculate_rsi(df['close'], period=14)
        df['ema_20'] = cls.calculate_ema(df['close'], period=20)
        df['ema_50'] = cls.calculate_ema(df['close'], period=50)

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        rsi_val = round(latest['rsi'], 2)
        ema_20_val = round(latest['ema_20'], 2)
        ema_50_val = round(latest['ema_50'], 2)
        current_price = latest['close']

        signal = "HOLD"
        reason = "Market in neutral zone"

        if (prev['ema_20'] <= prev['ema_50'] and latest['ema_20'] > latest['ema_50']) or (rsi_val < 30):
            signal = "BUY"
            reason = f"Bullish Crossover / Oversold RSI ({rsi_val})"
        elif (prev['ema_20'] >= prev['ema_50'] and latest['ema_20'] < latest['ema_50']) or (rsi_val > 70):
            signal = "SELL"
            reason = f"Bearish Crossover / Overbought RSI ({rsi_val})"

        return {
            "price": current_price,
            "rsi": rsi_val,
            "ema_20": ema_20_val,
            "ema_50": ema_50_val,
            "signal": signal,
            "reason": reason
        }
