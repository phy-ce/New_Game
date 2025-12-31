import sys
import os

# 프로젝트 루트 경로 추가 (backend 디렉토리가 보이도록)
sys.path.append(os.getcwd())

from backend.app.core.engine import GameState, Engine, Phase
from backend.app.core.card import CARD_DB


def test_debug_turn_system():
    # 1. 개발자 모드 켜기
    state = GameState(["User_A", "User_B"], debug=True)
    engine = Engine(state)
    engine.setup_game()

    print(f"현재 게임 시작! 턴: {state.turn_count}, 주인: {state.turn_owner}")
    
    # 2. User_A가 카드 한 장 쓰고 턴 종료
    engine.play_card("User_A", "Copper")
    engine.next_phase() # ACTION -> BUY
    engine.next_phase() # BUY -> 턴 종료 (자동 호출됨)

    # 3. 전체 로그 확인 (스냅샷 포함)
    print("\n--- 📜 개발자 모드 전체 로그 ---")
    for log in state.logs:
        print(log)

if __name__ == "__main__":
    test_debug_turn_system()