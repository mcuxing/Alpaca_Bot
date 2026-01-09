import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_performance():
    log_file = "performance_log.csv"
    
    if not os.path.exists(log_file):
        print(f"No log file found at {log_file}. Run main.py first to generate data.")
        return

    try:
        df = pd.read_csv(log_file)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df.set_index('Timestamp', inplace=True)
        
        # Calculate Returns
        initial_equity = df['Equity'].iloc[0]
        df['Return %'] = ((df['Equity'] - initial_equity) / initial_equity) * 100
        
        # Plot
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        # Plot Equity Curve
        color = 'tab:blue'
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Equity ($)', color=color)
        ax1.plot(df.index, df['Equity'], color=color, marker='o', label='Equity')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True)
        
        # Plot Position Size on secondary axis (optional, to see exposure)
        ax2 = ax1.twinx()  
        color = 'tab:orange'
        ax2.set_ylabel('Position Qty', color=color)  
        ax2.plot(df.index, df['Position_Qty'], color=color, linestyle='--', alpha=0.5, label='Holdings')
        ax2.tick_params(axis='y', labelcolor=color)
        
        plt.title('Live Trading Performance Tracking')
        fig.tight_layout()  
        
        output_img = "live_performance.png"
        plt.savefig(output_img)
        print(f"Performance chart saved to {output_img}")
        
        # Print Summary
        print("\n--- Performance Summary ---")
        print(df.tail(1)[['Equity', 'Return %', 'Position_Qty']])

    except Exception as e:
        print(f"Error plotting performance: {e}")

if __name__ == "__main__":
    plot_performance()
