import numpy
import pygame
import time

# 한 타일당 44픽셀
MAP_X = 19
MAP_Y = 19

tile_dict = {0: pygame.image.load('Tiles/0_0.png'),
             1: pygame.image.load('Tiles/1_tmp.png'),
             2: pygame.image.load('Tiles/2_tmp.png'),
             3: pygame.image.load('Tiles/3_tmp.png'),
             4: pygame.image.load('Tiles/4_tmp.png'),
             5: pygame.image.load('Tiles/5_tmp.png'),
             6: pygame.image.load('Tiles/6_tmp.png'),

             11: pygame.image.load('Tiles/1.png'),
             22: pygame.image.load('Tiles/2.png'),
             33: pygame.image.load('Tiles/3.png'),
             44: pygame.image.load('Tiles/4.png'),
             55: pygame.image.load('Tiles/5.png'),
             66: pygame.image.load('Tiles/6.png')
             }

tile_info = {  # 위, 오른쪽, 아래쪽, 왼쪽 ==> 시계 방향.
    11: ['B', 'W', 'W', 'B'],
    22: ['B', 'B', 'W', 'W'],
    33: ['W', 'B', 'B', 'W'],
    44: ['W', 'W', 'B', 'B'],
    55: ['W', 'B', 'W', 'B'],
    66: ['B', 'W', 'B', 'W']
}

# x 좌표 : 0 ~ 18,  y 좌표 : 0 ~ 18
mapArray = numpy.zeros((MAP_X, MAP_Y))


class DrawMap:
    # 생성자.
    def __init__(self, game=None):
        # 인스턴스 변수들
        self.game = game
        self.screen = game.screen
        self.click_count = 0
        self.autoSet_x = 0
        self.autoSet_y = 0

        # True 가 되면 게임이 초기화 됨.
        self.init_t = False

        # 추천 타일을 저장할 리스트.
        self.adjacent_tiles = ([])
        self.cnt = 0

        # 자동완성된 좌표를 저장할 리스트.
        self.auto_position_list = []

        # 고리 찾을 때 쓰는 리스트.
        self.win_list = ([])

        # past tile, 이전 (예비 1 ~ 6)타일 번호
        self.p_tile = 0

    # 맵을 갱신.
    def draw(self):
        if not self.init_t:
            for x in range(0, MAP_X):
                for y in range(0, MAP_Y):
                    current_tile = tile_dict[mapArray[x, y]]
                    self.screen.blit(current_tile, (x * 44, y * 44))
            pygame.display.flip()

    def map_init(self):
        return self.init_t

    @classmethod
    def is_set(cls, x, y):
        if mapArray[x, y] > 10:
            return True
        else:
            return False

    # 루프가 완성되면 맵을 초기화.
    def is_over(self):

        if self.init_t:
            mapArray.fill(0)
            self.cnt = 0
            self.p_tile = 0
            self.adjacent_tiles = ([])
            self.autoSet_x = 0
            self.autoSet_y = 0
            self.win_list = ([])
            self.click_count = 0
            self.init_t = False
            time.sleep(3)
            self.draw()
            return True

        else:
            return False

    # 최초 중앙에 놓일 타일을 결정
    def first_set(self, button):
        tile_num = 0

        # left click
        if button == 1:

            if self.click_count == 0:
                mapArray[9, 9] = 3
                tile_num = 3

            else:
                mapArray[9, 9] = 5
                tile_num = 5

            self.click_count = (self.click_count + 1) % 2
            return False, tile_num

        # right click && 예비 타일이 존재할 시.
        elif button == 3 and mapArray[9, 9] != 0:

            if self.click_count != 0:
                mapArray[9, 9] = 33
                tile_num = 33

            else:
                mapArray[9, 9] = 55
                tile_num = 55

            self.click_count = 0
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!게임 시작!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
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
        for index in tile_info:
            if color == tile_info[index][scope]:
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
            if mapArray[x, y - 1] > 10:
                # 착수된 것이라면 (x, y)의 위 타일의 아래 색상 정보를 얻어옴.
                color = tile_info[mapArray[x, y - 1]][2]
                # 착수한 타일의 수를 셈
                num_at += 1
                # 추천할 타일을 찾아서 저장.
                list_a[num_at - 1] = self.find_tile(color, 0)

        # (x, y)의 오른쪽 확인
        if x + 1 <= MAP_X - 1:
            if mapArray[x + 1, y] > 10:
                color = tile_info[mapArray[x + 1, y]][3]
                num_at += 1
                list_a[num_at - 1] = self.find_tile(color, 1)

        # (x, y) 아래쪽 확인.
        if y + 1 <= MAP_Y - 1:
            if mapArray[x, y + 1] > 10:
                color = tile_info[mapArray[x, y + 1]][0]
                num_at += 1
                list_a[num_at - 1] = self.find_tile(color, 2)

        # (x, y)의 왼쪽 확인.
        if x - 1 >= 0:
            if mapArray[x - 1, y] > 10:
                color = tile_info[mapArray[x - 1, y]][1]
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
            print("유효하지 않은 경우를", x, ", ", y, " 에서 발견하였습니다")
            # time.sleep(10)
            # self.init_t = True
            self.adjacent_tiles = ([0])

    # 주변에 확정된 타일이 있는지 검사.
    @classmethod
    def is_position(cls, x, y):

        if x == 9 and y == 9:
            return True

        # (x, y)의 adjacent_tiles, 맵 내 (x, y)의 인접 타일들.
        a_t = []

        if x - 1 >= 0:
            a_t.append([x - 1, y])

        if x + 1 <= MAP_X - 1:
            a_t.append([x + 1, y])

        if y - 1 >= 0:
            a_t.append([x, y - 1])

        if y + 1 <= MAP_Y - 1:
            a_t.append([x, y + 1])

        # tile 이 확정된 것이면 tile 의 값이 1
        # 주변에 확정된 타일이 하나라도 있는지 검사
        for e in a_t:
            i, j = e
            if mapArray[i, j] > 10:
                return True

        # 아무것도 없는 경우
        return False

    # 놓을 수 있는 예비 타일을 선택.
    def tile_choose(self, x, y, p_x, p_y):

        # 확정하지 않은 타일의 경우, 이전에 놓인 것과 지금 놓인 것 간에 같은지 확인.
        # 같지 않은 경우를 살핌.
        if not (x == p_x and y == p_y):
            # 확정된 타일인지 아닌지 확인.
            if 0 < mapArray[p_x, p_y] < 10:
                mapArray[p_x, p_y] = 0

        # 주변에 확정된 타일이 있는 경우에만 예비타일이 놓일 수 있음.
        if self.is_position(x, y):

            if len(self.adjacent_tiles) == 0:
                self.init_t = True
                # print("가능하지 않은 경우", x, "     ", y)
                time.sleep(20)
                return

            index = self.cnt % len(self.adjacent_tiles)
            mapArray[x, y] = self.p_tile = self.adjacent_tiles[index]
            self.cnt += 1

    def set_by_server(self, x, y, tile):
        self.p_tile = tile % 10
        mapArray[x, y] = self.p_tile
        # print("서버에게 받은 타일을 예비 타일로", self.p_tile)
        self.complete_set(x, y, tile)

    # 타일 확정.
    def tile_set(self, p_x, p_y):

        # 타일 확정, 착수!!
        if self.is_position(p_x, p_y) and 0 < mapArray[p_x, p_y] <= 7:

            # 추천 타일 리스트에는 1 ~ 6 의 번호만 저장되어 있음
            # 확정 타일로 착수하는 계산 ex) 1 ==>  1 x 10 + 1 == 11, 6 x 10 + 6 == 66
            tile_num = self.p_tile * 10 + self.p_tile
            # mapArray[p_x, p_y] = tile_num
            # print("타일셋~~!!", p_x, "  ", p_y, "  ", tile_num)
            return tile_num

        else:
            # 정중앙 타일인지 아닌지 확인, 아닌 경우가 참.
            if p_x != 9 or p_y != 9:
                # 착수되지 않은 타일인지 확인, 예비 타일이여야 다시 초록 타일로 돌아감.
                if mapArray[p_x, p_y] < 10:
                    mapArray[p_x, p_y] = 0
            return 0

    @classmethod
    def complete_set(cls, x, y, tile):
        mapArray[x, y] = tile

    def win_check(self, p_x, p_y):
        # 자동완성
        self.auto_complete(p_x, p_y)
        self.click_count = 0
        # 직선 판정은 보완이 필요함.
        # self.start_straight_row(p_x, p_y, 'W')
        # self.start_straight_row(p_x, p_y, 'B')

    # 직접적인 재귀 : find_roof 로부터 고리를 찾기 위한 첫 인자를 매개변수롤 받는 재귀 함수.
    def rfind_roof(self, x_in, y_in, to_in, color):

        if not (0 <= x_in <= MAP_X - 1 and 0 <= y_in <= MAP_Y - 1):
            self.win_list.clear()
            return

        temp = to_in
        tile = mapArray[x_in, y_in]
        if tile == 0:
            self.win_list.clear()
            return

        self.win_list.append([x_in, y_in, tile])

        if x_in == self.autoSet_x and y_in == self.autoSet_y:

            time.sleep(0.5)

            for i in range(5):
                for e in self.win_list:
                    mapArray[e[0], e[1]] = 0

                self.draw()
                time.sleep(0.6)

                for e in self.win_list:
                    mapArray[e[0], e[1]] = e[2]

                self.draw()
                time.sleep(0.6)

            print(color, "의 승리!!!")
            self.win_list.clear()
            self.init_t = True
            return

        out = 0

        for i in range(4):

            if i != to_in and tile_info[tile][i] == color:
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

        if self.init_t:
            return

        x = x_in
        y = y_in

        tile = mapArray[x_in, y_in]

        # 승리햇을시에 그다음 한번더 블랙 타일 재귀가 되므로 초기화 되었을때 타일 좌표를 0을 반환 할수 있으므로 리턴조건
        if tile == 0:
            return

        # print(x, y, color, "고리 탐색 시작")
        # print(tile,"번 타일부터 탐색")
        # print(self.white_x, self.white_y)

        # 처음만나는 타일 색상 인덱스를 저장할 변수.
        first_in = 0

        for i in range(4):  # 0 ~ 3 중에 하나가 first_in에 저장됨.
            if tile_info[tile][i] == color:
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
            if not (0 <= ad_x <= MAP_X - 1 and 0 <= ad_y <= MAP_Y - 1):
                continue

            # 착수되지 않은 좌표의 자동완성 가능성을 보는 것이므로 착수된 경우는 고려하지 않음.
            if mapArray[ad_x, ad_y] > 10:
                continue

            self.find_recommend_tiles(ad_x, ad_y)

            if len(self.adjacent_tiles) > 1 or self.adjacent_tiles[0] == 0:
                continue

            mapArray[ad_x, ad_y] = self.adjacent_tiles[0] * 10 + self.adjacent_tiles[0]
            print(ad_x, " ", ad_y, " 에",  mapArray[ad_x, ad_y], " 자동완성")
            self.auto_position_list.append([ad_x, ad_y])

            # time.sleep(0.8)
            self.draw()

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
            if tile_info[mapArray[x_in, y_in]][i] == color:
                c_list.append(i)

        t_list += self.find_straight_row(x_in, y_in, c_list[0], color)
        t_list.reverse()
        t_list.append([x_in, y_in, mapArray[x_in, y_in]])
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
                if mapArray[start_x, start_y] == 22 or mapArray[start_x, start_y] == 33 \
                        or mapArray[start_x, start_y] == 55:
                    if mapArray[end_x, end_y] == 11 or mapArray[end_x, end_y] == 44 or mapArray[end_x, end_y] == 55:
                        print("블랙 가로 직선 승리!!!")
                        is_win = True

            # 세로직선 판별
            elif abs(start_y - end_y) + 1 >= 8:
                if mapArray[start_x, start_y] == 11 or mapArray[start_x, start_y] == 22 \
                        or mapArray[start_x, start_y] == 66:
                    if mapArray[end_x, end_y] == 33 or mapArray[end_x, end_y] == 44 or mapArray[end_x, end_y] == 66:
                        print("블랙 세로 직선 승리!!!")
                        is_win = True

        elif color == 'W':
            # 가로직선 판별
            if abs(start_x - end_x) + 1 >= 8:
                if mapArray[start_x, start_y] == 11 or mapArray[start_x, start_y] == 44 \
                        or mapArray[start_x, start_y] == 66:
                    if mapArray[end_x, end_y] == 22 or mapArray[end_x, end_y] == 33 or mapArray[end_x, end_y] == 66:
                        print("화이트 가로 직선 승리!!!")
                        self.init_t = True
                        is_win = True

            # 세로직선 판별
            elif abs(start_y - end_y) + 1 >= 8:
                if mapArray[start_x, start_y] == 33 or mapArray[start_x, start_y] == 44 \
                        or mapArray[start_x, start_y] == 55:
                    if mapArray[end_x, end_y] == 11 or mapArray[end_x, end_y] == 22 or mapArray[end_x, end_y] == 55:
                        print("화이트 세로 직선 승리!!!")
                        self.init_t = True
                        is_win = True

        if is_win:

            for e in t_list:
                print(e[0], e[1], e[2], "  ", end=" ")
            print()

            time.sleep(0.5)

            for i in range(5):

                for e in t_list:
                    mapArray[e[0], e[1]] = 0

                self.draw()
                time.sleep(0.5)

                for e in t_list:
                    mapArray[e[0], e[1]] = e[2]

                self.draw()
                time.sleep(0.5)

            self.init_t = True
            t_list.clear()
            return

        t_list.clear()

    # 스트레이트 직선 리스트를 생성하고 리턴함.
    @classmethod
    def find_straight_row(cls, x_in, y_in, start, color):

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

            if not (0 <= x <= MAP_X - 1 and 0 <= y <= MAP_Y - 1):
                break

            tile = mapArray[x, y]
            if tile == 0:
                break

            t_list.append([x, y, tile])
            for i in range(4):

                if i == s:
                    continue

                if tile_info[mapArray[x, y]][i] == color:
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
