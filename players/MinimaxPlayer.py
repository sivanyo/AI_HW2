"""
MiniMax Player
"""
from players.AbstractPlayer import AbstractPlayer
import SearchAlgos
import copy
import utils

# TODO: you can import more modules, if needed
import time
from fractions import Fraction


class Player(AbstractPlayer):
    def __init__(self, game_time, penalty_score):
        # keep the inheritance of the parent's (AbstractPlayer) __init__()
        AbstractPlayer.__init__(self, game_time, penalty_score)
        self.board = None  # SH
        self.rival_pos = None  # SH
        self.pos = None  # SH
        self.scores = (0, 0)
        self.num_of_left = 0
        self.num_of_left_rival = 0
        self.min_dist_to_fruit = 0, None
        self.rival_min_dist_to_fruit = 0, None
        self.fruits_on_board_dict = {}
        self.my_move = None
        self.turns_till_fruit_gone = 0
        #self.turns = 0
        # TODO: initialize more fields, if needed, and the Minimax algorithm from SearchAlgos.py

    def set_game_params(self, board):
        """Set the game parameters needed for this player.
        This function is called before the game starts.
        (See GameWrapper.py for more info where it is called)
        input:
            - board: np.array, a 2D matrix of the board.
        No output is expected.
        """
        self.board = board
        # need to set my pos, the rival pos, all the grey area and all fruits
        available = 0
        self.turns_till_fruit_gone = min(len(board), len(board[0]))
        # max md in the board is row + col
        # this field is a tuple of (min dist, pos of fruit)
        self.min_dist_to_fruit = len(board) + len(board[0]), None
        for r, row in enumerate(board):
            for c, num in enumerate(row):
                if num is not -1:
                    available += 1
                if num == 1:
                    self.pos = (r, c)
                    # this my pos
                elif num == 2:
                    self.rival_pos = (r, c)
                    # this is the rival starting pos
                elif num > 2:
                    # this is fruit, need to add to dict
                    self.fruits_on_board_dict[r, c] = num
        self.min_dist_to_fruit = calc_min_dist_to_fruit(self, len(board) + len(board[0]), self.pos)
        self.rival_min_dist_to_fruit = calc_min_dist_to_fruit(self, len(board) + len(board[0]), self.rival_pos)
        # todo : add some info about fruits

    def make_move(self, time_limit, players_score):
        """Make move with this Player.
        input:
            - time_limit: float, time limit for a single turn.
        output:
            - direction: tuple, specifing the Player's movement, chosen from self.directions
        """
        print("start computing minimax move")  # TODO printing for test. del before sub
        start = time.time()
        self.turns_till_fruit_gone -= 1
        state = State(copy.deepcopy(self.board), self.pos, self.rival_pos, players_score, self.penalty_score,
                      self.turns_till_fruit_gone + 1, self.min_dist_to_fruit, self.rival_min_dist_to_fruit,
                      self.fruits_on_board_dict)
        minimax_algo = SearchAlgos.MiniMax(state.utility, state.succ, state.perform_move, state.goal)
        depth = 1
        iter_time = 0
        best_move = None, None
        while time.time() + (3 * iter_time) - start < time_limit-.01:
            # the time gap when the curr iter will end, is now-start + curr_iter_time
            cur_time = time.time()
            best_move = minimax_algo.search(state, copy.copy(depth), True)
            iter_time = time.time() - cur_time
            depth += 1
        if best_move[1] is None:
            # print("im out")
            exit(0)
        print("minmax choose the move: ", best_move)  # TODO printing for test. del before sub
        self.board[self.pos[0]][self.pos[1]] = -1
        tmp1 = best_move[1]

        self.pos = (self.pos[0] + tmp1[0], self.pos[1] + tmp1[1])
        # self.pos[0] += tmp1[0]
        # self.pos[1] += tmp1[1]
        self.board[self.pos[0]][self.pos[1]] = 1

        return best_move[1]

    def set_rival_move(self, pos):
        """Update your info, given the new position of the rival.
        input:
            - pos: tuple, the new position of the rival.
        No output is expected
        """
        # mark the rival move as green
        self.board[self.rival_pos[0]][self.rival_pos[1]] = -1
        self.board[pos[0]][pos[1]] = 2
        self.rival_pos = pos
        self.turns_till_fruit_gone -= 1
        if pos is self.min_dist_to_fruit[1]:
            # the rival just took the closest fruit to me, need to recalc the min dist
            self.min_dist_to_fruit = calc_min_dist_to_fruit(self, len(self.board) + len(self.board[0]), self.pos)
        # maybe should update info in self - ?

    def update_fruits(self, fruits_on_board_dict):
        """Update your info on the current fruits on board (if needed).
        input:
            - fruits_on_board_dict: dict of {pos: value}
                                    where 'pos' is a tuple describing the fruit's position on board,
                                    'value' is the value of this fruit.
        No output is expected.
        """
        self.fruits_on_board_dict = {}
        self.board = update_fruits_on_board(self.board, fruits_on_board_dict)

        if self.turns_till_fruit_gone == 0:  # TODO lets talk about it
            for r, row in enumerate(self.board):
                for c, num in enumerate(row):
                    if self.board[r][c] > 2:
                        # this is fruit
                        self.board[r][c] = 0
        # TODO: erase the following line and implement this function. In case you choose not to use it, use 'pass' instead of the following line.
        #raise NotImplementedError

    ########## helper functions in class ##########
    # TODO: add here helper functions in class, if needed

    ########## helper functions for MiniMax algorithm ##########
    # TODO: add here the utility, succ, and perform_move functions used in MiniMax algorithm


def update_fruits_on_board(board, fruits_on_board_dict):
    new_board = board
    for fruit in fruits_on_board_dict:
        # meaning it is a fruit
        # delete the fruit, put 0 because can still go there, but we won't get any points
        new_board[fruit[0]][fruit[1]] = 0
    return new_board

def calc_min_dist_to_fruit(player, max_md_dist, pos):
    min_dist_to_fruit = max_md_dist, None
    for fruit in player.fruits_on_board_dict:
        if md(fruit, pos) <= player.min_dist_to_fruit[0]:
            min_dist_to_fruit = md(fruit, pos), fruit
    return min_dist_to_fruit

def md(loc1, loc2):
    return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])


class State:
    def __init__(self, board, my_pos, rival_pos, scores, penalty_score, turns_till_fruit_gone, min_dist_to_fruit,
                 rival_min_dist_to_fruit, fruits_dict):
        self.board = board
        self.my_pos = my_pos
        self.rival_pos = rival_pos
        # scores[0] = my score, scores[1] = rival score
        self.scores = scores
        self.directions = utils.get_directions()
        self.penalty_score = penalty_score
        self.turns_till_fruit_gone = turns_till_fruit_gone
        self.min_dist_to_fruit = min_dist_to_fruit
        self.rival_min_dist_to_fruit = rival_min_dist_to_fruit
        self.turns = 0
        self.fruits_dict = fruits_dict

    def heuristic(self, maximizing_player):
        val = 0
        if maximizing_player:
            val += self.scores[0] - self.scores[1]
            val += self.number_pf_legal_moves(self.my_pos)
            val += 1 / self.min_dist_to_fruit[0]
            val += self.rival_min_dist_to_fruit[0]
        else:
            val += self.scores[1] - self.scores[0]
            val += self.number_pf_legal_moves(self.rival_pos)
            val += 1 / self.rival_min_dist_to_fruit[0]
            val += self.min_dist_to_fruit[0]

        return val

    def utility(self, maximizing_player, score_or_heuristic):
        if score_or_heuristic:
            if self.scores[0] - self.scores[1] > 0:
                return float('inf')  # if the player will win - so go for it!
            else:
                return self.scores[0] - self.scores[1]
        return self.heuristic(maximizing_player)

    def succ(self, maximizing_player):
        #print("start succ func")
        succ = []
        for op_move in self.directions:
            if maximizing_player:
                i = self.my_pos[0] + op_move[0]
                j = self.my_pos[1] + op_move[1]
            else:
                i = self.rival_pos[0] + op_move[0]
                j = self.rival_pos[1] + op_move[1]

            if 0 <= i < len(self.board) and 0 <= j < len(self.board[0]) and (self.board[i][j] not in [-1, 1, 2]):
                succ.append(op_move)

        if len(succ) == 0 and self.have_valid_move_check(not maximizing_player):
            self.scores[not maximizing_player] -= self.penalty_score

        self.turns_till_fruit_gone -= 1
        if self.turns_till_fruit_gone == 0:
            for r, row in enumerate(self.board):
                for c, num in enumerate(row):
                    if self.board[r][c] > 2 :
                        # this is fruit
                        self.board[r][c] = 0
        # print(self.scores)
        return succ

    def perform_move(self, maximizing_player, move):
        if maximizing_player:
            #print("this is my old pos: ", self.my_pos)
            self.board[self.my_pos[0]][self.my_pos[1]] = -1
            new_pos = (self.my_pos[0]+move[0], self.my_pos[1]+move[1])
            self.my_pos = new_pos
            #print("this is my new pos: ", self.my_pos)
            #
            # if not (0 <= self.my_pos[0] < len(self.board) and 0 <= self.my_pos[1] < len(self.board[0]) and \
            #         (self.board[new_pos[0]][new_pos[1]] not in [-1, 1, 2])):
            #         assert (1 == 0)
        else:
            self.board[self.rival_pos[0]][self.rival_pos[1]] = -1
            new_pos = (self.rival_pos[0]+move[0], self.rival_pos[1]+move[1])
            self.rival_pos = new_pos

        if self.board[new_pos[0]][new_pos[1]] > 2:
            self.scores[not maximizing_player] += self.board[new_pos[0]][new_pos[1]]
        self.board[new_pos[0]][new_pos[1]] = (not maximizing_player)+1

    def goal(self, maximizing_player):
        if not self.have_valid_move_check(maximizing_player):
            if self.have_valid_move_check(not maximizing_player):
                self.scores[not maximizing_player] -= self.penalty_score
            return True
        return False


    def have_valid_move_check(self, maximizing_player):
        for op_move in self.directions:
            if maximizing_player:
                i = self.my_pos[0] + op_move[0]
                j = self.my_pos[1] + op_move[1]
            else:
                i = self.rival_pos[0] + op_move[0]
                j = self.rival_pos[1] + op_move[1]
            if 0 <= i < len(self.board) and 0 <= j < len(self.board[0]) and (self.board[i][j] not in [-1, 1, 2]):
                return True
        return False

    def number_pf_legal_moves(self, pos):
        res = 0
        for op_move in self.directions:
            i = pos[0] + op_move[0]
            j = pos[1] + op_move[1]
            if 0 <= i < len(self.board) and 0 <= j < len(self.board[0]) and (self.board[i][j] not in [-1, 1, 2]):
                res += 1
        return res
