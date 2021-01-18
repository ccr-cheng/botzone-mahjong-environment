import random
import json
from typing import List

from MahjongGB import MahjongFanCalculator

from . import consts
from .consts import ActionType, RoundWind
from .player_data import PlayerData, Action
from .utils import request2str, response2str


class Mahjong:
    def __init__(self, random_seed=None):
        self.random_seed = random_seed
        random.seed(self.random_seed)

        self.training = None
        self.round_wind = None
        self.players_data = None

        self.done, self.rewards = False, None
        self.round_stage = None
        self.last_round_stage = None
        self.last_operation = None
        self.current_exposed_kung = self.current_concealed_kung = self.current_meld_kung = \
            self.last_exposed_kung = self.last_concealed_kung = self.last_meld_kung = False
        self.init_tiles = []
        self.played_tiles = None
        self.last_tile = None
        self.request_hist = []  # type: List[Action]
        self.fans = None

    def init(self, tile_wall=None, round_wind=None, round_stage=None) -> Action:
        self.training = tile_wall is not None
        self.round_wind = round_wind if self.training else self.__generate_round_wind()
        if self.training:
            for tile in tile_wall:
                tile.reverse()
        else:
            tile_wall = self.__generate_tile_wall()
        self.players_data = self.__deal(tile_wall)
        for player in self.players_data:
            self.init_tiles.append(player.tiles.copy())

        self.done, self.rewards = False, {str(i): 0 for i in range(consts.NUM_PLAYERS)}
        self.round_stage = round_stage if self.training else random.randrange(4)
        self.last_round_stage = None
        self.last_operation = None
        self.current_exposed_kung = self.current_concealed_kung = self.current_meld_kung = \
            self.last_exposed_kung = self.last_concealed_kung = self.last_meld_kung = False

        self.played_tiles = {tile: 0 for tile in consts.TILE_SET}
        self.last_tile = self.__draw_tile()
        first_act = Action(self.round_stage, ActionType.DRAW, self.last_tile)
        self.request_hist = [first_act]
        self.fans = None

        print(f"Initilized to {'training' if self.training else 'testing'} mode")
        print(f'Round wind: {self.round_wind}, Round stage: {self.round_stage}')
        return first_act

    def observation(self) -> str:
        obs = []
        for player in self.players_data:
            obs.append(''.join([
                'Tiles: ', ' '.join(sorted(player.tiles)),
                '; Claimings: ', ', '.join([str(c) for c in player.claimings]),
                '; Remain tiles: ', str(len(player.tile_wall))
            ]))
        return '\n'.join(obs)

    def player_obs(self, player_id: int) -> dict:
        def filter_draw(c):
            if c.act_type == ActionType.DRAW and c.player != player_id:
                return Action(c.player, c.act_type, None)
            return c

        player = self.players_data[player_id]
        return {
            'player_id': player_id,
            'tiles': sorted(player.tiles),
            'tile_count': [len(self.players_data[i].tile_wall) for i in range(4)],
            'claimings': player.claimings,
            'all_claimings': [self.players_data[i].get_claimings(i != player_id) for i in range(4)],
            'played_tiles': self.played_tiles,
            'last_player': self.round_stage % 4,
            'last_tile': None if self.last_operation == ActionType.DRAW
                                 and player_id != self.round_stage else self.last_tile,
            'last_operation': self.last_operation,
            'round_wind': self.round_wind,
            'request_hist': [filter_draw(c) for c in self.request_hist],
            'response_hist': player.response_hist,
        }

    def request_json(self, player_id: int) -> str:
        request = {'requests': [f'0 {player_id} {self.round_wind}',  # first round
                                f'1 0 0 0 0 {" ".join(self.init_tiles[player_id])}'],  # second round
                   'responses': [response2str(act) for act in self.players_data[player_id].response_hist]}
        request['requests'].extend([request2str(act, player_id) for act in self.request_hist])
        return json.dumps(request)

    def request_simple(self, player_id: int) -> str:
        request = [f'{len(self.request_hist) + 2}',  # first line
                   f'0 {player_id} {self.round_wind}', f'PASS',  # first action
                   f'1 0 0 0 0 {" ".join(self.init_tiles[player_id])}', f'PASS']  # second action
        for req_act, res_act in zip(self.request_hist[:-1], self.players_data[player_id].response_hist):
            request.append(request2str(req_act, player_id))
            request.append(response2str(res_act))
        request.append(request2str(self.request_hist[-1], player_id))
        return '\n'.join(request)

    @staticmethod
    def __generate_round_wind() -> int:
        return random.choice([RoundWind.EAST, RoundWind.SOUTH,
                              RoundWind.WEST, RoundWind.NORTH]).value

    @staticmethod
    def __generate_tile_wall() -> List[List[str]]:
        tile_wall = list()
        # 数牌(万, 条, 饼), 风牌, 箭牌
        for _ in range(4):
            for i in range(1, 9 + 1):
                tile_wall.append(f"W{i}")
                tile_wall.append(f"T{i}")
                tile_wall.append(f"B{i}")
            for i in range(1, 4 + 1):
                tile_wall.append(f"F{i}")
            for i in range(1, 3 + 1):
                tile_wall.append(f"J{i}")
        random.shuffle(tile_wall)
        thr = len(tile_wall) // consts.NUM_PLAYERS
        return [tile_wall[:thr], tile_wall[thr:2 * thr], tile_wall[2 * thr:3 * thr], tile_wall[3 * thr:]]

    @staticmethod
    def __deal(tile_wall: List[List[str]]) -> List[PlayerData]:
        players_data = [PlayerData(i, tile) for i, tile in enumerate(tile_wall)]
        for player in players_data:
            for _ in range(consts.NUM_HAND_TILES):
                player.tiles.append(player.tile_wall.pop())
        return players_data

    def __win(self, player: int, fan: int):
        self.last_operation = ActionType.HU
        self.done = True
        self.rewards = {p: 0 for p in range(consts.NUM_PLAYERS)}
        for i in range(consts.NUM_PLAYERS):
            if self.round_stage < 4:
                if i == player:
                    self.rewards[i] = 3 * (8 + fan)
                else:
                    self.rewards[i] = -(8 + fan)
            else:
                if i == player:
                    self.rewards[i] = 3 * 8 + fan
                elif self.round_stage == i + 4:
                    self.rewards[i] = -(8 + fan)
                elif self.round_stage == i + 8 and (self.last_meld_kung or self.last_concealed_kung):
                    self.rewards[i] = -(8 + fan)
                else:
                    self.rewards[i] = -8

    def __lose(self, player: int):
        self.last_operation = ActionType.HU
        self.done = True
        self.rewards = {p: 10 if p != player else -30 for p in range(consts.NUM_PLAYERS)}

    def __huang(self):
        self.done = True
        self.rewards = {p: 0 for p in range(consts.NUM_PLAYERS)}

    def __check_pass(self, player: int, action: Action) -> bool:
        if action.act_type != ActionType.PASS:
            self.__lose(player)
            return False
        return True

    def __check_draw(self, player: int, action: Action) -> bool:
        action_type, action_content = action.act_type, action.tile
        if action_type == ActionType.HU:
            fan = self.__calculate_fan(player)
            self.__lose(player) if fan < 8 else self.__win(player, fan)
            return False
        elif action_type in {ActionType.PLAY, ActionType.KONG,
                             ActionType.MELD_KONG}:
            self.players_data[player].tiles.append(self.last_tile)
            self.last_tile = action_content
            if action_type == ActionType.PLAY:
                if self.players_data[player].play(action_content) is True:
                    self.last_operation = ActionType.PLAY
                    self.round_stage += 4
                    return True
            elif action_type == ActionType.KONG:
                if len(self.players_data[player].tile_wall) == 0 or \
                        len(self.players_data[(player + 1) % consts.NUM_PLAYERS].tiles) == 0:
                    self.__lose(player)
                    return False
                if self.players_data[player].kong(self.last_tile, player) is True:
                    self.last_operation = ActionType.KONG
                    self.current_concealed_kung = True
                    self.current_exposed_kung = self.last_exposed_kung = self.current_meld_kung = self.last_meld_kung = False
                    self.round_stage = player + 8
                    return True
            elif action_type == ActionType.MELD_KONG:
                if len(self.players_data[player].tile_wall) == 0 or \
                        len(self.players_data[(player + 1) % consts.NUM_PLAYERS].tiles) == 0:
                    self.__lose(player)
                    return False
                if self.players_data[player].meld_kong(self.last_tile) is True:
                    self.played_tiles[self.last_tile] = 4
                    self.last_operation = ActionType.MELD_KONG
                    self.current_meld_kung = True
                    self.current_concealed_kung = self.last_concealed_kung = self.current_exposed_kung = self.last_exposed_kung = False
                    self.round_stage = player + 8
                    return True
        self.__lose(player)
        return False

    def __check_hu(self, player: int, action: Action) -> bool:
        if action.act_type == ActionType.HU:
            fan = self.__calculate_fan(player)
            self.__lose(player) if fan < 8 else self.__win(player, fan)
            return False
        return True

    def __check_pung_kong(self, player: int, action: Action) -> bool:
        action_type, action_content = action.act_type, action.tile
        if action_type == ActionType.PASS:
            return True
        elif action_type == ActionType.KONG:
            if self.players_data[player].kong(self.last_tile, self.round_stage % 4) is False:
                self.__lose(player)
                return False
            self.played_tiles[self.last_tile] = 4
            self.last_operation = ActionType.KONG
            self.current_exposed_kung = True
            self.last_meld_kung = self.current_meld_kung = self.last_concealed_kung = self.current_concealed_kung = False
            self.round_stage = player + 8
            return False
        elif action_type == ActionType.PUNG:
            if self.players_data[player].pung(self.last_tile, self.round_stage % 4) is False:
                self.__lose(player)
                return False
            self.played_tiles[self.last_tile] += 3
            self.last_operation = ActionType.PUNG
            self.last_tile = action_content
            if self.players_data[player].play(action_content) is False:
                self.__lose(player)
                return False
            self.round_stage = player + 4
            return False
        elif action_type != ActionType.CHOW:
            self.__lose(player)
            return False
        return True

    def __check_chow(self, player: int, action: Action) -> bool:
        action_type, action_content = action.act_type, action.tile
        if action_type != ActionType.CHOW:
            return True

        if (self.round_stage - player) % consts.NUM_PLAYERS != 3:
            self.__lose(player)
            return False
        chow_tiles_middle, play_tile = action_content.split()
        if chow_tiles_middle[0] not in {"W", "B", "T"} or chow_tiles_middle[0] != self.last_tile[0] or abs(
                int(self.last_tile[1]) - int(chow_tiles_middle[1])) > 1:
            self.__lose(player)
            return False
        self.players_data[player].tiles.append(self.last_tile)
        suit, number = chow_tiles_middle
        chow_tiles = [f"{suit}{int(number) - 1}", chow_tiles_middle, f"{suit}{int(number) + 1}"]
        chow_tile_index = 0
        for i in range(len(chow_tiles)):
            if self.last_tile == chow_tiles[i]:
                chow_tile_index = i + 1
                break
        if self.players_data[player].chow(chow_tiles, chow_tile_index) is False:
            self.__lose(player)
            return False
        self.last_operation = ActionType.CHOW
        self.last_tile = play_tile
        if self.players_data[player].play(play_tile) is False:
            self.__lose(player)
            return False
        self.round_stage = player + 4
        return False

    def __check_kong(self, player: int, action: Action) -> bool:
        action_type = action.act_type
        if action_type == ActionType.PASS:
            return True
        if self.last_meld_kung is True and self.round_stage % consts.NUM_PLAYERS != player and action_type == ActionType.HU:
            fan = self.__calculate_fan(player)
            self.__lose(player) if fan < 8 else self.__win(player, fan)
            return False
        self.__lose(player)
        return False

    def step(self, actions: List[Action]) -> Action:
        if self.done:
            raise TypeError('Step after done!')
        if self.training is None:
            raise TypeError('Not initialized! Call self.init() first!')

        self.last_round_stage = self.round_stage
        for player, act in zip(self.players_data, actions):
            player.response_hist.append(act)

        pass_flag = True
        if 0 <= self.round_stage < 4:
            for i in range(consts.NUM_PLAYERS):
                if self.round_stage != i:
                    pass_flag = self.__check_pass(i, actions[i])
                    if not pass_flag:
                        break
                else:
                    pass_flag = self.__check_draw(i, actions[i])
                    if not pass_flag:
                        break
                    self.last_exposed_kung = self.current_exposed_kung
                    self.last_concealed_kung = self.current_concealed_kung
                    self.last_meld_kung = self.current_meld_kung
                    self.current_exposed_kung = self.current_concealed_kung = self.current_meld_kung = False
        elif 4 <= self.round_stage < 8:
            for i in range(consts.NUM_PLAYERS):
                if i == 0:
                    pass_flag = self.__check_pass(self.round_stage % consts.NUM_PLAYERS,
                                                  actions[self.round_stage % consts.NUM_PLAYERS])
                    if not pass_flag:
                        break
                else:
                    pass_flag = self.__check_hu((self.round_stage + i) % consts.NUM_PLAYERS,
                                                actions[(self.round_stage + i) % consts.NUM_PLAYERS])
                    if not pass_flag:
                        self.round_stage = self.round_stage + i
                        break

            for i in range(consts.NUM_PLAYERS):
                if pass_flag is True and self.round_stage != i + 4:
                    pass_flag = self.__check_pung_kong(i, actions[i])

            for i in range(consts.NUM_PLAYERS):
                if pass_flag is True and self.round_stage != i + 4:
                    pass_flag = self.__check_chow(i, actions[i])

            if pass_flag is True:
                self.round_stage = (self.round_stage + 1) % consts.NUM_PLAYERS
                self.played_tiles[self.last_tile] += 1
        else:
            for i in range(consts.NUM_PLAYERS):
                if self.__check_hu((self.round_stage + i) % consts.NUM_PLAYERS,
                                   actions[(self.round_stage + i) % consts.NUM_PLAYERS]) is False:
                    break
            if not self.done:
                self.round_stage -= 8

        if pass_flag:
            if 0 <= self.round_stage < 4:
                if len(self.players_data[self.round_stage % consts.NUM_PLAYERS].tile_wall) == 0:
                    self.__huang()
                else:
                    self.last_tile = self.__draw_tile()
            elif 4 <= self.round_stage < 8:
                if len(self.players_data[(self.last_round_stage + 1) % consts.NUM_PLAYERS].tile_wall) == 0 and \
                        self.last_operation in {ActionType.CHOW, ActionType.PUNG}:
                    self.__lose(self.round_stage % consts.NUM_PLAYERS)
            else:
                if len(self.players_data[(self.last_round_stage + 1) % consts.NUM_PLAYERS].tile_wall) == 0 and \
                        self.last_operation in {ActionType.KONG, ActionType.MELD_KONG}:
                    self.__lose(self.round_stage % consts.NUM_PLAYERS)

        player_id = self.round_stage % 4
        if self.last_operation == ActionType.DRAW:
            self.request_hist.append(Action(player_id, ActionType.DRAW, self.last_tile))
        elif self.last_concealed_kung:
            self.request_hist.append(Action(player_id, ActionType.KONG, None))
        else:
            self.request_hist.append(actions[player_id])
        if self.done:
            self.training = None
        return self.request_hist[-1]

    def __calculate_fan(self, player: int) -> int:
        claimings, tiles = self.players_data[player].claimings_and_tiles  # 明牌, 暗牌
        win_tile = self.last_tile  # 和牌
        flower_count = 0  # 补花数
        is_self_draw = player == self.round_stage  # 自摸
        is_fourth_tile = self.played_tiles[self.last_tile] == 3  # 绝张
        is_kong = self.last_meld_kung or self.last_concealed_kung or self.current_meld_kung  # 杠
        is_last_tile = len(self.players_data[(self.round_stage + 1) % consts.NUM_PLAYERS].tile_wall) == 0  # 牌墙最后一张
        player_wind = player  # 门风
        round_wind = self.round_wind  # 圈风

        try:
            result = MahjongFanCalculator(claimings, tiles, win_tile, flower_count, is_self_draw, is_fourth_tile,
                                          is_kong, is_last_tile, player_wind, round_wind)
            self.fans = result
            return sum([res[0] for res in result])
        except Exception as exception:
            if str(exception) == "ERROR_NOT_WIN":
                return -1
            raise

    def __draw_tile(self) -> str:
        self.last_operation = ActionType.DRAW
        return self.players_data[self.round_stage].tile_wall.pop()
