import random
from collections import Counter

from typing import List

from .consts import ActionType, ClaimingType
from .player_data import Action

from MahjongGB import MahjongFanCalculator


class BaseMahjongBot:
    @staticmethod
    def check_hu(obs) -> int:
        player = obs['player_id']
        win_tile = obs['last_tile']
        claimings = []
        for claiming in obs['claimings']:
            if claiming.claiming_type == ClaimingType.CHOW:
                data = claiming.data
            else:
                data = (claiming.data - player + 4) % 4
            claimings.append((claiming.claiming_type, claiming.tile, data))
        claimings = tuple(claimings)
        tiles = tuple(obs['tiles'])

        flower_count = 0  # 补花数
        is_self_draw = obs['last_operation'] == ActionType.DRAW  # 自摸
        is_fourth_tile = obs['played_tiles'][win_tile] == 4  # 绝张
        is_kong = obs['last_operation'] == ActionType.MELD_KONG  # 杠
        is_kong |= len(obs['request_hist']) >= 2 \
                   and obs['request_hist'][-2].act_type == ActionType.KONG \
                   and obs['request_hist'][-2].player == player
        is_last_tile = obs['tile_count'][(player + 1) % 4] == 0  # 牌墙最后一张
        player_wind = player  # 门风
        round_wind = obs['round_wind']  # 圈风

        try:
            result = MahjongFanCalculator(claimings, tiles, win_tile, flower_count, is_self_draw, is_fourth_tile,
                                          is_kong, is_last_tile, player_wind, round_wind)
            return sum([res[0] for res in result])
        except Exception as exception:
            if str(exception) == "ERROR_NOT_WIN":
                return -1
            raise

    @staticmethod
    def check_kong(obs) -> bool:
        player = obs['player_id']
        if obs['tile_count'][player] == 0 or obs['tile_count'][(player + 1) % 4] == 0:
            return False
        if obs['tiles'].count(obs['last_tile']) == 3:
            return True
        return False

    @staticmethod
    def check_meld_kong(obs) -> bool:
        player = obs['player_id']
        if obs['tile_count'][player] == 0 or obs['tile_count'][(player + 1) % 4] == 0:
            return False
        for claiming in obs['claimings']:
            if claiming.claiming_type == ClaimingType.PUNG and claiming.tile == obs['last_tile']:
                return True
        return False

    @staticmethod
    def check_pung(obs) -> bool:
        if obs['tiles'].count(obs['last_tile']) == 2:
            return True
        return False

    @staticmethod
    def check_chow(obs) -> List[str]:
        if (obs['last_player'] - obs['player_id']) % 4 != 3:
            return []
        tile_t, tile_v = obs['last_tile']
        tile_v = int(tile_v)
        if tile_t in 'FJ':
            return []

        tiles = obs['tiles']
        chow_list = []
        if tile_v >= 3:
            if tiles.count(f'{tile_t}{tile_v - 1}') and tiles.count(f'{tile_t}{tile_v - 2}'):
                chow_list.append(f'{tile_t}{tile_v - 1}')
        if 2 <= tile_v <= 8:
            if tiles.count(f'{tile_t}{tile_v - 1}') and tiles.count(f'{tile_t}{tile_v + 1}'):
                chow_list.append(f'{tile_t}{tile_v}')
        if tile_v <= 7:
            if tiles.count(f'{tile_t}{tile_v + 1}') and tiles.count(f'{tile_t}{tile_v + 2}'):
                chow_list.append(f'{tile_t}{tile_v + 1}')
        return chow_list

    def action(self, obs: dict) -> Action:
        raise NotImplementedError


class RandomMahjongBot(BaseMahjongBot):
    @staticmethod
    def choose_play(tiles):
        cnt = Counter(tiles)
        single = [c for c, n in cnt.items() if n == 1]
        if len(single) == 0:
            double = [c for c, n in cnt.items() if n == 2]
            return random.choice(double)
        winds = [c for c in single if c[0] in 'FJ']
        if len(winds) != 0:
            return random.choice(winds)
        return random.choice(single)

    def action(self, obs: dict) -> Action:
        if len(obs) == 0:
            return Action(0, ActionType.PASS, None)
        player = obs['player_id']
        last_player = obs['last_player']
        pass_action = Action(player, ActionType.PASS, None)

        if obs['last_operation'] == ActionType.DRAW:
            if last_player != player:
                return pass_action
            else:
                fan = self.check_hu(obs)
                if fan >= 8:
                    return Action(player, ActionType.HU, None)

                if self.check_kong(obs):
                    return Action(player, ActionType.KONG, obs['last_tile'])
                if self.check_meld_kong(obs):
                    return Action(player, ActionType.MELD_KONG, obs['last_tile'])
                play_tile = self.choose_play(obs['tiles'] + [obs['last_tile']])
                return Action(player, ActionType.PLAY, play_tile)

        if obs['last_operation'] == ActionType.KONG:
            return pass_action
        if last_player == player:
            return pass_action

        fan = self.check_hu(obs)
        if fan >= 8:
            return Action(player, ActionType.HU, None)
        if obs['last_operation'] == ActionType.MELD_KONG:
            return pass_action
        if self.check_kong(obs):
            return Action(player, ActionType.KONG, None)
        if self.check_pung(obs):
            tiles = obs['tiles'].copy()
            tiles.remove(obs['last_tile'])
            tiles.remove(obs['last_tile'])
            play_tile = self.choose_play(tiles)
            return Action(player, ActionType.PUNG, play_tile)

        chow_list = self.check_chow(obs)
        if len(chow_list) != 0:
            chow_tile = random.choice(chow_list)
            chow_t, chow_v = chow_tile[0], int(chow_tile[1])
            tiles = obs['tiles'].copy()
            for i in range(chow_v - 1, chow_v + 2):
                if i == int(obs['last_tile'][1]):
                    continue
                else:
                    tiles.remove(f'{chow_t}{i}')
            play_tile = self.choose_play(tiles)
            return Action(player, ActionType.CHOW, f'{chow_tile} {play_tile}')
        return pass_action
