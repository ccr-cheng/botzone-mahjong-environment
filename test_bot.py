import json

from mahjong_env.core import Mahjong
from mahjong_env.consts import ActionType
from mahjong_env.player_data import Action
from mahjong_env.base_bot import RandomMahjongBot


def play_round(rd, env):
    res = env.init(rd['tiles'], rd['round_wind'], rd['first_player'])
    print(res)
    for actions in zip(*rd['actions']):
        for player in env.players_data:
            print('Tile:', ' '.join(sorted(player.tiles)),
                  ', Claiming:', '; '.join([str(c) for c in player.claimings]),
                  ', Remain tiles:', len(player.tile_wall))
        print()
        act_list = [Action(i, ActionType(act[0]), None if len(act) == 1 else act[1])
                    for i, act in enumerate(actions)]
        res = env.step(act_list)
        print(res)
    print('Done:', env.done)
    if env.fans is not None:
        print('Fans:', env.fans)
    print('Rewards:', env.rewards)
    print()


def random_test():
    env = Mahjong()
    res = env.init()
    print(res)
    agent = RandomMahjongBot()

    while not env.done:
        print(env.observation())
        print()
        obs = [env.player_obs(i) for i in range(4)]
        actions = [agent.action(ob) for ob in obs]
        res = env.step(actions)
        print(res)
    if env.fans is not None:
        print('Fans:', env.fans)
    print('Rewards:', env.rewards)
    print()


def play_test():
    rounds = []
    with open('mahjong_data/processed_data_sample.json') as f:
        for line in f:
            rounds.append(json.loads(line))
    print(len(rounds))

    env = Mahjong()
    for rd in rounds:
        play_round(rd, env)


def main():
    random_test()
    play_test()


if __name__ == '__main__':
    main()
