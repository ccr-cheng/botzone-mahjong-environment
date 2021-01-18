import json

from mahjong_env.base_bot import RandomMahjongBot
from mahjong_env.utils import request2obs, act2response


def main():
    agent = RandomMahjongBot()
    request = json.loads(input())
    obs = request2obs(request)
    act = agent.action(obs)
    response = act2response(act)
    print(json.dumps(response))


if __name__ == '__main__':
    main()
