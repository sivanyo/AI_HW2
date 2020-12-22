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
                 rival_min_dist_to_fruit, fruits_dict, max_turns):
        self.board = board
        self.my_pos = my_pos
        self.rival_pos = rival_pos
        self.scores = scores  # scores[0] = my score, scores[1] = rival score
        self.directions = get_directions()
        self.penalty_score = penalty_score
        self.turns_till_fruit_gone = turns_till_fruit_gone
        self.min_dist_to_fruit = min_dist_to_fruit
        self.rival_min_dist_to_fruit = rival_min_dist_to_fruit
        self.turns = 0
        self.fruits_dict = fruits_dict
        self.max_turns = max_turns

    def heuristic(self, maximizing_player):
        val = 0
        if maximizing_player:
            val += self.scores[0] - self.scores[1]
            val += self.number_pf_legal_moves(self.my_pos)
            val += 1 / self.min_dist_to_fruit[0]
            val += self.rival_min_dist_to_fruit[0]
        else:
            val -= self.scores[1] - self.scores[0]
            val -= self.number_pf_legal_moves(self.rival_pos)
            val -= 1 / self.rival_min_dist_to_fruit[0]
            val -= self.min_dist_to_fruit[0]

        return val

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
    state.board[new_pos[0]][new_pos[1]] = (not maximizing_player) + 1


def goal(state, maximizing_player):
    if not state.have_valid_move_check(maximizing_player):
        if state.have_valid_move_check(not maximizing_player):
            state.scores[not maximizing_player] -= state.penalty_score
        return True
    return False


def succ(state, maximizing_player):
    succ = []
    for op_move in state.directions:
        if maximizing_player:
            i = state.my_pos[0] + op_move[0]
            j = state.my_pos[1] + op_move[1]
        else:
            i = state.rival_pos[0] + op_move[0]
            j = state.rival_pos[1] + op_move[1]

        if 0 <= i < len(state.board) and 0 <= j < len(state.board[0]) and (state.board[i][j] not in [-1, 1, 2]):
            succ.append(op_move)

    if len(succ) == 0 and state.have_valid_move_check(not maximizing_player):
        state.scores[not maximizing_player] -= state.penalty_score

    state.turns_till_fruit_gone -= 1
    if state.turns_till_fruit_gone == 0:
        for r, row in enumerate(state.board):
            for c, num in enumerate(row):
                if state.board[r][c] > 2:
                    # this is fruit
                    state.board[r][c] = 0
    return succ


def utility(state, score_or_heuristic):
    if score_or_heuristic:
        return state.scores[0] - state.scores[1]  # TODO maybe mul 10 or 100
    #     if self.scores[0] - self.scores[1] > 0:  # TODO
    #         return float('inf')  # if the player will win - so go for it!
    #     else:
    #         return self.scores[0] - self.scores[1]

    val = 0
    if state.scores[0] - state.penalty_score > state.scores[1] and state.number_pf_legal_moves(state.rival_pos) == 0:
        val += (state.scores[0] - state.scores[1]) * 10
    elif state.scores[0] - state.scores[1] > 0:
        val += (state.scores[0] - state.scores[1]) * 3 / (state.max_turns - state.turns)
    elif state.scores[0] == state.scores[1]:
        val += 0
    else:
        val += state.scores[0] - state.scores[1]

    val += state.number_pf_legal_moves(state.my_pos) + (4 - state.number_pf_legal_moves(state.rival_pos))

    val += len(state.board)*len(state.board[0]) / state.min_dist_to_fruit[0]

    return val


    # else:  # alternate heuristic
    #     val = state.scores[0] - state.scores[1]
    #     if val > state.penalty_score:
    #         val *= 2
    #     tmp1 = state.number_pf_legal_moves(state.my_pos)
    #     tmp2 = state.number_pf_legal_moves(state.rival_pos)
    #     if tmp1 != 0 and tmp2 == 0:
    #         return val + state.penalty_score
    #     val += (tmp1 - tmp2)*4
    #     val += (1 / state.min_dist_to_fruit[0])*2 ## TODO
    #     val -= (1 / state.rival_min_dist_to_fruit[0])
    #     # print(val)
    #     return val

    # return self.heuristic(maximizing_player)  # TODO