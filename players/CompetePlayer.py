"""
Player for the competition
"""
from players.AbstractPlayer import AbstractPlayer
#TODO: you can import more modules, if needed
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

        self.game_time = game_time
        self.time_for_search_8 = 0  # more fields for this player
        self.time_for_curr_iter = 0

        self.first_run_flag = True
        self.my_turns = 0

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


    def make_move(self, time_limit, players_score):
        """Make move with this Player.
        input:
            - time_limit: float, time limit for a single turn.
        output:
            - direction: tuple, specifing the Player's movement, chosen from self.directions
        """
        print("start computing COMPETITION-PLAYER move")  # TODO printing for test. del before sub
        start_time = time.time()
        state = utils.State(copy.deepcopy(self.board), self.pos, self.rival_pos, players_score, self.penalty_score,
                            self.turns_till_fruit_gone, self.fruits_on_board_dict)
        search_algo = SearchAlgos.AlphaBeta(competittion_utility, utils.succ, utils.perform_move, utils.goal)

        best_move = None
        first_time_iter = 0
        if self.first_run_flag:
            self.first_run_flag = False
            self.time_for_curr_iter = (-2 / 3) * self.game_time / (((1 / 3) ** self.max_turns) - 1)
            search_algo = SearchAlgos.AlphaBeta(competittion_utility, utils.succ, utils.perform_move, utils.goal)
            cur_time = time.time()
            best_move = search_algo.search(state, 8, True)
            self.time_for_search_8 = time.time() - cur_time
            first_time_iter = self.time_for_search_8

        risk_factor_mul = 2.1712*(1+self.max_turns-self.my_turns)/self.max_turns  # TODO risky1
        risk_factor_add_depth = 2  # TODO risky2

        depth = 10  # min depth. already calc depth is 15 (9-1)
        allowed_time = min(self.time_for_curr_iter, time_limit) - first_time_iter
        tmp_time = self.time_for_search_8
        if allowed_time > 1.1:
            while tmp_time < allowed_time - 0.001:
                depth += 1
                tmp_time *= risk_factor_mul
            print("i search to depth: ", depth - 1 + risk_factor_add_depth)
            best_move = search_algo.search(state, depth - 1 + risk_factor_add_depth, True)
        elif best_move is None:
            min_depth_op = 10*(1+self.max_turns+self.my_turns)/self.max_turns  # different from prev formula
            print("i search to depth: ", min_depth_op)
            best_move = search_algo.search(state, min_depth_op, True)

        if best_move[1] is None:
            print("ops... i am out")
            exit(0)

        self.time_for_curr_iter = (self.time_for_curr_iter/risk_factor_mul) + allowed_time - (time.time() - start_time)
        print("next iter will take: ", self.time_for_curr_iter)  # TODO printing for test

        print("COMPETITION-PLAYER choose the move: ", best_move)  # TODO printing for test. del before sub
        self.board[self.pos] = -1
        tmp1 = best_move[1]
        self.pos = (self.pos[0] + tmp1[0], self.pos[1] + tmp1[1])
        self.board[self.pos] = 1
        self.turns_till_fruit_gone -= 1
        self.my_turns += 2  # TODO check
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
    #TODO: add here helper functions in class, if needed


    ########## helper functions for the search algorithm ##########
    #TODO: add here the utility, succ, and perform_move functions used in AlphaBeta algorithm


def competittion_utility(state, score_or_heuristic):
    if score_or_heuristic:
        if state.scores[0] - state.scores[1] > 0:
            return (state.scores[0] - state.scores[1]) * 1000
        return state.scores[0] - state.scores[1]

    val = (state.scores[0] - state.scores[1])
    if state.scores[0] - state.penalty_score > state.scores[1] and state.number_pf_legal_moves(state.rival_pos) == 0:
        return (state.scores[0] - state.scores[1] + state.penalty_score) * 1000

    potential_fruit_val = 0
    if state.turns_till_fruit_gone > 0:
        for fruit_pos in state.fruits_dict.keys():
            curr_fruit_dist = abs(fruit_pos[0] - state.my_pos[0]) + abs(fruit_pos[1] - state.my_pos[1])  # max player
            if curr_fruit_dist <= state.turns_till_fruit_gone:
                potential_fruit_val += state.fruits_dict[fruit_pos] / curr_fruit_dist

            curr_fruit_dist = abs(fruit_pos[0] - state.rival_pos[0]) + abs(fruit_pos[1] - state.rival_pos[1])  # min pl
            if curr_fruit_dist <= state.turns_till_fruit_gone:
                potential_fruit_val -= state.fruits_dict[fruit_pos] / curr_fruit_dist

    val += potential_fruit_val*2/3

    val += (state.number_pf_legal_moves(state.my_pos) - state.number_pf_legal_moves(state.rival_pos))*state.\
        penalty_score/2

    return val