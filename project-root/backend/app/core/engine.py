from enum import Enum
from typing import List, Dict, Any, Tuple
import random

# 외부 모듈 참조 (앞서 만든 파일들)
from .card import CARD_DB, ActionCard, TreasureCard
from .deck import DeckManager

# ──────────────────────────────────────────────────────────────
# 1️⃣ 게임 단계 정의
# ──────────────────────────────────────────────────────────────
class Phase(Enum):
    ACTION = 1   # 액션 카드 사용 단계
    BUY    = 2   # 구매 단계
    CLEAN_UP = 3 # 정리 단계 (손패 재정비 - 엔진 내부에서 자동 처리)


# ──────────────────────────────────────────────────────────────
# 2️⃣ 전체 게임 상태 객체 (순수 데이터)
# ──────────────────────────────────────────────────────────────
class GameState:
    def __init__(self, player_ids: List[str]):
        self.player_ids = player_ids
        self.phase: Phase = Phase.ACTION
        self.turn_owner: str = player_ids[0]

        # 중앙 공급처 수량
        self.supply: Dict[str, int] = {
            "Copper": 60, "Silver": 40, "Gold": 30,
            "Estate": 24, "Duchy": 12, "Province": 12,
            "Village": 10, "Smithy": 10, "Market": 10
        }

        # 플레이어별 가변 상태
        self.players: Dict[str, Dict[str, Any]] = {
            pid: {
                "hand": [],      # 손패 (카드 이름 리스트)
                "deck": [],      # 덱
                "discard": [],   # 버림패
                "actions": 1,    # 남은 액션 횟수
                "buys": 1,       # 남은 구매 횟수
                "gold": 0,       # 이번 턴에 발생한 구매력
                "victory_points": 3, # 초기 사유지 3장의 점수
                "hp" : 20,
                "mana": 10
            } for pid in player_ids
        }

        self.logs: List[str] = []


# ──────────────────────────────────────────────────────────────
# 3️⃣ 게임 엔진 (규칙 집행자)
# ──────────────────────────────────────────────────────────────
class Engine:
    def __init__(self, game_state: GameState):
        self.state = game_state
        # 플레이어별 덱 매니저 연결 (참조 전달)
        self.deck_managers = {
            pid: DeckManager(self.state.players[pid]) 
            for pid in self.state.player_ids
        }
    # 플레이어 상대방 ID 반환
    def get_opponent_id(self, player_id: str) -> str:
        """현재 플레이어를 제외한 상대방의 ID를 반환합니다."""
        # player_ids 리스트에서 현재 player_id가 아닌 첫 번째 요소를 찾음
        return [pid for pid in self.state.player_ids if pid != player_id][0]
    
    # [초기화] 게임 시작 세팅
    def setup_game(self) -> None:
        """모든 플레이어의 초기 덱을 설정하고 5장을 드로우합니다."""
        for pid in self.state.player_ids:
            self.deck_managers[pid].initialize_deck()
            self.deck_managers[pid].draw(5)
        self.state.logs.append("🎮 게임이 시작되었습니다! 각자 5장의 카드를 뽑습니다.")

    # [액션/재물] 카드 사용 통합 로직
    def play_card(self, player_id: str, card_name: str) -> Tuple[bool, str]:
        """플레이어가 핸드에서 카드를 클릭했을 때 실행되는 핵심 함수"""
        player = self.state.players[player_id]
        
        # 1. 공통 검증
        if self.state.turn_owner != player_id:
            return False, "현재 본인의 턴이 아닙니다."
        
        if card_name not in player["hand"]:
            return False, f"손패에 {card_name} 카드가 없습니다."

        card = CARD_DB.get(card_name)
        if not card:
            return False, "존재하지 않는 카드 데이터입니다."

        # 2. 카드 타입별 개별 검증 및 페이즈 전환
        if isinstance(card, ActionCard):
            if self.state.phase != Phase.ACTION:
                msg = "액션 페이즈가 아닙니다."
                self.state.logs.append(f"❌ {player_id}: {msg}") # 로그 추가
                return False, msg
            if player["actions"] <= 0:
                msg = "사용 가능한 액션 횟수가 없습니다."
                self.state.logs.append(f"❌ {player_id}: {msg}") # 로그 추가
                return False, msg
            player["actions"] -= 1

        elif isinstance(card, TreasureCard):
            # 재물을 내면 자동으로 구매 페이즈로 전환 (도미니언 규칙)
            if self.state.phase == Phase.ACTION:
                self.state.phase = Phase.BUY
                self.state.logs.append(f"💰 {player_id}가 재물을 사용하며 구매 페이즈로 전환합니다.")
        
        else:
            return False, "이 카드는 플레이할 수 없습니다 (승점 카드 등)."

        # 3. 카드 이동 및 효과 실행
        player["hand"].remove(card_name)

        self.state.logs.append(f"✨ {player_id}님이 {card_name} 카드를 사용했습니다.")
        # 다형성 활용: ActionCard.play() 또는 TreasureCard.play() 자동 실행
        card.play(self, player_id) 
        
        # 사용한 카드는 버림패로 (도미니언은 필드에 두지만 구현 편의상 버림패로 바로 이동)
        self.deck_managers[player_id].add_to_discard(card_name)
        

        return True, "성공"

    # [구매] 카드 구매 로직
    def buy_card(self, player_id: str, card_name: str) -> Tuple[bool, str]:
        player = self.state.players[player_id]
        card = CARD_DB.get(card_name)

        # 1. 검증
        if self.state.phase != Phase.BUY:
            return False, "구매 페이즈가 아닙니다."
        if player["buys"] <= 0:
            return False, "남은 구매 횟수가 없습니다."
        if self.state.supply.get(card_name, 0) <= 0:
            return False, "해당 카드의 재고가 없습니다."
        
        cost = card.cost if card else 999
        if player["gold"] < cost:
            return False, f"골드가 부족합니다 (필요: {cost}, 보유: {player['gold']})"

        # 2. 처리
        player["buys"] -= 1
        player["gold"] -= cost
        self.state.supply[card_name] -= 1
        self.deck_managers[player_id].add_to_discard(card_name)

        self.state.logs.append(f"🛒 {player_id}님이 {card_name}을(를) 구매했습니다.")
        
        # 승점 카드인 경우 점수 합산 (선택 사항)
        if card.card_type == "VICTORY":
            player["victory_points"] += getattr(card, 'points', 0)

        return True, "구매 성공"

    # [페이즈] 다음 단계로 전환
    def next_phase(self) -> None:
        """유저가 '페이즈 종료' 버튼을 눌렀을 때 호출"""
        if self.state.phase == Phase.ACTION:
            self.state.phase = Phase.BUY
            self.state.logs.append("➡️ 구매 페이즈로 넘어갑니다.")
        elif self.state.phase == Phase.BUY:
            # 구매 종료 시 정리 단계는 자동으로 수행 후 다음 플레이어 턴으로
            self._end_turn()
            self.state.phase = Phase.ACTION

    # [턴 종료] 내부 정리 로직
    def _end_turn(self) -> None:
        pid = self.state.turn_owner
        manager = self.deck_managers[pid]

        # 1. 정리(Clean-up): 손패 다 버리고 5장 새로 뽑기
        manager.discard_hand()
        manager.draw(5)

        # 2. 자원 초기화
        player = self.state.players[pid]
        player["actions"] = 1
        player["buys"] = 1
        player["gold"] = 0

        # 3. 턴 주인 교체
        pids = self.state.player_ids
        current_idx = pids.index(pid)
        self.state.turn_owner = pids[(current_idx + 1) % len(pids)]
        
        self.state.logs.append(f"턴 종료. 이제 {self.state.turn_owner}의 턴입니다.")

    # [드로우] 로그 출력을 포함한 드로우 대행 (카드 효과 등에서 호출)
    def draw_card(self, player_id: str, count: int = 1) -> None:
        actual_drawn = self.deck_managers[player_id].draw(count)
        if actual_drawn > 0:
            self.state.logs.append(f"🎴 {player_id}님이 {actual_drawn}장의 카드를 뽑았습니다.")

    def apply_hp_change(self, target_id: str, amount: int):
        target = self.state.players[target_id]
        
        # 소문자 hp에 연산 적용
        target["hp"] += amount 
        
        action_type = "회복" if amount > 0 else "자해"
        self.state.logs.append(f"🩸 {target_id}가 {abs(amount)}만큼 {action_type}했습니다. (남은 hp: {target['hp']})")

        if target["hp"] <= 0:
            self.state.is_game_over = True
            winner_id = self.get_opponent_id(target_id)
            self.state.winner = winner_id
            self.state.logs.append(f"💀 {target_id}가 사망했습니다! 승자: {winner_id}")

    def apply_damage(self, opponent_id: str, damage: int):
        """상대방에게 공격을 가함 (apply_hp_change의 래퍼 함수)"""
        self.apply_hp_change(opponent_id, -damage)