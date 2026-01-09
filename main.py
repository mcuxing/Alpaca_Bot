from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed
from utils import load_alpaca_credentials
from strategy import BollingerRSIStrategy
from datetime import datetime, timedelta
import os
import warnings
import pandas as pd
import csv

# Suppress the OpenSSL warning common on macOS
warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')

def log_performance(equity, cash, buying_power, position_qty, symbol):
    """
    Logs the daily performance to a CSV file.
    """
    log_file = "performance_log.csv"
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Check if file exists to write header
    file_exists = os.path.isfile(log_file)
    
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Equity", "Cash", "Buying_Power", "Symbol", "Position_Qty"])
        
        writer.writerow([today, equity, cash, buying_power, symbol, position_qty])
    
    print(f"Performance logged to {log_file}")

def main():
    # Define path to credentials file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    creds_path = os.path.join(current_dir, "paper_account_api_key.txt")
    
    print(f"Loading credentials from {creds_path}...")
    try:
        creds = load_alpaca_credentials(creds_path)
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return

    api_key = creds.get("api_key")
    secret_key = creds.get("secret_key")
    
    if not api_key or not secret_key:
        print("Error: API Key or Secret Key missing in credentials file.")
        return

    print("Initializing Clients...")
    trading_client = TradingClient(api_key, secret_key, paper=True)
    data_client = StockHistoricalDataClient(api_key, secret_key)

    # Get Account Info
    try:
        account = trading_client.get_account()
        print(f"\n--- Account Status ---")
        print(f"Buying Power: ${account.buying_power}")
        print(f"Equity: ${account.portfolio_value}")
        
        if float(account.buying_power) <= 0:
            print("⚠️ Insufficient buying power. Please add funds in Alpaca Dashboard.")
            return
            
    except Exception as e:
        print(f"Error getting account info: {e}")
        return

    # --- Strategy Execution ---
    symbol = "AVGO"
    print(f"\n--- Running Bollinger+RSI Strategy for {symbol} ---")
    
    # 1. Fetch recent data (enough for the strategy window)
    end_time = datetime.now() - timedelta(minutes=16) # Delay to avoid realtime restrictions
    start_time = end_time - timedelta(days=100) # Fetch 100 days to ensure we cover the windows
    
    request_params = StockBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=TimeFrame.Day,
        start=start_time,
        end=end_time,
        feed=DataFeed.IEX # Use IEX for free/paper tier
    )
    
    bars = data_client.get_stock_bars(request_params)
    if bars.df.empty:
        print("No data found for strategy calculation.")
        return
    df = bars.df.loc[symbol]
    
    # 2. Run Strategy Logic
    strategy = BollingerRSIStrategy(symbol)
    signals = strategy.generate_signals(df)
    
    # 3. Check latest signal
    latest_signal = signals['target_position'].iloc[-1]
    latest_price = df['close'].iloc[-1]
    current_volatility = signals['volatility'].iloc[-1]
    
    print(f"Latest Close Price: ${latest_price:.2f}")
    print(f"Latest Signal (1=Long, 0=Cash): {latest_signal}")
    print(f"Signal Reason: {signals['signal_type'].iloc[-1]}")
    
    # 4. PDT Protection Check (Simplified)
    # In a real bot, you would check trading_client.get_account().daytrade_count
    # or track your own trades for the day.
    
    try:
        # Check current position
        try:
            position = trading_client.get_open_position(symbol)
            current_qty = float(position.qty)
            print(f"Current Position: {current_qty} shares")
        except:
            current_qty = 0
            print(f"Current Position: 0 shares")
        
        # Execution Logic
        if latest_signal == 1 and current_qty == 0:
            print("Signal says BUY.")
            
            # Dynamic Position Sizing
            available_cash = float(account.cash)
            # Use the strategy's sizing logic
            qty_to_buy = strategy.calculate_position_size(latest_price, available_cash, current_holdings=0, volatility=current_volatility)
            
            if qty_to_buy > 0:
                print(f"Placing Market Buy Order for {qty_to_buy} shares...")
                order_data = MarketOrderRequest(symbol=symbol, qty=qty_to_buy, side=OrderSide.BUY, time_in_force=TimeInForce.DAY)
                trading_client.submit_order(order_data)
                print("Buy Order Submitted.")
            else:
                print("Calculated buy quantity is 0 (Insufficient funds?).")
            
        elif latest_signal == 0 and current_qty > 0:
            print("Signal says SELL.")
            # Check for PDT rule roughly: did we buy today?
            # A simple check is to see if position was entered today. 
            # (Skipping complex PDT check implementation for now, assuming user manages day trades or has >25k)
            
            print("Placing Market Sell Order...")
            trading_client.close_position(symbol)
            print("Sell Order Submitted (Position Closed).")
            
        else:
            print("No action required based on current position and signal.")
            
    except Exception as e:
        print(f"Error executing trade: {e}")
        
    # 5. Log Performance
    log_performance(account.portfolio_value, account.cash, account.buying_power, current_qty, symbol)

if __name__ == "__main__":
    main()
