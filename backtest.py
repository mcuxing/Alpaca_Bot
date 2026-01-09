from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed
from utils import load_alpaca_credentials
from strategy import BollingerRSIStrategy
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime, timedelta

def run_backtest():
    # 1. Load Credentials
    current_dir = os.path.dirname(os.path.abspath(__file__))
    creds_path = os.path.join(current_dir, "paper_account_api_key.txt")
    creds = load_alpaca_credentials(creds_path)
    
    # 2. Fetch Historical Data
    print("Fetching historical data...")
    data_client = StockHistoricalDataClient(creds["api_key"], creds["secret_key"])
    
    symbol = "AVGO" # Updated symbol to AVGO
    end_time = datetime.now() - timedelta(minutes=16) 
    start_time = end_time - timedelta(days=365) # 1 year of data
    
    request_params = StockBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=TimeFrame.Day,
        start=start_time,
        end=end_time,
        feed=DataFeed.IEX 
    )
    
    try:
        bars = data_client.get_stock_bars(request_params)
        if bars.df.empty:
            print("No data found for the specified period.")
            return
        df = bars.df.loc[symbol]
    except Exception as e:
        print(f"Error fetching data: {e}")
        return
    
    # 3. Apply Strategy
    print(f"Running Bollinger+RSI Strategy on {len(df)} bars for {symbol}...")
    strategy = BollingerRSIStrategy(symbol)
    signals = strategy.generate_signals(df)
    
    # 4. Simulate Portfolio with $1,000,000
    initial_capital = 1000000.0
    cash = initial_capital
    holdings = 0
    portfolio_value = []
    
    # We need to iterate to simulate dynamic position sizing and capital updates
    for i in range(len(df)):
        price = df['close'].iloc[i]
        signal = signals['target_position'].iloc[i]
        
        # Calculate dynamic size based on current portfolio value (Cash + Stock Value)
        current_total_value = cash + (holdings * price)
        
        # Position Sizing Logic from Strategy Class
        # If signal is 1 (Long), we want to be fully invested (subject to sizing rules)
        if signal == 1 and holdings == 0:
            # Buy Entry
            # Check volatility for sizing
            volatility = signals['volatility'].iloc[i] if 'volatility' in signals.columns else None
            shares_to_buy = strategy.calculate_position_size(price, current_total_value, volatility=volatility)
            
            cost = shares_to_buy * price
            if cost <= cash:
                holdings = shares_to_buy
                cash -= cost
        
        elif signal == 0 and holdings > 0:
            # Sell Exit
            cash += holdings * price
            holdings = 0
            
        portfolio_value.append(cash + (holdings * price))
        
    portfolio_series = pd.Series(portfolio_value, index=df.index)
    
    # Calculate Benchmarks
    cumulative_returns = portfolio_series / initial_capital
    cumulative_buy_hold = (1 + df['close'].pct_change()).cumprod()
    
    # 5. Output Results
    print("\n--- Backtest Results (Capital: $1,000,000) ---")
    print(f"Period: {start_time.date()} to {end_time.date()}")
    print(f"Strategy Total Return: {(cumulative_returns.iloc[-1] - 1)*100:.2f}%")
    print(f"Buy & Hold Return: {(cumulative_buy_hold.iloc[-1] - 1)*100:.2f}%")
    print(f"Final Portfolio Value: ${portfolio_series.iloc[-1]:,.2f}")
    
    # 6. Plot
    plt.figure(figsize=(12,6))
    plt.plot(cumulative_returns, label='Bollinger+RSI Strategy')
    plt.plot(cumulative_buy_hold, label='Buy & Hold (AVGO)')
    plt.title(f'Backtest Result: {symbol} (BB+RSI)')
    plt.legend()
    plt.grid(True)
    
    output_img = "backtest_result.png"
    plt.savefig(output_img)
    print(f"\nChart saved to {output_img}")

if __name__ == "__main__":
    run_backtest()
