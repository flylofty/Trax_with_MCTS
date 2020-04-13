from random import *
from Game import draw_map


class Simulation:
    # 생성자.
    def __init__(self, first_x, first_y, first_tile, map_array=None, non_list=None):
        # 인스턴스 변수들
        self.autoSet_x = 0
        self.autoSet_y = 0
        self.cnt = 0
        self.click_count = 0

        self.temp = 0

        # x 좌표 : 0 ~ 18,  y 좌표 : 0 ~ 18
        # self.map_array = numpy.zeros((MAP_X, MAP_Y))
        self.map_array = map_array
        self.non_at = non_list

        # True 가 되면 게임이 초기화 됨.
        self.init_t = False

        # 추천 타일을 저장할 리스트.
        self.adjacent_tiles = ([])

        # 자동완성된 좌표를 저장할 리스트.
        self.auto_position_list = []

        # 고리 찾을 때 쓰는 리스트.
        self.win_list = ([])

        # past tile, 이전 (예비 1 ~ 6)타일 번호
        self.p_tile = 0
        self.who_win = None

        self.is_first_set = False
        self.first_x = first_x
        self.first_y = first_y
        self.first_tile = first_tile

    def auto_loop(self):
        while True:
            self.auto_tile_set()
            # 흰이나 검 루프가 완성되면 맵을 초기화.
            if self.is_over():
                self.non_at = None
                self.map_array = None
                return self.who_win, self.temp

    # 착수한 곳의 좌표가 다음에 놓일 수 있는 타일을 저장해둔 리스트에 있으면 삭제
    def remove_set_position(self, x, y):
        if self.non_at.count([x, y]) > 0:
            length = self.non_at.count([x, y])
            for i in range(length):
                self.non_at.remove([x, y])

    def enqueue_adjacent_tile(self, x, y):
        # 위 오른쪽 아래 왼쪽, 순서로 인접 타일의 좌표를 넣음.
        if y - 1 >= 0:
            if self.map_array[x, y - 1] == 0:
                self.remove_set_position(x, y - 1)
                self.non_at.append([x, y - 1])

        if x + 1 <= 18:
            if self.map_array[x + 1, y] == 0:
                self.remove_set_position(x + 1, y)
                self.non_at.append([x + 1, y])

        if y + 1 <= 18:
            if self.map_array[x, y + 1] == 0:
                self.remove_set_position(x, y + 1)
                self.non_at.append([x, y + 1])

        if x - 1 >= 0:
            if self.map_array[x - 1, y] == 0:
                self.remove_set_position(x - 1, y)
                self.non_at.append([x - 1, y])

        # 착수한 곳의 좌표가 다음에 놓일 수 있는 타일을 저장해둔 리스트에 있으면 삭제
        self.remove_set_position(x, y)
        # print(len(self.non_at), "착수가능한 원소의 개수.")

    # auto tile set
    def auto_tile_set(self):

        # 최초 타일 놓기.
        if self.map_array[9, 9] == 0:

            # 클릭카운트에 0과 1 중에 랜덤으로 선택된 수 대입.
            # 바로 접근하지 않고 대입할 수 있는 방법 찾기!!
            self.click_count = randint(0, 1)

            # draw_map class 의 멤버 함수인 first_set 의 elif 에 걸리기 위한 임시조취.
            self.map_array[9, 9] = 7
            self.first_set(3)

            self.is_first_set = True
            self.enqueue_adjacent_tile(9, 9)
            return

        # 착수 되지 않은 인접 타일의 리스트의 인덱스 하나를 랜덤으로 뽑음.
        # 중복을 제거하고 사용할 수 있는 x, y를 뽑아주는 메서드가 있으면 좋을 것 같음.

        end = None
        index = None
        x = None
        y = None
        end2 = None
        index2 = None

        if self.is_first_set is False:
            x = self.first_x
            y = self.first_y
            self.p_tile = self.first_tile
            self.first_x = self.first_y = self.first_tile = None
            self.is_first_set = True

        else:
            end = len(self.non_at) - 1
            index = randint(0, end)
            x = self.non_at[index][0]
            y = self.non_at[index][1]
            self.non_at.pop(index)

            self.enqueue_adjacent_tile(x, y)
            self.find_recommend_tiles(x, y)
            end2 = len(self.adjacent_tiles) - 1

            if end2 == -1:
                return

            index2 = randint(0, end2)
            self.p_tile = self.adjacent_tiles[index2]

        self.map_array[x, y] = 7
        tile = self.tile_set(x, y)
        return

    def is_set(self, x, y):
        if self.map_array[x, y] > 10:
            return True
        else:
            return False

    # 루프가 완성되면 맵을 초기화.
    def is_over(self):
        if self.init_t:
            # print(self.map_array)
            self.non_at = None
            self.auto_position_list = None
            # self.map_array = None
            self.cnt = None
            self.p_tile = None
            self.adjacent_tiles = None
            self.autoSet_x = None
            self.autoSet_y = None
            self.win_list = None
            self.click_count = None
            self.init_t = False
            return True
        else:
            return False

    # 최초 중앙에 놓일 타일을 결정
    def first_set(self, button):
        tile_num = 0

        # left click
        if button == 1:

            if self.click_count == 0:
                self.map_array[9, 9] = 3
                tile_num = 3

            else:
                self.map_array[9, 9] = 5
                tile_num = 5

            self.click_count = (self.click_count + 1) % 2
            return False, tile_num

        # right click && 예비 타일이 존재할 시.
        elif button == 3 and self.map_array[9, 9] != 0:

            if self.click_count != 0:
                self.map_array[9, 9] = 33
                tile_num = 33

            else:
                self.map_array[9, 9] = 55
                tile_num = 55

            self.click_count = 0
            return True, tile_num

    # 새로운 좌표 클릭 시, 추천 타일 리스트 초기화, 추천 타일 찾기, 카운트 초기화.
    def find_recommend_tiles(self, x, y):

        self.adjacent_tiles.clear()
        self.find_adjacent_tiles(x, y)
        self.cnt = 0

    # 추천할 타일을 찾음.
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

    # 착수 가능한 타일을 찾아 리스트에 넣음.
    def find_adjacent_tiles(self, x, y):

        # 3 x 3 리스트를 만듦.
        list_a = [[0] * 3 for _ in range(4)]

        # 착수 가능한 인접 타일의 수를 세는 변수
        # number of Adjacent_Tiles
        num_at = 0

        # (x, y)좌표 위의 좌표가 맵(배열)의 범위 내에 존재하는지 확인
        if y - 1 >= 0:
            # 해당 좌표에 타일이 착수한 것인지 확인
            if self.map_array[x, y - 1] > 10:
                # 착수된 것이라면 (x, y)의 위 타일의 아래 색상 정보를 얻어옴.
                color = draw_map.tile_info[self.map_array[x, y - 1]][2]
                # 착수한 타일의 수를 셈
                num_at += 1
                # 추천할 타일을 찾아서 저장.
                list_a[num_at - 1] = self.find_tile(color, 0)

        # (x, y)의 오른쪽 확인
        if x + 1 <= draw_map.MAP_X - 1:
            if self.map_array[x + 1, y] > 10:
                color = draw_map.tile_info[self.map_array[x + 1, y]][3]
                num_at += 1
                list_a[num_at - 1] = self.find_tile(color, 1)

        # (x, y) 아래쪽 확인.
        if y + 1 <= draw_map.MAP_Y - 1:
            if self.map_array[x, y + 1] > 10:
                color = draw_map.tile_info[self.map_array[x, y + 1]][0]
                num_at += 1
                list_a[num_at - 1] = self.find_tile(color, 2)

        # (x, y)의 왼쪽 확인.
        if x - 1 >= 0:
            if self.map_array[x - 1, y] > 10:
                color = draw_map.tile_info[self.map_array[x - 1, y]][1]
                num_at += 1
                list_a[num_at - 1] = self.find_tile(color, 3)

        # (x, y)의 착수한 인접 타일을 찾고 (x, y)에 올 수 있는 타일의 교집합을 구함.
        if num_at == 4:
            self.adjacent_tiles = list(set(list_a[0]).intersection(set(list_a[1]).intersection
                                                                   (set(list_a[2]).intersection(list_a[3]))))

        elif num_at == 3:
            self.adjacent_tiles = list(set(list_a[0]).intersection(set(list_a[1]).intersection(list_a[2])))

        elif num_at == 2:
            self.adjacent_tiles = list(set(list_a[0]).intersection(list_a[1]))

        elif num_at == 1:
            self.adjacent_tiles = list(set(list_a[0]))

        else:
            # print("유효하지 않은 경우를", x, ", ", y, " 에서 발견하였습니다")
            # self.init_t = True
            self.adjacent_tiles = ([0])

    # 주변에 확정된 타일이 있는지 검사.
    def is_position(self, x, y):

        if x == 9 and y == 9:
            return True

        # (x, y)의 adjacent_tiles, 맵 내 (x, y)의 인접 타일들.
        a_t = []

        if x - 1 >= 0:
            a_t.append([x - 1, y])

        if x + 1 <= draw_map.MAP_X - 1:
            a_t.append([x + 1, y])

        if y - 1 >= 0:
            a_t.append([x, y - 1])

        if y + 1 <= draw_map.MAP_Y - 1:
            a_t.append([x, y + 1])

        # tile 이 확정된 것이면 tile 의 값이 1
        # 주변에 확정된 타일이 하나라도 있는지 검사
        for e in a_t:
            i, j = e
            if self.map_array[i, j] > 10:
                return True

        # 아무것도 없는 경우
        return False

    # 타일 확정.
    def tile_set(self, p_x, p_y):

        # 타일 확정, 착수!!
        if self.is_position(p_x, p_y) and 0 < self.map_array[p_x, p_y] <= 7:

            # 추천 타일 리스트에는 1 ~ 6 의 번호만 저장되어 있음
            # 확정 타일로 착수하는 계산 ex) 1 ==>  1 x 10 + 1 == 11, 6 x 10 + 6 == 66
            tile_num = self.p_tile * 10 + self.p_tile
            self.map_array[p_x, p_y] = tile_num
            self.temp += 1
            self.win_check(p_x, p_y)
            return tile_num

        else:
            # 정중앙 타일인지 아닌지 확인, 아닌 경우가 참.
            if p_x != 9 or p_y != 9:
                # 착수되지 않은 타일인지 확인, 예비 타일이여야 다시 초록 타일로 돌아감.
                if self.map_array[p_x, p_y] < 10:
                    self.map_array[p_x, p_y] = 0
            return 0

    def win_check(self, p_x, p_y):
        # 자동완성
        self.auto_complete(p_x, p_y)
        self.click_count = 0
        # self.start_straight_row(p_x, p_y, 'W')
        # self.start_straight_row(p_x, p_y, 'B')

    # 직접적인 재귀 : find_roof 로부터 고리를 찾기 위한 첫 인자를 매개변수롤 받는 재귀 함수.
    def rfind_roof(self, x_in, y_in, to_in, color):

        # print(x_in, " ", y_in)

        if not (0 <= x_in <= draw_map.MAP_X - 1 and 0 <= y_in <= draw_map.MAP_Y - 1):
            self.win_list.clear()
            return

        temp = to_in
        tile = self.map_array[x_in, y_in]
        if tile == 0:
            self.win_list.clear()
            return

        self.win_list.append([x_in, y_in, tile])

        if x_in == self.autoSet_x and y_in == self.autoSet_y:
            if color == 'W':
                self.who_win = 'W'
            else:
                self.who_win = 'B'
            self.win_list.clear()
            self.init_t = True
            return

        out = 0
        for i in range(4):

            if i != to_in and draw_map.tile_info[tile][i] == color:
                out = i
                break

        if out == 0:
            y_in = y_in - 1
            temp = 2

        elif out == 1:
            x_in = x_in + 1
            temp = 3

        elif out == 2:
            y_in = y_in + 1
            temp = 0

        elif out == 3:
            x_in = x_in - 1
            temp = 1

        self.rfind_roof(x_in, y_in, temp, color)

    # 간접 재귀 : 고리를 찾기 위한 적절한 첫 인수를 rfind_roof 에 넘겨줌.
    def find_roof(self, x_in, y_in, color):

        # print("find_roof 의 시작")
        # print(x_in, " ", y_in, " ", color)
        # print(self.non_at)
        # print(self.map_array)

        if self.init_t:
            return

        x = x_in
        y = y_in

        tile = self.map_array[x_in, y_in]

        # 승리햇을시에 그다음 한번더 블랙 타일 재귀가 되므로 초기화 되었을때 타일 좌표를 0을 반환 할수 있으므로 리턴조건
        if tile == 0:
            return

        # 처음만나는 타일 색상 인덱스를 저장할 변수.
        first_in = 0

        for i in range(4):  # 0 ~ 3 중에 하나가 first_in에 저장됨.
            if draw_map.tile_info[tile][i] == color:
                first_in = i
                break

        # 위쪽으로 루프를 돌아보게 하기 위한 변수 설정.
        if first_in == 0:
            first_in = 2
            y = y - 1

        # 오른쪽
        elif first_in == 1:
            first_in = 3
            x = x + 1

        # 아래쪽
        elif first_in == 2:
            first_in = 0
            y = y + 1

        # 왼쪽
        elif first_in == 3:
            first_in = 1
            x = x - 1

        self.rfind_roof(x, y, first_in, color)

    # 타일 하나가 놓인 직후 자동완성이 되는 곳이 있는지를 찾고 놓음.
    def auto_complete(self, x_in, y_in):

        if self.init_t:
            return

        dx = [0, 1, 0, -1]
        dy = [-1, 0, 1, 0]

        for i in range(4):

            # (x_in, y_in)의 위, 오른, 아래, 왼쪽 좌표를 찾음.
            ad_x, ad_y = x_in + dx[i], y_in + dy[i]

            # 범위 안에 들지 않을 경우 넘겨버림.
            if not (0 <= ad_x <= draw_map.MAP_X - 1 and 0 <= ad_y <= draw_map.MAP_Y - 1):
                continue

            # 착수되지 않은 좌표의 자동완성 가능성을 보는 것이므로 착수된 경우는 고려하지 않음.
            if self.map_array[ad_x, ad_y] > 10:
                continue

            self.find_recommend_tiles(ad_x, ad_y)

            # print(self.adjacent_tiles)
            # print(len(self.adjacent_tiles))

            if len(self.adjacent_tiles) == 0:
                continue

            if len(self.adjacent_tiles) > 1 or self.adjacent_tiles[0] == 0:
                continue

            self.map_array[ad_x, ad_y] = self.adjacent_tiles[0] * 10 + self.adjacent_tiles[0]
            # print(ad_x, " ", ad_y, " 에",  self.map_array[ad_x, ad_y], " 자동완성")
            self.auto_position_list.append([ad_x, ad_y])

            self.autoSet_x = ad_x
            self.autoSet_y = ad_y
            self.find_roof(ad_x, ad_y, 'W')
            self.find_roof(ad_x, ad_y, 'B')
            self.auto_complete(ad_x, ad_y)

    # 직선 승리 판정을 위한 초기 작업을 할 함수, 몇 열(row)로 직선이 이어지는지 판단함.
    # 수정이 필요함!!!
    def start_straight_row(self, x_in, y_in, color):

        if self.init_t:
            return

        t_list = ([])
        c_list = ([])
        is_win = False

        for i in range(4):
            if draw_map.tile_info[self.map_array[x_in, y_in]][i] == color:
                c_list.append(i)

        t_list += self.find_straight_row(x_in, y_in, c_list[0], color)
        t_list.reverse()
        t_list.append([x_in, y_in, self.map_array[x_in, y_in]])
        t_list += self.find_straight_row(x_in, y_in, c_list[1], color)

        if len(t_list) == 0:
            return

        start_x = t_list[0][0]
        start_y = t_list[0][1]
        end_x = t_list[len(t_list) - 1][0]
        end_y = t_list[len(t_list) - 1][1]

        if color == 'B':
            # 가로직선 판별
            if abs(start_x - end_x) + 1 >= 8:
                if self.map_array[start_x, start_y] == 22 or self.map_array[start_x, start_y] == 33 \
                        or self.map_array[start_x, start_y] == 55:
                    if self.map_array[end_x, end_y] == 11 or self.map_array[end_x, end_y] == 44 or self.map_array[end_x, end_y] == 55:
                        print("블랙 가로 직선 승리!!!")
                        is_win = True

            # 세로직선 판별
            elif abs(start_y - end_y) + 1 >= 8:
                if self.map_array[start_x, start_y] == 11 or self.map_array[start_x, start_y] == 22 \
                        or self.map_array[start_x, start_y] == 66:
                    if self.map_array[end_x, end_y] == 33 or self.map_array[end_x, end_y] == 44 or self.map_array[end_x, end_y] == 66:
                        print("블랙 세로 직선 승리!!!")
                        is_win = True

        elif color == 'W':
            # 가로직선 판별
            if abs(start_x - end_x) + 1 >= 8:
                if self.map_array[start_x, start_y] == 11 or self.map_array[start_x, start_y] == 44 \
                        or self.map_array[start_x, start_y] == 66:
                    if self.map_array[end_x, end_y] == 22 or self.map_array[end_x, end_y] == 33 or self.map_array[end_x, end_y] == 66:
                        print("화이트 가로 직선 승리!!!")
                        self.init_t = True
                        is_win = True

            # 세로직선 판별
            elif abs(start_y - end_y) + 1 >= 8:
                if self.map_array[start_x, start_y] == 33 or self.map_array[start_x, start_y] == 44 \
                        or self.map_array[start_x, start_y] == 55:
                    if self.map_array[end_x, end_y] == 11 or self.map_array[end_x, end_y] == 22 or self.map_array[end_x, end_y] == 55:
                        print("화이트 세로 직선 승리!!!")
                        self.init_t = True
                        is_win = True

        if is_win:

            for e in t_list:
                print(e[0], e[1], e[2], "  ", end=" ")
            print()

            # time.sleep(0.5)

            for i in range(5):

                for e in t_list:
                    self.map_array[e[0], e[1]] = 0

                # self.draw()
                # time.sleep(0.5)

                for e in t_list:
                    self.map_array[e[0], e[1]] = e[2]

                # self.draw()
                # time.sleep(0.5)

            self.init_t = True
            t_list.clear()
            return

        t_list.clear()

    # 스트레이트 직선 리스트를 생성하고 리턴함.
    def find_straight_row(self, x_in, y_in, start, color):

        x = x_in
        y = y_in
        s = start
        t_list = ([])

        if s == 0:
            s = 2
            y -= 1
        elif s == 1:
            s = 3
            x += 1
        elif s == 2:
            s = 0
            y += 1
        else:
            s = 1
            x -= 1

        while True:

            if not (0 <= x <= draw_map.MAP_X - 1 and 0 <= y <= draw_map.MAP_Y - 1):
                break

            tile = self.map_array[x, y]
            if tile == 0:
                break

            t_list.append([x, y, tile])
            for i in range(4):

                if i == s:
                    continue

                if draw_map.tile_info[self.map_array[x, y]][i] == color:
                    s = i
                    break

            if s == 0:
                s = 2
                y -= 1
            elif s == 1:
                s = 3
                x += 1
            elif s == 2:
                s = 0
                y += 1
            else:
                s = 1
                x -= 1

        return t_list
