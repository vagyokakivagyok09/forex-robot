�H"""
Trade History Tracker

Tracks executed trades, their outcomes, and calculates statistics
"""

import json
import os
from datetime import datetime


class TradeTracker:
    """Manages trade history and statistics"""
    
    def __init__(self, history_file='trade_history.json'):
        """
        Initialize Trade Tracker
        
        Args:
            history_file: Path to JSON file for storing history
        """
        self.history_file = history_file
        self.history = self.load_history()
    
    def load_history(self):
        """Load trade history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Error loading history: {e}")
                return {}
        return {}
    
    def save_history(self):
        """Save trade history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving history: {e}")
    
    def add_signal(self, symbol, signal_type, entry, tp, sl, current_price):
        """
        Record a new trading signal
        
        Args:
            symbol: Currency pair
            signal_type: 'BUY' or 'SELL'
            entry: Entry price
            tp: Take profit price
            sl: Stop loss price
            current_price: Current market price
        
        Returns:
            bool: True if signal was new (not duplicate)
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check if signal already exists for today
        if symbol in self.history:
            if self.history[symbol].get('date') == today:
                return False  # Duplicate signal
        
        # Calculate pip values
        pip_multiplier = 100 if "JPY" in symbol else 10000
        
        if signal_type == 'BUY':
            pips_target = (tp - entry) * pip_multiplier
            pips_risk = (entry - sl) * pip_multiplier
        else:  # SELL
            pips_target = (entry - tp) * pip_multiplier
            pips_risk = (sl - entry) * pip_multiplier
        
        # Store signal
        self.history[symbol] = {
            'date': today,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'direction': signal_type,
            'entry': entry,
            'tp': tp,
            'sl': sl,
            'status': 'open',
            'pips_target': pips_target,
            'pips_risk': pips_risk,
            'current_price': current_price
        }
        
        self.save_history()
        return True
    
    def check_trade_outcome(self, symbol, current_price):
        """
        Check if an open trade has hit TP or SL
        
        Args:
            symbol: Currency pair
            current_price: Current market price
        
        Returns:
            dict or None: {'outcome': 'tp_hit'|'sl_hit', 'pips': float} or None
        """
        if symbol not in self.history:
            return None
        
        trade = self.history[symbol]
        
        if trade.get('status') != 'open':
            return None  # Already closed
        
        direction = trade['direction']
        tp = trade['tp']
        sl = trade['sl']
        entry = trade['entry']
        
        pip_multiplier = 100 if "JPY" in symbol else 10000
        
        # Check for TP hit
        if direction == 'BUY':
            if current_price >= tp:
                pips_result = trade['pips_target']
                self.history[symbol]['status'] = 'tp_hit'
                self.history[symbol]['exit_price'] = current_price
                self.history[symbol]['pips_result'] = pips_result
                self.history[symbol]['exit_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.save_history()
                return {'outcome': 'tp_hit', 'pips': pips_result}
            
            elif current_price <= sl:
                pips_result = -trade['pips_risk']
                self.history[symbol]['status'] = 'sl_hit'
                self.history[symbol]['exit_price'] = current_price
                self.history[symbol]['pips_result'] = pips_result
                self.history[symbol]['exit_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.save_history()
                return {'outcome': 'sl_hit', 'pips': pips_result}
        
        else:  # SELL
            if current_price <= tp:
                pips_result = trade['pips_target']
                self.history[symbol]['status'] = 'tp_hit'
                self.history[symbol]['exit_price'] = current_price
                self.history[symbol]['pips_result'] = pips_result
                self.history[symbol]['exit_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.save_history()
                return {'outcome': 'tp_hit', 'pips': pips_result}
            
            elif current_price >= sl:
                pips_result = -trade['pips_risk']
                self.history[symbol]['status'] = 'sl_hit'
                self.history[symbol]['exit_price'] = current_price
                self.history[symbol]['pips_result'] = pips_result
                self.history[symbol]['exit_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.save_history()
                return {'outcome': 'sl_hit', 'pips': pips_result}
        
        return None
    
    def get_statistics(self):
        """
        Calculate trading statistics
        
        Returns:
            dict: Statistics summary
        """
        total_trades = 0
        wins = 0
        losses = 0
        open_trades = 0
        total_pips = 0.0
        
        for symbol, data in self.history.items():
            if symbol.startswith('_'):  # Skip metadata
                continue
            
            status = data.get('status')
            
            if status == 'tp_hit':
                wins += 1
                total_trades += 1
                total_pips += data.get('pips_result', 0)
            
            elif status == 'sl_hit':
                losses += 1
                total_trades += 1
                total_pips += data.get('pips_result', 0)
            
            elif status == 'open':
                open_trades += 1
        
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'open_trades': open_trades,
            'win_rate': win_rate,
            'total_pips': total_pips
        }
    
    def get_open_trades(self):
        """
        Get all open trades
        
        Returns:
            dict: Open trades
        """
        open_trades = {}
        
        for symbol, data in self.history.items():
            if symbol.startswith('_'):
                continue
            
            if data.get('status') == 'open':
                open_trades[symbol] = data
        
        return open_trades
    
    def clear_old_signals(self, days=7):
        """
        Remove signals older than specified days
        
        Args:
            days: Number of days to keep
        """
        today = datetime.now()
        to_remove = []
        
        for symbol, data in self.history.items():
            if symbol.startswith('_'):
                continue
            
            date_str = data.get('date')
            if date_str:
                try:
                    signal_date = datetime.strptime(date_str, '%Y-%m-%d')
                    age = (today - signal_date).days
                    
                    if age > days and data.get('status') != 'open':
                        to_remove.append(symbol)
                
                except:
                    pass
        
        for symbol in to_remove:
            del self.history[symbol]
        
        if to_remove:
            self.save_history()
            print(f"🧹 Cleaned up {len(to_remove)} old signals")


# Example usage
if __name__ == "__main__":
    print("🔍 Testing Trade Tracker\n")
    
    tracker = TradeTracker()
    
    # Test 1: Add signal
    print("Test 1: Add new signal")
    success = tracker.add_signal(
        symbol='EURUSD',
        signal_type='BUY',
        entry=1.08500,
        tp=1.08700,
        sl=1.08300,
        current_price=1.08550
    )
    print(f"Signal added: {success}\n")
    
    # Test 2: Check statistics
    print("Test 2: Get statistics")
    stats = tracker.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()
    
    # Test 3: Check trade outcome
    print("Test 3: Check for TP hit")
    outcome = tracker.check_trade_outcome('EURUSD', 1.08750)
    print(f"Outcome: {outcome}")
�H*cascade082,file:///c:/Users/Tomi/FOREX/trade_tracker.py