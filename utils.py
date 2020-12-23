import operator
import numpy as np
import os
import copy

# TODO: edit the alpha and beta initialization values for AlphaBeta algorithm.
# instead of 'None', write the real initialization value, learned in class.
# hint: you can use np.inf
ALPHA_VALUE_INIT = float('-inf')  # TODO why np.inf and not like this? they gave as code with float('inf')
BETA_VALUE_INIT = float('inf')


def get_directions():
    """Returns all the possible directions of a player in the game as a list of tuples.
    """
    return [(1, 0), (0, 1), (-1, 0), (0, -1)]


def tup_add(t1, t2):
    """
    returns the sum of two tuples as tuple.
    """
    return tuple(map(operator.add, t1, t2))


def get_board_from_csv(board_file_name):
    """Returns the board data that is saved as a csv file in 'boards' folder.
    The board data is a list that contains: 
        [0] size of board
        [1] blocked poses on board
        [2] starts poses of the players
    """
    board_path = os.path.join('boards', board_file_name)
    board = np.loadtxt(open(board_path, "rb"), delimiter=" ")

    # mirror board
    board = np.flipud(board)
    i, j = len(board), len(board[0])
    blocks = np.where(board == -1)
    blocks = [(blocks[0][i], blocks[1][i]) for i in range(len(blocks[0]))]
    start_player_1 = np.where(board == 1)
    start_player_2 = np.where(board == 2)

    if len(start_player_1[0]) != 1 or len(start_player_2[0]) != 1:
        raise Exception('The given board is not legal - too many start locations.')

    start_player_1 = (start_player_1[0][0], start_player_1[1][0])
    start_player_2 = (start_player_2[0][0], start_player_2[1][0])

    return [(i, j), blocks, [start_player_1, start_player_2]]

    ################### from here down, its only our code ###################


class State:
    def __init__(self, board, my_pos, rival_pos, scores, penalty_score, turns_till_fruit_gone, fruits_dict):
        self.board = board
        self.my_pos = my_pos
        self.rival_pos = rival_pos
        self.scores = scores  # scores[0] = my score, scores[1] = rival score
        self.directions = get_directions()
        self.penalty_score = penalty_score
        self.turns_till_fruit_gone = turns_till_fruit_gone
        self.fruits_dict = fruits_dict

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


def goal(state, maximizing_player):
    if not state.have_valid_move_check(maximizing_player):
        if state.have_valid_move_check(not maximizing_player):
            state.scores[not maximizing_player] -= state.penalty_score
        return True
    return False


def succ(state, maximizing_player):
    op_moves = []
    for op_move in state.directions:
        if maximizing_player:
            i = state.my_pos[0] + op_move[0]
            j = state.my_pos[1] + op_move[1]
        else:
            i = state.rival_pos[0] + op_move[0]
            j = state.rival_pos[1] + op_move[1]

        if 0 <= i < len(state.board) and 0 <= j < len(state.board[0]) and (state.board[i][j] not in [-1, 1, 2]):
            op_moves.append(op_move)

    if len(op_moves) == 0 and state.have_valid_move_check(not maximizing_player):
        state.scores[not maximizing_player] -= state.penalty_score

    return op_moves


def perform_move(state, maximizing_player, move):
    if maximizing_player:
        state.board[state.my_pos[0]][state.my_pos[1]] = -1
        new_pos = (state.my_pos[0] + move[0], state.my_pos[1] + move[1])
        state.my_pos = new_pos
    else:
        state.board[state.rival_pos[0]][state.rival_pos[1]] = -1
        new_pos = (state.rival_pos[0] + move[0], state.rival_pos[1] + move[1])
        state.rival_pos = new_pos

    if state.board[new_pos[0]][new_pos[1]] > 2:
        state.scores[not maximizing_player] += state.board[new_pos[0]][new_pos[1]]
        del state.fruits_dict[new_pos]
    state.board[new_pos[0]][new_pos[1]] = (not maximizing_player) + 1

    state.turns_till_fruit_gone -= 1

    if state.turns_till_fruit_gone == 0:
        for r, row in enumerate(state.board):
            for c, num in enumerate(row):
                if state.board[r][c] > 2:  # this is fruit
                    state.board[r][c] = 0


def utility(state, score_or_heuristic):
    if score_or_heuristic:
        return state.scores[0] - state.scores[1]

    val = (state.scores[0] - state.scores[1])
    if state.scores[0] - state.penalty_score > state.scores[1] and state.number_pf_legal_moves(state.rival_pos) == 0:
        val += state.penalty_score

    potential_fruit_val = 0
    if state.turns_till_fruit_gone > 0:
        for fruit_pos in state.fruits_dict.keys():
            curr_fruit_dist = abs(fruit_pos[0] - state.my_pos[0]) + abs(fruit_pos[1] - state.my_pos[1])  # max player
            if curr_fruit_dist <= state.turns_till_fruit_gone:
                potential_fruit_val += state.fruits_dict[fruit_pos] / curr_fruit_dist

            curr_fruit_dist = abs(fruit_pos[0] - state.rival_pos[0]) + abs(fruit_pos[1] - state.rival_pos[1])  # min pl
            if curr_fruit_dist <= state.turns_till_fruit_gone:
                potential_fruit_val -= state.fruits_dict[fruit_pos] / curr_fruit_dist

    val += potential_fruit_val/2

    val += (state.number_pf_legal_moves(state.my_pos) - state.number_pf_legal_moves(state.rival_pos))*state.\
        penalty_score/10

    return val
