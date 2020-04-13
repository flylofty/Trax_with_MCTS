from Game import draw_map
import copy
from random import *
from MCTS import simulation
import numpy as np


class Node:

    def __init__(self, map_arr=None, adj_list=None, color=None, ai_color=None, simul=None,  # color == 'W' or 'B'
                 move=None, parent=None, tile_x=None, tile_y=None, tile=None):  # 타일정보 추가해야함

        self.is_expanded = False
        self.move = move  # 노드 번호로 생각
        self.parent = parent
        self.children = []

        # backup 에서 갱신해야할 사항.
        self.win_num = 0
        self.visit = 0

        # 루트에만 최초 들어 온 맵을 깊은 복사로 저장.
        self.map_arr = map_arr
        # print("생성자에서 맵출력\n", self.map_arr)

        # 착수가능 인접좌표를 넣을 리스트.
        self.adj_list = adj_list
        # print("생성자에서 착수리스트출력\n", self.adj_list)

        # 객체가  White 또는 Black 의 차례의 수인지 구별하는 변수.
        self.color = color
        self.ai_color = ai_color

        # 타일 정보
        self.tile = tile
        # print("생성자에서 타일출력\n", self.tile)
        self.tile_x = tile_x
        self.tile_y = tile_y

        # self.is_end = False

        # True/False 가 올 수 있는데 Root 는 무조건 True
        self.simul = simul

    def trax_select(self):

        current = self
        # print(" 시작   ", self)

        # print("trax_select")
        while current.is_expanded:  # 리프노드 까지 돌림

            maximum_uct_value = -100.0

            for child in current.children:

                visit = child.visit
                win_num = child.win_num

                # print("trax_select 포문")

                if visit == 0:
                    visit = 1e-4

                exploitation_value = win_num / visit
                exploration_value = np.sqrt(np.log(self.visit) / visit)
                uct_value = exploitation_value + 15 * exploration_value

                if uct_value > maximum_uct_value:
                    maximum_uct_value = uct_value
                    current = child

        return current

    def trax_expand(self):

        # 자식 추가
        self.is_expanded = True

        if self.simul:
            self.add_child()

    def trax_simulation(self):

        end = None
        index = None
        child = None
        if self.simul:
            end = len(self.children) - 1
            index = randint(0, end)
            child = self.children[index]
            child.simul = True
        else:
            child = self
            self.simul = True
            self.is_expanded = False

        # 자식의 시뮬레이션을 돌릴 맵 상태 만들기.
        leaf = child.parent
        set_list = []
        while True:
            if leaf.parent is not None:
                # print("leaf.parent is not None:")
                set_list.append([leaf.tile_x, leaf.tile_y, leaf.tile])
                leaf = leaf.parent
            else:
                # print("else leaf.parent is not None:")
                child.map_arr = copy.deepcopy(leaf.map_arr)
                for e in set_list:
                    child.map_arr[e[0], e[1]] = e[2] * 10 + e[2]  # 각 객체의 tile 은 1 ~ 6의 수로 저장되어 있음.
                set_list.clear()
                break

        # 여기에 시뮬레이션 한 번
        si = simulation.Simulation(child.tile_x, child.tile_y, child.tile, copy.deepcopy(child.map_arr),
                                   copy.deepcopy(child.adj_list))

        win_color, cnt = si.auto_loop()

        if cnt == 1:
            print(child.tile_x, child.tile_y, child.tile)
            if len(child.children) > 0:
                child.children.clear()
            child.simul = False

        child.map_arr = None
        return child, win_color

    def trax_backup(self, win_color):
        current = self
        while current is not None:  # 이부분에 승률 추가해야할 듯

            current.visit += 1

            # 일단 비기는 경우는 제외함.
            if self.ai_color == win_color:
                current.win_num += 1
            # else:
            #     current.win_num -= 1

            current = current.parent

    # root 의 경우 최초 adj_list 를 넘겨주지만
    # 그 밖에 root 가 아닌 자식들은 adj_list 를 찾아줘야함.
    def add_child(self):

        # 1. 현재 맵 상태 만들기.
        leaf = self
        set_list = []
        while True:
            if leaf.parent is not None:
                set_list.append([leaf.tile_x, leaf.tile_y, leaf.tile])
                leaf = leaf.parent
            else:
                self.map_arr = copy.deepcopy(leaf.map_arr)
                for e in set_list:
                    self.map_arr[e[0], e[1]] = e[2] * 10 + e[2]
                break

        # 2. (x, y, t) 리스트 만들기.
        child_list = []
        for e in self.adj_list:
            t_list = self.find_adjacent_tiles(e[0], e[1])
            for ele in t_list:  # 여기서 각 인접좌표의 인접색상을 알아내면 색상별 승률판단에 기여할 수 있을 것 같음.
                child_list.append([e[0], e[1], ele])  # ele 는 10보다 작은 수임, 추천 예비 타일임!!
            t_list.clear()

        # 3. 각각 자식들의 adj_list 만들고 자식 붙이기.
        # 여기서 자식의 개수를 제한할 수 있음!!

        next_color = ''
        if self.color is 'W':
            next_color = 'B'
        else:
            next_color = 'W'

        for index, e in enumerate(child_list):

            adj_list = self.enqueue_adjacent_tile(e[0], e[1], e[2])

            node = Node(map_arr=None, adj_list=adj_list, color=next_color, ai_color=self.ai_color, simul=False,
                        move=index, parent=self, tile_x=e[0], tile_y=e[1], tile=e[2])
            self.children.append(node)

        # print(len(self.children), " 자식의 수!")
        if self.parent is not None:
            self.map_arr = None

    @classmethod
    def remove_set_position(cls, non_at, x, y):
        if non_at.count([x, y]) > 0:
            length = non_at.count([x, y])
            for i in range(length):
                non_at.remove([x, y])

    def enqueue_adjacent_tile(self, x, y, tile):
        # 위 오른쪽 아래 왼쪽, 순서로 인접 타일의 좌표를 넣음.

        self.map_arr[x, y] = tile * 10 + tile
        non_at = copy.deepcopy(self.adj_list)
        self.remove_set_position(non_at, x, y)

        if y - 1 >= 0:
            if self.map_arr[x, y - 1] == 0:
                self.remove_set_position(non_at, x, y - 1)
                non_at.append([x, y - 1])

        if x + 1 <= 18:
            if self.map_arr[x + 1, y] == 0:
                self.remove_set_position(non_at, x + 1, y)
                non_at.append([x + 1, y])

        if y + 1 <= 18:
            if self.map_arr[x, y + 1] == 0:
                self.remove_set_position(non_at, x, y + 1)
                non_at.append([x, y + 1])

        if x - 1 >= 0:
            if self.map_arr[x - 1, y] == 0:
                self.remove_set_position(non_at, x - 1, y)
                non_at.append([x - 1, y])

        self.map_arr[x, y] = 0
        # print(non_at)
        # print("여기서 프린트를 종료합니다.")

        return non_at

    @classmethod
    def find_tile(cls, color, scope):
        # 한 타일의 위, 오른, 아래, 왼쪽에 인접할 수 있는 수는 많아봐야 세 개임.
        temp_list = [0, 0, 0]
        i = 0
        # 사전에 저장해둔 타일 정보 딕셔너리를 순회하며 인근에 착수 가능한 타일의 수 찾기.
        for index in draw_map.tile_info:
            if color == draw_map.tile_info[index][scope]:
                temp_list[i] = index % 10
                i += 1
        return temp_list

    def find_adjacent_tiles(self, x, y):

        # 3 x 3 리스트를 만듦.
        list_a = [[0] * 3 for _ in range(4)]

        # 착수 가능한 인접 타일의 수를 세는 변수
        # number of Adjacent_Tiles
        num_at = 0

        # (x, y)좌표 위의 좌표가 맵(배열)의 범위 내에 존재하는지 확인
        if y - 1 >= 0:
            # 해당 좌표의 인접좌표의 타일이 착수한 것인지 확인
            if self.map_arr[x, y - 1] > 10:
                # 착수된 것이라면 (x, y)의 위 타일의 아래 색상 정보를 얻어옴.
                color = draw_map.tile_info[self.map_arr[x, y - 1]][2]
                # 착수한 타일의 수를 셈
                # print(x, " ", y, "  인접", x, " ", y - 1, " ", color)
                num_at += 1
                # 추천할 타일을 찾아서 저장.
                list_a[num_at - 1] = self.find_tile(color, 0)

        # (x, y)의 오른쪽 확인
        if x + 1 <= draw_map.MAP_X - 1:
            if self.map_arr[x + 1, y] > 10:
                color = draw_map.tile_info[self.map_arr[x + 1, y]][3]
                num_at += 1
                list_a[num_at - 1] = self.find_tile(color, 1)

        # (x, y) 아래쪽 확인.
        if y + 1 <= draw_map.MAP_Y - 1:
            if self.map_arr[x, y + 1] > 10:
                color = draw_map.tile_info[self.map_arr[x, y + 1]][0]
                num_at += 1
                list_a[num_at - 1] = self.find_tile(color, 2)

        # (x, y)의 왼쪽 확인.
        if x - 1 >= 0:
            if self.map_arr[x - 1, y] > 10:
                color = draw_map.tile_info[self.map_arr[x - 1, y]][1]
                num_at += 1
                list_a[num_at - 1] = self.find_tile(color, 3)

        temp_list = []

        # (x, y)의 착수한 인접 타일을 찾고 (x, y)에 올 수 있는 타일의 교집합을 구함.
        if num_at == 4:
            temp_list = list(set(list_a[0]).intersection(set(list_a[1]).intersection
                                                                   (set(list_a[2]).intersection(list_a[3]))))

        elif num_at == 3:
            temp_list = list(set(list_a[0]).intersection(set(list_a[1]).intersection(list_a[2])))

        elif num_at == 2:
            temp_list = list(set(list_a[0]).intersection(list_a[1]))

        elif num_at == 1:
            temp_list = list(set(list_a[0]))

        else:
            print("유효하지 않은 경우를", x, ", ", y, " 에서 발견하였습니다")
            # time.sleep(10)
            # self.init_t = True
            temp_list = ([0])
            return temp_list

        return temp_list


class DummyNode:
    def __init__(self, child):
        self.parent = None
        self.winning_rate = 0
        self.visit = 0
        self.child = child
