"""
MiniMax Player with AlphaBeta pruning
"""
from players.AbstractPlayer import AbstractPlayer
import SearchAlgos
import copy
import utils
#TODO: you can import more modules, if needed
import time


class Player(AbstractPlayer):
    def __init__(self, game_time, penalty_score):
        AbstractPlayer.__init__(self, game_time, penalty_score) # keep the inheritance of the parent's (AbstractPlayer) __init__()
        self.board = None
        self.rival_pos = None
        self.pos = None
        self.scores = (0, 0)
        # self.num_of_left = 0
        # self.num_of_left_rival = 0
        self.min_dist_to_fruit = 0, None
        self.rival_min_dist_to_fruit = 0, None
        self.fruits_on_board_dict = {}
        self.my_move = None
        self.turns_till_fruit_gone = 0
        # self.turns = 0


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
        # self.min_dist_to_fruit = len(board) + len(board[0]), None
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
        # self.min_dist_to_fruit = calc_min_dist_to_fruit(self, len(board) + len(board[0]), self.pos)
        # self.rival_min_dist_to_fruit = calc_min_dist_to_fruit(self, len(board) + len(board[0]), self.rival_pos)

    def make_move(self, time_limit, players_score):
        """Make move with this Player.
        input:
            - time_limit: float, time limit for a single turn.
        output:
            - direction: tuple, specifing the Player's movement, chosen from self.directions
        """
        print("start computing alpha-beta move")  # TODO printing for test. del before sub
        self.turns_till_fruit_gone -= 1

        state = State(copy.deepcopy(self.board), self.pos, self.rival_pos, players_score, self.penalty_score,
                      self.turns_till_fruit_gone + 1, self.min_dist_to_fruit, self.rival_min_dist_to_fruit,
                      self.fruits_on_board_dict)

        search_algo = SearchAlgos.AlphaBeta(state.utility, state.succ, state.perform_move, state.goal)
        best_move = search_algo.search(state, len(self.board)*len(self.board[0])/2, True)  # TODO depth
        if best_move[1] is None:
            exit(0)
        print("alpha-beta choose the move: ", best_move)  # TODO printing for test. del before sub
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
        self.board[self.rival_pos[0]][self.rival_pos[1]] = -1
        self.board[pos[0]][pos[1]] = 2
        self.rival_pos = pos
        self.turns_till_fruit_gone -= 1
        # if pos is self.min_dist_to_fruit[1]:
        #     # the rival just took the closest fruit to me, need to recalc the min dist
        #     self.min_dist_to_fruit = calc_min_dist_to_fruit(self, len(self.board) + len(self.board[0]), self.pos)
        # maybe should update info in self - ?

    def update_fruits(self, fruits_on_board_dict):
        """Update your info on the current fruits on board (if needed).
        input:
            - fruits_on_board_dict: dict of {pos: value}
                                    where 'pos' is a tuple describing the fruit's position on board,
                                    'value' is the value of this fruit.
        No output is expected.
        """
        # TODO i wrote this diffrent from minimax. lets talk about it
        self.fruits_on_board_dict = fruits_on_board_dict

        if self.turns_till_fruit_gone == 0:  # TODO lets talk about it
            for r, row in enumerate(self.board):
                for c, num in enumerate(row):
                    if self.board[r][c] > 2:
                        # this is fruit
                        self.board[r][c] = 0

        #TODO: erase the following line and implement this function. In case you choose not to use this function, 
        # use 'pass' instead of the following line.

    ########## helper functions in class ##########
    #TODO: add here helper functions in class, if needed


    ########## helper functions for AlphaBeta algorithm ##########
    #TODO: add here the utility, succ, and perform_move functions used in AlphaBeta algorithm

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
        # self.min_dist_to_fruit = min_dist_to_fruit
        # self.rival_min_dist_to_fruit = rival_min_dist_to_fruit
        # self.turns = 0
        self.fruits_dict = fruits_dict

    def utility(self, maximizing_player=True, score_or_heuristic=True):
        return self.scores[0] - self.scores[1]
        # if self.scores[0] - self.scores[1] > 0:  # TODO this trick does not work with alpha-beta
        #     return float('inf')  # if the player will win - so go for it!
        # else:
        #     return self.scores[0] - self.scores[1]

    def succ(self, maximizing_player):
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
                    if self.board[r][c] > 2:
                        # this is fruit
                        self.board[r][c] = 0
        # print(self.scores)
        return succ

    def perform_move(self, maximizing_player, move):
        if maximizing_player:
            self.board[self.my_pos[0]][self.my_pos[1]] = -1
            new_pos = (self.my_pos[0]+move[0], self.my_pos[1]+move[1])
            self.my_pos = new_pos
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
