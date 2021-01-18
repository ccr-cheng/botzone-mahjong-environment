from typing import List

from . import consts


class Claiming:
    def __init__(self, claiming_type: int, tile: str, data: int):
        self.claiming_type = claiming_type
        self.tile = tile
        self.data = data

    def __repr__(self):
        return f'{self.claiming_type} {self.tile} {self.data}'


class Action:
    def __init__(self, player: int, action: consts.ActionType, tile):
        self.player = player
        self.act_type = action
        self.tile = tile

    def __repr__(self):
        s = f'{self.player} {self.act_type.name}'
        if self.tile is not None:
            s += f' {self.tile}'
        return s


class PlayerData:
    def __init__(self, index: int, tile_wall: List[str]):
        self.index = index
        self.tile_wall = tile_wall
        self.tiles = []  # type: List[str]
        self.claimings = []  # type: List[Claiming]
        self.response_hist = []  # type: List[Action]

    @property
    def claimings_and_tiles(self):
        claimings = []
        for claiming in self.claimings:
            if claiming.claiming_type == consts.ClaimingType.CHOW:
                data = claiming.data
            else:
                data = (claiming.data - self.index + consts.NUM_PLAYERS) % consts.NUM_PLAYERS
            claimings.append((claiming.claiming_type, claiming.tile, data))
        return tuple(claimings), tuple(self.tiles)

    def get_claimings(self, filter=True):
        def filter_kong(c):
            if c.claiming_type == consts.ClaimingType.KONG and c.tile == 0:
                return Claiming(c.claiming_type, '<conceal>', 0)
            return c

        return [filter_kong(c) for c in self.claimings] if filter else self.claimings

    def play(self, tile: str) -> bool:
        if tile not in self.tiles:
            return False
        self.tiles.remove(tile)
        return True

    def pung(self, tile: str, offer_player: int) -> bool:
        if self.tiles.count(tile) < 2:
            return False
        for _ in range(2):
            self.tiles.remove(tile)
        self.claimings.append(Claiming(consts.ClaimingType.PUNG, tile, offer_player))
        return True

    def kong(self, tile: str, offer_player: int) -> bool:
        n_kong = 4 if offer_player == self.index else 3
        if self.tiles.count(tile) < n_kong:
            return False
        for _ in range(n_kong):
            self.tiles.remove(tile)
        self.claimings.append(Claiming(consts.ClaimingType.KONG, tile, offer_player))
        return True

    def meld_kong(self, tile: str) -> bool:
        claiming_index = -1
        for i in range(len(self.claimings)):
            claiming = self.claimings[i]
            if claiming.claiming_type == consts.ClaimingType.PUNG and claiming.tile == tile:
                claiming_index = i
                break
        if claiming_index == -1:
            return False
        if tile not in self.tiles:
            return False
        self.tiles.remove(tile)
        self.claimings[claiming_index].claiming_type = consts.ClaimingType.KONG
        return True

    def chow(self, tiles: List[str], data: int) -> bool:
        for tile in tiles:
            if tile not in self.tiles:
                return False
        for tile in tiles:
            self.tiles.remove(tile)
        self.claimings.append(Claiming(consts.ClaimingType.CHOW, tiles[1], data))
        return True
