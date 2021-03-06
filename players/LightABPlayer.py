"""
MiniMax Player with AlphaBeta pruning with light heuristic
"""
from players.AbstractPlayer import AbstractPlayer
import SearchAlgos
import copy
import utils


class Player(AbstractPlayer):
    def __init__(self, game_time, penalty_score):
        AbstractPlayer.__init__(self, game_time, penalty_score)
        self.board = None
        self.pos = None
        self.rival_pos = None
        self.fruits_on_board_dict = {}
        self.turns_till_fruit_gone = 0
        self.first_player = -1
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
        self.turns_till_fruit_gone = min(len(board), len(board[0])) * 2
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
        # print("start computing Light alpha-beta move")  # printing for self test
        if self.first_player == -1:
            self.first_player = True
        state = utils.State(copy.deepcopy(self.board), self.pos, self.rival_pos, players_score, self.penalty_score,
                            self.turns_till_fruit_gone, self.fruits_on_board_dict, self.first_player)
        search_algo = SearchAlgos.AlphaBeta(light_utility, utils.succ, utils.perform_move, utils.goal)
        heavy_player_depth = 3
        i = 3
        best_move = search_algo.search(state, i - 1 + heavy_player_depth, True)
        if best_move[1] is None:
            exit(0)
        # print("Light alpha-beta choose the move: ", best_move)  # printing for self test
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
        if self.first_player == -1:
            self.first_player = False

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

    ########## helper functions for AlphaBeta algorithm ##########
    # TODO: add here the utility, succ, and perform_move functions used in AlphaBeta algorithm

    """ ********************** State and common func are implement in utils.py ********************** """


def light_utility(state, score_or_heuristic):
    if score_or_heuristic:
        return state.scores[0] - state.scores[1]

    max_player_steps = 0
    min_player_steps = 0
    for d in state.directions:
        i = state.my_pos[0] + d[0]
        j = state.my_pos[0] + d[1]

        n = state.my_pos[0] + d[0]
        m = state.my_pos[0] + d[1]

        # check legal move for max
        if 0 <= i < len(state.board) and 0 <= j < len(state.board[0]) and (state.board[i][j] not in [-1, 1, 2]):
            max_player_steps += 1
        # check legal move for min
        if 0 <= n < len(state.board) and 0 <= m < len(state.board[0]) and (state.board[n][m] not in [-1, 1, 2]):
            min_player_steps += 1

        return max_player_steps - min_player_steps

