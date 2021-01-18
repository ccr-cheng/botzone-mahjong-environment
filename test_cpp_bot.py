from mahjong_env.core import Mahjong
from mahjong_env.utils import response2act

import MahjongBot


def random_test():
    env = Mahjong()
    res = env.init()
    print(res)

    while not env.done:
        print(env.observation())
        print()
        obs = [env.request_simple(i) for i in range(4)]
        actions = [response2act(MahjongBot.action(ob), i)
                   for i, ob in enumerate(obs)]
        res = env.step(actions)
        print(res)
    if env.fans is not None:
        print('Fans:', env.fans)
    print('Rewards:', env.rewards)
    print()


def main():
    random_test()


if __name__ == '__main__':
    main()
