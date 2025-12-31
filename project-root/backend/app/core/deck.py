# 플레이어별 덱/핸드 관리 logic

# project-root/backend/app/core/deck.py
import random
from typing import List, Dict, Any

class DeckManager:
    def __init__(self, player_state: Dict[str, Any]):
        """
        GameState 내부의 특정 플레이어 데이터를 참조로 받아 직접 수정합니다.
        player_state: { "hand": [], "deck": [], "discard": [], ... }
        """
        self.state = player_state

    def shuffle_discard_into_deck(self) -> None:
        """버림패를 섞어서 덱으로 만듭니다."""
        if not self.state["discard"]:
            return
            
        new_deck = self.state["discard"][:]
        random.shuffle(new_deck)
        self.state["deck"] = new_deck
        self.state["discard"] = []

    def draw(self, count: int = 1) -> int:
        """카드를 뽑아 핸드로 옮기고, 실제 뽑은 장수를 반환합니다."""
        drawn_count = 0
        for _ in range(count):
            if not self.state["deck"]:
                self.shuffle_discard_into_deck()
                
            if not self.state["deck"]: # 셔플 후에도 없으면 중단
                break
                
            card = self.state["deck"].pop()
            self.state["hand"].append(card)
            drawn_count += 1
        return drawn_count

    def discard_hand(self) -> None:
        """손패의 모든 카드를 버림패로 옮깁니다."""
        self.state["discard"].extend(self.state["hand"])
        self.state["hand"] = []

    def add_to_discard(self, card_name: str) -> None:
        """구매하거나 획득한 카드를 버림패에 추가합니다."""
        self.state["discard"].append(card_name)

    def initialize_deck(self) -> None:
        """게임 시작 시 구리 7장, 사유지 3장으로 초기 덱 구성"""
        starting_cards = ["Copper"] * 7 + ["Estate"] * 3
        random.shuffle(starting_cards)
        self.state["deck"] = starting_cards