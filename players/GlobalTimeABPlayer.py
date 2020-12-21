"""
MiniMax Player with AlphaBeta pruning and global time
"""
from players.AbstractPlayer import AbstractPlayer
# TODO: you can import more modules, if needed
import SearchAlgos
import copy
import utils
import math
import time


class Player(AbstractPlayer):
    def __init__(self, game_time, penalty_score):
        AbstractPlayer.__init__(self, game_time,
                                penalty_score)  # keep the inheritance of the parent's (AbstractPlayer) __init__()
        self.board = None
        self.rival_pos = None
        self.pos = None
        self.scores = (0, 0)
        self.num_of_left = 0
        self.num_of_left_rival = 0
        self.min_dist_to_fruit = 0, None
        self.rival_min_dist_to_fruit = 0, None
        self.fruits_on_board_dict = {}
        self.my_move = None
        self.turns_till_fruit_gone = 0
        self.max_turns = 0
        self.turns = 0
        self.time_for_search_5 = 0
        time.game_time = game_time
        self.time_for_curr_iter = 0
        print("first turn will take : ", self.time_for_curr_iter, "global time is : ", self.game_time)

    def set_game_params(self, board):
        """Set the game parameters needed for this player.
        This function is called before the game starts.
        (See GameWrapper.py for more info where it is called)
        input:
            - board: np.array, a 2D matrix of the board.
        No output is expected.
        """
        self.board = board
        self.max_turns = math.ceil(len(self.board)*len(self.board[0])/2)
        self.time_for_curr_iter = (-2/3) * self.game_time / (((1/3) ** self.max_turns) - 1)
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
        self.min_dist_to_fruit = utils.calc_min_dist_to_fruit(self, len(board) + len(board[0]), self.pos)
        self.rival_min_dist_to_fruit = utils.calc_min_dist_to_fruit(self, len(board) + len(board[0]), self.rival_pos)
        state = utils.State(copy.deepcopy(self.board), self.pos, self.rival_pos, [0, 0], self.penalty_score,
                      self.turns_till_fruit_gone + 1, self.min_dist_to_fruit, self.rival_min_dist_to_fruit,
                      self.fruits_on_board_dict)
        search_algo = SearchAlgos.AlphaBeta(state.utility, state.succ, state.perform_move, state.goal)
        cur_time = time.time()
        move = search_algo.search(state, 5, True)
        self.time_for_search_5 = time.time() - cur_time
        # todo : add some info about fruits

    def make_move(self, time_limit, players_score):
        """Make move with this Player.
        input:
            - time_limit: float, time limit for a single turn.
        output:
            - direction: tuple, specifing the Player's movement, chosen from self.directions
        """
        print("start computing Global AB move")  # TODO printing for test. del before sub

        state = utils.State(copy.deepcopy(self.board), self.pos, self.rival_pos, players_score, self.penalty_score,
                      self.turns_till_fruit_gone + 1, self.min_dist_to_fruit, self.rival_min_dist_to_fruit,
                      self.fruits_on_board_dict)
        search_algo = SearchAlgos.AlphaBeta(state.utility, state.succ, state.perform_move, state.goal)
        # if self.time_for_search_5 == 0:
        #     cur_time = time.time()
        #     move = search_algo.search(state,5, True)
        #     self.time_for_search_5 = time.time() - cur_time

        self.turns_till_fruit_gone -= 1
        # calc depth
        depth = 5
        allowed_time = self.time_for_curr_iter
        tmp_time = self.time_for_search_5
        if allowed_time < 1.5:
            depth = 9
        else:
            while tmp_time < allowed_time - 0.001:
                depth += 1
                tmp_time *= 3

        best_move = search_algo.search(state, depth-1, True)  # TODO depth
        if best_move[1] is None:
            print("best move is None")
            exit(0)
        print("i search to depth: ", depth -1 )
        print("Global AB choose the move: ", best_move)  # TODO printing for test. del before sub
        self.board[self.pos[0]][self.pos[1]] = -1
        tmp1 = best_move[1]

        self.pos = (self.pos[0] + tmp1[0], self.pos[1] + tmp1[1])
        # self.pos[0] += tmp1[0]
        # self.pos[1] += tmp1[1]
        self.board[self.pos[0]][self.pos[1]] = 1

        self.time_for_curr_iter /= 3
        print("next iter will take: ", self.time_for_curr_iter)

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
            self.min_dist_to_fruit = utils.calc_min_dist_to_fruit(self, len(self.board) + len(self.board[0]), self.pos)
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
        self.board = utils.update_fruits_on_board(self.board, fruits_on_board_dict)

        if self.turns_till_fruit_gone == 0:  # TODO lets talk about it
            for r, row in enumerate(self.board):
                for c, num in enumerate(row):
                    if self.board[r][c] > 2:
                        # this is fruit
                        self.board[r][c] = 0

