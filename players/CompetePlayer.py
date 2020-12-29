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
        self.first_player = -1
        self.max_turns = 0

        self.game_time = game_time  # more fields for this player
        self.time_for_curr_iter = 0
        self.time_for_each_iter = None
        self.my_turn = None
        self.extra_safe_time = 0.012
        self.risk_factor1 = 2.2
        self.risk_factor2 = 2.1712

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

        self.time_for_curr_iter = (-2 / 3) * self.game_time / (((1 / 3) ** self.max_turns) - 1)

        min_iter_time = time.time()
        state = utils.State(copy.deepcopy(self.board), self.pos, self.rival_pos, [0,0], self.penalty_score,
                            self.turns_till_fruit_gone, self.fruits_on_board_dict, True)
        search_algo = SearchAlgos.AlphaBeta(comp_utility, utils.succ, utils.perform_move, utils.goal)
        search_algo.search(state, 2, True)  # TODO 2

        min_iter_time = (time.time() - min_iter_time) * 1.1

        self.my_turn = int((1+self.max_turns)/2)
        tmp = self.time_for_curr_iter
        tmp_depth = self.my_turn
        while tmp_depth and tmp_depth > min_iter_time:  # check every iter is possible for at least depth=1
            tmp = tmp / self.risk_factor1
            tmp_depth -= 1

        if tmp_depth < min_iter_time:  # not every iter is possible for at least depth=1. plan B for time sharing:
            avg_time = self.game_time/self.my_turn
            self.time_for_each_iter = {}
            index_left = self.my_turn
            index_right = 0
            exchange_tmp = avg_time - min_iter_time
            while index_left >= index_right and exchange_tmp > 0:  # exchange time between the latest iter and the first
                self.time_for_each_iter[index_left] = avg_time + exchange_tmp
                self.time_for_each_iter[index_right] = min_iter_time + self.extra_safe_time
                index_right += 1
                index_left -= 1
                min_iter_time *= self.risk_factor2  # TODO lets be brave and put 2.171 instead
                exchange_tmp = avg_time - (min_iter_time + self.extra_safe_time)

            while index_left >= index_right:
                self.time_for_each_iter[index_left] = avg_time
                self.time_for_each_iter[index_right] = avg_time
                index_right += 1
                index_left -= 1

            self.time_for_curr_iter = self.time_for_each_iter[self.my_turn]
            self.my_turn -= 1

    def make_move(self, time_limit, players_score):
        """Make move with this Player.
        input:
            - time_limit: float, time limit for a single turn.
        output:
            - direction: tuple, specifing the Player's movement, chosen from self.directions
        """
        print("start computing CompetePlayer move")  # TODO printing for test. del before sub
        start_time = time.time()
        allowed_time = min(self.time_for_curr_iter, time_limit)

        if self.first_player == -1:
            self.first_player = True

        state = utils.State(copy.deepcopy(self.board), self.pos, self.rival_pos, players_score, self.penalty_score,
                            self.turns_till_fruit_gone, self.fruits_on_board_dict, self.first_player, time.time() +
                            allowed_time - self.extra_safe_time)
        search_algo = SearchAlgos.AlphaBeta(comp_utility, utils.succ, utils.perform_move, utils.goal)
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
        if self.time_for_each_iter is not None:
            print("my turn is: ", self.my_turn)   # TODO printing for test. del before sub
            self.time_for_curr_iter += self.time_for_each_iter[self.my_turn] - (time.time()-start_time)
            self.my_turn -= 1
        else:
            self.time_for_curr_iter += (self.time_for_curr_iter/self.risk_factor1) - (time.time()-start_time)
        print("current iter took: ", time.time()-start_time)   # TODO printing for test. del before sub
        print("next iter will take: ", self.time_for_curr_iter)  # TODO printing for test
        print("CompetePlayer choose the move: ", best_move)  # TODO printing for test. del before sub
        self.max_turns -= 1
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
        self.max_turns -= 1
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
    #TODO: add here helper functions in class, if needed


    ########## helper functions for the search algorithm ##########
    #TODO: add here the utility, succ, and perform_move functions used in AlphaBeta algorithm


def comp_utility(state, score_or_heuristic):
    if score_or_heuristic:
        if state.scores[0] - state.scores[1] > 0:
            return (state.scores[0] - state.scores[1]) * 1000
        return state.scores[0] - state.scores[1]

    val = (state.scores[0] - state.scores[1])
    # if state.scores[0] - state.penalty_score > state.scores[1] and state.number_pf_legal_moves(state.rival_pos) == 0:  # TODO why
    #     return (state.scores[0] - state.scores[1] + state.penalty_score) * 1000
    if state.number_pf_legal_moves(state.rival_pos) == 0:
        val += state.penalty_score
    else:
        val += (state.number_pf_legal_moves(state.my_pos) - state.number_pf_legal_moves(state.rival_pos)) * state. \
            penalty_score / 10

    tmp1 = calc_left_moves(copy.copy(state.board), state.my_pos)
    tmp2 = calc_left_moves(copy.copy(state.board), state.rival_pos)
    if tmp1 > tmp2+2:
        val += state.penalty_score/2
    elif tmp1+2 < tmp2:
        val -= state.penalty_score/2

    return val


def calc_left_moves(board, pos):
    sum_moves = 1
    for direction in utils.get_directions():
        i = pos[0] + direction[0]
        j = pos[1] + direction[1]
        if 0 <= i < len(board) and 0 <= j < len(board[0]) and (board[i][j] not in [-1, 1, 2]):
            board[i][j] = -1
            sum_moves += calc_left_moves(board, (i, j))
    return sum_moves
