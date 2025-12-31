import sys
import os
import random

# 프로젝트 루트 경로 추가
sys.path.append(os.getcwd())

from backend.app.core.engine import GameState, Engine, Phase
from backend.app.core.card import CARD_DB, ActionCard, TreasureCard

def run_10_turn_simulation():
    print("🏟️ [10턴 시뮬레이션 시작] 개발자 모드 활성화\n")
    
    player_ids = ["User_A", "User_B"]
    state = GameState(player_ids, debug=True)
    engine = Engine(state)
    engine.setup_game()

    # 10턴(각 플레이어당 10번, 총 20회 턴 소유) 진행
    # 턴 종료 로직에서 turn_count가 올라가므로 이를 기준으로 루프
    while state.turn_count <= 10:
        current_pid = state.turn_owner
        p_data = state.players[current_pid]
        
        print(f"\n--- [TURN {state.turn_count}] {current_pid}의 시작 ---")

        # 1. 액션 단계 (손패에 액션 카드가 있고 액션 횟수가 남았을 때)
        while p_data["actions"] > 0:
            actions_in_hand = [c for c in p_data["hand"] if isinstance(CARD_DB.get(c), ActionCard)]
            if not actions_in_hand:
                break
            
            # 전략: 아무 액션이나 하나 사용 (여기서는 첫 번째 카드)
            card_to_play = actions_in_hand[0]
            engine.play_card(current_pid, card_to_play)

        # 2. 재물 단계 (손패의 모든 재물 카드 사용)
        while True:
            treasures_in_hand = [c for c in p_data["hand"] if isinstance(CARD_DB.get(c), TreasureCard)]
            if not treasures_in_hand:
                break
            engine.play_card(current_pid, treasures_in_hand[0])

        # 3. 구매 단계 (가장 가치 있는 카드 구매)
        # 전략: 8원이면 Province, 5원이면 Market/Duchy, 3원이면 Silver 등
        while p_data["buys"] > 0:
            affordable = [name for name, count in state.supply.items() 
                         if count > 0 and CARD_DB[name].cost <= p_data["gold"]]
            
            if not affordable:
                break
            
            # 전략적 우선순위 순으로 정렬 (Province > Gold > Market > Silver ...)
            priority = ["Province", "Gold", "Duchy", "Market", "Smithy", "Village", "Silver", "Estate", "Copper"]
            to_buy = None
            for p in priority:
                if p in affordable:
                    to_buy = p
                    break
            
            if to_buy:
                engine.buy_card(current_pid, to_buy)
            else:
                break

        # 4. 페이즈 종료 및 턴 넘기기
        # 현재 ACTION/BUY 페이즈일 것이므로 next_phase를 호출하여 _end_turn까지 유도
        while state.turn_owner == current_pid:
            engine.next_phase()

    # ────────────────────────────────────────────────────────────
    # 📜 최종 결과 보고
    # ────────────────────────────────────────────────────────────
    print("\n" + "="*60)
    print("🏆 10턴 시뮬레이션 종료 리포트")
    print("="*60)
    
    for pid in player_ids:
        p = state.players[pid]
        print(f"[{pid}] HP: {p['hp']} | 점수: {p['victory_points']} | 최종 골드 보유력: {p['gold']}")
        # 전체 카드 리스트 확인 (Hand + Deck + Discard)
        all_cards = p["hand"] + p["deck"] + p["discard"]
        print(f"보유 카드 전체: {all_cards}\n")

    print("📜 [DEBUG LOG] 전체 로그")
    for log in state.logs:
        print(f"> {log}")

if __name__ == "__main__":
    run_10_turn_simulation()