"""
거래 데이터 로깅 유틸리티
"""

import json
import os
from datetime import datetime
from typing import Dict, List


class TradingLogger:
    def __init__(self, log_file='trading_data.json'):
        self.log_file = log_file
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """로그 파일이 없으면 생성"""
        if not os.path.exists(self.log_file):
            initial_data = {
                'current_position': None,
                'trades': [],
                'scans': []
            }
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=2)

    def load_data(self) -> Dict:
        """데이터 로드"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                'current_position': None,
                'trades': [],
                'scans': []
            }

    def save_data(self, data: Dict):
        """데이터 저장"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def log_scan(self, top_coins: List[Dict], gpt_recommendation: Dict = None):
        """스캔 결과 기록"""
        data = self.load_data()

        scan_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'top_coins': top_coins,
            'gpt_recommendation': gpt_recommendation
        }

        data['scans'].append(scan_entry)

        # 최근 50개만 유지
        data['scans'] = data['scans'][-50:]

        self.save_data(data)

    def log_buy(self, coin: str, price: float, amount: float, investment: float):
        """매수 기록"""
        data = self.load_data()

        data['current_position'] = {
            'coin': coin,
            'entry_price': price,
            'amount': amount,
            'investment': investment,
            'entry_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        self.save_data(data)

    def log_sell(self, coin: str, entry_price: float, exit_price: float,
                 amount: float, reason: str, profit_rate: float):
        """매도 기록"""
        data = self.load_data()

        trade_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'coin': coin,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'amount': amount,
            'profit_rate': profit_rate,
            'reason': reason,
            'profit_krw': (exit_price - entry_price) * amount
        }

        data['trades'].append(trade_entry)
        data['current_position'] = None

        self.save_data(data)

    def update_position(self, current_price: float, profit_rate: float):
        """현재 포지션 업데이트"""
        data = self.load_data()

        if data['current_position']:
            data['current_position']['current_price'] = current_price
            data['current_position']['profit_rate'] = profit_rate
            data['current_position']['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            self.save_data(data)

    def get_current_position(self) -> Dict:
        """현재 포지션 조회"""
        data = self.load_data()
        return data.get('current_position')

    def get_trades(self) -> List[Dict]:
        """거래 내역 조회"""
        data = self.load_data()
        return data.get('trades', [])

    def get_recent_scans(self, limit: int = 10) -> List[Dict]:
        """최근 스캔 결과 조회"""
        data = self.load_data()
        scans = data.get('scans', [])
        return scans[-limit:]

    def get_stats(self) -> Dict:
        """통계 계산"""
        trades = self.get_trades()

        if not trades:
            return {
                'total_trades': 0,
                'win_trades': 0,
                'lose_trades': 0,
                'win_rate': 0,
                'total_profit_rate': 0,
                'avg_profit_rate': 0
            }

        win_trades = [t for t in trades if t['profit_rate'] > 0]
        lose_trades = [t for t in trades if t['profit_rate'] <= 0]

        total_profit_rate = sum(t['profit_rate'] for t in trades)

        return {
            'total_trades': len(trades),
            'win_trades': len(win_trades),
            'lose_trades': len(lose_trades),
            'win_rate': (len(win_trades) / len(trades) * 100) if trades else 0,
            'total_profit_rate': total_profit_rate,
            'avg_profit_rate': total_profit_rate / len(trades) if trades else 0
        }
