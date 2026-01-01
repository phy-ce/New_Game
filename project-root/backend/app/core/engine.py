from enum import Enum
from typing import List, Dict, Any, Tuple
import random

# 외부 모듈 참조 (앞서 만든 파일들)
from .card import CARD_DB, CLASS_DB, ActionCard, TreasureCard
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
    def __init__(self, player_ids: List[str], debug: bool = False):
        self.player_ids = player_ids
        self.phase: Phase = Phase.ACTION
        self.turn_owner: str = player_ids[0]
        self.debug: bool = debug
        self.turn_count = 1  # 현재 게임의 총 턴 수

        self.is_game_over = False 
        self.winner = None


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
                "play_mat": [],  # 플레이 매트 (사용한 카드들)
                "actions": 1,    # 남은 액션 횟수
                "buys": 1,       # 남은 구매 횟수
                "gold": 0,       # 이번 턴에 발생한 구매력
                "victory_points": 3, # 초기 사유지 3장의 점수
                "hp" : 20,
                "mana": 10,


                "private_market": {
                    "BloodDraw": 5, 
                    "BloodArrow": 5, 
                    "Madness": 2,
                    "HolyLight": 10
                                },



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
    def setup_game(self, player_classes: dict):
        for pid in self.state.player_ids:
            class_name = player_classes.get(pid, "Warrior") # 기본값은 전사
            class_data = CLASS_DB.get(class_name)
            
            p = self.state.players[pid]
            
            # 1. 스탯 초기화
            p["hp"] = class_data["hp"]
            p["gold"] = class_data["gold"]
            p["actions"] = class_data["actions"]
            p["private_market"] = class_data["private_market"].copy()
            
            # 2. 클래스별 초기 덱 구성
            # 기존에는 모두 똑같이 Copper 7, Estate 3이었지만 이제 클래스에 따라 다름
            p["deck"] = class_data["initial_deck"].copy()
            import random
            random.shuffle(p["deck"])
            
            # 3. 초기 핸드 드로우 (5장)
            self.draw_card(pid, 5)

        self.log_success("SYSTEM", "각 플레이어의 클래스에 맞춰 초기 세팅이 완료되었습니다.")


    def log_success(self, player_id: str, message: str, is_debug: bool = False) -> Tuple[bool, str]:
        if not is_debug or self.state.debug:
            prefix = "[Debug] " if is_debug else ""
            self.state.logs.append(f"{prefix}✨ {player_id}: {message}")
            
            # 조건: 디버그 모드 ON + 자잘한 로그 아님 + 게임 셋업 완료 후(turn_count > 0)
            if self.state.debug and not is_debug and self.state.turn_count > 0:
                snapshot_type = "GAME_OVER_FINAL" if self.state.is_game_over else "EVENT_OCCURRED"
                self._print_debug_snapshot(action_type=snapshot_type)
                
                
        return True, "성공"

    def log_fail(self, player_id: str, message: str) -> Tuple[bool, str]:
        """
        실패 사유를 로그에 남기고 (False, 에러메시지)를 반환합니다.
        실패는 수치 변화가 없으므로 스냅샷을 찍지 않습니다.
        """
        self.state.logs.append(f"❌ {player_id}: {message}")
        return False, message

        
    # [액션/재물] 카드 사용 통합 로직
    def play_card(self, player_id: str, card_name: str) -> Tuple[bool, str]:
        """플레이어가 핸드에서 카드를 클릭했을 때 실행되는 핵심 함수"""
        player = self.state.players[player_id]
        card = CARD_DB.get(card_name)
        errors = []

        # ----------------------------------------------------------
        # 1. 검증 단계 (에러 수집)
        # ----------------------------------------------------------
        # 공통 검증
        if self.state.turn_owner != player_id:
            errors.append("현재 본인의 턴이 아닙니다.")
        
        if card_name not in player["hand"]:
            errors.append(f"손패에 {card_name} 카드가 없습니다.")

        if not card:
            errors.append("존재하지 않는 카드 데이터입니다.")
        else:
            # 카드 타입별 개별 검증
            if isinstance(card, ActionCard):
                if self.state.phase != Phase.ACTION:
                    errors.append("액션 페이즈가 아닙니다.")
                if player["actions"] <= 0:
                    errors.append("사용 가능한 액션 횟수가 없습니다.")
            
            elif isinstance(card, TreasureCard):
                # 재물은 액션이나 구매 페이즈 모두에서 낼 수 있지만, 
                # 상태가 CLEANUP 같은 곳에 있으면 안 됨 (확장성을 위해 체크)
                if self.state.phase not in [Phase.ACTION, Phase.BUY]:
                    errors.append("현재 페이즈에서는 재물을 사용할 수 없습니다.")
            
            else:
                errors.append("이 카드는 플레이할 수 없습니다 (승점 카드 등).")

        # 수집된 에러가 있으면 한 번에 리턴
        if errors:
            return self.log_fail(player_id, " | ".join(errors))

        # ----------------------------------------------------------
        # 2. 처리 단계 (검증 통과 후)
        # ----------------------------------------------------------
        # [추가] 게임 종료 후 액션 방지



        # 자원 차감 및 페이즈 전환
        if isinstance(card, ActionCard):
            player["actions"] -= 1
        elif isinstance(card, TreasureCard):
            if self.state.phase == Phase.ACTION:
                self.state.phase = Phase.BUY
                self.log_success(player_id, "재물을 사용하며 구매 페이즈로 전환합니다.", is_debug=True)
        

        self.log_success(player_id, f"{card_name} 카드를 사용합니다.")
        # 효과 실행
        player["hand"].remove(card_name)
        self.deck_managers[player_id].add_to_play_mat(card_name)
        card.play(self, player_id) 
        self.log_success(player_id, f"{card_name} 카드를 사용했습니다.")





        # 최종 성공 로그 반환
        return True, "성공"

    # [구매] 카드 구매 로직
    def buy_card(self, player_id: str, card_name: str) -> Tuple[bool, str]:
        player = self.state.players[player_id]
        card = CARD_DB.get(card_name)
        errors = []

        if self.state.phase != Phase.BUY:
            errors.append("구매 페이즈가 아닙니다.")
        
        if player["buys"] <= 0:
            errors.append("남은 구매 횟수가 없습니다.")
        
        if not card:
            errors.append("존재하지 않는 카드입니다.")
        elif player["gold"] < card.cost: # 카드가 있을 때만 가격 비교 가능
            errors.append(f"골드가 부족합니다 (필요: {card.cost}, 보유: {player['gold']})")

        # 마켓 및 재고 체크 (카드가 존재할 때만 실행)
        if card:
            is_private = card_name in player["private_market"]
            is_common = card_name in self.state.supply
            
            if is_private and player["private_market"][card_name] <= 0:
                errors.append(f"개인 마켓에 {card_name} 재고가 없습니다.")
            elif is_common and self.state.supply[card_name] <= 0:
                errors.append(f"공동 마켓에 {card_name} 재고가 없습니다.")
            elif not is_private and not is_common:
                errors.append(f"어느 마켓에도 {card_name} 카드가 없습니다.")

        # [핵심] 수집된 에러가 있다면 한꺼번에 로그를 남기고 종료
        if errors:
            full_error_msg = " | ".join(errors) # "골드 부족 | 재고 없음" 식으로 합침
            return self.log_fail(player_id, full_error_msg)
        # 2. 처리 시작
        player["buys"] -= 1
        player["gold"] -= card.cost

        # [수정 포인트] 여기서 return 하지 말고 로그 메시지만 변수에 담습니다.
        if is_private:
            player["private_market"][card_name] -= 1
            log_msg = f"🎁 '개인 마켓'에서 {card_name}을(를) 구매했습니다."
        else:
            self.state.supply[card_name] -= 1
            log_msg = f"🛒 '공동 마켓'에서 {card_name}을(를) 구매했습니다."

        # 이제 이 아래 코드들이 정상적으로 실행됩니다!
        # 덱 매니저 처리
        self.deck_managers[player_id].add_to_discard(card_name)
        
        # 승점 업데이트
        if card.card_type == "VICTORY":
            points = getattr(card, 'points', 0)
            player["victory_points"] += points
            # 승점 획득 상세 정보는 디버그 로그로 남기면 깔끔합니다.
            self.log_success(player_id, f"승점 획득: +{points}", is_debug=True)

        # 3. 마지막에 한 번만 성공 리턴
        return self.log_success(player_id, log_msg)
    

    def _apply_stat_change(self, player_id: str, stat_name: str, amount: int, is_debug: bool = True):
        """내부적으로 플레이어의 스탯을 변경하고 로그를 남깁니다."""
        if amount == 0: return
        
        player = self.state.players[player_id]
        player[stat_name] += amount
        
        # 아이콘 매핑
        icons = {"buys": "🛒", "actions": "⚡", "gold": "💰", "mana": "🔮", "hp": "🩸"}
        icon = icons.get(stat_name, "✨")
        
        # 우리가 만든 통합 로그 시스템 활용 (기본적으로 디버그 로그로 처리)
        msg = f"{icon} {stat_name} {amount:+} (현재: {player[stat_name]})"
        self.log_success(player_id, msg, is_debug=is_debug)


    # [페이즈] 다음 단계로 전환
    def next_phase(self) -> None:
        """유저가 '페이즈 종료' 버튼을 눌렀을 때 호출"""
        if self.state.phase == Phase.ACTION:
            self.state.phase = Phase.BUY
            self.log_success("SYSTEM", "➡️ 구매 페이즈로 넘어갑니다.")
        elif self.state.phase == Phase.BUY:
            # 구매 종료 시 정리 단계는 자동으로 수행 후 다음 플레이어 턴으로
            self._end_turn()
            self.state.phase = Phase.ACTION

# [턴 종료] 내부 정리 로직
    def _end_turn(self) -> None:
        pid = self.state.turn_owner
        player = self.state.players[pid]
        
        # 1. 정리(Clean-up) 시작 알림
        # log_success를 사용하면 스냅샷이 찍히므로, 정리 전 상태를 볼 수 있습니다.
        self.log_success("SYSTEM", f"🧹 {pid}님의 필드와 손패를 정리합니다.")
        
        # 2. 카드 이동 (Play Mat + Hand -> Discard)
        # 이번 턴에 사용한 카드와 남은 손패를 리스트로 합칩니다.
        all_to_discard = list(player["play_mat"]) + list(player["hand"])
        
        if all_to_discard:
            self.deck_managers[pid].discard_pile(all_to_discard)
        
        # 3. 공간 및 자원 초기화
        player["play_mat"] = []
        player["hand"] = []
        player["actions"] = 1
        player["buys"] = 1
        player["gold"] = 0
        
        # 4. 새 카드 드로우 (5장)
        self.draw_card(pid, 5)
        
        # 5. [수정] 정리가 완료된 '후'의 스냅샷은 다음 사람을 위해 찍습니다.
        # 아래 로직에서 turn_owner가 바뀌기 때문에 지금 찍는 것이 좋습니다.
        if self.state.debug:
            self._print_debug_snapshot(action_type="TURN_CLEANUP_COMPLETE")
        
        # 6. 턴 주인 교체 및 페이즈 초기화
        pids = self.state.player_ids
        current_idx = pids.index(pid)
        next_idx = (current_idx + 1) % len(pids)
        
        if next_idx == 0:
            self.state.turn_count += 1
            
        self.state.turn_owner = pids[next_idx]
        self.state.phase = Phase.ACTION

        # 7. 다음 턴 시작 알림
        self.log_success("SYSTEM", f"=== 턴 {self.state.turn_count}: {self.state.turn_owner}의 차례 ===")

    # [드로우] 로그 출력을 포함한 드로우 대행 (카드 효과 등에서 호출)
    def draw_card(self, player_id: str, count: int = 1) -> None:
        actual_drawn = self.deck_managers[player_id].draw(count)
        if actual_drawn > 0:
            self.log_success(player_id, f"🎴 {actual_drawn}장의 카드를 뽑았습니다.", is_debug=False)

    def apply_hp_change(self, target_id: str, amount: int):
        target = self.state.players[target_id]
        
        # 1. 수치 변경
        target["hp"] += amount 
        
        # 2. 로그 메시지 구성
        action_type = "회복" if amount > 0 else "데미지를 입"
        msg = f"🩸 {abs(amount)}만큼 {action_type}었습니다. (남은 HP: {target['hp']})"
        
        # 3. [변경] append 대신 log_success 호출 (자동 스냅샷 트리거)
        self.log_success(target_id, msg)

        # 4. 사망 판정
        if target["hp"] <= 0:
            self.state.is_game_over = True
            winner_id = self.get_opponent_id(target_id)
            self.state.winner = winner_id
            
            # [변경] 사망 로그도 log_success로 기록하여 최종 상태 스냅샷 남기기
            death_msg = f"💀 체력이 0이 되어 사망했습니다! 최종 승자: {winner_id}"
            self.log_success(target_id, death_msg)


    def apply_damage(self, opponent_id: str, damage: int):
        """상대방에게 공격을 가함 (apply_hp_change의 래퍼 함수)"""
        self.apply_hp_change(opponent_id, -damage)
    
    def debug_log(self, message: str, is_debug: bool = False):
        """로그를 추가하는 내부 메서드. 개발자 모드일 때만 상세 로그를 남깁니다."""
        if is_debug and not self.state.debug:
            return  # 디버그 로그인데 개발자 모드가 아니면 무시
        self.state.logs.append(message)
    
    def _print_debug_snapshot(self, action_type: str = "STATE"):
        """
        현재 게임의 모든 물리적 수치와 논리적 상태를 시각적으로 출력합니다.
        데이터가 없는 경우에도 안전하게 처리하여 에러를 방지합니다.
        """
        if not self.state.debug:
            return

        lines = [f"\n🔍 [DEBUG SNAPSHOT: {action_type}] {'='*40}"]

        for pid in self.state.player_ids:
            # [핵심] 플레이어 객체가 없거나 불완전해도 죽지 않도록 방어
            p = self.state.players.get(pid)
            if not p: continue 

            # 모든 필드를 .get(키, 기본값)으로 가져옵니다.
            hp = p.get("hp", 0)
            gold = p.get("gold", 0)
            mana = p.get("mana", 0)
            actions = p.get("actions", 1)
            buys = p.get("buys", 1)
            vp = p.get("victory_points", 0)
            
            # 리스트 데이터 안전하게 가져오기
            hand = p.get("hand", [])
            play_mat = p.get("play_mat", [])
            deck = p.get("deck", [])
            discard = p.get("discard", [])

            turn_mark = "▶️ " if self.state.turn_owner == pid else "   "
            
            lines.append(f"{turn_mark}PLAYER: {pid}")
            lines.append(f"   ❤️  HP: {hp:<3} | 💰 GOLD: {gold:<3} | ⚡ ACT: {actions:<3} | 🛒 BUY: {buys:<3}")
            lines.append(f"   🏆 VP: {vp:<3} | 🔮 MANA: {mana:<3}")
            
            # 핸드 출력 (리스트가 확실하므로 안전함)
            hand_str = ', '.join(hand) if hand else 'Empty'
            lines.append(f"   🃏 HAND ({len(hand)}): {hand_str}")
            
            # 플레이매트 출력
            mat_str = ', '.join(play_mat) if play_mat else 'Empty'
            lines.append(f"   🎭 PLAY MAT: {mat_str}")
            
            lines.append(f"   📚 DECK: {len(deck):<2} | 🗑️  DISCARD: {len(discard):<2}")
            
            # 개인 마켓
            private_market = p.get("private_market", {})
            if private_market:
                market_items = [f"{k}({v})" for k, v in private_market.items()]
                lines.append(f"   🎁 PRIVATE MARKET: {', '.join(market_items)}")
            lines.append("-" * 50)

        # 공동 마켓
        supply_items = [f"{k}:{v}" for k, v in self.state.supply.items() if v > 0]
        lines.append(f"🏪 COMMON SUPPLY: {', '.join(supply_items)}")
        
        lines.append(f"🚩 PHASE: {self.state.phase.name} | TURN: {self.state.turn_count} | OVER: {self.state.is_game_over}")
        lines.append("=" * 65 + "\n")

        self.state.logs.append("\n".join(lines))