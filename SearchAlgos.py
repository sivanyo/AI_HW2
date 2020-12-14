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
        if depth is 0:
            return 0  # TODO!!!!
            #return self.utility(state, maximizing_player), None
        # i add state param here
        succ_moves = self.succ(state, maximizing_player)
        if len(succ_moves) == 0:
            return self.goal(), None

        if maximizing_player:
            best_val = float('-inf')
            best_move = None
            print("MAX. lets choose between: ", succ_moves)
            for move in succ_moves:
                state_copy = copy.deepcopy(state)
                self.perform_move(state_copy, move)
                val = self.search(state_copy, depth-1, False)
                if val[0] > best_val:
                    best_val = val[0]
                    best_move = move
                print("MAX. i chose in :", best_move)
                return best_val, best_move
        else:
            worst_val = float('inf')
            worst_move = None
            print("MIN. lets choose between: ", succ_moves)
            for move in succ_moves:
                state_copy = copy.deepcopy(state)
                self.perform_move(state_copy, move)
                val = self.search(state_copy, depth-1, True)
                if val[0] < worst_val:
                    worst_val = val[0]
                    worst_move = move
                print("MIN. i chose in :", worst_move)
                return worst_val, worst_move

        #
        # if maximizing_player:
        #     # max node
        #     best_val = -float('inf')
        #     best_move = None
        #     for d in self.succ(state):
        #         val = self.search(d, depth-1, not maximizing_player)
        #         if val[0] > best_val:
        #             best_val = val[0]
        #             best_move = val[1]
        #     self.perform_move(best_move)
        #     return best_val, best_move
        # else:
        #     # min node
        #     worst_val = float('inf')
        #     worst_move = None
        #     for d in self.succ(state):
        #         val = self.search(d, depth-1, not maximizing_player)
        #         if val[0] < worst_val:
        #             worst_val = val[0]
        #             worst_move = val[1]
        #     self.perform_move(worst_move)
        #     return worst_val, worst_move


class AlphaBeta(SearchAlgos):

    def search(self, state, depth, maximizing_player, alpha=ALPHA_VALUE_INIT, beta=BETA_VALUE_INIT):
        """Start the AlphaBeta algorithm.
        :param state: The state to start from.
        :param depth: The maximum allowed depth for the algorithm.
        :param maximizing_player: Whether this is a max node (True) or a min node (False).
        :param alpha: alpha value
        :param: beta: beta value
        :return: A tuple: (The min max algorithm value, The direction in case of max node or None in min mode)
        """
        #TODO: erase the following line and implement this function.
        raise NotImplementedError
