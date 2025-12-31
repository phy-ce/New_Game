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
    def __init__(self, name: str, cost: int, add_cards=0, add_actions=0, add_buys=0,
                  add_hp=0, add_mana=0, add_gold=0, op_add_hp=0, op_add_mana=0):
        super().__init__(name, cost, "ACTION")
        self.add_cards = add_cards
        self.add_actions = add_actions
        self.add_buys = add_buys
        self.add_gold = add_gold
        self.add_hp = add_hp
        self.add_mana = add_mana
        self.op_add_hp = op_add_hp
        self.op_add_mana = op_add_mana

    def play(self, engine, player_id: str):
        player = engine.state.players[player_id]

        player["actions"] += self.add_actions
        player["buys"] += self.add_buys
        player["gold"] += self.add_gold
        player["mana"] += self.add_mana

        #   체력 조정

        if self.add_hp != 0:
            # 엔진의 메서드를 호출하여 죽음 판정까지 같이 처리
            engine.apply_hp_change(player_id, self.add_hp)

        #   드로우
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

    # 내 피 10을 깎고 카드 3장을 뽑는 '혈액 순환'
    "BloodDraw": ActionCard("BloodDraw", 3, add_cards=3, add_hp=-10),
    
    # 내 피 5를 깎고 상대에게 15 데미지를 주는 '피의 화살'
    "BloodArrow": ActionCard("BloodArrow", 2, op_add_hp=-15, add_hp=-5),
    
    # 내 피 20을 깎는 대신 액션을 3개나 더 얻는 '광기'
    "Madness": ActionCard("Madness", 4, add_actions=3, add_hp=-20),

    # 반대로 피를 채우는 '치유'
    "HolyLight": ActionCard("HolyLight", 2, add_hp=15)
}