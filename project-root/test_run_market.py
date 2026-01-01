import sys
import os

sys.path.append(os.getcwd())

from backend.app.core.engine import GameState, Engine, Phase
from backend.app.core.card import CARD_DB

def run_pure_economy_test():
    player_ids = ["User_A", "User_B"]
    state = GameState(player_ids, debug=True)
    engine = Engine(state)

    # 1. 클래스 셋업 (전사: BloodArrow(5원), 마법사: BloodDraw(3원))
    selections = {"User_A": "Warrior", "User_B": "Mage"}
    engine.setup_game(player_classes=selections)

    for pid in player_ids:
        state.turn_owner = pid
        p_state = state.players[pid]
        
        # [단계 1] 액션 단계 (그냥 통과)
        state.phase = Phase.ACTION
        
        # [단계 2] 구매 단계 진입
        state.phase = Phase.BUY
        
        # [중요] 보너스 골드 주입 금지! 오직 핸드의 재물 카드만 한 장씩 사용
        print(f"\n--- {pid}의 재물 사용 단계 ---")
        for card_name in list(p_state["hand"]):
            card = CARD_DB.get(card_name)
            if card and card.card_type == "TREASURE":
                engine.play_card(pid, card_name) # 여기서 골드가 1씩 올라가야 함

        # [단계 3] 구매 시도
        # 전사(User_A)는 시작 핸드에 구리 3~4장(3~4원)뿐이라 5원짜리 BloodArrow 구매에 실패해야 정상입니다.
        target_card = "BloodArrow" if pid == "User_A" else "BloodDraw"
        print(f"\n--- {pid}의 구매 시도: {target_card} ---")
        success, msg = engine.buy_card(pid, target_card)
        
        if not success:
            print(f"❌ 예상대로 구매 실패: {msg}")

    # 최종 로그 출력
    print("\n" + "="*60)
    print("📜 [순수 경제 시스템 로그]")
    print("="*60)
    for log in state.logs:
        if "SNAPSHOT" not in log:
            print(f"| {log}")
    print("="*60)

if __name__ == "__main__":
    run_pure_economy_test()