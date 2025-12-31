# test_run.py
from backend.app.core.engine import GameState, Engine, Phase

def test_game():
    # 1. 초기화
    player_ids = ["User_A", "User_B"]
    state = GameState(player_ids)
    engine = Engine(state)

    print("--- 1단계: 게임 셋업 ---")
    engine.setup_game()
    
    # 플레이어 A의 상태 확인
    a_hand = state.players["User_A"]["hand"]
    print(f"User_A의 첫 핸드: {a_hand}")

    print("\n--- 2단계: 카드 사용 테스트 (액션) ---")
    # 강제로 핸드에 'Smithy' 한 장을 넣어줍니다 (테스트용)
    state.players["User_A"]["hand"].append("Smithy")
    
    # Smithy 사용 (대장장이는 +3 드로우 효과가 있어야 함)
    success, msg = engine.play_card("User_A", "Smithy")
    print(f"Smithy 사용 결과: {success}, {msg}")
    print(f"User_A의 현재 핸드 개수: {len(state.players['User_A']['hand'])}장")
    print(f"남은 액션 포인트: {state.players['User_A']['actions']}")

    print("\n--- 3단계: 페이즈 전환 및 구매 테스트 ---")
    engine.next_phase() # BUY 페이즈로 이동
    print(f"현재 페이즈: {state.phase}")

    # 강제로 돈 10원 주기
    state.players["User_A"]["gold"] = 10
    
    # 'Province' (8원) 구매 시도
    success, msg = engine.buy_card("User_A", "Province")
    print(f"Province 구매 결과: {success}, {msg}")
    print(f"상점의 Province 남은 수량: {state.supply['Province']}")

    print("\n--- 4단계: 턴 종료 및 교체 ---")
    engine.next_phase() # CLEAN_UP 및 턴 교체
    print(f"새로운 턴 주인: {state.turn_owner}")
    print(f"User_A의 버림패 상황: {state.players['User_A']['discard']}")

    print("\n--- 전체 로그 확인 ---")
    for log in state.logs:
        print(f"[LOG] {log}")

if __name__ == "__main__":
    test_game()