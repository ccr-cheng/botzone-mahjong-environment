from mahjong_env import consts
from mahjong_env.core import Mahjong
from mahjong_env.player_data import Action


def init() -> Mahjong:
    env = Mahjong(random_seed=42)
    res = env.init()
    print(res)
    return env


def step(env: Mahjong, actions: list):
    print(env.observation())
    print()
    request = env.step(actions)
    print(request)


def test_false_hu():
    env = init()
    actions = [Action(0, consts.ActionType.HU, None), Action(1, consts.ActionType.PASS, None),
               Action(2, consts.ActionType.PASS, None), Action(3, consts.ActionType.PASS, None)]
    step(env, actions)
    print()
    print(f"done: {env.done}")
    print(f"reward: {env.rewards}")
    assert env.done, True
    assert env.rewards, {"0": -30, "1": 10, "2": 10, "3": 10}


def test_true_hu():
    env = init()
    # 3 play F1
    actions = [Action(0, consts.ActionType.PASS, None), Action(1, consts.ActionType.PASS, None),
               Action(2, consts.ActionType.PASS, None), Action(3, consts.ActionType.PLAY, "F1")]
    step(env, actions)

    # 1 pung and play F2
    actions = [Action(0, consts.ActionType.PASS, None), Action(1, consts.ActionType.PUNG, "F2"),
               Action(2, consts.ActionType.PASS, None), Action(3, consts.ActionType.PASS, None)]
    step(env, actions)

    # all pass
    actions = [Action(0, consts.ActionType.PASS, None), Action(1, consts.ActionType.PASS, None),
               Action(2, consts.ActionType.PASS, None), Action(3, consts.ActionType.PASS, None)]
    step(env, actions)

    # 2 play W4
    actions = [Action(0, consts.ActionType.PASS, None), Action(1, consts.ActionType.PASS, None),
               Action(2, consts.ActionType.PLAY, "W4"), Action(3, consts.ActionType.PASS, None)]
    step(env, actions)

    # 3 chow W4
    actions = [Action(0, consts.ActionType.PASS, None), Action(1, consts.ActionType.PASS, None),
               Action(2, consts.ActionType.PASS, None), Action(3, consts.ActionType.CHOW, "W3 W3")]
    step(env, actions)

    # all pass
    actions = [Action(0, consts.ActionType.PASS, None), Action(1, consts.ActionType.PASS, None),
               Action(2, consts.ActionType.PASS, None), Action(3, consts.ActionType.PASS, None)]
    step(env, actions)

    # cheat, let 0 hu 😂
    env.players_data[0].tiles = ["W1", "W1", "W1", "W2", "W2", "W2", "W3", "W3", "W3", "W4", "W4", "W4", "W5"]
    env.last_tile = "W5"
    actions = [Action(0, consts.ActionType.HU, None), Action(1, consts.ActionType.PASS, None),
               Action(2, consts.ActionType.PASS, None), Action(3, consts.ActionType.PASS, None)]
    step(env, actions)

    print()
    print(f"done: {env.done}")
    print(f"reward: {env.rewards}")
    assert env.done, True
    assert env.rewards, {"0": 438, "1": -146, "2": -146, "3": -146}


if __name__ == '__main__':
    test_false_hu()
    test_true_hu()
