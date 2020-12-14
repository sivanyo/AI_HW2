"""
MiniMax Player
"""
from players.AbstractPlayer import AbstractPlayer
import SearchAlgos
import copy
import utils


# TODO: you can import more modules, if needed


class Player(AbstractPlayer):
    def __init__(self, game_time, penalty_score):
        # keep the inheritance of the parent's (AbstractPlayer) __init__()
        AbstractPlayer.__init__(self, game_time, penalty_score)
        self.board = None  # SH
        self.rival_pos = None  # SH
        self.pos = None  # SH
        self.fruit = None  # SH
        self.scores = (0, 0)
        self.num_of_left = 0
        self.num_of_left_rival = 0
        self.min_dist_to_fruit = 0
        self.fruits_on_board_dict = {}
        self.my_move = None
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
        for r, row in board:
            for c, num in row:
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
                    self.fruits_on_board_dict[[r, c]] = num
        # todo : add some info about fruits

    def make_move(self, time_limit, players_score):
        """Make move with this Player.
        input:
            - time_limit: float, time limit for a single turn.
        output:
            - direction: tuple, specifing the Player's movement, chosen from self.directions
        """
        minimax_algo = SearchAlgos.MiniMax(self.utility(), self.succ(), self.perform_move(), self.goal())
        state = State(copy.deepcopy(self.board), self.pos, self.rival_pos, players_score, self.penalty_score)
        best_move = minimax_algo.search(state, 100, True)
        if best_move[1] is None:
            exit(0)
        return best_move[1]

    def set_rival_move(self, pos):
        """Update your info, given the new position of the rival.
        input:
            - pos: tuple, the new position of the rival.
        No output is expected
        """
        # mark the rival move as green
        self.board[pos[0]][pos[1]] = -1
        # maybe should update info in self - ?

    def update_fruits(self, fruits_on_board_dict):
        """Update your info on the current fruits on board (if needed).
        input:
            - fruits_on_board_dict: dict of {pos: value}
                                    where 'pos' is a tuple describing the fruit's position on board,
                                    'value' is the value of this fruit.
        No output is expected.
        """
        # TODO: erase the following line and implement this function. In case you choose not to use it, use 'pass' instead of the following line.
        raise NotImplementedError

    ########## helper functions in class ##########
    # TODO: add here helper functions in class, if needed

    ########## helper functions for MiniMax algorithm ##########
    # TODO: add here the utility, succ, and perform_move functions used in MiniMax algorithm


class State:
    def __init__(self, board, my_pos, rival_pos, scores, penalty_score):
        self.board = board
        self.my_pos = my_pos
        self.rival_pos = rival_pos
        # scores[0] = my score, scores[1] = rival score
        self.scores = scores
        self.directions = utils.get_directions()
        self.penalty_score = penalty_score

    def heuristic(self):
        # count num of available steps
        num_steps_available = 0
        for d in self.directions:
            i = self.pos[0] + d[0]
            j = self.pos[1] + d[1]
            # check legal move
            if 0 <= i < len(self.board) and 0 <= j < len(self.board[0]) and \
                    (self.board[i][j] not in [-1, 1, 2]):
                num_steps_available += 1

        return num_steps_available + (1 / self.min_dist_to_fruit) + self.num_of_left + (1 / self.num_of_left_rival)

    def utility(self):
        # need to get state and min or max node
        if self.num_of_left is 0 and self.num_of_left_rival is not 0:
            # im stuck
            return self.self_score - self.penalty_score - self.rival_score
        else:
            return self.self_score - self.rival_score + self.penalty_score

    def succ(self, maximizing_player):
        succ = []
        for op_move in self.directions:
            if maximizing_player:
                i = self.my_pos[0] + op_move[0]
                j = self.my_pos[1] + op_move[1]
            else:
                i = self.rival_pos[0] + op_move[0]
                j = self.rival_pos[1] + op_move[1]
            if 0 <= i < len(self.board) and 0 <= j < len(self.state.board[0]) and \
                    (self.state.board[i][j] not in [-1, 1, 2]):
                succ.append(op_move)

        if len(succ) == 0:
            self.scores[not maximizing_player] -= self.penalty_score

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

        if self.board[move[0]][move[1]] > 2:
            self.scores[not maximizing_player] += self.board[new_pos[0]][new_pos[1]]

        self.board[new_pos[0]][new_pos[1]] = (not maximizing_player)+1

        return self.scores[0] - self.scores[1]

    def goal(self, moves):
        return self.scores[0] - self.scores[1]

        # # only on leaf
        # if self.num_of_left is 0 and self.num_of_left_rival is not 0:
        #     # im stack
        #     return self.self_score - self.penalty_score - self.rival_score > 0
        #     # im the winner
        # else:
        #     # the rival stack
        #     return self.self_score - self.rival_score + self.penalty_score > 0


    # def get_min_max(self, maximizing_player):
    #     if maximizing_player:
    #         return self.scores[0] - self.scores[1] - self.penalty_score
    #     return self.scores[0] - self.scores[1] + self.penalty_score
