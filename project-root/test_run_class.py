import sys
import os

sys.path.append(os.getcwd())

from backend.app.core.engine import GameState, Engine, Phase
from backend.app.core.card import CARD_DB

# 1. 클래스 데이터 정의 (테스트용)
CLASS_DB = {
    "Warrior": {
        "hp": 40, "gold": 0, "actions": 1, 
        "initial_deck": ["Copper"] * 7 + ["Estate"] * 3,
        "private_market": {"BloodArrow": 5}  # 전사 전용
    },
    "Mage": {
        "hp": 25, "gold": 0, "actions": 1,
        "initial_deck": ["Copper"] * 5 + ["Estate"] * 3 + ["Madness"] * 2,
        "private_market": {"BloodDraw": 3}   # 마법사 전용
    }
}

def run_class_test():
    print("🎭 [클래스 시스템 검증 시뮬레이션] 시작\n")
    
    player_ids = ["User_A", "User_B"]
    state = GameState(player_ids, debug=True)
    engine = Engine(state)

    # 2. 클래스 선택 및 게임 세팅
    # User_A: Warrior (탱커), User_B: Mage (유리대포)
    selections = {"User_A": "Warrior", "User_B": "Mage"}
    
    # Engine의 setup_game이 CLASS_DB를 참조하여 초기화한다고 가정
    # (실제 코드에서는 setup_game 내부에 위에서 만든 로직이 들어가야 함)
    engine.setup_game(player_classes=selections)

    print("\n--- 🛒 전용 마켓 접근 권한 검증 ---")
    
    # [검증 1] 전사(User_A)가 마법사 전용 카드 구매 시도
    state.turn_owner = "User_A"
    state.phase = Phase.BUY
    state.players["User_A"]["gold"] = 10
    success, msg = engine.buy_card("User_A", "BloodDraw")
    print(f"Warrior가 BloodDraw 구매 시도: {success} ({msg})")

    # [검증 2] 마법사(User_B)가 자기 전용 카드 구매 시도
    state.turn_owner = "User_B"
    state.players["User_B"]["gold"] = 10
    success, msg = engine.buy_card("User_B", "BloodDraw")
    print(f"Mage가 BloodDraw 구매 시도: {success} ({msg})")

    print("\n--- 🃏 초기 덱 구성 검증 ---")
    
    # [검증 3] 마법사(User_B)는 덱에 Madness를 가지고 시작함
    mage_deck_all = state.players["User_B"]["deck"] + state.players["User_B"]["hand"]
    has_madness = "Madness" in mage_deck_all
    print(f"Mage의 전체 카드 리스트에 'Madness' 포함 여부: {has_madness}")

    # 3. 최종 스냅샷 출력
    print("\n" + "="*65)
    print("📊 클래스별 초기화 결과 스냅샷")
    print("="*65)
    for pid in player_ids:
        p = state.players[pid]
        print(f"[{pid} - {selections[pid]}]")
        print(f" ❤️ HP: {p['hp']} | 💰 Gold: {p['gold']} | ⚡ Actions: {p['actions']}")
        print(f" 🎁 Private Market: {list(p['private_market'].keys())}")
        print("-" * 40)

if __name__ == "__main__":
    run_class_test()