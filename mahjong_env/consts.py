from enum import Enum

NUM_PLAYERS = 4
NUM_HAND_TILES = 13


# 风圈
class RoundWind(Enum):
    EAST = 0
    SOUTH = 1
    WEST = 2
    NORTH = 3


class TileSuit(Enum):
    CHARACTERS = 1  # 万
    BAMBOO = 2  # 条
    DOTS = 3  # 饼
    HONORS = 4  # 字


class ActionType(Enum):
    PASS = 0  # 无操作
    DRAW = 1  # 摸牌
    PLAY = 2  # 打牌
    CHOW = 3  # 吃牌
    PUNG = 4  # 碰牌
    KONG = 5  # 杠牌
    MELD_KONG = 6  # 补杠
    HU = 7  # 和牌


class ClaimingType:
    CHOW = "CHI"
    PUNG = "PENG"
    KONG = "GANG"


TILE_SET = (
    'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9',  # 万
    'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9',  # 条
    'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9',  # 筒
    'F1', 'F2', 'F3', 'F4', 'J1', 'J2', 'J3',  # 字牌
)
