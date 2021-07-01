from tkinter import Frame, Label, CENTER, Button

import random, math, itertools, time

import logic
import constants as c

SAMPLE_TIMES = 32
TEST_TIMES = 1

W_MAX_CORNERs = [10000]
W_SAME_BLOCKs = [2]
W_SIMILAR_BLOCKs = [2]
W_ISOLATE_BLOCKs = [8]
W_BLOCK_CNTs = [32]
BIG_BLOCKs = [32]
W_SCORE = [0]


parameters_list = itertools.product(W_MAX_CORNERs, W_SAME_BLOCKs,
                                    W_SIMILAR_BLOCKs, W_ISOLATE_BLOCKs,
                                    W_BLOCK_CNTs, BIG_BLOCKs, W_SCORE)


def gen():
    return random.randint(0, c.GRID_LEN - 1)


class GameGrid(Frame):
    def __init__(self):
        Frame.__init__(self)

        self.grid()
        self.master.title('2048')
        # self.master.bind("<Key>", self.key_down)

        self.commands = {c.KEY_UP: logic.up, c.KEY_DOWN: logic.down,
                         c.KEY_LEFT: logic.left, c.KEY_RIGHT: logic.right,
                         c.KEY_UP_ALT: logic.up, c.KEY_DOWN_ALT: logic.down,
                         c.KEY_LEFT_ALT: logic.left, c.KEY_RIGHT_ALT: logic.right,
                         c.KEY_H: logic.left, c.KEY_L: logic.right,
                         c.KEY_K: logic.up, c.KEY_J: logic.down}

        self.grid_cells = []
        self.init_grid()


        self.mainloop()

    def startloop(self):
        for parameters in parameters_list:
            self.W_M, self.W_SA, self.W_SI, \
            self.W_ISO, self.W_CNT, self.BB, self.W_S = parameters
            self.start()

    def start(self):
        f = open('test.txt', 'r+')
        f.read()
        f.write("\n--------------Test start-------------")
        scores = []
        best_block = dict()
        for rnd in range(TEST_TIMES):
            print("ROUND " + str(rnd))
            f.write("\nROUND " + str(rnd))
            self.matrix = logic.new_game(c.GRID_LEN)
            self.score = 0
            self.history_matrixs = [self.matrix]
            self.history_scores = [0]
            self.update_grid_cells()
            self.block_count = 0
            while 1:
                self.block_count = 0
                for i in range(c.GRID_LEN):
                    # print(self.matrix[i])
                    for j in range(c.GRID_LEN):
                        if self.matrix[i][j] > 0:
                            self.block_count += 1
                action = self.get_action()
                self.key_down(action)
                self.update_grid_cells()
                if logic.game_state(self.matrix) == 'lose':
                    # score = 0
                    max_block = 0
                    for i in range(c.GRID_LEN):
                        print(self.matrix[i])
                        f.write("\n" + str(self.matrix[i]))
                        # score += sum(self.matrix[i])
                        for j in range(c.GRID_LEN):
                            if max_block < self.matrix[i][j]:
                                max_block = self.matrix[i][j]
                    if max_block not in best_block:
                        best_block[max_block] = 0
                    best_block[max_block] += 1
                    scores.append(self.score)
                    break
        average_score = sum(scores) / TEST_TIMES
        f.write("\n--------------Test result-------------")
        f.write("\nW_MAX_CORNER = " + str(self.W_M))
        f.write("\nW_SAME_BLOCK = " + str(self.W_SA))
        f.write("\nW_SIMILAR_BLOCK = " + str(self.W_SI))
        f.write("\nW_ISOLATE_BLOCK = " + str(self.W_ISO))
        f.write("\nW_BLOCK_CNT = " + str(self.W_CNT))
        f.write("\nBIG_BLOCK = " + str(self.BB))
        f.write("\nscores: " + str(scores))
        f.write("\n" + str(best_block))
        f.write("\nAverage_score: " + str(average_score))

        f.close()

    def init_grid(self):
        background = Frame(self, bg=c.BACKGROUND_COLOR_GAME,
                           width=c.SIZE, height=c.SIZE)
        background.grid()

        for i in range(c.GRID_LEN):
            grid_row = []
            for j in range(c.GRID_LEN):
                cell = Frame(background, bg=c.BACKGROUND_COLOR_CELL_EMPTY,
                             width=c.SIZE / c.GRID_LEN,
                             height=c.SIZE / c.GRID_LEN)
                cell.grid(row=i, column=j, padx=c.GRID_PADDING,
                          pady=c.GRID_PADDING)
                t = Label(master=cell, text="",
                          bg=c.BACKGROUND_COLOR_CELL_EMPTY,
                          justify=CENTER, font=c.FONT, width=5, height=2)
                t.grid()
                grid_row.append(t)

            self.grid_cells.append(grid_row)
        restart_button = Button(self, text='AI', font=("黑体", 16, "bold"),
                                bg="#8f7a66", fg="#f9f6f2", command=self.startloop)
        restart_button.grid(row=4, column=3, padx=5, pady=5)

    def update_grid_cells(self):
        for i in range(c.GRID_LEN):
            for j in range(c.GRID_LEN):
                new_number = self.matrix[i][j]
                if new_number == 0:
                    self.grid_cells[i][j].configure(text="", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                else:
                    self.grid_cells[i][j].configure(text=str(new_number), bg=c.BACKGROUND_COLOR_DICT[new_number],
                                                    fg=c.CELL_COLOR_DICT[new_number])
        self.update_idletasks()

    def key_down(self, key):
        done = False
        if key == c.KEY_BACK and len(self.history_matrixs) >= 2:
            self.history_matrixs.pop()
            self.matrix = self.history_matrixs[-1]
            self.history_scores.pop()
            self.score = self.history_scores[-1]
        elif key in self.commands:
            self.matrix, done, points = self.commands[key](self.matrix)
            if done:
                self.matrix = logic.add_two(self.matrix)
                self.score += points
                # record last move
                self.history_matrixs.append(self.matrix)
                self.history_scores.append(self.score)
        return done

    def generate_next(self):
        index = (gen(), gen())
        while self.matrix[index[0]][index[1]] != 0:
            index = (gen(), gen())
        self.matrix[index[0]][index[1]] = 2

    def get_random_action(self):
        key = random.randint(0, 100) % 4
        if key == 0:
            return c.KEY_UP
        elif key == 1:
            return c.KEY_RIGHT
        elif key == 2:
            return c.KEY_DOWN
        else:
            return c.KEY_LEFT

    def get_action(self):
        max_score = -999999999999999999
        best_action = c.KEY_UP
        for action in [c.KEY_UP, c.KEY_LEFT, c.KEY_DOWN, c.KEY_RIGHT]:
            score = self.get_score(action, SAMPLE_TIMES)
            if score > max_score:
                max_score = score
                best_action = action

        # if best_action == c.KEY_UP:
        #     print('up')
        # elif best_action == c.KEY_RIGHT:
        #     print('right')
        # elif best_action == c.KEY_DOWN:
        #     print('down')
        # elif best_action == c.KEY_LEFT:
        #     print('left')
        # else:
        #     print('error')

        return best_action

    def get_score(self, action, times):
        scores = []
        for _ in range(times):
            max_score = -999999999999
            if self.key_down(action):
                for action2 in [c.KEY_UP, c.KEY_LEFT, c.KEY_DOWN, c.KEY_RIGHT]:
                    if self.key_down(action2):
                        score = self.evaluate(self.matrix, self.block_count)
                        if score > max_score:
                            max_score = score
                        self.key_down(c.KEY_BACK)
                self.key_down(c.KEY_BACK)
                scores.append(max_score)
            else:
                return -9999999999999999
        score = sum(scores) / times
        return score


    def evaluate(self, matrix, prev_block_count):
        block_count = 0
        block_tree = dict()
        for i in range(c.GRID_LEN):
            for j in range(c.GRID_LEN):
                if matrix[i][j] != 0:
                    block_count += 1
                    if matrix[i][j] not in block_tree:
                        block_tree[matrix[i][j]] = list()
                    block_tree[matrix[i][j]].append((i, j))

        connectivity = 0
        prev_layer = []
        max_block = 0
        for i in reversed(sorted(block_tree.keys())):
            if not prev_layer:
                max_block = i
                # if max_block >= 1024:
                    # self.W_M, self.W_SA, self.W_SI, \
                    # self.W_ISO, self.W_CNT, self.BB, self.W_S = [10000, 2, 2, 8, 32, 32, 0]
                for m in block_tree[i]:
                    max_corner = m[0] == 0 and m[1] == 0
                    dist = m[0] + m[1]
                    connectivity += max_corner * self.W_M
                    connectivity -= dist * self.W_M
            if i >= 32:
                for m in block_tree[i]:
                    dist = min(m[0], m[1])
                    connectivity -= dist * i
                    
            for m, n in itertools.product(block_tree[i], repeat=2):
                dist = abs(m[0] - n[0]) + abs(m[1] - n[1])
                if dist == 1:
                    connectivity += i * self.W_SA
                if dist > 1:
                    connectivity -= dist * i * self.W_SA

            for m in block_tree[i]:
                down_diff = 999999
                up_diff = 999999
                min_diff = 999999
                max_diff = 0
                for n in [(max(0, m[0] - 1), m[1]),
                          (min(3, m[0] + 1), m[1]),
                          (m[0], max(0, m[1] - 1)),
                          (m[0], min(3, m[1] + 1))]:
                    if m == n:
                        continue

                    if i >= matrix[n[0]][n[1]]:
                        diff = i / max(matrix[n[0]][n[1]], 2)
                        if diff < down_diff:
                            down_diff = diff
                    else:
                        diff = matrix[n[0]][n[1]] / i
                        if diff < up_diff:
                            up_diff = diff
                    if diff < min_diff:
                        min_diff = diff
                    if diff > max_diff:
                        max_diff = diff

                if min_diff > 2:
                    connectivity -= min_diff * max(self.W_ISO, math.log2(max_block))
    
                

            if i < self.BB:
                prev_layer = block_tree[i]
                continue

            for m, n in itertools.product(prev_layer, block_tree[i]):
                dist = abs(m[0] - n[0]) + abs(m[1] - n[1])
                if dist == 1:
                    connectivity += i * self.W_SI
                if dist > 1:
                    connectivity -= dist * i * self.W_SI

            prev_layer = block_tree[i]

        return connectivity - block_count * self.W_CNT + self.score * self.W_S


game_grid = GameGrid()
