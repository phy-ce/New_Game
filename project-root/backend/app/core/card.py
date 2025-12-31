# 카드 데이터 및 효과 logic

# project-root/backend/app/core/card.py
from abc import ABC, abstractmethod
from typing import Dict

class Card(ABC):
    def __init__(self, name: str, cost: int, card_type: str):
        self.name = name
        self.cost = cost
        self.card_type = card_type

    @abstractmethod
    def play(self, engine, player_id: str):
        """카드를 사용했을 때 발생하는 개별 효과"""
        pass

# --- 액션 카드 ---
class ActionCard(Card):
    def __init__(self, name: str, cost: int, add_cards=0, add_actions=0, add_buys=0, add_gold=0):
        super().__init__(name, cost, "ACTION")
        self.add_cards = add_cards
        self.add_actions = add_actions
        self.add_buys = add_buys
        self.add_gold = add_gold

    def play(self, engine, player_id: str):
        player = engine.state.players[player_id]
        player["actions"] += self.add_actions
        player["buys"] += self.add_buys
        player["gold"] += self.add_gold
        if self.add_cards > 0:
            engine.draw_card(player_id, self.add_cards)

# --- 재물 카드 ---
class TreasureCard(Card):
    def __init__(self, name: str, cost: int, value: int):
        super().__init__(name, cost, "TREASURE")
        self.value = value

    def play(self, engine, player_id: str):
        player = engine.state.players[player_id]
        player["gold"] += self.value

# --- 승점 카드 ---
class VictoryCard(Card):
    def __init__(self, name: str, cost: int, points: int):
        super().__init__(name, cost, "VICTORY")
        self.points = points

    def play(self, engine, player_id: str):
        pass # 승점 카드는 사용 효과가 없음

# --- 카드 데이터베이스 ---
CARD_DB: Dict[str, Card] = {
    "Copper": TreasureCard("Copper", 0, 1),
    "Silver": TreasureCard("Silver", 3, 2),
    "Gold": TreasureCard("Gold", 6, 3),
    "Estate": VictoryCard("Estate", 2, 1),
    "Duchy": VictoryCard("Duchy", 5, 3),
    "Province": VictoryCard("Province", 8, 6),
    "Village": ActionCard("Village", 3, add_cards=1, add_actions=2),
    "Smithy": ActionCard("Smithy", 4, add_cards=3),
}