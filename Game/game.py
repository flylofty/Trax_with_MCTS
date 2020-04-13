import pygame
import sys
from Game import draw_map, auto


# 완성된 고리를 확인하고 싶을 때 사용

# ########## DrawMap 객체를 만들고 메서드를 통해서만 해당 객체(클래스)의 변수에 접근을 함. ########## #


class Game:
    # 아래의 변수를 클래스 변수라고 함(클래스들의 전역변수 같은 느낌.)
    # apple = 0

    # 생성자 안에 변수를 인스턴스 변수라고 함.
    def __init__(self, color, mode=None, width=836, height=836):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((width, height))
        self.my_color = color
        self.mode = mode
        self.my_turn = True
        self.AI_color = None

        # 게임을 시작하게할 bool 변수.
        # 맵의 정중앙에 3 => 33, 5 => 55 둘 중 하나로 착수될 때만 본격적으로 게임이 시작될 수 있음.
        self.real_start = None
        self.system_count = 0
        self.flask_connect = None
        self.view = None

        # past x, y, 이전 좌표
        self.p_x = None
        self.p_y = None

        # DrawMap 객체나, Auto 객체를 받아올 변수.
        self.map = None

    def ai_loop(self):

        # AI의 차례 결정.
        # 먼저 수를 놓을 경우
        if self.my_color == "White":
            self.AI_color = "Black"
            self.real_start = False
        # 나중에 수를 놓을 경우
        else:
            self.AI_color = "White"
            self.my_turn = False
            self.real_start = True

        # Auto 클래스는 DrawMap 클래스를 상속 받음.
        self.map = auto.Auto(self, self.AI_color)
        self.map.draw()

        while True:
            # CPU 이용률을 낮춤.
            self.clock.tick(7)

            # self.my_turn = self.map.auto_tile_set(self.my_turn)
            self.my_turn = self.map.uct(self.my_turn, self.my_color)

            self.mouse_event()

            self.map.draw()

            # 승리가 판별 되면 맵을 초기화.
            if self.map.is_over():
                self.real_start = False
                self.p_x = self.p_y = 9
                return

    # 사람 사용자가 있을 경우 사용.
    def mouse_event(self):
        events = pygame.event.get()
        for event in events:

            if self.my_turn is not True:
                events.clear()
                return

            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP and self.my_turn:

                # 현재 클릭한 좌표.
                x = event.pos[0] // 44
                y = event.pos[1] // 44

                if draw_map.mapArray[x, y] > 10:
                    print(x, " ", y, ",  타일 : ", draw_map.mapArray[x, y])

                # 최초 9, 9 좌표에 33 혹은 55 번 타일만 놓을 수 있음.
                if not self.real_start:

                    # left click, 예비 타일 3, 5번 중 하나만 놓일 수 있음.
                    if event.button == 1:
                        self.real_start, tile = self.map.first_set(1)

                    # right click, 예비 타일 3, 5번을 확정하고 게임을 본격적으로 시작함.
                    elif event.button == 3:

                        self.real_start, tile = self.map.first_set(3)

                        if self.mode == 'AI' and self.real_start:
                            self.map.set_by_server(9, 9, tile)
                            self.map.enqueue_adjacent_tile(9, 9)
                            pygame.event.clear()
                            self.my_turn = False

                # 본격적인 게임 시작
                else:

                    # 현재 좌표와 이전 좌표가 같은지 확인.
                    if not (x == self.p_x and y == self.p_y):

                        # 예비 타일을 저장한 리스트를 초기화, 추천 타일을 찾음, 카운트 초기화.
                        self.map.find_recommend_tiles(x, y)

                    # 확정된 타일이 아닐경우
                    if not self.map.is_set(x, y):  # if_is_not_set

                        # left click, 좌클릭한 경우
                        if event.button == 1:

                            # 예비 타일을 놓아줌.
                            self.map.tile_choose(x, y, self.p_x, self.p_y)

                        # right click, 우클릭한 경우.
                        elif event.button == 3:

                            # 타일 확정, 착수, 자동완성!!
                            tile = self.map.tile_set(self.p_x, self.p_y)

                            if tile > 10:
                                if self.mode == 'AI':
                                    self.map.set_by_server(self.p_x, self.p_y, tile)
                                    # self.map.remove_list_by_user(self.p_x, self.p_y)
                                    print(self.my_color, "님께서 ", self.p_x, " ", self.p_y, "에 착수하셨습니다")
                                    self.map.enqueue_adjacent_tile(self.p_x, self.p_y)
                                    self.map.win_check(self.p_x, self.p_y)
                                    self.map.add_non_at_list_by_auto_set_list()
                                    pygame.event.clear()
                                    self.my_turn = False

                # 현재 타일의 좌표를 저장
                self.p_x = x
                self.p_y = y
