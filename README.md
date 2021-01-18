# `mahjong_env`环境介绍

——by ccr

18th Jan. 2021

这是一个Botzone平台[Chinese Standard Mahjong](https://www.botzone.org.cn/game/Chinese-Standard-Mahjong)（国标麻将·复式）游戏的Python版本模拟器，提供与Botzone对应的接口以在本地运行Bot程序、进行强化学习等任务，并提供了简单的Python Bot和测试程序。



## 使用方法

### 本地模拟

以下代码创建了一个麻将模拟环境和一个随机策略Bot（由于策略相同，可以由一个Bot模拟所有四位玩家），并模拟一场随机牌局。详见`test_bot.py`。

```python
from mahjong_env.core import Mahjong
from mahjong_env.base_bot import RandomMahjongBot

def main():
    env = Mahjong() # 创建一个麻将模拟环境
    res = env.init() # 初始化，没有传参数即初始化一场随机牌局
    print(res)
    agent = RandomMahjongBot() # 创建一个随机Bot
    while not env.done: # 没有结束
        print(env.observation()) # 显示当前牌桌信息
        print()
        obs = [env.player_obs(i) for i in range(4)] # 得到每个玩家观测
        actions = [agent.action(ob) for ob in obs] # Bot做出决策
        res = env.step(actions) # 运行一步环境
        print(res)
    if env.fans is not None: # 和则打印番型
        print('Fans:', env.fans)
    print('Rewards:', env.rewards)
    print()

if __name__ == '__main__':
    main()
```

样例输出（部分）：

```
Initilized to testing mode
Round wind: 0, Round stage: 0
0 DRAW B7
Tiles: B2 B3 B8 F3 F4 T1 T2 T2 T9 W2 W3 W3 W5; Claimings: ; Remain tiles: 20
Tiles: B1 B1 B6 F1 F1 F4 T1 T1 T7 T7 T8 W1 W5; Claimings: ; Remain tiles: 21
Tiles: B1 B7 B9 F2 J2 J3 T1 T2 T3 T5 T6 W1 W9; Claimings: ; Remain tiles: 21
Tiles: B4 B6 B7 B8 F2 J1 J2 J3 T9 W2 W5 W6 W7; Claimings: ; Remain tiles: 21

0 PLAY F4
Tiles: B2 B3 B7 B8 F3 T1 T2 T2 T9 W2 W3 W3 W5; Claimings: ; Remain tiles: 20
Tiles: B1 B1 B6 F1 F1 F4 T1 T1 T7 T7 T8 W1 W5; Claimings: ; Remain tiles: 21
Tiles: B1 B7 B9 F2 J2 J3 T1 T2 T3 T5 T6 W1 W9; Claimings: ; Remain tiles: 21
Tiles: B4 B6 B7 B8 F2 J1 J2 J3 T9 W2 W5 W6 W7; Claimings: ; Remain tiles: 21

...

3 PLAY T7
Tiles: T6; Claimings: CHI B7 1, GANG T2 2, GANG W2 3, GANG W3 1; Remain tiles: 1
Tiles: F1 F1 F1 W4; Claimings: CHI T8 3, PENG T1 0, PENG W7 3; Remain tiles: 3
Tiles: W1; Claimings: CHI T6 3, PENG T4 1, CHI B7 1, CHI B2 2; Remain tiles: 5
Tiles: B2 B9 T9 T9; Claimings: CHI B8 3, GANG W9 2, PENG W6 0; Remain tiles: 3

0 DRAW T6
Tiles: T6; Claimings: CHI B7 1, GANG T2 2, GANG W2 3, GANG W3 1; Remain tiles: 0
Tiles: F1 F1 F1 W4; Claimings: CHI T8 3, PENG T1 0, PENG W7 3; Remain tiles: 3
Tiles: W1; Claimings: CHI T6 3, PENG T4 1, CHI B7 1, CHI B2 2; Remain tiles: 5
Tiles: B2 B9 T9 T9; Claimings: CHI B8 3, GANG W9 2, PENG W6 0; Remain tiles: 3

0 HU
Fans: ((32, '三杠'), (2, '双同刻'), (2, '断幺'), (1, '单钓将'), (1, '自摸'))
Rewards: {0: 138, 1: -46, 2: -46, 3: -46}
```

### Botzone平台

由于Botzone平台每轮决策都会重新调用Bot，因此每一轮只需做出一次决策即可。代码如下，详见`__main__.py`：

```python
import json
from mahjong_env.base_bot import RandomMahjongBot
from mahjong_env.utils import request2obs, act2response

def main():
    agent = RandomMahjongBot() # 创建Bot
    request = json.loads(input()) # 读取request
    obs = request2obs(request) # 转化为于mahjong_env相同的观测
    act = agent.action(obs) # 决策
    response = act2response(act) # 转化为Botzone输出
    print(json.dumps(response))

if __name__ == '__main__':
    main()
```

格式化后的样例输入（**实际输入为一行**）：

```json
{
  "requests":[
    "0 0 1","1 0 0 0 0 W6 B6 T9 F1 T9 J1 F2 T1 F1 T7 B7 T2 T6",
    "2 B8","3 0 PLAY J1","3 1 DRAW","3 1 PLAY F4","3 2 PENG T3",
    "3 3 DRAW","3 3 PLAY F4","2 B2"
  ], "responses":[
    "PASS","PASS","PLAY J1","PASS","PASS","PASS","PASS","PASS","PASS"
  ]
}
```

样例输出：

```json
{"response": "PLAY F2"}
```

由于Botzone平台仅接收单个文件作为Bot程序，需要将源码打包成zip文件，并且创建`__main__.py`作为程序接入点。注意，`__main__.py`**必须在压缩包顶层**，详见[这里](https://wiki.Botzone.org.cn/index.php?title=BundleMultiPython)。例如如果你把源码文件夹打包成`mahjong.zip`你可以通过以下代码测试是否打包成功：

```bash
python mahjong.zip
```

以上运行应同直接在文件夹内运行`python __main__.py`一致。



## `mahjong_env`: 麻将模拟环境

环境部分架构参考了Botzone[官方本地模拟器](https://github.com/ailab-pku/Chinese-Standard-Mahjong/tree/local-simulator)，但对其做了大量修改使之和Botzone接口尽可能接近，同时提供交互接口能够用于强化学习或其它出牌算法。除此之外，与官方提供的[裁判程序](https://github.com/ailab-pku/Chinese-Standard-Mahjong/blob/master/judge/main.cpp)不同，模拟环境存储了牌局的公共数据，使之不需要每轮调用程序，很大程度上提高了运行速度，并节约了内存开销。大部分接口都被封装在相应类中，详见以下的介绍。由于逻辑较为复杂，**请尽量避免直接修改环境接口！**

### `consts.py`

定义了麻将中的常量。例如风圈、动作类型、鸣牌类型、麻将牌等。

- `class RoundWind(Enum)` 风圈。
  - `EAST = 0` 东风；
  - `SOUTH = 1` 南风；
  - `WEST = 2` 西风；
  - `NORTH = 3` 北风。
- `class ActionType(Enum)` 动作类型。
  - `PASS = 0` 过；
  - `DRAW = 1` 摸牌，仅在request中出现；
  - `PLAY = 2` 打牌；
  - `CHOW = 3` 吃；
  - `PUNG = 4` 碰；
  - `KONG = 5` 杠；
  - `MELD_KONG = 6` 补杠；
  - `HU = 7` 和。
- `class ClaimingType` 鸣牌类型。
  - `CHOW = "CHI"` 吃；
  - `PUNG = "PENG"` 碰；
  - `KONG = "GANG"` 杠。
- `TILE_SET: tuple(str)` 含有34个元素的元组，表示34种牌。


### `player_data.py`

定义了重要的类，包括：

- `class Claiming` 鸣牌类。
  - `claiming_type: int` 鸣牌类型。0-2表示吃碰杠。
  - `tile: str` 代表鸣牌的牌。吃为**顺子中间那张牌**，其他玩家的暗杠将以`'<conceal>'`代替。
  - `data: int` 鸣牌数据。碰杠时表示牌来自哪位玩家，0-3表示玩家id，如为自己id，则为暗杠；吃时123表示第几张是上家供牌。注意这里用的是**绝对id**，而算番器用的是相对id（即0123分别表示自家、下家、对家、上家），详见`BaseMahjongBot.check_hu`中的转换。
  
- `class Action` 动作类。

  - `player: int` 做出动作的玩家id；
  - `act_type: ActionType` 动作类型；
  - `tile: Union[str, None]` 动作数据。

  Botzone平台request和response格式有所不同，而`Action`类统一表示request或response中的一个动作，其中`tile`格式基本于Botzone平台一致：

  - `PASS`: `None`；
  - `DRAW`: 仅在request中出现，摸牌玩家得到所摸牌，其他玩家为`None`；
  - `PLAY`: 所打牌；
  - `CHOW `: 空格分隔的吃牌顺子中间牌和所打牌；
  - `PUNG`: 所打牌；
  - `KONG `: request中总为`None`，response中明杠时为`None`，暗杠时为暗杠牌；
  - `MELD_KONG `: 补杠牌；
  - `HU`: `None`。

- `class PlayerData` 内部玩家类，存储玩家数据，并维护出牌、吃、碰、杠、补杠操作。请避免使用和访问这一类；如需要获得玩家状态，请使用`Mahjong.player_obs`方法。

### `core.py`

核心代码，定义了`Mahjong`类维护每局数据，其方法包括：

- `__init__(self, random_seed=None)`

  构造函数。

- `init(self, tile_wall=None, round_wind=None, round_stage=None) -> Action`

  初始化函数。**必须**在调用`step`前调用。如不带参数调用，则随机生成一轮牌局；如带参数调用，三个参数都需要指定，这些数据可以通过下节处理人类玩家数据获得。

  - `tile_wall: list[list[str]]`：四个玩家的牌墙，形状为4 × 34，从而确保每轮摸牌无随机性；
  - `round_wind: int`：圈风；
  - `round_stage: int`：局风，即第一个出牌玩家；
  - 返回值：初始request，一定是第一个出牌玩家抽牌。

- `step(self, actions: list[Action]) -> Action`

  运行一步环境。注意在此步中会自动检测出牌的合法性，如不合法则设定`self.done`标识并设定`self.rewards`（第一个不合法玩家-30，其他玩家+10）。如某位玩家发出和牌动作，则会同时判定是否和牌与和牌番种并存储在`self.fans`中，并返回相应收益。

  - `actions`：四位玩家的动作；
  - 返回值：新一轮的request。

  `step`函数的运行逻辑概述：

  1. 每一轮分为两个阶段，第一阶段为摸牌，第二阶段为玩家响应打出牌；
  2. 第一阶段摸牌后，玩家决定动作；
  3. 如和，进入检测程序，给出收益，结束牌局；
  4. 如杠（暗杠、补杠），此玩家继续摸牌，返回2（如补杠，还要检测抢杠和）；
  5. 否则，玩家出牌，进入第二阶段；
  6. 如和，返回3检测；
  7. 如果有玩家杠（明杠），则返回2，此玩家摸牌；
  8. 如果有玩家碰，则返回5；
  9. 如果有玩家吃，则返回5；
  10. 否则，返回2，下一位玩家摸牌；
  11. 任意阶段出现不合法动作都将使牌局直接结束。

- `player_obs(self, player_id: int) -> dict`

  获取某位玩家的观测状态。

  - `player_id`：玩家id，从0到3；
  - 返回值：观测字典，确保以下所有值能通过Botzone平台所给的request还原，包括
    - `'player_id': int`：玩家id；
    - `'tiles': list[str]`：玩家手牌，**不包括刚抽到的牌**，已排序；
    - `'tile_count': list[int]`：四位玩家剩余牌墙长度，在算番和判定是否能吃碰杠时有用；
    - `'claimings': list[Claiming]`：玩家鸣牌；
    - `'all_claimings': list[list[Claiming]]`：所有玩家鸣牌（包括自己）；
    - `'played_tiles': dict`：所有已打出牌计数，包括弃牌和除暗杠外的鸣牌；
    - `'last_player': int`：上一动作玩家id（可能是自己）；
    - `'last_tile': str`：上一动作打出的牌，或**刚抽到的牌**，如别人抽牌或杠则为`None`；
    - `'last_operation': ActionType`：上一动作类型；
    - `'round_wind': int`：风圈，算番时有用；
    - `'request_hist': list[Action]`：request历史；
    - `'response_hist': list[Action]`：玩家动作(response)历史。

  如需要扩充观测数据，**请不要直接修改这一函数**，而是写一个包装函数，这样能确保所用的观测可以通过request复原。例如，以下函数增加了上一回合是否为自家杠`'is_kong': bool`这一数据：

  ```python
  def my_obs(obs):
      is_kong = obs['last_operation'] == ActionType.MELD_KONG
      is_kong |= len(obs['request_hist']) >= 2 \
                 and obs['request_hist'][-2].act_type == ActionType.KONG \
                 and obs['request_hist'][-2].player == obs['player_id']
      obs['is_kong'] = is_kong
      return obs
  ```

- `observation(self) -> str`

  返回表示牌局的四行字符串，包括四位玩家的手牌、鸣牌、牌堆剩余数量。

- `request_json(self, player_id: int) -> str`

  返回Botzone平台json格式的request。

- `request_simple(self, player_id: int) -> str`

  返回Botzone平台simple格式的request。

其重要属性包括：

- `done: bool`：本局是否结束；
- `fans: list`：和牌结束时，记录所和番型；
- `rewards: dict[int, int]`：结束时，记录四位玩家的收益；
- `training: bool`：如果以现有牌局初始化，将会置为`True`。

### `utils.py`

定义了Botzone平台转换接口。

- `str2act(s: str) -> ActionType`

  将动作类型字符串转换为`ActionType`。

- `act2str(act: ActionType) -> str`

  将`ActionType`转换为相应字符串。

- `response2str(act: Action)`

  将response中的动作转换为Botzone平台字符串。

- `request2str(act: Action, player_id: int)`

  将request中的动作转换为Botzone平台字符串。由于Botzone中request和response格式是不同的，因此需要两个函数。

- `request2obs(request: dict) -> dict`

  将request字典（`json.loads`之后）转换为与`Mahjong.player_obs`返回值中格式相同的观测字典。

- `act2response(act: Action) -> dict`

  将response动作转换为字典（`json.dumps`之后即可输出）。

- `response2act(response: str, player_id: int) -> Action`

  将response字符串转换为`Action`。
  
- `json2simple(request: dict) -> str`

  将Botzone平台json格式request转换为simple格式request。

### `base_bot.py`

定义了麻将Bot基类和一个简单的随机Bot。

- `BaseMahjongBot`：麻将Bot基类。

  - `staticmethod check_hu(obs) -> int`
    

检测当前是否和牌，如和则返回番数（包括小于8番），如没和则返回-1。
    
- `staticmethod check_kong(obs) -> bool`
  
  检测当前是否能杠上一张别人打出或摸进的牌。
  
  - `staticmethod check_meld_kong(obs) -> bool`
  
  检测当前是否能补杠上一张别人打出的牌。
  
- `staticmethod check_pung(obs) -> bool`
  

检测当前是否能碰上一张别人打出的牌。
    
  - `staticmethod check_chow(obs) -> List[str]`

  检测当前是否能吃上一张别人打出的牌。如不能则返回空列表，否则返回**所有**合法吃牌顺子的中间牌。

  - `action(self, obs: dict) -> Action`

  做出一个动作。需要在子类中实现。

- `RandomMahjongBot(BaseMahjongBot)`

  实现了一个`action`函数，能鸣牌就鸣牌，否则随机打一张单张，否则随机出牌。

### Requirements

需要使用Botzone平台提供的算番器，详见[这里](https://github.com/ailab-pku/Chinese-Standard-Mahjong/tree/master/fan-calculator-usage)。其中Python版本为包装程序，需要在本地用`setup.py`安装（在`fan-calculator-usage/Mahjong-GB-Python/`路径下）：

```bash
python setup.py install
```

Botzone平台已预安装了这一算番器。算番器C++源码见[这里](https://github.com/summerinsects/ChineseOfficialMahjongHelper)。如果安装成功，可以运行同一路径下的`test.py`测试，输出为：

```
((64, '四暗刻'), (48, '一色四节高'), (24, '清一色'), (8, '妙手回春'), (1, '幺九刻'), (1, '花牌'))
((48, '一色四节高'), (24, '清一色'), (16, '三暗刻'), (1, '幺九刻'), (1, '明杠'), (1, '花牌'))
ERROR_WRONG_TILES_COUNT
ERROR_NOT_WIN
```



## `mahjong_data`: 人类牌局数据

`mahjong_data`文件夹下包含了数据预处理脚本`preprocess.py`与测试用的数据文件`processed_data_sample.json`。

数据来自Botzone官网提供的`mjdata.zip`，详见[这里](https://www.Botzone.org.cn/static/gamecontest2020a.html)。链接：[百度网盘](https://pan.baidu.com/s/1vXzYUsRBNpH245SQku0b3A)，提取码：rm79。其中包含人类玩家对局的12140场流局，132994场自摸，及385324场点炮。

### ⚠️

由于每场比赛数据记录在一个txt文件中，解压极有可能会把一般电脑的文件资源管理器搞炸，因此**请不要尝试解压**！！预处理脚本会自动处理压缩包，在不解压的情况下读取数据。

### `preprocess.py`

将比赛数据处理为方便`mahjong_env`读取的格式。默认不读取流局，只读取自摸和点炮的数据，如需要流局数据，可以在源码中反注释相应行。运行需要用到`tqdm`包（进度条）。使用以下命令运行脚本：

```bash
python preprocess.py <data_path>
```

其中`<data_path>`是`mjdata.zip`所在路径，如没有提供则默认在当前路径下。服务器上运行约需要10分钟（Intel Xeon E5-2697 v4），本地运行时间约40分钟。脚本会在当前路径输出文件`processed_data.json`。

### `processed_data.json`

约1.5G（不包括流局），每一行为代表一局游戏的json串，包含以下内容：

- `round_wind`: 圈风，0-4分别表示东西南北。

- `first_player`: 第一位玩家，由于东风位玩家编号总为0，此参数相当于局风。

- `tiles`: 四位玩家的牌墙，4 × 34的数组，每个元素为代表牌的字符串。注意，为了消除随机性，**玩家所有摸牌也会加入其中**。为了不影响`mahjong_env`对和牌的检查（海底捞月等），将每个人的手牌用空串补足到34张。

- `actions`: 四位玩家每轮动作。其中每个动作为一个数组，第一个元素为动作类型：

  - 0：过；
  - 1：摸牌，不应在数据中出现;
  - 2：出牌；
  - 3：吃；
  - 4：碰；
  - 5：杠；
  - 6：补杠；
  - 7：和。

  以上与`ActionType`一致。如有第二个元素，则表示动作参数，与Botzone接口一致，详见[Botzone规则说明](https://wiki.Botzone.org.cn/index.php?title=Chinese-Standard-Mahjong#Bot.E8.BE.93.E5.85.A5.E8.BE.93.E5.87.BA)。

例子（格式化后，格式化前为单行）：

```json
{
  "round_wind": 0,
  "first_player": 2, 
  "tiles": [
    ["B1", "B6", "W6", "T6", "T6", "W2", "B7", "B8", "W1", "T9",
     "F4", "J3", "B3", "T3", "W1", "T1", "B2", "W3", "F1", "B6",
     "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
    ["F3", "W1", "B5", "T4", "W3", "W5", "W6", "W2", "T4", "B4",
     "T1", "B9", "W6", "B7", "J2", "J1", "T2", "B2", "T7", "J2",
     "T8", "", "", "", "", "", "", "", "", "", "", "", "", ""],
    ["T8", "T8", "W7", "T3", "W4", "B1", "J1", "T7", "F2", "B1", 
     "B8", "W8", "W9", "F4", "T4", "F1", "T5", "W1", "B7", "B3", 
     "T2", "", "", "", "", "", "", "", "", "", "", "", "", ""], 
    ["T9", "T5", "J2", "T3", "T7", "B5", "J2", "W7", "J1", "B4", 
     "B3", "F3", "T6", "W3", "F2", "T6", "W6", "W5", "T9", "W7", 
     "T2", "", "", "", "", "", "", "", "", "", "", "", "", ""]
  ],
  "actions": [
    [[0], [0], [0], [0], [2, "F4"], [0], [0], [0], [0], [0], [0], [0],
      [2, "J3"], [0], [0], [0], [0], [2, "T9"], [0], [0], [0], [0], [0],
      [0], [0], [2, "W6"], [0], [0], [0], [0], [0], [0], [3, "W2 W1"], 
      [0], [0], [0], [0], [0], [0], [0], [2, "W3"], [0], [0], [0], [0], 
      [0], [0], [0], [2, "F1"], [0], [0], [0], [0], [0], [0], [0],
      [2, "B6"], [0], [0], [0], [0], [0], [0], [7]],
    [[0], [0], [0], [0], [0], [0], [2, "F3"], [0], [0], [0], [0], [0],
      [0], [0], [2, "J2"], [0], [0], [0], [0], [2, "J1"], [0], [0],
      [0], [0], [0], [0], [0], [2, "W6"], [0], [0], [0], [0], [0], [0],
      [2, "B2"], [0], [0], [0], [0], [0], [0], [0], [2, "T7"], [0], [0],
      [0], [0], [0], [0], [0], [2, "J2"], [0], [0], [0], [0], [0], [0],
      [0], [2, "T8"], [0], [0], [0], [0], [0]],
    [[2, "F2"], [0], [0], [0], [0], [0], [0], [0], [2, "F4"], [0], [0],
      [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [2, "J1"], [0],
      [0], [0], [0], [0], [0], [0], [2, "F1"], [0], [0], [0], [0], [0], 
      [0], [2, "W1"], [0], [0], [0], [0], [0], [0], [0], [2, "T8"], [0],
      [0], [0], [0], [0], [0], [0], [2, "B3"], [0], [0], [0], [0], [0],
      [0], [0], [2, "W4"], [0], [0], [0]],
    [[0], [0], [2, "J1"], [0], [0], [0], [0], [0], [0], [0], [2, "T3"],
      [0], [0], [0], [0], [4, "T9"], [0], [0], [0], [0], [0], [0], [0],
      [2, "T6"], [0], [0], [0], [0], [0], [0], [0], [2, "W3"], [0], [0],
      [0], [0], [0], [0], [2, "F2"], [0], [0], [0], [0], [0], [0], [0],
      [2, "T9"], [0], [0], [0], [0], [0], [0], [0], [2, "W7"], [0], [0],
      [0], [0], [0], [0], [0], [2, "T2"], [0]]
  ]
}
```

本项目中的`processed_data_sample.json`含有三局按以上格式处理后的数据，用于测试环境和bot。



## `mahjong_cpp`: C++调用接口

`mahjong_cpp`文件夹中包含了打包C++程序以供Python程序调用的样例。由于传统算法通常是C++程序以加快搜索速度，在强化学习中如需要C++程序作为对手学习，需要将其打包成Python模块。

文件夹中包含以下文件：

- `mahjong.h`: 定义了需要打包的接口函数：

  ```c++
  std::string action(std::string &requests);
  ```

  `action`接收一个输入字符串，并且输出一个代表动作的字符串。

- `mahjong.cpp`: 实现了上述函数（简单交互），修改自官方样例程序。

- `mahjong_wrapper.cpp`: Python包装接口。定义了模块名`MahjongBot`与方法名`MahjongBot.action`。

- `setup.py`: 安装脚本。

运行

```bash
python setup.py install
```

以安装自定义包。总的来说，结果是生成了名为`MahjongBot`的本地模块，其中包含`action`方法接收一个字符串，并输出一个字符串。如要改变实现，请修改`mahjong.cpp`；如要修改模块名和方法名，请修改`mahjong_wrapper.cpp`与`setup.py`。更多细节请参见https://docs.python.org/3/extending/extending.html。

为了测试是否成功安装，可以运行`test_cpp_bot.py`，将随机生成一场牌局。



## 测试程序

测试程序用以检测`mahjong_env`的部分功能，并提供接口的使用示例。项目中包含了以下测试程序：

- `test_bot.py`: Bot接口测试。先模拟一个随机牌局，再模拟`processed_data_sample.json`中的牌局。如果你实现了自己的Bot，可以通过修改此文件测试。
- `test_cpp_bot.py`: Python包装的C++ Bot接口测试，模拟一个随机牌局，用来测试C++接口是否成功调用。
- `test_mahjong.py`: （非常不全的）麻将环境测试。



## TODO

- [ ] 实现“长时运行”接口和Bot（详见[这里](https://wiki.botzone.org.cn/index.php?title=Bot#.E9.95.BF.E6.97.B6.E8.BF.90.E8.A1.8C)）
- [ ] 更全面的测试程序（包括一些极端情况例如海底捞月等等）