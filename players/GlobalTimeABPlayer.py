"""
MiniMax Player with AlphaBeta pruning and global time
"""
from players.AbstractPlayer import AbstractPlayer
# TODO: you can import more modules, if needed
import SearchAlgos
import copy
import utils
import time


class Player(AbstractPlayer):
    def __init__(self, game_time, penalty_score):
        AbstractPlayer.__init__(self, game_time, penalty_score)
        self.board = None
        self.pos = None
        self.rival_pos = None
        self.fruits_on_board_dict = {}
        self.turns_till_fruit_gone = 0
        self.max_turns = 0

        self.game_time = game_time  # more fields for this player
        self.time_for_curr_iter = 0

    def set_game_params(self, board):
        """Set the game parameters needed for this player.
        This function is called before the game starts.
        (See GameWrapper.py for more info where it is called)
        input:
            - board: np.array, a 2D matrix of the board.
        No output is expected.
        """
        self.board = board  # need to set my pos, the rival pos, all the grey area and all fruits
        self.max_turns = len(board) * len(board[0]) - 2
        self.turns_till_fruit_gone = min(len(board), len(board[0])) * 2
        for r, row in enumerate(board):
            for c, num in enumerate(row):
                if num == -1:
                    self.max_turns -= 1
                if num == 1:
                    self.pos = (r, c)  # this my pos
                elif num == 2:
                    self.rival_pos = (r, c)
                elif num > 2:
                    self.fruits_on_board_dict[(r, c)] = num  # need to do this manually only for this player

        self.time_for_curr_iter = (-2 / 3) * self.game_time / (((1 / 3) ** self.max_turns) - 1)  # TODO! need to save time for last iter weach is bigger than min time possibole

        min_iter_time = time.time()
        state = utils.State(copy.deepcopy(self.board), self.pos, self.rival_pos, [0,0], self.penalty_score,
                            self.turns_till_fruit_gone, self.fruits_on_board_dict)
        search_algo = SearchAlgos.AlphaBeta(utils.utility, utils.succ, utils.perform_move, utils.goal)
        search_algo.search(state, 1, True)

        min_iter_time = (time.time() - min_iter_time) * 0.9999  # TODO right now i dont do anything with this... need your help

        tmp = self.time_for_curr_iter
        tmp_depth = self.max_turns
        while tmp_depth and tmp_depth > min_iter_time:
            tmp = tmp/3
            tmp_depth -= 1

        if tmp_depth < min_iter_time:  # TODO right now i dont do anything with this... need your help
            print("need to make plan B for time sharing GBA...")

    def make_move(self, time_limit, players_score):
        """Make move with this Player.
        input:
            - time_limit: float, time limit for a single turn.
        output:
            - direction: tuple, specifing the Player's movement, chosen from self.directions
        """
        print("start computing Global AB move")  # TODO printing for test. del before sub
        start_time = time.time()
        allowed_time = min(self.time_for_curr_iter, time_limit)  # TODO need to speak about it

        state = utils.State(copy.deepcopy(self.board), self.pos, self.rival_pos, players_score, self.penalty_score,
                            self.turns_till_fruit_gone, self.fruits_on_board_dict, time.time() + allowed_time - .015)  # TODO time limit -.015
        search_algo = SearchAlgos.AlphaBeta(utils.utility, utils.succ, utils.perform_move, utils.goal)
        depth = 1
        best_move = None, None

        while depth <= self.max_turns:
            try:
                best_move = search_algo.search(state, depth, True)
            except TimeoutError:
                break
            depth += 1

        if best_move[1] is None:
            print("something went wrong,.. im out... probably not enough time for at least depth=1")  # TODO printing for test. del before sub
            exit(0)

        print("depth is : ", depth - 1)   # TODO printing for test. del before sub
        # self.time_for_curr_iter = (self.time_for_curr_iter/3)
        self.time_for_curr_iter = (self.time_for_curr_iter/3) + self.time_for_curr_iter - (time.time()-start_time)  # TODO Testing
        print("current iter took: ", time.time()-start_time)
        print("next iter will take: ", self.time_for_curr_iter)  # TODO printing for test

        print("Global AB choose the move: ", best_move)  # TODO printing for test. del before sub
        self.board[self.pos] = -1
        tmp1 = best_move[1]
        self.pos = (self.pos[0] + tmp1[0], self.pos[1] + tmp1[1])
        self.board[self.pos] = 1
        self.turns_till_fruit_gone -= 1
        return best_move[1]

    def set_rival_move(self, pos):
        """Update your info, given the new position of the rival.
        input:
            - pos: tuple, the new position of the rival.
        No output is expected
        """
        self.board[self.rival_pos] = -1
        self.board[pos] = 2
        self.rival_pos = pos
        self.turns_till_fruit_gone -= 1

    def update_fruits(self, fruits_on_board_dict):
        """Update your info on the current fruits on board (if needed).
        input:
            - fruits_on_board_dict: dict of {pos: value}
                                    where 'pos' is a tuple describing the fruit's position on board,
                                    'value' is the value of this fruit.
        No output is expected.
        """
        if self.turns_till_fruit_gone == 0 or self.turns_till_fruit_gone == -1:
            for fruit_pos in self.fruits_on_board_dict.keys():
                if self.board[fruit_pos] > 2:
                    self.board[fruit_pos] = 0

        self.fruits_on_board_dict = fruits_on_board_dict

