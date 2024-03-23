"""
Tic Tac Toe Player
"""

import math
import copy
from collections import Counter

X = "X"
O = "O"
EMPTY = None

class InvalidAction(Exception):
    def __init__(self, message):
        self.message = message

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    cnt_x = 0
    cnt_o = 0
    for row in board:
        cnt_x += row.count(X)
        cnt_o += row.count(O)

    if cnt_x <= cnt_o:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = []
    for row_index, row in enumerate(board):
        for col_index, col in enumerate(row):
            if col == EMPTY:
                actions.append((row_index, col_index))
    
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    value = player(board)
    row, col = action

    if board[row][col] != None:
        raise InvalidAction("Invalid Action")
    
    new = copy.deepcopy(board)
    new[row][col] = value
    
    return new


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for sign in [X, O]:
        # check row
        for row in board:
            if row == [sign] * 3:
                return sign
            
        # check column
        for col in range(3):
            column = [board[x][col] for x in range(3)]
            if column == [sign] * 3:
                return sign
            
        # check diagonal
        if [board[i][i] for i in range(3)] == [sign] * 3:
            return sign
        
        if [board[i][~i] for i in range(3)] == [sign] * 3:
            return sign
        
    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True

    # Draw
    for line in board:
        for element in line:
            if element == EMPTY:
                return  False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if not winner(board):
        return 0
    elif winner(board) == X:
        return 1
    else:
        return -1

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    if player(board) == X:
        best_value = -math.inf
        optimal_action = None
        for action in actions(board):
            max = min_value(result(board, action))
            if max > best_value:
                best_value = max
                optimal_action = action
        return optimal_action
    elif player(board) == O:
        best_value = math.inf
        optimal_action = None
        for action in actions(board):
            min = max_value(result(board, action))
            if min < best_value:
                best_value = min
                optimal_action = action
        return optimal_action


def min_value(board):
    if terminal(board):
        return utility(board)

    min_v = math.inf
    for action in actions(board):
        min_v = min(min_v, max_value(result(board, action)))
    
    return min_v


def max_value(board):
    if terminal(board):
        return utility(board)

    max_v = -math.inf
    for action in actions(board):
        max_v = max(max_v, min_value(result(board, action)))
    
    return max_v