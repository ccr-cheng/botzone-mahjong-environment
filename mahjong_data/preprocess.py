import json
import sys
from zipfile import ZipFile, Path

from tqdm import tqdm

ROUND_WIND = {'东': 0, '南': 1, '西': 2, '北': 3}
INIT_TILES_NUM = 13
ACTION = {'过': 0, '摸牌': 1, '补花后摸牌': 1, '杠后摸牌': 1, '打牌': 2,
          '吃': 3, '碰': 4, '明杠': 5, '暗杠': 5, '补杠': 6, '和牌': 7, }
NO_VALID_ACTION = ['补花']
NUM_PLAYERS = 4


def add_DRAW(res, index, tile):
    for i in range(NUM_PLAYERS):
        res['actions'][i].append([ACTION['过']])
    res['tiles'][index].append(tile)


def add_PASS(res, index):
    for i in range(NUM_PLAYERS):
        if i == index:
            continue
        res['actions'][i].append([ACTION['过']])


def add_PLAY(res, index, tile):
    res['actions'][index].append([ACTION['打牌'], tile])
    add_PASS(res, index)


def add_CHOW(res, index, tile, new_tile):
    res['actions'][index].append([ACTION['吃'], f'{tile} {new_tile}'])
    add_PASS(res, index)


def add_PENG(res, index, new_tile):
    res['actions'][index].append([ACTION['碰'], new_tile])
    add_PASS(res, index)


def add_GANG(res, index, tile):
    act = [ACTION['明杠']]
    if tile is not None:
        act.append(tile)
    res['actions'][index].append(act)
    add_PASS(res, index)


def add_BUGANG(res, index):
    res['actions'][index].append([ACTION['补杠']])
    add_PASS(res, index)


def add_HU(res, index):
    res['actions'][index].append([ACTION['和牌']])
    add_PASS(res, index)


def preprocess_file(lines):
    res = {
        'round_wind': 0,
        'first_player': 0,
        'tiles': [[] for _ in range(NUM_PLAYERS)],
        'actions': [[] for _ in range(NUM_PLAYERS)]
    }
    length = len(lines)
    i = 1
    while i < length:
        line = lines[i]
        line = line.strip().split()
        if i == 1:
            res['round_wind'] = ROUND_WIND[line[0]]  # 风圈
        elif 1 < i < 6:
            index = int(line[0])
            init_tiles = eval(line[1])
            if len(init_tiles) > INIT_TILES_NUM:
                res['first_player'] = index
            res['tiles'][index] = init_tiles
        else:
            index = int(line[0])
            if line[1] in NO_VALID_ACTION:
                i += 1
                continue
            op = ACTION[line[1]]
            if op == 1:  # 摸牌
                tile = line[2][2:-2]
                if tile[0] == 'H':
                    i += 1
                    continue
                add_DRAW(res, index, tile)
            elif op == 2:  # 打牌
                tile = line[2][2:-2]
                add_PLAY(res, index, tile)
            elif op == 3:  # 吃
                tile = eval(line[2])[1]
                i += 1
                new_line = lines[i].split()
                new_tile = new_line[2][2:-2]
                add_CHOW(res, index, tile, new_tile)
            elif op == 4:  # 碰
                i += 1
                new_line = lines[i].split()
                new_tile = new_line[2][2:-2]
                add_PENG(res, index, new_tile)
            elif op == 5:  # 杠
                gang_tile = None if line[1] == '明杠' else line[2][2:-2]
                add_GANG(res, index, gang_tile)
            elif op == 6:  # 补杠
                add_BUGANG(res, index)
            elif op == 7:
                add_HU(res, index)
        i += 1
    for tile in res['tiles']:
        tile.extend([''] * (34 - len(tile)))
    return res


def main():
    data_path = '' if len(sys.argv) == 1 else sys.argv[1]
    zip_root = 'output2017/'
    names = [
        # ('LIU', 12140)  # 流局, uncomment if you want
        ('MO', 132994),  # 自摸
        ('PLAY', 385324)  # 点炮
    ]

    # zipfile.Path is buggy until python 3.9.1
    # see https://bugs.python.org/issue40564 for details
    # Here we have to open the zip file several times
    with open('processed_data_sample.json', 'w') as fo:
        for name, n_game in names:
            print(f'Processing {name} directory ...')
            with ZipFile(data_path + 'mjdata.zip') as zipf:
                path = Path(zipf, zip_root + name + '/')
                for file_name in tqdm(path.iterdir(), total=n_game):
                    with file_name.open() as f:
                        lines = [line.decode('utf-8').strip() for line in f]
                        res = preprocess_file(lines)
                        json.dump(res, fo)
                        fo.write('\n')
            print(f'{name} processing complete with {n_game} games!')

    print('Finished!')


if __name__ == '__main__':
    main()
