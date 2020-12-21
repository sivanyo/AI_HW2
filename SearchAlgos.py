"""Search Algo: MiniMax, AlphaBeta
"""
from utils import ALPHA_VALUE_INIT, BETA_VALUE_INIT
# TODO: you can import more modules, if needed
import copy


class SearchAlgos:
    def __init__(self, utility, succ, perform_move, goal):
        """The constructor for all the search algos.
        You can code these functions as you like to, 
        and use them in MiniMax and AlphaBeta algos as learned in class
        :param utility: The utility function.
        :param succ: The succesor function.
        :param perform_move: The perform move function.
        :param goal: function that check if you are in a goal state.
        """
        self.utility = utility
        self.succ = succ
        self.perform_move = perform_move
        self.goal = goal

    def search(self, state, depth, maximizing_player):
        pass


class MiniMax(SearchAlgos):

    def search(self, state, depth, maximizing_player):
        """Start the MiniMax algorithm.
        :param state: The state to start from.
        :param depth: The maximum allowed depth for the algorithm.
        :param maximizing_player: Whether this is a max node (True) or a min node (False).
        :return: A tuple: (The min max algorithm value, The direction in case of max node or None in min mode)
        """
        if self.goal(maximizing_player):
            return self.utility(maximizing_player, True), None

        if depth <= 0:
            return self.utility(maximizing_player, False), None

        succ_moves = self.succ(maximizing_player)

        if maximizing_player:
            best_val = float('-inf')
            best_move = None
            for move in succ_moves:
                state_copy = copy.deepcopy(state)
                state_copy.perform_move(True, move)
                minimax_algo = MiniMax(state_copy.utility, state_copy.succ, state_copy.perform_move, state_copy.goal)
                val = minimax_algo.search(state_copy, depth - 1, False)
                if val[0] > best_val:
                    best_val = val[0]
                    best_move = move
            return best_val, best_move

        else:
            worst_val = float('inf')
            worst_move = None
            for move in succ_moves:
                state_copy = copy.deepcopy(state)
                state_copy.perform_move(False, move)
                minimax_algo = MiniMax(state_copy.utility, state_copy.succ, state_copy.perform_move, state_copy.goal)
                val = minimax_algo.search(state_copy, depth - 1, True)
                if val[0] < worst_val:
                    worst_val = val[0]
                    worst_move = move
            return worst_val, worst_move


class AlphaBeta(SearchAlgos):

    # TODO in the PDF they said we should get another parameters like game_time instead depth
    def search(self, state, depth, maximizing_player, alpha=float('-inf'), beta=float('inf')):
        """Start the AlphaBeta algorithm.
        :param state: The state to start from.
        :param depth: The maximum allowed depth for the algorithm.
        :param maximizing_player: Whether this is a max node (True) or a min node (False).
        :param alpha: alpha value
        :param: beta: beta value
        :return: A tuple: (The min max algorithm value, The direction in case of max node or None in min mode)
        """

        if self.goal(maximizing_player):  # TODO
            return self.utility(maximizing_player, True), None

        if depth <= 0:  # TODO
            return self.utility(maximizing_player, False), None

        succ_moves = self.succ(maximizing_player)

        if maximizing_player:  # max player
            best_val = float('-inf')
            best_move = None
            for move in succ_moves:
                state_copy = copy.deepcopy(state)
                state_copy.perform_move(True, move)
                search_algo = AlphaBeta(state_copy.utility, state_copy.succ, state_copy.perform_move, state_copy.goal)
                val = search_algo.search(state_copy, depth - 1, False, alpha, beta)
            #     if val[0] > best_val:  # TODO another option (same for mini). lets talk about it
            #         best_val = val[0]
            #         best_move = move
            #     alpha = max(alpha, best_val)
            #     if beta <= alpha:
            #         return float('inf'), None
            # return best_val, best_move
                if val[0] is not None and val[0] > best_val:  # TODO another option (same for mini). lets talk about it
                    best_val = val[0]
                    best_move = move
                alpha = max(alpha, best_val)
                if beta <= alpha:
                    return None, None
            return best_val, best_move

        else:  # min player
            worst_val = float('inf')
            worst_move = None
            for move in succ_moves:
                state_copy = copy.deepcopy(state)
                state_copy.perform_move(False, move)
                search_algo = AlphaBeta(state_copy.utility, state_copy.succ, state_copy.perform_move, state_copy.goal)
                val = search_algo.search(state_copy, depth - 1, True, alpha, beta)
                if val[0] is not None and val[0] < worst_val:
                    worst_val = val[0]
                    worst_move = move
                beta = min(beta, worst_val)
                if beta <= alpha:
                    return None, None
            return worst_val, worst_move
