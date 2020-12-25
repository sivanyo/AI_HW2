"""
MiniMax Player
"""
from players.AbstractPlayer import AbstractPlayer
import SearchAlgos
import copy
import utils

# TODO: you can import more modules, if needed
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
        self.turns_till_fruit_gone = min(len(board), len(board[0]))*2
        for r, row in enumerate(board):
            for c, num in enumerate(row):
                if num == -1:
                    self.max_turns -= 1
                elif num == 1:
                    self.pos = (r, c)  # this my pos
                elif num == 2:
                    self.rival_pos = (r, c)  # this is the rival starting pos

    def make_move(self, time_limit, players_score):
        """Make move with this Player.
        input:
            - time_limit: float, time limit for a single turn.
        output:
            - direction: tuple, specifing the Player's movement, chosen from self.directions
        """
        print("start computing minimax move")  # TODO printing for test. del before sub
        state = utils.State(copy.deepcopy(self.board), self.pos, self.rival_pos, players_score, self.penalty_score,
                      self.turns_till_fruit_gone, self.fruits_on_board_dict, time.time()+time_limit-.01)  # TODO time limit -.01
        search_algo = SearchAlgos.MiniMax(utils.utility, utils.succ, utils.perform_move, utils.goal)
        depth = 1
        best_move = None, None

        while depth <= self.max_turns:
            try:
                best_move = search_algo.search(state, depth, True)
            except TimeoutError:
                break
            depth += 1

        if best_move[1] is None:
            print("something went wrong,.. im out")  # TODO printing for test. del before sub
            exit(0)
        print("depth is : ", depth-1)
        print("minmax choose the move: ", best_move)  # TODO printing for test. del before sub
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


    ########## helper functions in class ##########
    # TODO: add here helper functions in class, if needed

    ########## helper functions for MiniMax algorithm ##########
    # TODO: add here the utility, succ, and perform_move functions used in MiniMax algorithm

    """ ********************** State and common func are implement in utils.py ********************** """
