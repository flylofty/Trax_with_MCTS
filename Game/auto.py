from Game import draw_map
from MCTS import mcts
import copy
import time


# For M.C.T.S Data
class Auto(draw_map.DrawMap):

    # self.adjacent_tiles 은 큐임.
    def __init__(self, game, color):
        draw_map.DrawMap.__init__(self, game)

        # nonSet_adjacent_tiles
        # 다음 착수 가능한 좌표를 저장하는 리스트.
        # ex) [(8, 9), (8, 10), (9, 8), (9, 11), (10, 9), (10, 10), (10, 11), (11, 10)]
        self.non_at = []

        # ai의 수, 차례를 저장.
        self.ai_color = color
        self.roof_num = 2000

    # 착수한 곳의 좌표가 다음에 놓일 수 있는 타일을 저장해둔 리스트에 있으면 삭제
    def remove_set_position(self, x, y):
        if self.non_at.count([x, y]) > 0:
            length = self.non_at.count([x, y])
            for i in range(length):
                self.non_at.remove([x, y])

    def enqueue_adjacent_tile(self, x, y):
        # 위 오른쪽 아래 왼쪽, 순서로 인접 타일의 좌표를 넣음.
        if y - 1 >= 0:
            if draw_map.mapArray[x, y - 1] == 0:
                self.remove_set_position(x, y - 1)
                self.non_at.append([x, y - 1])

        if x + 1 <= 18:
            if draw_map.mapArray[x + 1, y] == 0:
                self.remove_set_position(x + 1, y)
                self.non_at.append([x + 1, y])

        if y + 1 <= 18:
            if draw_map.mapArray[x, y + 1] == 0:
                self.remove_set_position(x, y + 1)
                self.non_at.append([x, y + 1])

        if x - 1 >= 0:
            if draw_map.mapArray[x - 1, y] == 0:
                self.remove_set_position(x - 1, y)
                self.non_at.append([x - 1, y])

        # 착수한 곳의 좌표가 다음에 놓일 수 있는 타일을 저장해둔 리스트에 있으면 삭제
        self.remove_set_position(x, y)
        print(len(self.non_at), "착수가능한 원소의 개수.")

    def add_non_at_list_by_auto_set_list(self):
        if len(self.auto_position_list) == 0:
            return

        print(self.auto_position_list)

        for e in self.auto_position_list:
            self.enqueue_adjacent_tile(e[0], e[1])

        self.auto_position_list.clear()

    # 4 step (select,expansion,simulation,backup)
    def uct(self, turn, man_color):

        if turn:
            return True

        color = None
        if man_color is "White":
            color = 'B'
        else:
            color = 'W'

        # print(draw_map.mapArray)
        root = mcts.Node(copy.deepcopy(draw_map.mapArray), copy.deepcopy(self.non_at), color,
                         color, simul=True, move=None, parent=None, tile_x=None, tile_y=None, tile=None)
        # print("루트의 맵\n", root.map_arr)

        for i in range(self.roof_num):  # self.roof_num 의 초기값은 1000
            print("반복 ", i)
            leaf = root.trax_select()
            leaf.trax_expand()
            leaf, win_color = leaf.trax_simulation()
            leaf.trax_backup(win_color)

        self.roof_num += 500

        print("루트방문", root.visit, " 루트의 자식의 수: ", len(root.children))
        print()
        lose_count = 0
        win_count = 0
        lose_list = []
        for e in root.children:
            rate = e.win_num / e.visit

            if rate == 0 and len(e.children) == 0:
                lose_count += 1
                lose_list.append([e.tile_x, e.tile_y, e.tile])
            elif rate == 1:
                win_count += 1

            print('%.5f' % rate, " == ", e.win_num, "  /  ", e.visit, "      좌표: ", e.tile_x, " ",
                  e.tile_y, "  타일: ", e.tile, "  자식의 수 :", len(e.children))

        print()
        print("루트방문", root.visit, " 루트의 자식의 수: ", len(root.children))

        select_node = sorted(root.children, key=lambda s: s.win_num / s.visit)
        best_child = sorted(select_node, key=lambda best: best.visit)[-1]
        worst_child = sorted(select_node, key=lambda worst: worst.visit, reverse=True)
        print()

        x = y = tile = None

        if lose_count >= 1 and win_count == 0:
            trace = 0
            max_value = -2
            is_positive = True
            for w_child in root.children:
                if len(w_child.children) is 0:
                    x = w_child.tile_x
                    y = w_child.tile_y
                    for index in worst_child:
                        if index.tile_x is x and index.tile_y is y:
                            tile = index.tile * 10 + index.tile
                            trace = 1
                            max_value = index.win_num / index.visit
                            if max_value < 0:
                                is_positive = False
                            print('%.5f' % max_value, "원래 놓을 좌표 ", x, " ", y, " ", tile, " positive", is_positive)
                            break
                if trace is 1:
                    print('%.5f' % max_value, " !!여기에 놓음!!  ", x, " ", y, " ", tile)
                    break
        else:
            # 여기서 양수일 경우 양수중에 제일 큰 값을 찾고 싶음.
            x = best_child.tile_x
            y = best_child.tile_y
            tile = best_child.tile * 10 + best_child.tile
            print('%.5f' % (best_child.win_num / best_child.visit), " 여기에 놓음.  ", x, " ", y, " ", tile)

        print(lose_count, " ", win_count, " ", x, " ", y, " ", tile, "  착수!!")
        if len(lose_list) > 0:
            print("-1 리스트 출력")
            for e in lose_list:
                print(e[0], " ", e[1], " ", e[2])
            lose_list.clear()

        print()
        print()
        print("착수한 좌표의 자식 출력.")
        for e in root.children:
            if e.tile_x == x and e.tile_y == y and e.tile == tile % 10:
                print(len(e.children))
                for ele in e.children:

                    if ele.visit == 0:
                        continue

                    rate = ele.win_num / ele.visit
                    print('%.5f' % rate, " == ", ele.win_num, "  /  ", ele.visit, "      좌표: ", ele.tile_x, " ",
                          ele.tile_y, "  타일: ", ele.tile, "  자식의 수 :", len(ele.children))
        print("착수한 좌표의 자식 출력.")
        print()
        print()

        if tile > 10:
            self.set_by_server(x, y, tile)
            self.draw()
            time.sleep(0.6)
            self.set_by_server(x, y, 0)
            self.draw()
            time.sleep(0.6)
            self.set_by_server(x, y, tile)
            self.draw()
            time.sleep(0.6)
            self.enqueue_adjacent_tile(x, y)
            self.win_check(x, y)
            self.add_non_at_list_by_auto_set_list()

        return True
