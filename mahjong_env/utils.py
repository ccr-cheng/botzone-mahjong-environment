from .consts import ActionType, ClaimingType, TILE_SET
from .player_data import Action, Claiming

str2act_dict = {
    'PASS': ActionType.PASS,
    'DRAW': ActionType.DRAW,
    'PLAY': ActionType.PLAY,
    'CHI': ActionType.CHOW,
    'PENG': ActionType.PUNG,
    'GANG': ActionType.KONG,
    'BUGANG': ActionType.MELD_KONG,
    'HU': ActionType.HU
}
act2str_dict = {
    ActionType.PASS: 'PASS',
    ActionType.DRAW: 'DRAW',
    ActionType.PLAY: 'PLAY',
    ActionType.CHOW: 'CHI',
    ActionType.PUNG: 'PENG',
    ActionType.KONG: 'GANG',
    ActionType.MELD_KONG: 'BUGANG',
    ActionType.HU: 'HU'
}


def str2act(s: str) -> ActionType:
    return str2act_dict[s]


def act2str(act: ActionType) -> str:
    return act2str_dict[act]


def response2str(act: Action) -> str:
    s = act2str(act.act_type)
    if act.tile is not None:
        s += f' {act.tile}'
    return s


def request2str(act: Action, player_id: int) -> str:
    if act.act_type == ActionType.DRAW:
        if act.player == player_id:
            return f'2 {act.tile}'
        else:
            return f'3 {act.player} DRAW'
    s = f'3 {act.player} {act2str(act.act_type)}'
    if act.tile is not None:
        s += f' {act.tile}'
    return s


def request2obs(request: dict) -> dict:
    if len(request['requests']) <= 2:
        # pass first two rounds
        return {}

    obs = {
        'player_id': None,
        'tiles': [],
        'tile_count': [21] * 4,
        'claimings': [],
        'all_claimings': [[] for _ in range(4)],
        'played_tiles': {t: 0 for t in TILE_SET},
        'last_player': None,
        'last_tile': None,
        'last_operation': None,
        'round_wind': None,
        'request_hist': [],
        'response_hist': []
    }

    request_hist = request['requests']
    general_info = request_hist[0].split()
    player_id = obs['player_id'] = int(general_info[1])
    obs['round_wind'] = int(general_info[2])
    obs['tiles'] = request_hist[1].split()[5:]

    for act in request_hist[2:]:
        act = act.split()
        msgtype = int(act[0])
        if msgtype == 2:  # self draw
            obs['tiles'].append(act[1])
            obs['tile_count'][player_id] -= 1
            obs['request_hist'].append(Action(player_id, ActionType.DRAW, act[1]))
            obs['last_player'] = player_id
            obs['last_operation'] = ActionType.DRAW
            obs['last_tile'] = act[1]
            continue

        player = int(act[1])
        is_self = player == player_id
        act_type = str2act(act[2])
        last_player = obs['last_player']
        last_op = obs['last_operation']
        last_tile = obs['last_tile']
        obs['last_player'] = player
        obs['last_operation'] = act_type

        if len(act) == 3:
            # kong, others draw
            obs['request_hist'].append(Action(player, act_type, None))
            if act_type == ActionType.KONG:
                claim = Claiming(ClaimingType.KONG, last_tile or '<conceal>', last_player)
                obs['all_claimings'][player].append(claim)

                is_conceal = last_op == ActionType.DRAW
                if not is_conceal:
                    obs['played_tiles'][last_tile] = 4
                if is_self:
                    for _ in range(4 if is_conceal else 3):
                        obs['tiles'].remove(last_tile)
            else:
                obs['tile_count'][player] -= 1
            obs['last_tile'] = None
            continue

        # play, chow, pung, meld kong
        obs['request_hist'].append(Action(player, act_type, ' '.join(act[3:])))
        play_tile = act[-1]
        obs['played_tiles'][play_tile] += 1
        obs['last_tile'] = play_tile
        if is_self:
            obs['tiles'].remove(play_tile)

        if act_type == ActionType.PLAY:
            # already removed!
            pass
        elif act_type == ActionType.MELD_KONG:
            for claim in obs['all_claimings'][player]:
                if claim.tile == play_tile:
                    claim.claiming_type = ClaimingType.KONG
                    break
        elif act_type == ActionType.CHOW:
            chow_tile = act[-2]
            chow_t, chow_v = chow_tile[0], int(chow_tile[1])
            offer_card = int(last_tile[1]) - chow_v + 2
            claim = Claiming(ClaimingType.CHOW, chow_tile, offer_card)
            obs['all_claimings'][player].append(claim)
            for v in range(chow_v - 1, chow_v + 2):
                cur_tile = f'{chow_t}{v}'
                if cur_tile != last_tile:
                    obs['played_tiles'][cur_tile] += 1
                    if is_self:
                        obs['tiles'].remove(cur_tile)
        elif act_type == ActionType.PUNG:
            claim = Claiming(ClaimingType.PUNG, last_tile, last_player)
            obs['all_claimings'][player].append(claim)
            obs['played_tiles'][last_tile] += 2
            if is_self:
                for _ in range(2):
                    obs['tiles'].remove(last_tile)
        else:
            raise TypeError(f"Wrong action {' '.join(act)}!")

    for res in request['responses']:
        res = res.split()
        act_type = str2act(res[0])
        tile = None if len(res) == 1 else ' '.join(res[1:])
        obs['response_hist'].append(Action(player_id, act_type, tile))

    obs['tiles'].sort()
    obs['claimings'] = obs['all_claimings'][player_id]
    if obs['last_operation'] == ActionType.DRAW and obs['last_player'] == player_id:
        # remove last draw (for calculating fan)
        obs['tiles'].remove(obs['last_tile'])
    return obs


def act2response(act: Action) -> dict:
    output = act2str(act.act_type)
    if act.tile is not None:
        output += f' {act.tile}'
    return {'response': output}


def response2act(response: str, player_id: int) -> Action:
    act = response.split()
    tile = None if len(act) == 1 else ' '.join(act[1:])
    return Action(player_id, str2act(act[0]), tile)


def json2simple(request: dict) -> str:
    req_hist = request['requests']
    res_hist = request['responses']
    simple = [str(len(req_hist))]
    for req_act, res_act in zip(req_hist, res_hist):
        simple.append(req_act)
        simple.append(res_act)
    simple.append(req_hist[-1])
    return '\n'.join(simple)
