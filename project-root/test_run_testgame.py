import sys
import os
import random

sys.path.append(os.getcwd())

from backend.app.core.engine import GameState, Engine, Phase
from backend.app.core.card import CARD_DB, CLASS_DB

def smart_ai_decision(pid, engine):
    """AI의 의사결정 로직"""
    p_state = engine.state.players[pid]
    
    # 1. 액션 페이즈 판단
    if engine.state.phase == Phase.ACTION:
        actions = [c for c in p_state["hand"] if CARD_DB[c].card_type == "ACTION"]
        if not actions:
            return None
        
        for card_name in actions:
            card = CARD_DB[card_name]
            # [전략] 체력이 20 이하인데 자폭 카드(Madness 등)라면 사용하지 않음
            if hasattr(card, 'add_hp') and card.add_hp < 0:
                if p_state["hp"] <= abs(card.add_hp) + 5: # 여유치 5 남김
                    continue
            return card_name
            
    # 2. 구매 페이즈 판단
    elif engine.state.phase == Phase.BUY:
        # [전략] 현재 골드로 살 수 있는 가장 비싼 전용 카드 혹은 실버/골드 선택
        available_private = [c for c in p_state["private_market"] if p_state["private_market"][c] > 0]
        affordable = [c for c in (available_private + ["Gold", "Silver"]) 
                      if CARD_DB[c].cost <= p_state["gold"]]
        
        if affordable:
            # 가장 비싼 카드 순으로 정렬하여 구매
            affordable.sort(key=lambda x: CARD_DB[x].cost, reverse=True)
            return affordable[0]
            
    return None

def run_smart_random_battle():
    # 1. 클래스 랜덤 선택
    available_classes = list(CLASS_DB.keys())
    selections = {
        "User_A": random.choice(available_classes),
        "User_B": random.choice(available_classes)
    }
    
    print(f"🎲 [랜덤 매치] {selections['User_A']}(A) vs {selections['User_B']}(B)\n")
    
    player_ids = ["User_A", "User_B"]
    state = GameState(player_ids, debug=True)
    engine = Engine(state)
    engine.setup_game(player_classes=selections)

    for turn in range(1, 21): # 더 긴 호흡의 전투를 위해 20턴으로 설정
        if state.is_game_over: break
        print(f"\n{'='*25} TURN {turn} {'='*25}")

        for _ in range(len(player_ids)):
            if state.is_game_over: break
            current_pid = state.turn_owner
            
            # --- [단계 1] 액션 페이즈 ---
            engine.state.phase = Phase.ACTION
            while state.players[current_pid]["actions"] > 0 and not state.is_game_over:
                action_to_take = smart_ai_decision(current_pid, engine)
                if not action_to_take: break
                engine.play_card(current_pid, action_to_take)

            # --- [단계 2] 구매 페이즈 ---
            if state.is_game_over: break
            engine.state.phase = Phase.BUY
            
            # 모든 재물 카드 자동 사용
            hand_copy = list(state.players[current_pid]["hand"])
            for c_name in hand_copy:
                if CARD_DB[c_name].card_type == "TREASURE":
                    engine.play_card(current_pid, c_name)
            
            # 최적의 카드 구매
            while state.players[current_pid]["buys"] > 0 and not state.is_game_over:
                buy_to_take = smart_ai_decision(current_pid, engine)
                if not buy_to_take: break
                engine.buy_card(current_pid, buy_to_take)

            # --- [단계 3] 턴 종료 ---
            engine._end_turn()

    # 최종 결과 출력 (이전과 동일)
    print(f"\n🏁 시뮬레이션 종료 | 승자: {state.winner if state.winner else '무승부'}")
    for log in state.logs: print(f"| {log}")

if __name__ == "__main__":
    run_smart_random_battle()